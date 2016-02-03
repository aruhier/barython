#!/usr/bin/env python3


import logging
import signal
import threading

from barython import _BarSpawner


logger = logging.getLogger("barython")


class Panel(_BarSpawner):
    #: command for lemonbar
    bar_cmd = "lemonbar"

    def add_screen(self, *screens, index=None):
        """
        Add a screen to the panel

        :param alignment: where adding the screen (left, center, right)
        :param *screens: screens to add
        :param index: if set, will insert the screens before the specified
                      index (default: None)
        """
        if index is None:
            self._screens.extend(screens)
        else:
            new_screen_list = (
                self._screens[:index] + list(screens) + self._screens[index:]
            )
            self._screens = new_screen_list
        for s in self._screens:
            s.panel = self
            self.hooks.merge(s.hooks)

    def gather(self):
        """
        Gather all widgets content
        """
        return "%{S+}".join(
             screen.gather() for screen in self._screens
        )

    def start(self):
        logging.debug("Starts the panel")
        super().start()
        self._stop.clear()
        try:
            signal.signal(signal.SIGINT, self.stop)
        except ValueError:
            pass
        if not self.instance_per_screen:
            self.init_bar()
        for screen in self._screens:
            threading.Thread(
                target=screen.start
            ).start()
        self._stop.wait()
        for screen in self._screens:
            screen.stop()

    def stop(self, *args, **kwargs):
        super().stop(*args, **kwargs)
        for screen in self._screens:
            screen.stop()

    def __init__(self, instance_per_screen=True, geometry=None, refresh=0.1,
                 screens=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #: launch one bar per screen or use only one with %{S+}
        self.instance_per_screen = instance_per_screen

        #: refresh rate
        self.refresh = refresh

        #: screens attached to this panel
        self._screens = screens if screens is not None else []

        #: geometry
        self.geometry = geometry

        self.hooks.listen = True
