#!/usr/bin/env python3

import fcntl
import logging
import os
import shlex
import subprocess
import threading
import time

from barython.hooks import HooksPool

logger = logging.getLogger("barython")


def protect_handler(handler):
    def handler_wrapper(self, *args, **kwargs):
        if not self._refresh_lock.acquire(blocking=False):
            return
        result = handler(self, *args, **kwargs)
        self._refresh_lock.release()
        return result
    return handler_wrapper


class Widget():
    """
    Basic Widget
    """
    #: cache the content after update
    _content = None
    _refresh = -1

    @property
    def content(self):
        return self._content

    @property
    def refresh(self):
        if self._refresh == -1 and self.screens:
            return min([screen.refresh for screen in self.screens])
        else:
            return max(0, self._refresh)

    @refresh.setter
    def refresh(self, value):
        self._refresh = value

    def decorate(self, text, fg=None, bg=None, padding=0, font=None, icon=None,
                 actions=None):
        """
        Decorate a text with custom properties

        :param fg: foreground
        :param bg: background
        :param padding: padding around the text
        :param font: index of font to use
        :param actions: dict of actions
        """
        try:
            joined_actions = "".join(
                "%{{A{}:{}:}}".format(a, cmd) for a, cmd in actions.items()
            )
        except (TypeError, AttributeError):
            joined_actions = ""
        # if colors are reset in text, padding will not have the good colors
        if padding:
            padding_str = self.decorate(padding * " ", fg=fg, bg=bg, font=font)
        else:
            padding_str = ""
        return (12*"{}").format(
            joined_actions,
            padding_str,
            "%{{B{}}}".format(bg) if bg else "",
            "%{{F{}}}".format(fg) if fg else "",
            "%{{T{}}}".format(font) if font else "",
            icon + " " if icon else "",
            text,
            "%{{T-}}".format(font) if font else "",
            "%{F-}" if fg else "",
            "%{B-}" if bg else "",
            padding_str,
            "%{A}" * len(actions) if actions else "",
        )

    def decorate_with_self_attributes(self, text, *args, **kwargs):
        """
        Return self.decorate but uses self attributes for default values
        """
        d_kwargs = {
            "fg": self.fg, "bg": self.bg, "padding": self.padding,
            "font": self.fonts[0] if self.fonts else None,
            "actions": self.actions, **kwargs
        }
        for parameter, value in zip(("fg", "bg", "padding", "font", "actions"),
                                    args):
            d_kwargs[parameter] = value

        return self.decorate(text, **d_kwargs)

    @protect_handler
    def handler(self, *args, **kwargs):
        """
        To use with hooks
        """
        with self._lock_update:
            self.update()
            time.sleep(self.refresh)

    def organize_result(self, *args, **kwargs):
        """
        Organize the info to show with the splitted infos received

        Organize the panel without handling the decoration (fg, bg, etc…)
        Override this method to change the way the info is printed
        """
        result = "{} ".format(self.icon) if self.icon else ""
        return result + "".join(*args)

    def _update_screens(self, new_content):
        """
        If content has changed, request the screen update
        """
        if self._content != new_content:
            self._content = new_content
            for screen in self.screens:
                threading.Thread(target=screen.update).start()

    def continuous_update(self):
        pass

    def update(self):
        pass

    def propage_hooks_changes(self):
        """
        Propage a change in the hooks pool
        """
        if getattr(self, "screens", None):
            for s in self.screens:
                s.hooks.merge(self)

    def start(self, *args, **kwargs):
        pass

    def stop(self, *args, **kwargs):
        pass

    def __init__(self, bg=None, fg=None, padding=0, fonts=None, icon="",
                 actions=None, refresh=-1, screens=None, infinite=False):
        #: background for the widget
        self.bg = bg

        #: foreground for the widget
        self.fg = fg

        #: list of fonts index used
        self.fonts = fonts if fonts is not None else tuple()

        #: icon to use. Can be a string or a dict for some widgets, where icon
        #  will depend about the current value.
        self.icon = icon

        #: dictionnary of actions
        self.actions = actions if actions is not None else dict()

        #: padding
        self.padding = padding

        #: refresh rate
        self.refresh = refresh

        #: screens linked. Used for callbacks
        self.screens = screens if screens is not None else set()

        #: pool of hooks
        self.hooks = HooksPool(parent=self)

        #: run in an infinite loop or not
        self.infinite = infinite

        self._lock_start = threading.Condition()
        self._lock_update = threading.Condition()
        self._refresh_lock = threading.Semaphore(2)


