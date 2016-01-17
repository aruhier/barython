#!/usr/bin/env python3

import itertools
import threading
import time


class Screen():
    _widgets_barrier = threading.Barrier(1)
    name = None
    panel = None
    _refresh = 0
    _widgets = {"l": list(), "c": list(), "r": list()}

    @property
    def refresh(self):
        if self._refresh == 0 and self.panel is not None:
            return self.panel.refresh
        else:
            return self._refresh

    @refresh.setter
    def refresh(self, value):
        self._refresh = value

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

    def draw(self):
        pass

    def update(self):
        if self._widgets_barrier.n_waiting <= 1:
            self._widgets_barrier.wait()
            self.draw()
            time.sleep(self.refresh)

    def run(self):
        thread_pool = []
        for widget in itertools.chain(*self._widgets.values()):
            thread_pool.append(threading.Thread(
                target=widget.update, daemon=True
            ))

    def __init__(self, name=None, refresh=None, panel=None):
        self.name = self.name if name is None else name
        if refresh:
            self._refresh = refresh
        self.panel = self.panel if panel is None else panel
