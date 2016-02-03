#!/usr/bin/env python3

import mpd
import time

from .base import ThreadedWidget


class MPDWidget(ThreadedWidget):
    """
    Requires python-mpd2
    """
    @property
    def status(self):
        try:
            r = self._mpdclient.status()["state"]
        except mpd.ConnectionError:
            self._mpdclient.connect(self.host, self.port)
            r = self._mpdclient.status()["state"]
        return r

    @property
    def current(self):
        try:
            r = self._mpdclient.currentsong()
        except mpd.ConnectionError:
            self._mpdclient.connect(self.host, self.port)
            r = self._mpdclient.currentsong()
        return r

    def password(self, value):
        self._mpdclient.password(value)

    def continuous_update(self):
        while True and not self._stop.is_set():
            try:
                self.update()
                time.sleep(self.refresh)
            except:
                time.sleep(self.refresh)

    def organize_result(self, status=None, current=None, running=True,
                        *args, **kwargs):
        """
        Override this method to change the infos to print
        """
        # avoid doing useless connections to mpd
        icon = self.icon
        if current:
            artist, title = current["artist"], current["title"]
        if icon:
            return (
                "{} {} - {}".format(icon, artist, title)
                if not current else "{}".format(icon)
            )
        else:
            return "{} - {}".format(artist, title)

    def update(self, *args, **kwargs):
        try:
            return self.trigger_global_update(
                self.organize_result(status=self.status, current=self.current)
            )
        except mpd.ConnectionError:
            return self.trigger_global_update(
                self.organize_result(running=False)
            )

    def __init__(self, host="localhost", port=6600, password=None,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.host = host
        self.port = port
        self._mpdclient = mpd.MPDClient()
        if password:
            self.password(password)
