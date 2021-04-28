#!/usr/bin/env python3

from datetime import datetime
import time

from .base import Widget


class ClockWidget(Widget):
    def organize_result(self, date_now, **kwargs):
        return super().organize_result(date_now.strftime(self.date_format))

    def update(self, *args, **kwargs):
        time.tzset()
        self.trigger_global_update(
            self.organize_result(datetime.now())
        )

    def __init__(self, date_format="%c", infinite=True, *args, **kwargs):
        super().__init__(infinite=True, *args, **kwargs)
        self.date_format = date_format
