#!/usr/bin/env python3

import logging

from .base import SubprocessWidget


logger = logging.getLogger("barython")


class PulseAudioWidget(SubprocessWidget):
    #: command to run. Can be an iterable or a string
    cmd = ["pulseaudio-ctl", "full-status"]
    #: used as a notify: run the command, wait for any output, then run cmd.
    subscribe_cmd = ["pactl", "subscribe", "-n", "barython"]
    _flush_time = 0.3

    def handle_result(self, output=None, *args, **kwargs):
        # As pulseaudio-ctl add events in pactl subscribe, flush output
        try:
            self._subscribe_subproc.communicate(timeout=self._flush_time)
        except:
            pass
        try:
            if output != "" and output is not None:
                volume, output_mute, _ = output.split()
                output = volume
            return super().handle_result(output=output)
        except Exception as e:
            logger.error("Error in PulseAudioWidget: {}", e)

    def __init__(self, refresh=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # As we wait self.flush_time seconds when flushing the output,
        if refresh is None:
            refresh = 0
        self.refresh = max(0, refresh - self._flush_time)
