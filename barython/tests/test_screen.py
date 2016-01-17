
import pytest

from barython.screen import Screen
from barython.widgets.base import Widget


def test_screen():
    s = Screen()
    s.run()


def test_screen_add_widget():
    s = Screen()
    w = Widget()

    s.add_widget("l", w)
    assert s._widgets["l"][0] == w

    s.add_widget("c", w)
    assert s._widgets["c"][0] == w

    s.add_widget("r", w)
    assert s._widgets["r"][0] == w


def test_screen_add_widget_insert():
    """
    Test to add widget before specified index
    """
    s = Screen()
    w = Widget()
    s.add_widget("l", w)

    w1 = Widget()
    w2 = Widget()
    s.add_widget("l", w1, w2, index=0)

    assert s._widgets["l"][0] == w1
    assert s._widgets["l"][1] == w2
