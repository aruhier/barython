#!/usr/bin/env python3

import logging
import xpybutil

from .base import Widget
from barython.hooks.xorg import XorgHook


logger = logging.getLogger("barython")


class ActiveWindowWidget(Widget):
    """
    Requires python-mpd2
    """
    #: list of atom names to catch
    _atom_names = ("_NET_ACTIVE_WINDOW", "WM_NAME")

    @property
    def active_window_name(self):
        active_name = ""
        try:
            active_window = xpybutil.ewmh.get_active_window().reply()
            active_name = xpybutil.ewmh.get_wm_name(active_window).reply()
        except Exception as e:
            logger.error("Cannot get the active window name: {}".format(e))
        return active_name

    def handler(self, events, *args, **kwargs):
        for e, aname in events:
            print(aname)
            if aname in self._atom_names:
                return super().handler(*args, **kwargs)

    def update(self, *args, **kwargs):
        return self.trigger_global_update(
            self.organize_result(active_window=self.active_window_name)
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.infinite = False
        self.hooks.subscribe(self.handler, XorgHook, refresh=self.refresh)
