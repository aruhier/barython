
import pytest
import threading
import time

import barython.screen
from barython.panel import Panel
from barython.screen import Screen
from barython.widgets.base import TextWidget


def test_panel_no_widget():
    """
    Test the Panel construction
    """
    Panel()


def test_pannel_add_screen():
    """
    Test to add a screen to a panel
    """
    p = Panel()
    assert len(p._screens) == 0

    s = Screen()
    p.add_screen(s)
    assert p._screens[0] == s


def test_pannel_global_instance_add_screen():
    """
    Test to add a screen to a panel
    """
    p = Panel(instance_per_screen=False)
    assert len(p._screens) == 0

    s = Screen()
    p.add_screen(s)
    assert p._screens[0] == s


def test_pannel_add_screen_insert():
    """
    Test the screen insertion in a panel, with multiple screens at a time
    """
    p = Panel()
    s = Screen()
    s1 = Screen()
    s2 = Screen()

    p.add_screen(s, s2)
    p.add_screen(s1, index=1)

    assert len(p._screens) == 3
    for screen, pscreen in zip((s, s1, s2), p._screens):
        assert screen == pscreen


def test_panel_gather_one_screen():
    p = Panel(instance_per_screen=False)
    w = TextWidget(text="test")

    s = Screen()
    p.add_screen(s)
    s.add_widget("l", w)
    w.update()

    assert p.gather() == "%{l}test"


def test_panel_gather_multiple_screens():
    p = Panel(instance_per_screen=False)
    w = TextWidget(text="test")

    s = Screen()
    p.add_screen(s)
    s.add_widget("l", w)

    s1 = Screen()
    p.add_screen(s1)
    s1.add_widget("l", w)
    w.update()

    assert p.gather() == "%{l}test%{S+}%{l}test"


def test_panel_clean_screens(monkeypatch):
    def mock_get_randr_screens(*args, **kwargs):
        return {"DVI-I-0": (1920, 1080, 50, 60)}

    monkeypatch.setattr(barython.panel, "get_randr_screens",
                        mock_get_randr_screens)

    p = Panel(instance_per_screen=False, keep_unplugged_screens=False)
    s0, s1 = Screen("DVI-I-0"), Screen("DVI-I-1")
    w = TextWidget(text="test")
    s0.add_widget("l", w)
    s1.add_widget("l", w)
    p.add_screen(s0, s1)

    assert tuple(p.clean_screens()) == (s0, )


def test_panel_clean_screens_instance_per_screen(monkeypatch):
    def mock_get_randr_screens(*args, **kwargs):
        return {"DVI-I-0": (1920, 1080, 50, 60)}

    monkeypatch.setattr(barython.panel, "get_randr_screens",
                        mock_get_randr_screens)

    p = Panel(instance_per_screen=True, keep_unplugged_screens=False)
    s0, s1 = Screen("DVI-I-0"), Screen("DVI-I-1")
    w = TextWidget(text="test")
    s0.add_widget("l", w)
    s1.add_widget("l", w)
    p.add_screen(s0, s1)

    assert tuple(p.clean_screens()) == (s0, )


@pytest.fixture
def fixture_useful_screens(monkeypatch, mocker):
    def mock_get_randr_screens(*args, **kwargs):
        return {"DVI-I-0": (1920, 1080, 50, 60)}

    monkeypatch.setattr(barython.panel, "get_randr_screens",
                        mock_get_randr_screens)

    p = Panel(keep_unplugged_screens=False)
    p.init_bar = mocker.stub()
    p._write_in_bar = mocker.stub()
    s0, s1 = Screen("DVI-I-0"), Screen("DVI-I-1")
    mocker.spy(s0, "start")
    s0.init_bar = mocker.stub()
    s0._write_in_bar = mocker.stub()
    mocker.spy(s1, "start")
    s1.init_bar = mocker.stub()
    s1._write_in_bar = mocker.stub()

    w = TextWidget(text="test")
    s0.add_widget("l", w)
    s1.add_widget("l", w)

    p.add_screen(s0, s1)
    return p, s0, s1


def test_panel_start_useful_screens(fixture_useful_screens):
    p, s0, s1 = fixture_useful_screens
    p.instance_per_screen = True
    try:
        threading.Thread(target=p.start).start()
        time.sleep(0.1)
        assert p.init_bar.call_count == 0
        assert s0.start.call_count == 1
        assert s1.start.call_count == 0
        assert s0.init_bar.call_count == 1
        assert s1.init_bar.call_count == 0
    finally:
        p.stop()


def test_panel_start_useful_screens_global_instance(fixture_useful_screens):
    p, s0, s1 = fixture_useful_screens
    p.instance_per_screen = False
    try:
        threading.Thread(target=p.start).start()
        time.sleep(0.1)
        assert p.init_bar.call_count == 1
        assert s0.start.call_count == 1
        assert s1.start.call_count == 0
        assert s0.init_bar.call_count == 0
        assert s1.init_bar.call_count == 0
    finally:
        p.stop()
