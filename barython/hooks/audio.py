#!/usr/bin/env python3

import logging
import shlex

from . import _Hook

logger = logging.getLogger("barython")


class PulseAudioHook(_Hook):
    """
    Listen on pulseaudio events with pactl
    """
    def run(self):
        self._subproc = self._init_subproc()
        while not self._stop.is_set():
            try:
                line = self._subproc.stdout.readline()
                self.notify(
                    event=line.decode().replace('\n', '').replace('\r', '')
                )
            except Exception as e:
                logger.error("Error when reading line: {}".format(e))
                try:
                    self._subproc.kill()
                except:
                    pass
                self._subproc = self._init_subproc()

    def __init__(self, cmd=["pactl", "subscribe", "-n", "barython"],
                 *args, **kwargs):
        super().__init__(*args, **kwargs)

        if isinstance(cmd, str):
            cmd = shlex.split(cmd)
        self.cmd = cmd
        self.shell = False
