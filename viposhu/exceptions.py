#!/usr/bin/env -S python3
# SPDX-License-Identifier: MIT
# Copyright 2022 hirmiura <https://github.com/hirmiura>


class VIPoshuException(Exception):
    pass


class ThreadNotFound(VIPoshuException):
    def __init__(self, url: str) -> None:
        self.url = url

    def __str__(self) -> str:
        return f"スレが見つかりません。Dat落ちか、URLが間違っている可能性があります。({self.url})"


class SubjectNotFetched(VIPoshuException):
    def __init__(self, url: str) -> None:
        self.url = url

    def __str__(self) -> str:
        return f"subject.txtが取得できません。ネットワークに問題があるか、URLが間違っている可能性があります。({self.url})"


class ThreadStopped(VIPoshuException):
    def __init__(self, url: str) -> None:
        self.url = url

    def __str__(self) -> str:
        return f"スレッドストップしています。({self.url})"


class ThreadOver1000(ThreadStopped):
    def __init__(self, url: str) -> None:
        self.url = url

    def __str__(self) -> str:
        return f"レス数が1000を超えています。({self.url})"
