#!/usr/bin/env python3

import logging

from .base import SubprocessWidget
from barython.hooks.audio import PulseAudioHook


logger = logging.getLogger("barython")


class PulseAudioWidget(SubprocessWidget):
    def handler(self, event, *args, **kwargs):
        """
        Filter events sent by the notifications
        """
        # Only notify if there is something changes in pulseaudio
        event_change_msg = "Event 'change' on destination"
        if event_change_msg in event:
            logger.debug("PA: line \"{}\" catched.".format(event))
            return self.update()

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

    def __init__(self, cmd=["pulseaudio-ctl", "full-status"],
                 *args, **kwargs):
        super().__init__(cmd, infinite=False, *args, **kwargs)

        # Update the widget when PA volume changes
        self.hooks.subscribe(self.handler, PulseAudioHook)
