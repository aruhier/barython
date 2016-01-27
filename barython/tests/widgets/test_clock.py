
import datetime
import pytest
import threading
import time

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

    threading.Thread(target=cw.start).start()
    time.sleep(0.1)
    try:
        assert cw.content == str(now)
    finally:
        cw.stop()