#!/usr/bin/env python3

import itertools
import threading
import time


class Screen():
    _widgets_barrier = threading.Barrier(1)
    name = None
    panel = None
    refresh = 0.1
    _widgets = {"l": list(), "c": list(), "r": list()}

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
