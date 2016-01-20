
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
