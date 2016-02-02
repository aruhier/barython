
from collections import OrderedDict
import pytest

from barython.widgets.bspwm import BspwmDesktopWidget


def test_bspwm_desktop_widget_organize_result():
    bspwm = BspwmDesktopWidget(
        fg_occupied="#FF000000", bg_occupied="#FFFFFF00",
        fg_free="#FF000001", bg_free="#FFFFFF01",
        fg_urgent="#FF000002", bg_urgent="#FFFFFF02",
        fg_monitor="#FF000003", bg_monitor="#FFFFFF03",
        fg_focused_occupied="#FF000004", bg_focused_occupied="#FFFFFF04",
        fg_focused_free="#FF000005", bg_focused_free="#FFFFFF05",
        fg_focused_urgent="#FF000006", bg_focused_urgent="#FFFFFF06",
        fg_focused_monitor="#FF000007", bg_focused_monitor="#FFFFFF07",
        padding=1, refresh=0
    )

    monitors = OrderedDict([
        ('HDMI-0',
            {'desktops': ['Of'], 'layout': 'T', 'focused': True}),
        ('DVI-D-0',
            {'desktops':
                ['fo', 'f7', 'fDesktop2', 'os', 'oq', 'fp', 'fi', 'Ou'],
             'layout': 'T', 'focused': False}),
        ('DVI-I-0', {'desktops': ['Od'], 'layout': 'T', 'focused': False})
    ])

    expected = (
        "%{A1:bspc monitor -f HDMI-0:}"
        "%{B#FFFFFF07}%{F#FF000006} %{F-}%{B-}"
        "%{B#FFFFFF07}%{F#FF000006}HDMI-0%{F-}%{B-}"
        "%{B#FFFFFF07}%{F#FF000006} %{F-}%{B-}"
        "%{A}"
        "%{A1:bspc desktop -f f:}"
        "%{B#FFFFFF04}%{F#FF000004} %{F-}%{B-}"
        "%{B#FFFFFF04}%{F#FF000004}f%{F-}%{B-}"
        "%{B#FFFFFF04}%{F#FF000004} %{F-}%{B-}"
        "%{A}"
        "%{A1:bspc monitor -f DVI-D-0:}"
        "%{B#FFFFFF03}%{F#FF000002} %{F-}%{B-}"
        "%{B#FFFFFF03}%{F#FF000002}DVI-D-0%{F-}%{B-}"
        "%{B#FFFFFF03}%{F#FF000002} %{F-}%{B-}"
        "%{A}"
        "%{A1:bspc desktop -f o:}"
        "%{B#FFFFFF01}%{F#FF000001} %{F-}%{B-}"
        "%{B#FFFFFF01}%{F#FF000001}o%{F-}%{B-}"
        "%{B#FFFFFF01}%{F#FF000001} %{F-}%{B-}"
        "%{A}"
        "%{A1:bspc desktop -f 7:}"
        "%{B#FFFFFF01}%{F#FF000001} %{F-}%{B-}"
        "%{B#FFFFFF01}%{F#FF000001}7%{F-}%{B-}"
        "%{B#FFFFFF01}%{F#FF000001} %{F-}%{B-}"
        "%{A}"
        "%{A1:bspc desktop -f Desktop2:}"
        "%{B#FFFFFF01}%{F#FF000001} %{F-}%{B-}"
        "%{B#FFFFFF01}%{F#FF000001}Desktop2%{F-}%{B-}"
        "%{B#FFFFFF01}%{F#FF000001} %{F-}%{B-}"
        "%{A}"
        "%{A1:bspc desktop -f s:}"
        "%{B#FFFFFF00}%{F#FF000000} %{F-}%{B-}"
        "%{B#FFFFFF00}%{F#FF000000}s%{F-}%{B-}"
        "%{B#FFFFFF00}%{F#FF000000} %{F-}%{B-}"
        "%{A}"
        "%{A1:bspc desktop -f q:}"
        "%{B#FFFFFF00}%{F#FF000000} %{F-}%{B-}"
        "%{B#FFFFFF00}%{F#FF000000}q%{F-}%{B-}"
        "%{B#FFFFFF00}%{F#FF000000} %{F-}%{B-}"
        "%{A}"
        "%{A1:bspc desktop -f p:}"
        "%{B#FFFFFF01}%{F#FF000001} %{F-}%{B-}"
        "%{B#FFFFFF01}%{F#FF000001}p%{F-}%{B-}"
        "%{B#FFFFFF01}%{F#FF000001} %{F-}%{B-}"
        "%{A}"
        "%{A1:bspc desktop -f i:}"
        "%{B#FFFFFF01}%{F#FF000001} %{F-}%{B-}"
        "%{B#FFFFFF01}%{F#FF000001}i%{F-}%{B-}"
        "%{B#FFFFFF01}%{F#FF000001} %{F-}%{B-}"
        "%{A}"
        "%{A1:bspc desktop -f u:}"
        "%{B#FFFFFF04}%{F#FF000004} %{F-}%{B-}"
        "%{B#FFFFFF04}%{F#FF000004}u%{F-}%{B-}"
        "%{B#FFFFFF04}%{F#FF000004} %{F-}%{B-}"
        "%{A}"
        "%{A1:bspc monitor -f DVI-I-0:}"
        "%{B#FFFFFF03}%{F#FF000002} %{F-}%{B-}"
        "%{B#FFFFFF03}%{F#FF000002}DVI-I-0%{F-}%{B-}"
        "%{B#FFFFFF03}%{F#FF000002} %{F-}%{B-}"
        "%{A}"
        "%{A1:bspc desktop -f d:}"
        "%{B#FFFFFF04}%{F#FF000004} %{F-}%{B-}"
        "%{B#FFFFFF04}%{F#FF000004}d%{F-}%{B-}"
        "%{B#FFFFFF04}%{F#FF000004} %{F-}%{B-}"
        "%{A}"
    )

    assert expected == "".join(bspwm._parse_and_decorate(monitors))
