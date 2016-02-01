
import datetime
import pytest

from barython.widgets.clock import ClockWidget


class MockDatetime(datetime.datetime):
    fixed_date = None

    @classmethod
    def now(cls):
        return cls.fixed_date


def test_clock_widget_construction():
    ClockWidget()


def test_clock_widget_content(mocker):
    cw = ClockWidget(date_format="%c")
    now = datetime.datetime.now().strftime("%c")
    MockDatetime.fixed_date = now
    datetime.datetime = MockDatetime

    cw.update()
    assert cw.content == str(now)
