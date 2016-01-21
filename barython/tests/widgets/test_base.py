
import pytest

from barython.screen import Screen
from barython.widgets.base import Widget


def test_base_widget_construction():
    Widget(fg="#FFFF11", bg="#FF9021", padding=1, fonts=[1, 2], refresh=2,
           screens=[Screen(), ])


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
    actions = {1: "firefox&", 3: "urxvt&"}

    decorated_text = w.decorate(
        text, fg=fg, bg=bg, font=font, padding=padding, actions=actions
    )
    expected_result = (
        "%{{A1:firefox&:}}%{{A3:urxvt&:}}%{{B{}}}%{{F{}}}%{{T{}}}"
        "  {}  "
        "%{{T-}}%{{F-}}%{{B-}}%{{A}}%{{A}}"
    ).format(bg, fg, font, text)
    assert decorated_text == expected_result


def test_base_widget_decorate_self_attributes_empty():
    """
    Test decorate_with_self_attributes without any parameter
    """
    w = Widget()
    kwargs = {
        "text": "test", "fg": "#FFFF11", "bg": "#FF9021", "font": 1,
        "padding": 2, "actions": {1: "firefox", 3: "urxvt"},
    }

    assert w.decorate_with_self_attributes(**kwargs) == w.decorate(**kwargs)


def test_base_widget_decorate_self_attributes():
    """
    Test decorate_with_self_attributes without any parameter
    """
    fg = "#FFFF11"
    bg = "#FF9021"
    padding = 2
    kwargs = {"fg": fg, "bg": bg, "padding": padding}

    w = Widget(fonts=[1, ], **kwargs)

    assert (w.decorate_with_self_attributes("test") ==
            w.decorate("test", font=1, **kwargs))
