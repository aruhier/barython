
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
        p.add_screen(s)

        w = TextWidget("Test")
        s.add_widget("l", w)
        s.fg = "#FF000000"
        s.bg = "#FFFFFFFF"
        s.run()
    except KeyboardInterrupt:
        s.stop()
