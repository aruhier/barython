
import pytest
import barython
from barython import Panel, Screen
from barython.screen import get_randr_screens
from barython.widgets.base import TextWidget, SubprocessWidget
from barython.widgets import ClockWidget


@pytest.fixture
def disable_sigcatch(monkeypatch):
    monkeypatch.setattr(barython.panel, "SIG_TO_CATCH", ())


@pytest.mark.needs_lemonbar
def test_empty_bar(disable_sigcatch):
    """
    Test an empty bar
    """
    p = Panel(instance_per_screen=False)
    p.refresh = 0.2
    s = Screen()
    s.fg = "#FFFFFFFF"
    s.bg = "#FF000000"
    p.add_screen(s)
    w = TextWidget(text="test", actions={1: "urxvt&"})
    w1 = TextWidget(text="test1")
    s.add_widget("l", w, w1)

    system_date_descr = TextWidget(text="Date by subprocess: ")
    system_date = SubprocessWidget("/usr/bin/date", refresh=0.5)
    s.add_widget("c", system_date_descr, system_date)

    clock = ClockWidget()
    s.add_widget("r", clock)

    try:
        p.start()
    except KeyboardInterrupt:
        p.stop()


@pytest.mark.needs_lemonbar
def test_empty_global_bar(disable_sigcatch):
    """
    Test an empty bar
    """
    p = Panel(instance_per_screen=False)
    p.fg = "#FFFFFFFF"
    p.bg = "#FF000000"
    s = Screen()
    p.add_screen(s)
    w = TextWidget(text="test")
    w1 = TextWidget(text="test1")
    s.add_widget("l", w, w1)

    try:
        p.start()
    except KeyboardInterrupt:
        p.stop()


@pytest.mark.needs_lemonbar
def test_bar_per_screen(disable_sigcatch):
    """
    Test an empty bar
    """
    p = Panel()
    w = TextWidget(text="test")
    w1 = TextWidget(text="test1")
    for screen_name in get_randr_screens().keys():
        s = Screen(screen_name)
        s.fg = "#FFFFFFFF"
        s.bg = "#FF000000"
        s.add_widget("c", w, w1)
        p.add_screen(s)

    try:
        p.start()
    except KeyboardInterrupt:
        p.stop()
