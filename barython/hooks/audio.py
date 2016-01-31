#!/usr/bin/env python3

import logging

from . import SubprocessHook

logger = logging.getLogger("barython")


class PulseAudioHook(SubprocessHook):
    """
    Listen on pulseaudio events with pactl
    """
    def __init__(self, cmd=["pactl", "subscribe", "-n", "barython"],
                 *args, **kwargs):
        super().__init__(*args, **kwargs, cmd=cmd)
