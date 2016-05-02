#!/usr/bin/env python3

import logging
import mpd
import select

from . import _Hook
from barython.tools import splitted_sleep

logger = logging.getLogger("barython")


class MPDHook(_Hook):
    """
    Listen on MPD events
    """
    def parse_event(self, event=None, run=True):
        """
        Parse event and return a kwargs meant be used by notify() then
        """
        return {"event": event, "run": run}

    def run(self):
        # killed will be here to track the last state of the connection. We
        # start at True to force the first print.
        killed = True
        while not self._stop_event.is_set():
            try:
                if killed:
                    # test the connection and notify to force printing the
                    # current song, as idle() will wait for any change in mpd
                    self._mpdclient.ping()
                    self._mpdclient.send_idle()
                    try:
                        self.notify(**self.parse_event(run=True))
                    except Exception as e:
                        logger.error(e)
                    killed = False
                else:
                    # wait for any change in mpd and then notify
                    changes = select.select(
                        [self._mpdclient], [], [], self.refresh
                    )
                    if not changes[0]:
                        continue
                    notify_kwargs = self.parse_event(
                        self._mpdclient.fetch_idle()
                    )
                    try:
                        self.notify(**notify_kwargs)
                    except Exception as e:
                        logger.error(e)
                    self._mpdclient.send_idle()
            except:
                killed = True
                try:
                    self._mpdclient.connect(self.host, self.port)
                except:
                    logger.error(
                        "MPD is maybe not running or host/port are not correct"
                    )
                    try:
                        notify_kwargs = self.parse_event(run=False)
                        try:
                            self.notify(**notify_kwargs)
                        except Exception as e:
                            logger.error(e)
                    except:
                        pass
                finally:
                    splitted_sleep(self.refresh, stop=self._stop_event.is_set)

    def is_compatible(self, hook):
        return (
            hook.host == self.host and hook.port == self.port and
            hook.password == self.password
        )

    def stop(self):
        super().stop()
        try:
            self._mpdclient.close()
        except:
            pass
        self._mpdclient.noidle()
        self._mpdclient.disconnect()

    def __init__(self, host="localhost", port=6600, password=None, refresh=1,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.host = host
        self.port = port
        self._mpdclient = mpd.MPDClient()
        self.password = password
        if password:
            self._mpdclient.password(password)
        #: When mpd is not running, how many time to wait ? Default to 1s
        if refresh == -1:
            refresh = 1
        self.refresh = refresh
