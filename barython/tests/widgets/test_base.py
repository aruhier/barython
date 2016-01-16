
import pytest

from barython.panel import Panel
from barython.widgets.base import Widget


def test_base_widget_construction():
    Widget()


def test_base_widget_decorate_simple():
    """
    Test the decorate function of Widget without any parameter
    """
    w = Widget()
    text = "test"

    assert w.decorate(text) == text, (
        "text and decoration with no parameter should be equals"
    )


def test_base_widget_decorate():
    """
    Test the decorate function of Widget
    """
    w = Widget()
    text = "test"
    fg = "#FFFF11"
    bg = "#FF9021"
    font = 1
    padding = 2

    decorated_text = w.decorate(
        text, fg=fg, bg=bg, font=font, padding=padding
    )
    expected_result = (
        "%{{B{}}}%{{F{}}}%{{T{}}}  {}  %{{T-}}%{{F-}}%{{B-}}".format(
            bg, fg, font, text
        )
    )
    assert decorated_text == expected_result
