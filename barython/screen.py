#!/usr/bin/env python3

from collections import OrderedDict
import itertools
import logging
import signal
import threading
import xcffib
import xcffib.xproto
import xcffib.randr

from barython import _BarSpawner


logger = logging.getLogger("barython")


def get_randr_screens():
    conn = xcffib.connect()
    conn.randr = conn(xcffib.randr.key)

    window = conn.get_setup().roots[0].root
    resources = conn.randr.GetScreenResourcesCurrent(window).reply()
    outputs = OrderedDict()

    for rroutput in resources.outputs:
        try:
            cookie = conn.randr.GetOutputInfo(
                rroutput, resources.config_timestamp
            )
            info = cookie.reply()
            name = "".join(map(chr, info.name))
            cookie = conn.randr.GetCrtcInfo(
                info.crtc, resources.config_timestamp
            )
            info = cookie.reply()
            if info:
                outputs[name] = (info.width, info.height, info.x, info.y)
        except Exception as e:
            logger.debug("Error when trying to fetch screens infos")
            logger.debug(e)
            continue
    return outputs


class Screen(_BarSpawner):
    @property
    def clickable(self):
        if self._clickable == -1 and self.panel is not None:
            return self.panel.clickable
        else:
            return self._clickable

    @clickable.setter
    def clickable(self, value):
        self._clickable = value

    @property
    def refresh(self):
        if self._refresh == -1 and self.panel is not None:
            return self.panel.refresh
        else:
            return self._refresh

    @refresh.setter
    def refresh(self, value):
        self._refresh = value

    @property
    def geometry(self):
        """
        Return the screen geometry in a tuple
        """
        if self._geometry:
            return self._geometry
        elif self.name:
            try:
                x, y, px, py = get_randr_screens().get(self.name, None)
                self._geometry = (x, self.height, px, py)
            except (ValueError, TypeError):
                logger.error(
                    "Properties of screen {} could not be fetched. Please "
                    "specify the geometry manually.".format(self.name)
                )
            return self._geometry

    @geometry.setter
    def geometry(self, value):
        self._geometry = value

    def add_widget(self, alignment, *widgets, index=None):
        """
        Add a widget to a screen

        :param alignment: where adding the widget (left, center, right)
        :param *widgets: widgets to add
        :param index: if set, will insert the widgets before the specified
                      index (default: None)
        """
        if alignment not in self._widgets.keys():
            raise ValueError("'alignement' might be either 'l', 'c' or 'r'")
        if index is None:
            self._widgets[alignment].extend(widgets)
        else:
            list_widgets = self._widgets[alignment]
            self._widgets[alignment] = (
                list_widgets[:index] + list(widgets) + list_widgets[index:]
            )
        for w in self._widgets[alignment]:
            w.screens.add(self)
            self.hooks.merge(w.hooks)

    def gather(self):
        """
        Gather all widgets content
        """
        return "".join(
            "%{{{}}}{}".format(
                alignment, "".join([
                    str(widget.content) if widget.content is not None
                    else "" for widget in widgets
                ])
            ) for alignment, widgets in self._widgets.items() if widgets
        )

    def update(self, *args, **kwargs):
        if self.panel.instance_per_screen:
            return super().update(*args, **kwargs)
        else:
            return self.panel.update()

    def start(self):
        """
        Start the screen panel

        If the global panel set that there might be one instance per screen,
        starts a local lemonbar.
        Starts all widgets in there own threads. They will callback a screen
        update in case of any change.
        """
        super().start()
        try:
            signal.signal(signal.SIGINT, self.stop)
        except ValueError:
            pass

        attached_widgets = list(itertools.chain(*self._widgets.values()))

        if self.panel.instance_per_screen:
            self.init_bar()
        elif len(attached_widgets) == 0:
            # No widget attached, no need to keep this thread opened
            # TODO: Add a test for it
            self.content = ""
            self.stop()
            return

        for widget in attached_widgets:
            threading.Thread(
                target=widget.start
            ).start()

        self._stop.wait()

    def stop(self, *args, **kwargs):
        super().stop(*args, **kwargs)
        for widget in itertools.chain(*self._widgets.values()):
            widget.stop()

    def __init__(self, name=None, refresh=-1, clickable=-1, geometry=None,
                 panel=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        #: screen name
        self.name = name

        #: refresh rate
        self._refresh = refresh

        #: clickable items (for lemonbar)
        self.clickable = clickable

        self.panel = panel

        #: bar geometry, in a tuple (x, y, position_x, position_y)
        self.geometry = geometry

        #: widgets to show on this screen
        self._widgets = OrderedDict([("l", []), ("c", []), ("r", [])])
