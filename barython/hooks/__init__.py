#!/usr/bin/env python3


import copy as copy_module
import logging
import shlex
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
        else:
            return self._subproc

    def parse_event(self, event):
        """
        Parse event and return a kwargs meant be used by notify() then
        """
        return {"event": event, }

    def notify(self, *args, **kwargs):
        for c in self.callbacks:
            try:
                threading.Thread(target=c, args=args, kwargs=kwargs).start()
            except Exception as e:
                logger.debug("Error in hook: {}".format(e))
                continue

    def start(self, *args, **kwargs):
        self._stop.clear()
        return super().start(*args, **kwargs)

    def stop(self):
        self._stop.set()
        if self._subproc:
            try:
                self._subproc.terminate()
            except:
                pass

    def is_compatible(self, hook):
        return True

    def copy(self):
        new_h = copy_module.copy(self)
        new_h.callbacks = self.callbacks.copy()
        return new_h

    def __init__(self, callbacks=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.daemon = True

        #: list of callbacks to use during when notify
        self.callbacks = set()
        if callbacks is not None:
            self.callbacks.update(callbacks)

        #: event to stop the screen
        self._stop = threading.Event()


class SubprocessHook(_Hook):
    def run(self):
        self._subproc = self._init_subproc()
        while not self._stop.is_set():
            try:
                line = self._subproc.stdout.readline()
                notify_kwargs = self.parse_event(
                    line.decode().replace('\n', '').replace('\r', '')
                )
                self.notify(**notify_kwargs)
                self._subproc = self._init_subproc()
            except Exception as e:
                logger.error("Error when reading line: {}".format(e))
                try:
                    self._subproc.kill()
                except:
                    pass
                self._subproc = self._init_subproc()

    def __init__(self, cmd, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if isinstance(cmd, str):
            cmd = shlex.split(cmd)
        self.cmd = cmd
        self.shell = False


class HooksPool():
    def merge_with_panel_or_screen(self):
        if getattr(self, "parent", None):
            # if widget, adds to screens
            if getattr(self.parent, "screens", None):
                for s in self.parent.screens:
                    self.parent.s.hooks.merge(self)
            elif getattr(self.parent, "panel", None):
                self.parent.panel.hooks.merge(self)

    def merge(self, *pools):
        """
        Merge with another pool
        """
        def merge_hook(h, hook_class):
            compatible = None
            self_lst_hook = self.hooks.get(hook_class, None)
            if self_lst_hook:
                for self_h in self_lst_hook:
                    if self_h.is_compatible(h):
                        compatible = self_h
                        break
            else:
                self.hooks[hook_class] = []
            if compatible:
                compatible.callbacks.update(h.callbacks)
            else:
                new_h = h.copy()
                self.hooks[hook_class].append(new_h)
                if self.listen:
                    new_h.start()

        if not len(pools):
            return
        for pool in pools:
            for hook_class, hook in pool.hooks.items():
                for h in hook:
                    merge_hook(h, hook_class)

    def subscribe(self, callback, event, *args, **kwargs):
        """
        Subscribe to event, listened on by the panel
        """
        existing_hook = self.hooks.get(event, None)
        # check if our current *args and **kwargs are compatibles with the
        # existing hook, if any. If not, construct a new hook
        hook = event(*args, **kwargs, callbacks={callback, })
        compatible = None
        if existing_hook:
            for h in existing_hook:
                if h.is_compatible(hook):
                    compatible = h
                    break
        else:
            self.hooks[event] = []
        if compatible:
            compatible.callbacks.add(callback)
        else:
            self.hooks[event].append(hook)
            if self.listen:
                hook.start()
        self.merge_with_panel_or_screen()

    def stop(self):
        for hook in self.hooks.values():
            for h in hook:
                h.stop()

    def __init__(self, listen=False, parent=None, *args, **kwargs):
        #: Actually listen on these events or not
        self.listen = listen

        #: A pool will always be attached to a parent
        self.parent = parent

        #: Keys will be the event to listen on, values will be sets of
        #  callbacks
        self.hooks = dict()
