
import pytest
from barython import Panel, Screen
from barython.screen import get_randr_screens
from barython.widgets.base import TextWidget


@pytest.mark.needs_lemonbar
def test_empty_bar():
    """
    Test an empty bar
    """
    p = Panel()
    s = Screen()
    s.fg = "#FFFFFFFF"
    s.bg = "#FF000000"
    p.add_screen(s)
    w = TextWidget(text="test")
    w1 = TextWidget(text="test1")
    s.add_widget("l", w, w1)

    try:
        s.start()
    except KeyboardInterrupt:
        s.stop()


@pytest.mark.needs_lemonbar
def test_bar_per_screen():
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
        p.add_screen(s)
        s.add_widget("c", w, w1)

    try:
        p.start()
    except KeyboardInterrupt:
        p.stop()
