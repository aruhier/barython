#!/usr/bin/env python3

import logging
import time

from .base import SubprocessWidget


logger = logging.getLogger("barython")


class PulseAudioWidget(SubprocessWidget):
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

    def __init__(self, cmd=["pulseaudio-ctl", "full-status"],
                 subscribe_cmd=["pactl", "subscribe", "-n", "barython"],
                 *args, **kwargs):
        super().__init__(cmd, subscribe_cmd, *args, **kwargs)
        self.refresh = max(0, self.refresh - self._flush_time)
