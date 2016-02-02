
import pytest
import threading
import time
import timeit

from barython.screen import Screen
from barython.panel import Panel
from barython.widgets.base import SubprocessWidget, TextWidget, Widget


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
        "%{{A1:firefox&:}}%{{A3:urxvt&:}}"
        "%{{B{}}}%{{F{}}}%{{T{}}}  %{{T-}}%{{F-}}%{{B-}}"
        "%{{B{}}}%{{F{}}}%{{T{}}}{}%{{T-}}%{{F-}}%{{B-}}"
        "%{{B{}}}%{{F{}}}%{{T{}}}  %{{T-}}%{{F-}}%{{B-}}%{{A}}%{{A}}"
    ).format(bg, fg, font, bg, fg, font, text, bg, fg, font)
    assert decorated_text == expected_result


def test_base_widget_decorate_self_attributes_empty():
    """
    Test decorate_with_self_attributes without any parameter
    """
    w = Widget()
    kwargs = {
        "text": "test", "fg": "#FFFF11", "bg": "#FF9021", "font": 1,
        "padding": 2, "actions": {1: "firefox", 3: "urxvt"}, "icon": "\uf04c",
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


def test_base_lock_update(mocker):
    """
    Test that only one update is running at a time by widget
    """
    p = Panel(instance_per_screen=False)
    w = SubprocessWidget(cmd="echo Test", refresh=0.2)
    for i in range(0, 4):
        s = Screen()
        s.add_widget("l", w)
        p.add_screen(s)
    mocker.spy(w, "continuous_update")

    try:
        threading.Thread(target=p.start).start()
        time.sleep(1)
        assert w.continuous_update.call_count == 1
    finally:
        p.stop()


def test_base_textwidget():
    tw = TextWidget(text="Test")
    tw.update()

    assert tw.content == "Test"


def test_base_subprocesswidget_init_subprocess():
    cmd = "echo Test"
    sw = SubprocessWidget(cmd=cmd)
    subproc = sw._init_subprocess(cmd)

    assert subproc.stdout.readline() == b"Test\n"


def test_base_subprocesswidget_notify():
    sw = SubprocessWidget(cmd="echo test", subscribe_cmd="sleep 0.5")
    total_time = timeit.timeit(sw.notify, number=2)
    assert int(total_time) == 1


def test_base_subprocesswidget_start():
    sw = SubprocessWidget(cmd="echo Test", subscribe_cmd="sleep 0.5")
    assert sw.content is None

    t = threading.Thread(target=sw.start)
    t.start()
    # Lets a little overtime to be sure it's finished
    time.sleep(0.7)
    sw.stop()
    assert sw.content == "Test"
