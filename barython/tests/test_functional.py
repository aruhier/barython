
import pytest
from barython import Panel, Screen
from barython.widgets.base import TextWidget


@pytest.mark.needs_lemonbar
def test_empty_bar():
    """
    Test an empty bar
    """
    try:
        p = Panel()
        s = Screen()
        s.fg = "#FFFFFFFF"
        s.bg = "#FF000000"
        p.add_screen(s)
        w = TextWidget(text="test")
        w1 = TextWidget(text="test1")
        s.add_widget("l", w, w1)
        s.start()
    except KeyboardInterrupt:
        s.stop()
