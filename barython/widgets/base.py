#!/usr/bin/env python3

import threading


class Widget():
    """
    Basic Widget
    """
    #: cache the content after update
    _content = None
    #: panel linked to
    panel = None
    #: background for the widget
    bg = None
    #: foreground for the widget
    fg = None
    #: padding
    padding = 0
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

        :param fg: foreground
        :param bg: background
        :param padding: padding around the text
        :param font: index of font to use
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

    def decorate_with_self_attributes(self, text, *args, **kwargs):
        """
        Return self.decorate but uses self attributes for default values
        """
        d_kwargs = {
            "fg": self.fg, "bg": self.bg, "padding": self.padding,
            "font": self.fonts[0] if self.fonts else None, **kwargs
        }
        for parameter, value in zip(("fg", "bg", "padding", "font"), args):
            d_kwargs[parameter] = value

        return self.decorate(text, **d_kwargs)

    def _update_panel(self, panel, new_content):
        """
        If content has changed, request the panel update
        """
        if self._content != new_content:
            self._content = new_content
            panel.update()

    def update(self, panel):
        pass

    def __init__(self, bg=None, fg=None, padding=0, fonts=None, refresh=0,
                 panel=None):
        self.bg = bg if bg else self.bg
        self.fg = fg if fg else self.fg
        self.fonts = fonts if fonts else self.fonts
        self.padding = padding if padding else self.padding
        self.refresh = refresh if refresh else self.refresh
        self.panel = panel


class TextWidget(Widget):
    text = ""

    def update(self):
        new_content = self.decorate_with_self_attributes(self.text)
        self._update_panel(new_content)

    def start(self):
        self.update()

    def __init__(self, text=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text = self.text if text is None else self.text


class ThreadedWidget(Widget):

    def start(self):
        if self.refresh == 0:
            self.refresh = self.panel.refresh
        t = threading.Thread(target=self.update)
        t.start()
