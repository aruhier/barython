#!/usr/bin/env python3


import logging
import os
import signal
import threading

from barython import _BarSpawner
from barython.screen import get_randr_screens


logger = logging.getLogger("barython")


class Panel(_BarSpawner):
    #: command for lemonbar
    bar_cmd = "lemonbar"

    @property
    def screens(self):
        return (self.clean_screens() if not self.keep_unplugged_screens else
                self._screens)

    def add_screen(self, *screens, index=None):
        """
        Add a screen to the panel

        :param alignment: where adding the screen (left, center, right)
        :param *screens: screens to add
        :param index: if set, will insert the screens before the specified
                      index (default: None)
        """
        for s in screens:
            self.hooks.merge(s.hooks)
            s.panel = self
            if not self.instance_per_screen:
                s.stop_bar()

        if index is None:
            self._screens.extend(screens)
        else:
            new_screen_list = (
                self._screens[:index] + list(screens) + self._screens[index:]
            )
            self._screens = new_screen_list

    def gather(self):
        """
        Gather all widgets content
        """
        return "%{S+}".join(screen.gather() for screen in self.screens)

    def clean_screens(self):
        """
        Clean unplugged screens

        If instance_per_screen, clean all screens without a geometry, otherwise
        stop iterating in screens when nb_randr_screens is reached
        """
        if self.instance_per_screen:
            for s in self._screens:
                if s.geometry:
                    yield s
        else:
            nb_randr_screens = len(get_randr_screens())
            for screen, i in zip(self._screens, range(nb_randr_screens)):
                yield screen

    def start(self):
        logging.debug("Starts the panel")
        for s in (signal.SIGINT, signal.SIGTERM, signal.SIGQUIT):
            signal.signal(s, self._handler_signal)

        super().start()

        # update to force drawing the bar
        if not self.instance_per_screen:
            self.update(no_wait=True)

        for screen in self.screens:
            threading.Thread(
                target=screen.start
            ).start()

        self._stop.wait()

    def stop(self, *args, **kwargs):
        super().stop(*args, **kwargs)
        if self.hooks.listen:
            try:
                self.hooks.stop()
            except:
                pass
        for screen in self.screens:
            try:
                screen.stop()
            except:
                continue

    def _handler_signal(self, *args, **kwargs):
        self.stop()
        os.sys.exit(0)

    def __init__(self, instance_per_screen=True, geometry=None, refresh=0.1,
                 screens=None, keep_unplugged_screens=False, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.hooks.listen = True

        #: screens attached to this panel
        self._screens = []
        if screens:
            self.add_screen(*screens)

        #: launch one bar per screen or use only one with %{S+}
        self.instance_per_screen = instance_per_screen

        #: doesn't start undetected/unplugged screens
        self.keep_unplugged_screens = keep_unplugged_screens

        #: refresh rate
        self.refresh = refresh

        #: geometry
        self.geometry = geometry
