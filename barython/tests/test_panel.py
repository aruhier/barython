
import pytest

from barython.panel import Panel


def test_panel_no_widget():
    p = Panel()
    p.run()
