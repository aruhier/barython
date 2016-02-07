
import pytest

from barython.panel import Panel
from barython.screen import Screen
from barython.widgets.base import Widget, TextWidget
import barython.screen


def test_screen():
    Screen()


def test_screen_refresh():
    """
    Test if a Screen object get the refresh of its panel if not set
    """
    s = Screen(refresh=-1)
    assert s.refresh == -1

    s.refresh = 1
    assert s.refresh == 1

    p = Panel(refresh=2, keep_unplugged_screens=True)
    s.refresh = -1
    s.panel = p
    assert s.refresh == p.refresh
    assert s.refresh == 2


def test_screen_add_widget():
    """
    Test to add a widget in different alignments
    """
    s = Screen()

    w = Widget()
    s.add_widget("l", w)
    assert s._widgets["l"][0] == w

    w = Widget()
    s.add_widget("c", w)
    assert s._widgets["c"][0] == w

    w = Widget()
    s.add_widget("r", w)
    assert s._widgets["r"][0] == w

    assert len(w.screens) == 1
    assert next(iter(w.screens)) == s


def test_screen_add_widget_bad_alignment():
    """
    Test to add a widget in different alignments
    """
    s = Screen()
    w = Widget()

    with pytest.raises(ValueError):
        s.add_widget(w)

    with pytest.raises(ValueError):
        s.add_widget("v", w)


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


def test_screen_geometry(monkeypatch):
    def mock_get_randr_screens(*args, **kwargs):
        return {"DVI-I-0": (1920, 1080, 50, 60)}

    monkeypatch.setattr(barython.screen, "get_randr_screens",
                        mock_get_randr_screens)
    s = Screen(name="DVI-I-0", height=20)
    assert s.geometry == (1920, 20, 50, 60)


def test_screen_gather():
    p = Panel(keep_unplugged_screens=True)
    s = Screen()
    p.add_screen(s)
    w = TextWidget(text="test")
    s.add_widget("l", w)
    w.update()

    content = s.gather()
    assert content == "%{l}test"


def test_screen_gather_multiple_widgets():
    """
    Test the gather function with more than one widget
    """
    p = Panel(keep_unplugged_screens=True)
    s = Screen()
    p.add_screen(s)
    w = TextWidget(text="test")
    w1 = TextWidget(text="test1")
    s.add_widget("l", w, w1)
    w.update()
    w1.update()

    s.add_widget("r", w, w1)
    s.add_widget("c", w, w1)

    content = s.gather()
    assert content == "%{l}testtest1%{c}testtest1%{r}testtest1"
