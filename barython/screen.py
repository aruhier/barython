#!/usr/bin/env python3

from collections import OrderedDict
import itertools
import threading
import time

from barython import tools


class Screen():
    #: widgets to show on this screen
    _widgets = None
    #: used to limit the update
    _widgets_barrier = None
    #: refresh rate
    _refresh = 0
    #: screen size
    _size = None
    #: screen name
    name = None
    fg = None
    bg = None
    fonts = None
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
    def size(self):
        if self._size:
            return self._size
        else:
            # TODO: shoud compute the screen size
            return None

    @size.setter
    def size(self, value):
        self._size = value

    def add_widget(self, alignment, *widgets, index=None):
        """
        Add a widget to a screen

        :param alignment: where adding the widget (left, center, right)
        :param *widgets: widgets to add
        :param index: if set, will insert the widgets before the specified
                      index (default: None)
        """
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
        pass

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
        try:
            self._bar.terminate()
        except:
            pass
        screen_size = self.size
        if screen_size:
            geometry = "{}x{}+{}+{}".format(
                screen_size[0] - self.offset[0],
                screen_size[1] - self.offset[1],
                *self.offset[2:]
            )
        else:
            geometry = None
        self._bar = tools.lemonbar(
            bar_cmd=self.panel.bar_cmd, geometry=geometry, fonts=self.fonts,
            fg=self.fg, bg=self.bg
        )

    def update(self):
        if self._widgets_barrier.n_waiting <= 1:
            self._widgets_barrier.wait()
            self.draw()
            time.sleep(self.refresh)

    def run(self):
        if self.panel.instance_per_screen:
            self.init_bar()

        thread_pool = []
        for widget in itertools.chain(*self._widgets.values()):
            thread_pool.append(threading.Thread(
                target=widget.update, daemon=True
            ))

    def __init__(self, name=None, refresh=None, offset=None, panel=None):
        self.name = self.name if name is None else name
        if refresh:
            self._refresh = refresh
        self.panel = self.panel if panel is None else panel
        self.offset = self.offset if offset is None else offset
        if self.offset is None:
            self.offset = (0, 0, 0, 0)
        self._widgets = OrderedDict([("l", []), ("c", []), ("r", [])])
        self._widgets_barrier = threading.Barrier(1)
