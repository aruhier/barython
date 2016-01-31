#!/usr/bin/env python3


import logging
import subprocess
import threading


logger = logging.getLogger("barython")


class _Hook(threading.Thread):
    _subproc = None

    def _init_subproc(self):
        """
        Init a subproc to listen on an event
        """
        process_dead = (
            self._subproc is None or
            self._subproc.poll() is not None
        )
        if process_dead:
            logger.debug("Launching {}".format(" ".join(self.cmd)))
            return subprocess.Popen(
                self.cmd, stdout=subprocess.PIPE, shell=self.shell
            )

    def notify(self, *args, **kwargs):
        for c in self.callbacks:
            try:
                threading.Thread(target=c, args=args, kwargs=kwargs).start()
            except:
                continue

    def start(self, *args, **kwargs):
        self._stop.clear()
        return super().start(*args, **kwargs)

    def stop(self):
        self._stop.set()

    def __init__(self, callbacks=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.daemon = True

        #: list of callbacks to use during when notify
        self.callbacks = set()
        if callbacks is not None:
            self.callbacks.update(callbacks)

        #: event to stop the screen
        self._stop = threading.Event()


class HooksPool():
    def merge(self, *pools):
        """
        Merge with another pool
        """
        if not len(pools):
            return
        for pool in pools:
            for hook_class, hook in pool.hooks.items():
                for c in hook.callbacks:
                    self.subscribe(c, hook_class)

    def subscribe(self, callback, *events):
        """
        Subscribe to events, listened by the panel
        """
        for e in events:
            if self.hooks.get(e, None) is None:
                hook = e(callbacks={callback, })
                self.hooks[e] = hook
                if self.listen:
                    hook.start()
            else:
                self.hooks[e].callbacks.add(callback)
        is_attached_to_panel = (
            getattr(self, "parent", None) and
            getattr(self.parent, "panel", None)
        )
        if is_attached_to_panel:
            self.parent.panel.hooks.subscribe(callback, *events)

    def __init__(self, listen=False, parent=None, *args, **kwargs):
        #: Actually listen on these events or not
        self.listen = listen

        #: A pool will always be attached to a parent
        self.parent = parent

        #: Keys will be the event to listen on, values will be sets of
        #  callbacks
        self.hooks = dict()
