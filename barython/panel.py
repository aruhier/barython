#!/usr/bin/env python3


class Panel():
    refresh = 0.1
    screens = list()

    def __init__(self, refresh=None, screens=None):
        self.refresh = self.refresh if refresh is None else refresh
        self.screens = self.screens if screens is None else screens
