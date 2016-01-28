#!/usr/bin/env python3


import logging
import threading


logger = logging.getLogger("barython")


class _Hook(threading.Thread):
    #: list of callbacks
    callbacks = None

    def notify(self, *args, **kwargs):
        for c in self.callbacks:
            try:
                threading.Thread(target=c, args=args, kwargs=kwargs).start()
            except:
                continue

    def __init__(self, callbacks=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.callbacks = []
        if callbacks is not None:
            self.callbacks.extend(callbacks)
