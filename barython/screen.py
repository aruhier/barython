#!/usr/bin/env python3

from collections import OrderedDict
import itertools
import logging
import threading
import time
import xcffib
import xcffib.xproto
import xcffib.randr

from barython import tools


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


class Screen():
    #: widgets to show on this screen
    _widgets = None
    #: used to limit the update
    _widgets_barrier = None
    #: refresh rate
    _refresh = 0
    #: bar geometry, in a tuple (x, y, position_x, position_y)
    _geometry = None
    _stop = False
    #: screen name
    name = None
    fg = None
    bg = None
    fonts = None
    height = 18
    offset = None
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

    def draw(self):
        """
        Draws the bar on the screen
        """
        def write_in_bar():
            self._bar.stdin.write(self.gather().encode())
            self._bar.stdin.flush()

        try:
            write_in_bar()
        except (BrokenPipeError, AttributeError):
            self.init_bar()
            write_in_bar()

    def gather(self):
        """
        Gather all widgets content
        """
        return "".join(
            "%{{{}}}{}".format(
                alignment, "".join([str(widget.content) for widget in widgets])
            ) for alignment, widgets in self._widgets.items() if widgets
        )

    def init_bar(self):
        """
        Spawn lemonbar and store the pipe in self._bar

        Before starting, tries to terminate self._bar in case of refresh
        """
        self.stop_bar()
        screen_geometry = self.geometry
        if screen_geometry:
            w, h, x, y = screen_geometry
            w -= self.offset[0] + self.offset[1]
            h = self.height
            x += self.offset[0]
            y += self.offset[2] - self.offset[3]
            geometry = (w, h, x, y)
        else:
            geometry = (None, self.height)
        self._bar = tools.lemonbar(
            bar_cmd=self.panel.bar_cmd, geometry=geometry, fonts=self.fonts,
            fg=self.fg, bg=self.bg
        )

    def stop_bar(self, kill=False):
        """
        Terminates or kill the bar
        """
        try:
            if kill:
                self._bar.kill()
            else:
                self._bar.terminate()
        except:
            pass

    def update(self):
        """
        Ask to redraw the screen or the global panel

        If more than one widget is waiting for the barrier, it is meaningless
        to wait too (because its value will be taken in account by the update
        ran by the waiting widget).
        A sleep is launched at the end to respect the refresh rate set for this
        Screen.
        """
        if self._widgets_barrier.n_waiting <= 1:
            self._widgets_barrier.wait()
            self.draw()
            time.sleep(self.refresh)

    def run(self):
        """
        Run the screen panel

        If the global panel set that there might be one instance per screen,
        starts a local lemonbar.
        Starts all widgets in there own threads. They will callback a screen
        update in case of any change.
        """
        self._stop = False
        if self.panel.instance_per_screen:
            self.init_bar()

        thread_pool = []
        for widget in itertools.chain(*self._widgets.values()):
            thread_pool.append(threading.Thread(
                target=widget.update
            ))
        # TODO: find a cleaner solution
        while not self._stop:
            time.sleep(self.refresh)
        self._bar.terminate()

    def stop(self):
        """
        Stop the screen
        """
        self._stop = True

    def __init__(self, name=None, refresh=None, offset=None, height=None,
                 geometry=None, panel=None):
        self.name = self.name if name is None else name
        if refresh:
            self._refresh = refresh
        self.panel = self.panel if panel is None else panel
        self.height = self.height if height is None else height
        self.offset = self.offset if offset is None else offset
        if self.offset is None:
            self.offset = (0, 0, 0, 0)
        self._widgets = OrderedDict([("l", []), ("c", []), ("r", [])])
        self._widgets_barrier = threading.Barrier(1)
