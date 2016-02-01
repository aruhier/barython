
from collections import OrderedDict
import pytest

from barython.hooks.bspwm import BspwmHook


def test_bspwm_hook_parse_event():
    bh = BspwmHook()
    status = ("WmHDMI-0:Ou:LT:MDVI-D-0:fo:f7:fDesktop2:os:Of:fp:oq:fi:LT:"
              "mDVI-I-0:Od:LT")
    expected = OrderedDict([
        ('HDMI-0', {'desktops': ['Ou'], 'focused': False, 'layout': 'T'}),
        ('DVI-D-0', {
            'desktops': ['fo', 'f7', 'fDesktop2', 'os', 'Of', 'fp', 'oq',
                         'fi'],
            'focused': True, 'layout': 'T'
        }),
        ('DVI-I-0', {'desktops': ['Od'], 'focused': False, 'layout': 'T'})
    ])

    assert expected == bh.parse_event(status)["monitors"]
