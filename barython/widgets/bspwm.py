#!/usr/bin/env python3

import logging
import re

from .base import Widget, protect_handler
from barython.tools import splitted_sleep
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
    def handler(self, monitors, run=True, *args, **kwargs):
        """
        Filter events sent by notifications
        """
        if not run:
            return

        new_content = self.decorate_with_self_attributes(
            self.organize_result(monitors)
        )
        with self._lock_update:
            self._update_screens(new_content)
            splitted_sleep(self.refresh, stop=self._stop.is_set)

    def _actions_desktop(self, desktop, *args, **kwargs):
        return {1: "bspc desktop -f \"{}\"".format(desktop)}

    def _actions_monitor(self, monitor, *args, **kwargs):
        return {1: "bspc monitor -f \"{}\"".format(monitor)}

    def _sort_fixed_order(self, desktops_to_sort):
        """
        Return a copy of desktops but sorted in a fix order

        Useful if you swap your desktops and do not want the order to change.
        Uses the fixed_order attribute to sort desktops_to_sort.

        :param desktops_to_sort: list of desktops to reorder
        """
        d = desktops_to_sort.copy()
        # All desktops that are not in self._fixed_order will be put at the
        # end
        max_index = len(self.fixed_order)
        d.sort(key=lambda x: self.fixed_order.index(x[1:])
               if x[1:] in self.fixed_order else max_index)
        return d

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
            desktop_list = (self._sort_fixed_order(prop["desktops"])
                            if self.fixed_order else prop["desktops"])
            for d in desktop_list:
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
                 fixed_order=None, bspwm_version="0.9.2",
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

        #: fix order of desktop. Desktops will not be respect the bspwm order
        #  anymore, but the one specified here. All desktop that do not match
        #  will be put at the end, in respecting (this time) the bspwm order.
        self.fixed_order = fixed_order or []

        #: bspwm version
        self.bspwm_version = bspwm_version

        #: registered the focused desktop of each monitors
        self._focused = dict()

        # Update the widget when PA volume changes
        self.hooks.subscribe(
            self.handler, BspwmHook, bspwm_version=self.bspwm_version
        )


class BspwmDesktopPoolWidget(BspwmDesktopWidget):
    """
    Show desktops as a pool, for bspwm

    Doesn't show monitors, and targets setups where all monitors share a same
    pool of desktops. An order can be indicated, so the widget will be able to
    always show desktops in the same order (and will not fully respect the
    order returned by bspwm).
    """
    def _swap_desktop(self, target_d):
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
                return self._swap_desktop(target_d)
        # If attached to multiple screens, cannot know on which monitor the
        # widget is shown.
        return super()._actions_desktop(target_d, target_m)

    def _parse_desktop(self, d, m):
        if len(self.screens) == 1:
            current_m = next(iter(self.screens)).bspwm_monitor_name
            # If the desktop is focused on an other screen, ignore the focus.
            if current_m != m:
                d = d[0].lower() + d[1:]
        return super()._parse_desktop(d, m)

    def _sort_fixed_order(self, desktops_to_sort):
        """
        :param desktops_to_sort: here, is a list of tuple, [(d, m), ], with d
                                 the desktop, and m its monitor
        """
        d = desktops_to_sort.copy()
        # All desktops that are not in self._fixed_order will be put at the
        # end
        max_index = len(self.fixed_order)
        d.sort(key=lambda x: self.fixed_order.index(x[0][1:])
               if x[0][1:] in self.fixed_order else max_index)
        return d

    def _parse_and_decorate(self, infos):
        def get_desktops():
            for m, prop in infos.items():
                self._focused[m] = next(
                    self._get_focused_desktop(prop["desktops"])
                )
                for d in prop["desktops"]:
                    yield d, m

        desktop_list = (self._sort_fixed_order(list(get_desktops()))
                        if self.fixed_order else get_desktops())
        for d, m in desktop_list:
            yield self._parse_desktop(d, m)
