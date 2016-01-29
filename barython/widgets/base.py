#!/usr/bin/env python3

import fcntl
import logging
import os
import shlex
import subprocess
import threading
import time


logger = logging.getLogger("barython")


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
        if self._refresh == -1 and self.screens is not None:
            return min([screen.refresh for screen in self.screens])
        else:
            return max(0, self._refresh)

    @refresh.setter
    def refresh(self, value):
        self._refresh = value

    def decorate(self, text, fg=None, bg=None, padding=0, font=None,
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
        return (9*"{}").format(
            joined_actions,
            "%{{B{}}}".format(bg) if fg else "",
            "%{{F{}}}".format(fg) if fg else "",
            "%{{T{}}}".format(font) if font else "",
            text.center(len(text) + 2*padding),
            "%{{T-}}".format(font) if font else "",
            "%{F-}" if fg else "",
            "%{B-}" if bg else "",
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

    def organize_result(self, *args, **kwargs):
        """
        Organize the info to show with the splitted infos received

        Organize the panel without handling the decoration (fg, bg, etc…)
        Override this method to change the way the info is printed
        """
        return "".join(*args)

    def _update_screens(self, new_content):
        """
        If content has changed, request the screen update
        """
        if self._content != new_content:
            self._content = new_content
            for screen in self.screens:
                screen.update()

    def update(self):
        pass

    def start(self, *args, **kwargs):
        pass

    def stop(self, *args, **kwargs):
        pass

    def __init__(self, bg=None, fg=None, padding=0, fonts=None,
                 actions=None, refresh=-1, screens=None):
        #: background for the widget
        self.bg = bg

        #: foreground for the widget
        self.fg = fg

        #: list of fonts index used
        self.fonts = fonts if fonts is not None else tuple()

        #: dictionnary of actions
        self.actions = actions if actions is not None else dict()

        #: padding
        self.padding = padding

        #: refresh rate
        self.refresh = refresh

        #: screens linked. Used for callbacks
        self.screens = screens if screens is not None else set()

        self._lock_start = threading.Condition()


class TextWidget(Widget):
    text = ""

    def update(self):
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


class ThreadedWidget(Widget):
    def handle_result(self, output=None, *args, **kwargs):
        new_content = self.decorate_with_self_attributes(output)
        threading.Thread(
            target=self._update_screens, args=(new_content,)
        ).start()

    def update(self, *args, **kwargs):
        pass

    def start(self):
        self._stop.clear()
        with self._lock_start:
            self.update()

    def stop(self):
        self._stop.set()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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

    def update(self, *args, **kwargs):
        self._subproc = self._init_subprocess(self.cmd)
        while not self._stop.is_set():
            try:
                output = self._subproc.stdout.readline()
                finished = self._subproc.poll()
                if output != b"":
                    self.handle_result(self.organize_result(
                        output.decode().replace('\n', '').replace('\r', '')
                    ))
                if finished is not None and self.notify():
                    self._subproc = self._init_subprocess(self.cmd)
            except Exception as e:
                logger.error(e)
                try:
                    self._subproc.terminate()
                except:
                    pass
                self.notify()
                self._subproc = self._init_subprocess(self.cmd)
            finally:
                time.sleep(self.refresh)
        try:
            self._subproc.terminate()
        except:
            pass

    def stop(self, *args, **kwargs):
        super().stop(*args, **kwargs)
        try:
            self._subscribe_subproc.terminate()
        except:
            pass
        try:
            self._subproc.terminate()
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