class TextWidget(Widget):
    text = ""

    def update(self):
        with self._lock_update:
            new_content = self.decorate_with_self_attributes(
                self.organize_result(self.text)
            )
            self._update_screens(new_content)

    def start(self):
        with self._lock_start:
            self.update()

    def __init__(self, text=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text = self.text if text is None else text
        self.infinite = False


class ThreadedWidget(Widget):
    def trigger_global_update(self, output=None, *args, **kwargs):
        new_content = self.decorate_with_self_attributes(output)
        self._update_screens(new_content)

    def continuous_update(self, *args, **kwargs):
        while True and not self._stop.is_set():
            self.update()
            time.sleep(self.refresh)

    def update(self, *args, **kwargs):
        pass

    def start(self):
        self._stop.clear()
        if not self._lock_start.acquire(blocking=False):
            return
        if self.infinite:
            self.continuous_update()
        else:
            return self.update()
        self._lock_start.release()

    def stop(self):
        self._stop.set()

    def __init__(self, infinite=True, *args, **kwargs):
        super().__init__(*args, **kwargs, infinite=infinite)
        #: event to stop the widget
        self._stop = threading.Event()


class SubprocessWidget(ThreadedWidget):
    """
    Run a subprocess in a loop
    """
    _subscribe_subproc = None
    _subproc = None

    def _no_blocking_read(self, output):
        """
        Set the output to be non blockant and read it
        """
        fd = output.fileno()
        fl = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
        try:
            result = output.read()
        except:
            result = b""
        fcntl.fcntl(fd, fcntl.F_SETFL, fl)
        return result

    def _init_subprocess(self, cmd):
        """
        Start cmd in a subprocess, and split it if needed
        """
        if self._stop.is_set():
            return None
        if isinstance(cmd, str):
            cmd = shlex.split(cmd)
        logger.debug("Launching {}".format(" ".join(cmd)))
        return subprocess.Popen(
            cmd, stdout=subprocess.PIPE, shell=self.shell
        )

    def _init_subscribe_subproc(self):
        process_dead = (
            self._subscribe_subproc is None or
            self._subscribe_subproc.poll() is not None
        )
        if process_dead:
            self._subscribe_subproc = self._init_subprocess(
                self.subscribe_cmd
            )

    def notify(self, *args, **kwargs):
        if self.subscribe_cmd:
            self._init_subscribe_subproc()
            self._subscribe_subproc.stdout.readline()
            # hack to flush the stdout
            try:
                self._no_blocking_read(self._subscribe_subproc.stdout)
            except:
                pass
        return True

    def continuous_update(self):
        while not self._stop.is_set():
            try:
                self.update()
            except Exception as e:
                logger.error(e)
                try:
                    self._subproc.terminate()
                except:
                    pass
            finally:
                time.sleep(self.refresh)
                self.notify()
        try:
            self._subproc.terminate()
        except:
            pass

    def update(self, *args, **kwargs):
        with self._lock_update:
            self._subproc = self._init_subprocess(self.cmd)
            output = self._subproc.stdout.readline()
            if output != b"":
                self.trigger_global_update(self.organize_result(
                    output.decode().replace('\n', '').replace('\r', '')
                ))
            if self._subproc.poll() is not None:
                self._subproc = self._subproc.terminate()

    def stop(self, *args, **kwargs):
        super().stop(*args, **kwargs)
        try:
            self._subscribe_subproc.terminate()
            self._subscribe_subproc = self._subscribe_subproc.wait()
        except:
            pass
        try:
            self._subproc = self._subproc.terminate()
            self._subproc = self._subproc.wait()
        except:
            pass

    def __init__(self, cmd, subscribe_cmd=None, shell=False,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)

        #: command to run. Can be an iterable or a string
        self.cmd = cmd

        #: used as a notify: run the command, wait for any output, then run
        #  cmd.
        self.subscribe_cmd = subscribe_cmd

        #: value for the subprocess.Popen shell parameter. Default to False
        self.shell = shell
