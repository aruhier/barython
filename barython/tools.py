#!/usr/bin/env python3

import logging
import subprocess


logging.getLogger("barython")


def lemonbar(bar_cmd="lemonbar", geometry=None, fonts=None, fg=None, bg=None,
             clickable=None, others=None):
    """
    Spawn a subprocess of lemonbar

    :param bar_cmd: path of command for lemonbar (default: lemonbar)
    :param geometry: -g option value
    :param fonts: list of fonts
    :param fg: foreground value
    :param bg: background value
    :param clickable: number of clickable areas
    :param others: list of additional options to join to the command
    """
    cmd = [bar_cmd, ]
    if geometry:
        cmd.extend(["-g", geometry])
    if fonts:
        for f in fonts:
            cmd.extend(["-f", f])
    if fg:
        cmd.extend(["-F", fg])
    if bg:
        cmd.extend(["-B", bg])
    if clickable:
        cmd.extend(["-a", clickable])
    if others:
        cmd.extend(others)
    logging.debug("Launch {}".format(cmd))
    return subprocess.Popen(cmd, stdin=subprocess.PIPE)
