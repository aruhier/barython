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
    padding = 0
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
        return self._content

    def decorate(self, text, fg=None, bg=None, padding=0, font=None):
        """
        Decorate a text with custom properties
        """
        return (9*"{}").format(
            "%{{B{}}}".format(bg) if fg else "",
            "%{{F{}}}".format(fg) if fg else "",
            "%{{T{}}}".format(font) if font else "",
            " " * padding,
            text,
            " " * padding,
            "%{{T-}}".format(font) if font else "",
            "%{F-}" if fg else "",
            "%{B-}" if bg else ""
        )

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
                new_content = self.decorate(
                    self.text, fg=self.fg, bg=self.bg, padding=self.padding,
                    font=self.fonts[0] if self.fonts else None
                )
                if self._content != new_content:
                    self._content = new_content
                    panel.update()
                time.sleep(self.refresh)

        if self.refresh == 0:
            self.refresh = panel.refresh
        t = threading.Thread(target=thread_update)
        t.start()

    def __init__(self, text, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text = text if text else self.text
