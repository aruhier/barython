
import logging
import time
import threading

from . import tools


logger = logging.getLogger("barython")


class _BarSpawner():
    #: used to limit the update
    _update_lock = None
    _refresh_lock = None
    #: event to stop the screen
    _stop = None
    fg = None
    bg = None
    fonts = None
    height = 18
    offset = None

    def draw(self):
        """
        Draws the bar on the screen
        """
        def write_in_bar():
            content = (self.gather() + "\n").encode()
            self._bar.stdin.write(content)
            logger.debug("Writing {}".format(content))
            self._bar.stdin.flush()

        try:
            write_in_bar()
        except (BrokenPipeError, AttributeError):
            logger.info("Lemonbar is off, init it")
            self.init_bar()
            write_in_bar()

    def gather(self):
        """
        Gather all widgets content
        """
        raise NotImplemented

    def update(self):
        """
        Ask to redraw the screen or the global panel

        If more than one widget is waiting for the barrier, it is meaningless
        to wait too (because its value will be taken in account by the update
        ran by the waiting widget).
        A sleep is launched at the end to respect the refresh rate set for this
        Screen.
        """
        locked = self._refresh_lock.acquire(blocking=False)
        # More than 2 threads are already here, doesn't make any sense to wait
        # because the screen will be updated
        if locked is False:
            return
        with self._update_lock:
            self.draw()
            time.sleep(self.refresh)
        self._refresh_lock.release()

    def init_bar(self):
        """
        Spawn lemonbar and store the pipe in self._bar

        Before starting, tries to terminate self._bar in case of refresh
        """
        self.stop_bar()
        screen_geometry = self.geometry
        if screen_geometry:
            w, h, x, y = screen_geometry
            w -= self.offset[0] + self.offset[1]
            h = self.height
            x += self.offset[0]
            y += self.offset[2]
            geometry = (w, h, x, y)
        else:
            geometry = (None, self.height)
        bar_cmd = getattr(self, "bar_cmd", None) or self.panel.bar_cmd
        self._bar = tools.lemonbar(
            bar_cmd=bar_cmd, geometry=geometry, fonts=self.fonts,
            fg=self.fg, bg=self.bg
        )

    def start(self):
        raise NotImplemented

    def stop_bar(self, kill=False):
        """
        Terminates or kill the bar
        """
        try:
            if kill:
                self._bar.kill()
            else:
                self._bar.terminate()
        except:
            pass

    def stop(self, *args, **kwargs):
        """
        Stop the screen
        """
        self._stop.set()
        self.stop_bar()

    def __init__(self, offset=None, height=None, geometry=None, fg=None,
                 bg=None, fonts=None):
        self.height = self.height if height is None else height
        self.offset = self.offset if offset is None else offset
        if self.offset is None:
            self.offset = (0, 0, 0)
        self.geometry = geometry
        self.fg = self.fg if fg is None else fg
        self.bg = self.bg if bg is None else bg
        self.fonts = self.fonts if fonts is None else fonts
        self._update_lock = threading.Lock()
        self._refresh_lock = threading.Semaphore(2)
        self._stop = threading.Event()


from .panel import Panel
from .screen import Screen
