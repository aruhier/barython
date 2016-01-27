#!/usr/bin/env python3

import logging
import time

from .base import SubprocessWidget


logger = logging.getLogger("barython")


class PulseAudioWidget(SubprocessWidget):
    #: command to run. Can be an iterable or a string
    cmd = ["pulseaudio-ctl", "full-status"]
    #: used as a notify: run the command, wait for any output, then run cmd.
    subscribe_cmd = ["pactl", "subscribe", "-n", "barython"]
    #: this value should be changed if something produces a lot of pulseaudio
    #  events
    _flush_time = 0.05

    def notify(self, *args, **kwargs):
        if self.subscribe_cmd:
            self._init_subscribe_subproc()
            while not self._stop.is_set():
                try:
                    line = self._subscribe_subproc.stdout.readline()
                    # Only notify if there is something changes in pulseaudio
                    event_change_msg = b"Event 'change' on destination"
                    if event_change_msg in line:
                        logger.debug("PA: line \"{}\" catched.".format(line))
                        return True
                except Exception as e:
                    logger.error("Error when reading line: {}".format(e))
                    self._init_subscribe_subproc()
        return True

    def organize_result(self, volume, output_mute=None, input_mute=None,
                        *args, **kwargs):
        """
        Override this method to change the infos to print
        """
        return "{}".format(volume)

    def handle_result(self, output=None, *args, **kwargs):
        # As pulseaudio-ctl add events in pactl subscribe, flush output
        try:
            if output != "" and output is not None:
                output = self.organize_result(*output.split())
            super().handle_result(output=output)
        except Exception as e:
            logger.error("Error in PulseAudioWidget: {}", e)
        if self._flush_time:
            time.sleep(self._flush_time)
            self._no_blocking_read(self._subscribe_subproc.stdout)

    def __init__(self, refresh=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # As we wait self.flush_time seconds when flushing the output,
        if refresh is None:
            refresh = 0
        self.refresh = max(0, refresh - self._flush_time)
