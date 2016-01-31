
import pytest

from barython.hooks import HooksPool, _Hook


def test_base_hooks_pool_subscribe():
    def callback():
        pass

    hp = HooksPool()
    hp.subscribe(callback, _Hook)


def test_base_hooks_pool_subscribe_listen():
    def callback():
        pass

    hp = HooksPool(listen=True)
    hp.subscribe(callback, _Hook)
