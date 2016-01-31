
import pytest

from barython.hooks import HooksPool, _Hook


def test_base_hook_notify(mocker):
    """
    Test _Hook.notify
    """
    stub = mocker.stub()
    hook = _Hook(callbacks={stub, })
    hook.notify()
    stub.assert_called_once_with()


def test_base_hook_notify_without_callback(mocker):
    hook = _Hook()
    hook.notify()


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


def test_base_hooks_pool_merge():
    def callback0():
        pass

    def callback1():
        pass

    hp0, hp1 = HooksPool(), HooksPool()
    hp0.subscribe(callback0, _Hook)
    hp1.subscribe(callback1, _Hook)

    hp0.merge(hp1)
    assert hp0.hooks[_Hook].callbacks == {callback0, callback1}
