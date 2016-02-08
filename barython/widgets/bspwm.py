#!/usr/bin/env python3

import logging
import re
import time

from .base import Widget, protect_handler
from barython.hooks.bspwm import BspwmHook


logger = logging.getLogger("barython")


class BspwmDesktopWidget(Widget):
    """
    Show monitors and desktops, for bspwm
    """
    #: Associates desktops prefix and colors to define
    _desktop_colors_prefix = {
        "O": ("bg_focused_occupied", "fg_focused_occupied"),
        "o": ("bg_occupied", "fg_occupied"),
        "F": ("bg_focused_free", "fg_focused_free"),
        "f": ("bg_free", "fg_free"),
        "U": ("bg_focused_urgent", "fg_focused_urgent"),
        "u": ("bg_urgent", "fg_urgent"),
    }

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

    def _actions_desktop(self, desktop, *args, **kwargs):
        return {1: "bspc desktop -f {}".format(desktop)}

    def _actions_monitor(self, monitor, *args, **kwargs):
        return {1: "bspc monitor -f {}".format(monitor)}

    def _parse_monitor(self, m, prop):
        decorate_kwargs = {
            "text": m, "padding": self.padding,
            "actions": self._actions_monitor(m, prop)
        }
        if prop["focused"]:
            fg = self.fg_focused_monitor or self.fg
            bg = self.bg_focused_monitor or self.bg
        else:
            fg = self.fg_monitor or self.fg
            bg = self.bg_monitor or self.bg
        return self.decorate(fg=fg, bg=bg, **decorate_kwargs)

    def _parse_desktop(self, d, m):
        d_name = d[1:]
        decorate_kwargs = {
            "text": d_name, "padding": self.padding,
            "actions": self._actions_desktop(d_name, m)
        }

        bg, fg = self._desktop_colors_prefix.get(
            d[0], ("bg", "fg")
        )
        return self.decorate(
            fg=getattr(self, fg, None) or self.fg,
            bg=getattr(self, bg, None) or self.bg,
            **decorate_kwargs
        )

    def _get_focused_desktop(self, desktops):
        """
        Return the focused desktop in a list of desktops
        """
        starts_with_uppercase = re.compile(r"^[A-Z]")
        for d in desktops:
            if re.match(starts_with_uppercase, d):
                yield d[1:]

    def _parse_and_decorate(self, infos):
        for m, prop in infos.items():
            self._focused[m] = next(
                self._get_focused_desktop(prop["desktops"])
            )
            if len(list(infos.keys())) > 1:
                yield self._parse_monitor(m, prop)
            for d in prop["desktops"]:
                yield self._parse_desktop(d, m)

    def organize_result(self, monitors, *args, **kwargs):
        """
        Override this method to change the infos to print
        """
        return "".join(self._parse_and_decorate(monitors))

    def __init__(self, fg_occupied=None, bg_occupied=None,
                 fg_free=None, bg_free=None,
                 fg_urgent=None, bg_urgent=None,
                 fg_monitor=None, bg_monitor=None,
                 fg_current_monitor=None, bg_current_monitor=None,
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
        self.fg_monitor = fg_monitor

        #: background of the current monitor (the monitor where this widget is)
        self.bg_current_monitor = bg_current_monitor
        #: foreground of the current monitor (the monitor where this widget is)
        self.fg_current_monitor = fg_current_monitor

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
        self.fg_focused_monitor = fg_focused_monitor

        #: registered the focused desktop of each monitors
        self._focused = dict()

        # Update the widget when PA volume changes
        self.hooks.subscribe(self.handler, BspwmHook)


class BspwmDesktopPoolWidget(BspwmDesktopWidget):
    """
    Show desktops as a pool, for bspwm

    Doesn't show monitors, and targets setups where all monitors share a same
    pool of desktops. An order can be indicated, so the widget will be able to
    always show desktops in the same order (and will not fully respect the
    order returned by bspwm).
    """
    def _swap_desktop(self, target_d, target_m):
        """
        Swap desktop d of monitor m with the one on the current screen
        """
        current_m = next(iter(self.screens)).bspwm_monitor_name
        current_d = self._focused[current_m]
        return {1: "bspc desktop \"{}\" -s \"{}\"".format(target_d, current_d)}

    def _actions_desktop(self, target_d, target_m):
        # If attached to only one screen, swap the desktop of the current
        # screen with the one sent in parameter
        if len(self.screens) == 1:
            current_m = next(iter(self.screens)).bspwm_monitor_name
            if current_m != target_m and current_m in self._focused:
                return self._swap_desktop(target_d, target_m)
        # If attached to multiple screens, cannot know on which monitor the
        # widget is shown.
        return super()._actions_desktop(target_d, target_m)

    def _parse_and_decorate(self, infos):
        for m, prop in infos.items():
            self._focused[m] = next(
                self._get_focused_desktop(prop["desktops"])
            )
            for d in prop["desktops"]:
                yield self._parse_desktop(d, m)
