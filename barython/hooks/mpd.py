#!/usr/bin/env python3

import logging
import mpd
import select

from . import _Hook
from barython.tools import splitted_sleep
from . import SubprocessHook

logger = logging.getLogger("barython")


class MPDHook(SubprocessHook):
    """
    Listen on MPD events
    """

    _name = "mpd"

    def __init__(self, cmd=["mpc", "idle"], failure_refresh=3, *args, **kwargs):
        super().__init__(*args, **kwargs, cmd=cmd, failure_refresh=failure_refresh)
