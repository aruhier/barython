#!/usr/bin/env python3

import logging
import mpd

from .base import ThreadedWidget
from barython.hooks.mpd import MPDHook


logger = logging.getLogger("barython")


class MPDWidget(ThreadedWidget):
    """
    Requires python-mpd2
    """
    _icon = None

    @property
    def icon(self):
        status = self.status
        no_icon = self._icon is None or not status
        if isinstance(self._icon, str) or no_icon:
            return self._icon
        global_icon = self._icon.get("global", None)
        return self._icon.get(status, global_icon)

    @icon.setter
    def icon(self, value):
        self._icon = value

    @property
    def status(self):
        try:
            r = self._mpdclient.status()["state"]
        except Exception:
            self._mpdclient.connect(self.host, self.port)
            r = self._mpdclient.status()["state"]
        return r

    @property
    def current(self):
        try:
            r = self._mpdclient.currentsong()
        except Exception:
            self._mpdclient.connect(self.host, self.port)
            r = self._mpdclient.currentsong()
        return r

    def password(self, value):
        self._mpdclient.password(value)

    def organize_result(self, status=None, current=None, running=True,
                        *args, **kwargs):
        """
        Override this method to change the infos to print
        """
        # avoid doing useless connections to mpd
        icon = self.icon
        if current:
            artist, title = current["artist"], current["title"]
        if not running:
            return "{}".format(icon) if icon else ""
        if icon:
            return (
                "{} {} - {}".format(icon, artist, title)
                if current else "{}".format(icon)
            )
        else:
            return "{} - {}".format(artist, title)

    def handler(self, event=None, run=True, *args, **kwargs):
        if not run:
            return self.trigger_global_update(
                self.organize_result(running=False)
            )
        return super().handler(event=event, run=run, *args, **kwargs)

    def update(self, *args, **kwargs):
        try:
            return self.trigger_global_update(
                self.organize_result(status=self.status, current=self.current)
            )
        except Exception as e:
            logger.debug(
                "MPD is not running or cannot be joined: {}".format(e)
            )
            return self.trigger_global_update(
                self.organize_result(running=False)
            )

    def __init__(self, host="localhost", port=6600, password=None,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.infinite = False
        self.host = host
        self.port = port
        self._mpdclient = mpd.MPDClient()
        if password:
            self.password(password)
        self.hooks.subscribe(
            self.handler, MPDHook, host=self.host, port=self.port,
            password=password, refresh=self.refresh
        )
