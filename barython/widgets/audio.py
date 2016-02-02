#!/usr/bin/env python3

from bisect import bisect_left
import logging

from .base import SubprocessWidget
from barython.hooks.audio import PulseAudioHook


logger = logging.getLogger("barython")


class PulseAudioWidget(SubprocessWidget):
    _icon = None
    _volume = 0
    _input_mute = False
    _output_mute = False

    @property
    def icon(self):
        # In case the icon is static
        if isinstance(self._icon, str) or self._icon is None:
            return self._icon
        elif self._output_mute and "ouput_mute" in self._icon:
            return self._icon["ouput_mute"]
        elif "volume" in self._icon:
            volume_icons = sorted(self._icon["volume"], key=lambda k: k[0])
            keys = [i[0] for i in volume_icons]
            return volume_icons[bisect_left(keys, self._volume, lo=1) - 1][1]

    @icon.setter
    def icon(self, value):
        self._icon = value

    def handler(self, event, *args, **kwargs):
        """
        Filter events sent by notifications
        """
        # Only notify if there is something changes in pulseaudio
        event_change_msg = "Event 'change' on destination"
        if event_change_msg in event:
            logger.debug("PA: line \"{}\" catched.".format(event))
            return self.update()

    def organize_result(self, output, *args, **kwargs):
        """
        Override this method to change the infos to print
        """
        volume, output_mute, input_mute = output.split()
        self._volume = int(volume)
        self._output_mute = output_mute == "yes"
        self._input_mute = input_mute == "yes"
        if self.icon:
            return (
                "{} {}".format(self.icon, self._volume)
                if not self._output_mute else "{}".format(self.icon)
            )
        else:
            return "{}".format(self._volume)

    def __init__(self, cmd=["pulseaudio-ctl", "full-status"],
                 *args, **kwargs):
        super().__init__(*args, **kwargs, cmd=cmd, infinite=False)

        # Update the widget when PA volume changes
        self.hooks.subscribe(self.handler, PulseAudioHook)
