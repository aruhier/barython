#!/usr/bin/env python3

from datetime import datetime
import time

from .base import ThreadedWidget


class ClockWidget(ThreadedWidget):
    date_format = "%c"

    def update(self, *args, **kwargs):
        while True and not self._stop.is_set():
            new_content = self.decorate_with_self_attributes(
                datetime.now().strftime(self.date_format)
            )
            super().update(new_content=new_content, *args, **kwargs)
            time.sleep(self.refresh)

    def __init__(self, date_format=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.date_format = (
            self.date_format if date_format is None else date_format
        )
