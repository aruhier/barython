#!/usr/bin/env python3


import copy as copy_module
import logging
import os
import select
import shlex
import subprocess
import threading

from barython.tools import splitted_sleep


logger = logging.getLogger("barython")


class _Hook:
    _running_thread = None

    def parse_event(self, event):
        """
        Parse event and return a kwargs meant be used by notify() then
        """
        return {
            "event": event,
        }

    def notify(self, *args, **kwargs):
        for c in self.callbacks:
            try:
                threading.Thread(target=c, args=args, kwargs=kwargs).start()
            except Exception as e:
                logger.debug("Error in hook: {}".format(e))
                continue
        if self.refresh:
            splitted_sleep(self.refresh, stop=self._stop_event.is_set)

    def run(self, *args, **kwargs):
        raise NotImplementedError()

    def start(self, *args, **kwargs):
        if self._running_thread and self._running_thread.is_alive():
            raise threading.ThreadError("Thread already running")

        self._stop_event.clear()
        self._running_thread = threading.Thread(
            target=self.run, args=args, kwargs=kwargs, daemon=self.daemon
        )
        self._running_thread.start()

    def is_started(self):
        return not self._stop_event.is_set()

    def stop(self, *args, **kwargs):
        self._stop_event.set()
        if self._running_thread:
            self._running_thread.join()

    def is_compatible(self, hook):
        return True

    def copy(self):
        new_h = copy_module.copy(self)
        new_h.callbacks = self.callbacks.copy()
        new_h._running_thread = None
        return new_h

    def __init__(self, callbacks=None, refresh=0, failure_refresh=0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.daemon = False

        #: list of callbacks to use during when notify
        self.callbacks = set()
        if callbacks is not None:
            self.callbacks.update(callbacks)

        #: "protect" hook by providing the ability to wait between 2 notifies
        self.refresh = refresh
        #: time to wait between 2 failures
        self.failure_refresh = failure_refresh

        #: event to stop the screen. _stop_event because _stop interfers with
        #  the Thread attribute
        self._stop_event = threading.Event()
        self._stop_event.set()


class SubprocessHook(_Hook):
    _subproc = None
    _name = "Undefined"

    def _init_subproc(self):
        """
        Init a subproc to listen on an event
        """
        if self._stop_event.is_set():
            return None
        process_dead = self._subproc is None or self._subproc.poll() is not None
        if process_dead:
            logger.debug("Launching {}".format(" ".join(self.cmd)))
            return subprocess.Popen(
                self.cmd, stdout=subprocess.PIPE, shell=self.shell, env=self.env
            )
        else:
            return self._subproc

    def run(self):
        running = True
        while not self._stop_event.is_set():
            try:
                self._subproc = self._init_subproc()
                if self._subproc is None:
                    splitted_sleep(self.failure_refresh, stop=self._stop_event.is_set)
                    continue

                notify_kwargs = self.parse_event("")
                line = None
                if not running:
                    # Checks that the handler didn't crash by fetching a quick stdout.
                    lines = select.select([self._subproc.stdout], [], [], 0.1)[0]
                    if lines:
                        line = lines[0].readline()
                else:
                    line = self._subproc.stdout.readline()
                if line:
                    notify_kwargs.update(
                        self.parse_event(
                            line.decode().replace("\n", "").replace("\r", "")
                        )
                    )

                return_code = self._subproc.poll()
                if return_code is not None and return_code not in self.return_codes:
                    logger.error(
                        "Handler %s failed with return code %s",
                        self._name,
                        return_code,
                    )
                    running = False
                else:
                    running = True

                self.notify(run=running, **notify_kwargs)
            except Exception as e:
                logger.error("Error when reading line: {}".format(e))
                try:
                    self._subproc.kill()
                except:
                    pass
            finally:
                if not running:
                    splitted_sleep(self.failure_refresh, stop=self._stop_event.is_set)
        try:
            self._subproc.kill()
        except:
            pass

    def stop(self):
        self._stop_event.set()
        try:
            if self._subproc:
                self._subproc.terminate()
                self._subproc.wait()
        except Exception as e:
            logger.error("Error when shutting down {}: \n{}".format(self.__class__, e))
        super().stop()

    def __init__(self, cmd, return_codes=(0,), *args, **kwargs):
        super().__init__(*args, **kwargs)
        if isinstance(cmd, str):
            cmd = shlex.split(cmd)

        #: override environment variables to get the same output everywhere
        self.env = dict(os.environ)
        self.env["LANG"] = "en_US"
        self.cmd = cmd
        #: authorized return codes. By default, only 0 is accepted.
        self.return_codes = return_codes
        self.shell = False


class HooksPool:
    def propage_changes(self):
        """
        Propage changes to all parents of the current parent
        """
        if getattr(self, "parent", None):
            self.parent.propage_hooks_changes()

    def merge_hook(self, h, hook_class):
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

    def merge(self, *pools):
        """
        Merge with another pool
        """
        if not len(pools):
            return
        for pool in pools:
            for hook_class, hook in pool.hooks.items():
                for h in hook:
                    self.merge_hook(h, hook_class)
        self.propage_changes()

    def subscribe(self, callback, event, *args, **kwargs):
        """
        Subscribe to event, listened on by the panel
        """
        existing_hook = self.hooks.get(event, None)
        # check if our current *args and **kwargs are compatibles with the
        # existing hook, if any. If not, construct a new hook
        hook = event(
            *args,
            **kwargs,
            callbacks={
                callback,
            }
        )
        compatible = None
        if existing_hook:
            for h in (h for h in existing_hook if h.is_compatible(hook)):
                compatible = h
                break
        else:
            self.hooks[event] = []
        if compatible:
            compatible.callbacks.add(callback)
        else:
            self.hooks[event].append(hook)
        self.propage_changes()

    def start(self):
        if self.listen:
            for h in (h for hook in self.hooks.values() for h in hook):
                try:
                    if not h.is_started():
                        h.start()
                except Exception as e:
                    logger.error(
                        "Error when starting hook {}: {}".format(h.__class__, e)
                    )

    def stop(self):
        for h in (h for hook in self.hooks.values() for h in hook):
            try:
                h.stop()
                if h.is_started():
                    logger.error("Error when stopping hook {}".format(h.__class__))
            except Exception as e:
                logger.error("Error when stopping hook {}: {}".format(h.__class__, e))
                continue

    def __init__(self, listen=False, parent=None, *args, **kwargs):
        #: Actually listen on these events or not
        self.listen = listen

        #: A pool will always be attached to a parent
        self.parent = parent

        #: Keys will be the event to listen on, values will be sets of
        #  callbacks
        self.hooks = dict()
