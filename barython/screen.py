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
    outputs = {}

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
    #: widgets to show on this screen
    _widgets = None
    #: refresh rate
    _refresh = 0
    #: bar geometry, in a tuple (x, y, position_x, position_y)
    _geometry = None
    #: screen name
    name = None
    panel = None

    @property
    def refresh(self):
        if self._refresh == 0 and self.panel is not None:
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
        else:
            try:
                x, y, px, py = get_randr_screens().get(self.name, None)
                self._geometry = (x, self.height, px, py)
            except (ValueError, TypeError):
                logger.error(
                    "Properties of screen {} could not be fetched. Please "
                    "specify the geometry manually."
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

    def gather(self):
        """
        Gather all widgets content
        """
        return "".join(
            "%{{{}}}{}".format(
                alignment, "".join([str(widget.content) for widget in widgets])
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
        self._stop.clear()
        try:
            signal.signal(signal.SIGINT, self.stop)
        except ValueError:
            pass
        if self.panel.instance_per_screen:
            self.init_bar()

        for widget in itertools.chain(*self._widgets.values()):
            threading.Thread(
                target=widget.start, daemon=True
            ).start()

        self._stop.wait()

    def __init__(self, name=None, refresh=None, geometry=None, panel=None,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = self.name if name is None else name
        if refresh:
            self._refresh = refresh
        self.panel = self.panel if panel is None else panel
        self.geometry = geometry
        self._widgets = OrderedDict([("l", []), ("c", []), ("r", [])])
