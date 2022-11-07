#!/usr/bin/env -S python3
# SPDX-License-Identifier: CC-PDDC
# https://emptypage.jp/notes/pyevent.html
from typing import Optional


class Event:
    def __init__(self, doc: Optional[str] = None) -> None:
        """コンストラクタ

        Args:
            doc: このイベントの説明を入れる
        """
        self.__doc__ = doc

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return EventHandler(self, obj)

    def __set__(self, obj, value):
        pass


class EventHandler:
    def __init__(self, event: Event, obj):
        self.event = event
        self.obj = obj

    def _getfunctionlist(self):
        """(internal use)"""
        try:
            eventhandler = self.obj.__eventhandler__
        except AttributeError:
            eventhandler = self.obj.__eventhandler__ = {}
        return eventhandler.setdefault(self.event, [])

    def add(self, func):
        """イベントハンド関数を追加します。

        イベントハンドラ関数は、func(sender, earg)のように定義する必要があります。
        また、'+='演算子でハンドラを追加することもできます。
        """
        self._getfunctionlist().append(func)
        return self

    def remove(self, func):
        """既存のイベントハンドラ関数を削除する。

        また、'-='演算子でハンドラを削除することができます。
        """
        lst = self._getfunctionlist()
        if func in lst:
            lst.remove(func)
        return self

    def fire(self, earg=None):
        """イベントを発生させ、すべてのハンドラ関数を呼び出す。

        e.fire(earg)ではなく、e(earg)のようにイベントハンドラオブジェクト自体を
        呼び出すことができます。
        """
        for func in self._getfunctionlist():
            func(self.obj, earg)

    __iadd__ = add
    __isub__ = remove
    __call__ = fire
