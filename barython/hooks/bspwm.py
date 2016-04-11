#!/usr/bin/env python3

from collections import OrderedDict
import logging

from . import SubprocessHook

logger = logging.getLogger("barython")


class BspwmHook(SubprocessHook):
    """
    Subscribe to bspwm
    """
    def parse_event(self, event):
        """
        Parse event and return a kwargs meant be used by notify() then
        """
        monitors = OrderedDict()
        # remove the "W" at the begining of the status
        status = event[1:]
        parsed_status = status.split(":")
        for i in parsed_status:
            if i.startswith("M"):
                # focused monitor
                monitors[i[1:]] = {"focused": True, "desktops": []}
            elif i.startswith("m"):
                # unfocused monitor
                monitors[i[1:]] = {"focused": False, "desktops": []}
            elif i.startswith(("O", "o", "F", "f", "U", "u")):
                # desktop
                last_monitor = tuple(monitors.keys())[-1]
                monitors[last_monitor]["desktops"].append(i)
            elif i.startswith("L"):
                # layout
                last_monitor = tuple(monitors.keys())[-1]
                monitors[last_monitor]["layout"] = i[1:]
        return {"monitors": monitors}

    def __init__(self, bspwm_version="0.9", cmd=None, failure_refresh=1,
                 *args, **kwargs):
        if cmd is None:
            if bspwm_version == "0.9":
                cmd = ["bspc", "control", "--subscribe"]
            elif bspwm_version == "0.9.1":
                cmd = ["bspc", "subscribe", "report"]
        self.bspwm_version = bspwm_version
        super().__init__(*args, **kwargs, cmd=cmd,
                         failure_refresh=failure_refresh)
