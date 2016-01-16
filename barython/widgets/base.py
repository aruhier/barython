#!/usr/bin/env python3

import threading
import time


class Widget():
    """
    Basic Widget
    """
    #: cache the content after update
    _content = None
    #: padding
    padding = 1
    #: background for the widget
    bg = None
    #: foreground for the widget
    fg = None
    #: list of fonts index used
    fonts = tuple()
    #: refresh rate
    refresh = 0

    @property
    def content(self):
        return self._cache_content

    def update(self, panel):
        panel.update()

    def __init__(self, bg=None, fg=None, fonts=None, refresh=0):
        self.bg = bg if bg else self.bg
        self.fg = fg if fg else self.fg
        self.fonts = fonts if fonts else self.fonts
        self.refresh = refresh if refresh else self.refresh


class TextWidget(Widget):
    text = ""

    def update(self, panel):
        def thread_update():
            while True:
                new_content = "{}{}{}{}{}{}{}".format(
                    "%{{B{}}}".format(self.bg) if self.fg else None,
                    "%{{F{}}}".format(self.fg) if self.fg else None,
                    " " * self.padding,
                    self.text,
                    " " * self.padding,
                    "%{F-}" if self.fg else None,
                    "%{B-}" if self.bg else None
                )
                if self._content != new_content:
                    self._content = new_content
                    panel.update()
                time.sleep(self.refresh)

        if self.refresh == 0:
            self.refresh = panel.refresh
        t = threading.Thread(target=thread_update)
        t.run()

    def __init__(self, text, *args, **kwargs):
        super().__init__(args, **kwargs)
        self.text = text if text else self.text
