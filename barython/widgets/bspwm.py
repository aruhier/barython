#!/usr/bin/env python3

import logging
import time

from .base import Widget, protect_handler
from barython.hooks.bspwm import BspwmHook


logger = logging.getLogger("barython")


class BspwmDesktopWidget(Widget):
    @protect_handler
    def handler(self, monitors, *args, **kwargs):
        """
        Filter events sent by notifications
        """
        new_content = self.decorate_with_self_attributes(
            self.organize_result(monitors)
        )
        with self._lock_update:
            self._update_screens(new_content)
            time.sleep(self.refresh)

    def _actions_desktop(self, desktop):
        return {1: "bspc desktop -f {}".format(desktop)}

    def _actions_monitor(self, monitor):
        return {1: "bspc monitor -f {}".format(monitor)}

    def _parse_and_decorate(self, infos):
        for m, prop in infos.items():
            if len(list(infos.keys())) > 1:
                if prop["focused"]:
                    yield self.decorate(
                        m, fg=self.fg_focused_monitor or self.fg,
                        bg=self.bg_focused_monitor or self.bg,
                        padding=self.padding,
                        actions=self._actions_monitor(m),
                    )
                else:
                    yield self.decorate(
                        m, fg=self.fg_monitor or self.fg,
                        bg=self.bg_monitor or self.bg,
                        padding=self.padding,
                        actions=self._actions_monitor(m),
                    )
            for d in prop["desktops"]:
                d_name = d[1:]
                if d.startswith("O"):
                    yield self.decorate(
                        d_name, fg=self.fg_focused_occupied or self.fg,
                        bg=self.bg_focused_occupied or self.bg,
                        padding=self.padding,
                        actions=self._actions_desktop(d_name),
                    )
                elif d.startswith("o"):
                    yield self.decorate(
                        d_name, fg=self.fg_occupied or self.fg,
                        bg=self.bg_occupied or self.bg,
                        padding=self.padding,
                        actions=self._actions_desktop(d_name),
                    )
                elif d.startswith("F"):
                    yield self.decorate(
                        d_name, fg=self.fg_focused_free or self.fg,
                        bg=self.bg_focused_free or self.bg,
                        padding=self.padding,
                        actions=self._actions_desktop(d_name),
                    )
                elif d.startswith("f"):
                    yield self.decorate(
                        d_name, fg=self.fg_free or self.fg,
                        bg=self.bg_free or self.bg,
                        padding=self.padding,
                        actions=self._actions_desktop(d_name),
                    )
                elif d.startswith("U"):
                    yield self.decorate(
                        d_name, fg=self.fg_focused_urgent or self.fg,
                        bg=self.bg_focused_urgent or self.bg,
                        padding=self.padding,
                        actions=self._actions_desktop(d_name),
                    )
                elif d.startswith("u"):
                    yield self.decorate(
                        d_name, fg=self.fg_urgent or self.fg,
                        bg=self.bg_urgent or self.bg,
                        padding=self.padding,
                        actions=self._actions_desktop(d_name),
                    )

    def organize_result(self, monitors, *args, **kwargs):
        """
        Override this method to change the infos to print
        """
        return "".join(self._parse_and_decorate(monitors))

    def __init__(self, fg_occupied=None, bg_occupied=None,
                 fg_free=None, bg_free=None,
                 fg_urgent=None, bg_urgent=None,
                 fg_monitor=None, bg_monitor=None,
                 fg_focused_occupied=None, bg_focused_occupied=None,
                 fg_focused_free=None, bg_focused_free=None,
                 fg_focused_urgent=None, bg_focused_urgent=None,
                 fg_focused_monitor=None, bg_focused_monitor=None,
                 *args, **kwargs):
        super().__init__(*args, **kwargs, infinite=False)

        #: background occupied desktop
        self.bg_occupied = bg_occupied
        #: foreground occupied desktop
        self.fg_occupied = fg_occupied

        #: background free desktop
        self.bg_free = bg_free
        #: foreground free desktop
        self.fg_free = fg_free

        #: background urgent desktop
        self.bg_urgent = bg_urgent
        #: foreground urgent desktop
        self.fg_urgent = fg_urgent

        #: background monitor
        self.bg_monitor = bg_monitor
        #: foreground monitor
        self.fg_monitor = fg_urgent

        #: background focused occupied desktop
        self.bg_focused_occupied = bg_focused_occupied
        #: foreground focused occupied desktop
        self.fg_focused_occupied = fg_focused_occupied

        #: background focused free desktop
        self.bg_focused_free = bg_focused_free
        #: foreground focused free desktop
        self.fg_focused_free = fg_focused_free

        #: background focused urgent desktop
        self.bg_focused_urgent = bg_focused_urgent
        #: foreground focused urgent desktop
        self.fg_focused_urgent = fg_focused_urgent

        #: background focused monitor
        self.bg_focused_monitor = bg_focused_monitor
        #: foreground monitor
        self.fg_focused_monitor = fg_focused_urgent

        # Update the widget when PA volume changes
        self.hooks.subscribe(self.handler, BspwmHook)
