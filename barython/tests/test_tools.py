
import logging
import subprocess

import barython.tools
from barython.tools import lemonbar, splitted_sleep


logging.basicConfig(level=logging.DEBUG)


def test_lemonbar(monkeypatch):
    def mockpopen(cmd, *args, **kwargs):
        return cmd
    monkeypatch.setattr(subprocess, "Popen", mockpopen)

    launched_cmd = lemonbar(
        "lemonbar", geometry="250x250+5+5",
        fonts=[
            "DejaVu Sans Mono for Powerline:size=10",
            "FontAwesome:size=12"
        ], fg="#FFFFFFFF", bg="#FF000000", clickable=20, others=["-u", "2"]
    )
    expected_cmd = [
        "lemonbar", "-g", "250x250+5+5",
        "-f", "DejaVu Sans Mono for Powerline:size=10",
        "-f", "FontAwesome:size=12", "-F", "#FFFFFFFF", "-B", "#FF000000",
        "-a", "20", "-u", "2"
    ]

    assert launched_cmd == expected_cmd


def test_splitted_sleep(mocker):
    mocker.patch("barython.tools.time.sleep")
    mocker.spy(barython.tools.time, "sleep")
    splitted_sleep(2, 0.5)
    assert barython.tools.time.sleep.call_count == 4
