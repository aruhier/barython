
import pytest
import time
import threading

from barython.panel import Panel
from barython.screen import Screen
from barython.widgets.base import Widget
from barython.hooks import HooksPool, _Hook


class TestHook(_Hook):
    def run(self, *args, **kwargs):
        return self.notify()


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


def test_base_hooks_pool_subscribe(mocker):
    callback = mocker.stub()
    hp = HooksPool()
    hp.subscribe(callback, _Hook)
    assert isinstance(hp.hooks[_Hook][0], _Hook)
    assert hp.hooks[_Hook][0].callbacks == {callback, }


def test_base_hooks_pool_subscribe_listen(mocker):
    callback = mocker.stub()
    hp = HooksPool(listen=True)
    hp.subscribe(callback, TestHook)
    assert isinstance(hp.hooks[TestHook][0], TestHook)
    try:
        threading.Thread(target=hp.start).start()
        time.sleep(0.1)
        callback.assert_called_once_with()
    finally:
        hp.stop()


def test_base_hook_copy(mocker):
    callback0 = mocker.stub()

    h = _Hook(callbacks={callback0})
    h_cpy = h.copy()

    assert h.callbacks == h_cpy.callbacks
    assert h.callbacks is not h_cpy.callbacks
    assert h.daemon == h_cpy.daemon


def test_base_hooks_pool_merge(mocker):
    callback0, callback1 = mocker.stub(), mocker.stub()
    hp0, hp1 = HooksPool(), HooksPool()
    hp0.subscribe(callback0, _Hook)
    hp1.subscribe(callback1, _Hook)

    hp0.merge(hp1)
    assert hp0.hooks[_Hook][0].callbacks == {callback0, callback1}


def test_base_hooks_with_panel(mocker):
    callback0, callback1 = mocker.stub(), mocker.stub()
    p = Panel()
    s = Screen()
    w0, w1 = Widget(), Widget()
    w0.hooks.subscribe(callback0, _Hook)
    w1.hooks.subscribe(callback1, _Hook)

    s.add_widget("l", w0, w1)
    p.add_screen(s)

    assert p.hooks.hooks[_Hook][0].callbacks == {callback0, callback1}
