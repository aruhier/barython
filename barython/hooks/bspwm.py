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
        notify_kwargs = OrderedDict()
        # remove the "W" at the begining of the status
        status = event[1:]
        parsed_status = status.split(":")
        for i in parsed_status:
            if i.startswith("M"):
                # focused monitor
                notify_kwargs[i[1:]] = {"focused": True, "desktops": []}
            elif i.startswith("m"):
                # unfocused monitor
                notify_kwargs[i[1:]] = {"focused": False, "desktops": []}
            elif i.startswith(("O", "o", "F", "f", "U", "u")):
                # desktop
                last_monitor = tuple(notify_kwargs.keys())[-1]
                notify_kwargs[last_monitor]["desktops"].append(i)
            elif i.startswith("L"):
                # layout
                last_monitor = tuple(notify_kwargs.keys())[-1]
                notify_kwargs[last_monitor]["layout"] = i[1:]
        return notify_kwargs

    def __init__(self, cmd=["bspc", "control", "--subscribe"],
                 *args, **kwargs):
        super().__init__(*args, **kwargs, cmd=cmd)
