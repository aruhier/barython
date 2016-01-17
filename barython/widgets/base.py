#!/usr/bin/env python3

import threading


class Widget():
    """
    Basic Widget
    """
    #: cache the content after update
    _content = None
    #: refresh rate
    _refresh = 0
    #: screens linked. Used for callbacks
    screens = None
    #: background for the widget
    bg = None
    #: foreground for the widget
    fg = None
    #: padding
    padding = 0
    #: list of fonts index used
    fonts = tuple()

    @property
    def content(self):
        return self._content

    @property
    def refresh(self):
        if self._refresh == 0 and self.screen is not None:
            return min([screen.refresh for screen in self.screens])
        else:
            return self._refresh

    @refresh.setter
    def refresh(self, value):
        self._refresh = value

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

    def _update_screen(self, new_content):
        """
        If content has changed, request the screen update
        """
        if self._content != new_content:
            self._content = new_content
            for screen in self.screens:
                screen.update()

    def update(self):
        pass

    def __init__(self, bg=None, fg=None, padding=None, fonts=None,
                 refresh=None, screens=None):
        self.bg = self.bg if bg is None else bg
        self.fg = self.fg if fg is None else fg
        self.fonts = self.fonts if fonts is None else fonts
        self.padding = self.padding if padding is None else padding
        if refresh is not None:
            self._refresh = refresh
        self.screens = self.screens if screens is None else self.screens
        if not self.screens:
            self.screens = []


class TextWidget(Widget):
    text = ""

    def update(self):
        new_content = self.decorate_with_self_attributes(self.text)
        self._update_screen(new_content)

    def start(self):
        self.update()

    def __init__(self, text=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text = self.text if text is None else text


class ThreadedWidget(Widget):

    def start(self):
        if self.refresh == 0:
            self.refresh = self.screen.refresh
        t = threading.Thread(target=self.update)
        t.start()
