#!/usr/bin/env python3

from datetime import datetime
import time

from .base import ThreadedWidget


class ClockWidget(ThreadedWidget):
    def continuous_update(self):
        while True and not self._stop.is_set():
            self.update()
            time.sleep(self.refresh)

    def organize_result(self, date_now, **kwargs):
        return super().organize_result(date_now.strftime(self.date_format))

    def update(self, *args, **kwargs):
        self.trigger_global_update(
            self.organize_result(datetime.now())
        )

    def __init__(self, date_format="%c", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.date_format = date_format
