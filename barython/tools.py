#!/usr/bin/env python3

import logging
import subprocess


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
