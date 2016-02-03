
import logging
import time
import threading

from barython import tools
from barython.hooks import HooksPool


logger = logging.getLogger("barython")


class _BarSpawner():
    _cache = None

    def _write_in_bar(self, content):
        self._bar.stdin.write(content)
        logger.debug("Writing {}".format(content))
        self._bar.stdin.flush()

    def draw(self):
        """
        Draws the bar on the screen
        """
        content = (self.gather() + "\n").encode()
        if self._cache == content:
            return
        self._cache = content
        # if stopped, do not init lemonbar
        if not self._stop.is_set():
            try:
                self._write_in_bar(content)
            except (BrokenPipeError, AttributeError):
                logger.info("Lemonbar is off, init it")
                self.init_bar()
                self._write_in_bar(content)

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
            fg=self.fg, bg=self.bg, clickable=self.clickable
        )

    def start(self):
        self._cache = None
        self._stop.clear()
        self.hooks.start()

    def stop_bar(self, kill=False):
        """
        Terminates or kill the bar
        """
        try:
            if kill:
                self._bar.kill()
            else:
                self._bar.terminate()
            self._bar = None
        except:
            pass

    def stop(self, *args, **kwargs):
        """
        Stop the screen
        """
        self._stop.set()
        self.hooks.stop()
        self.stop_bar()

    def restart(self, *args, **kwargs):
        self.stop()
        threading.Thread(target=self.start).start()

    def __init__(self, offset=None, height=18, geometry=None, fg=None,
                 bg=None, fonts=None, clickable=10):
        #: used to limit the update
        self._update_lock = threading.Lock()

        self._refresh_lock = threading.Semaphore(2)
        #: event to stop the screen
        self._stop = threading.Event()
        self._stop.set()

        self.height = height
        self.offset = offset if offset is not None else (0, 0, 0)
        self.geometry = geometry
        self.fg = fg
        self.bg = bg
        self.fonts = fonts
        self.clickable = clickable

        self.hooks = HooksPool(parent=self)


from .panel import Panel
from .screen import Screen
