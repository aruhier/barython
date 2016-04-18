#!/usr/bin/env python3

from decimal import Decimal
import logging
import subprocess
import time


logging.getLogger("barython")


def lemonbar(bar_cmd="lemonbar", geometry=None, fonts=None, fg=None, bg=None,
             clickable=None, others=None):
    """
    Spawn a subprocess of lemonbar

    :param bar_cmd: path of command for lemonbar (default: lemonbar)
    :param geometry: -g option value, or a tuple of width, heigh, x, y
    :param fonts: list of fonts
    :param fg: foreground value
    :param bg: background value
    :param clickable: number of clickable areas
    :param others: list of additional options to join to the command
    """
    cmd = [bar_cmd, ]
    if geometry and isinstance(geometry, str):
        cmd.extend(("-g", geometry))
    elif geometry:
        w, h, x, y = (
            [i if i is not None else "" for i in geometry] +
            ["", ]*(4 - len(geometry))
        )
        cmd.extend(("-g", "{}x{}+{}+{}".format(w, h, x, y)))
    if fonts:
        for f in fonts:
            cmd.extend(("-f", f))
    if fg:
        cmd.extend(("-F", fg))
    if bg:
        cmd.extend(("-B", bg))
    if clickable:
        cmd.extend(("-a", "{}".format(clickable)))
    if others:
        cmd.extend(others)
    logging.debug("Launch {}".format(cmd))
    bar = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    try:
        subprocess.Popen("bash", stdin=bar.stdout, stdout=subprocess.PIPE)
    except AttributeError:
        pass
    return bar


def splitted_sleep(time_sleep, interval=0.5, stop=None,
                   stop_args=[], stop_kwargs={}):
    """
    Launch many time.sleep() with little values to often check the
    condition sent

    In order to regularely check a condition and stop the sleep if needed,
    it will wait the wanted value with many time.sleep()

    .. warning:: If stop() takes a long time, the function will sleep more
                 time that what you actually want!

    :param time_sleep: time to sleep in total
    :param interval: interval between each time.sleep(), in seconds.
                     Default to 0.5 seconds.
    :param stop: function called between each interval. If returning True,
                 stop to sleep and exit, otherwise, continue.
    :param stop_args: args for stop()
    :param stop_kwargs: kwargs for stop()
    """
    time_sleep, interval = Decimal(str(time_sleep)), Decimal(str(interval))
    for i in range(int(time_sleep/interval)):
        time.sleep(interval)
        if stop is not None and stop(*stop_args, **stop_kwargs):
            return
    if time_sleep % interval:
        time.sleep(time_sleep % interval)
