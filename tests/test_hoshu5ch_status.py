#!/usr/bin/env -S python3
# SPDX-License-Identifier: MIT
# Copyright 2022 hirmiura <https://github.com/hirmiura>
from datetime import datetime

import pytest

from viposhu.hoshu5ch_status import JST, Hoshu5chStatus

now_list = [
    (datetime(2022, 1, 2, 3, 4, tzinfo=JST)),
    (datetime(2022, 12, 31, 23, 59, 59, 123000, tzinfo=JST)),
]


@pytest.mark.parametrize(("now"), now_list)
def test_update_last_check(freezer, now):
    s = Hoshu5chStatus()
    assert s
    assert s.last_check is None
    assert s.last_post is None
    freezer.move_to(now)
    s.update_last_check()
    assert s.last_check == now
    assert s.last_post is None


@pytest.mark.parametrize(("now"), now_list)
def test_update_last_post(freezer, now):
    s = Hoshu5chStatus()
    assert s
    assert s.last_check is None
    assert s.last_post is None
    freezer.move_to(now)
    s.update_last_post()
    assert s.last_check is None
    assert s.last_post == now


data_for_get_interval_to_next_check1 = [
    (
        90,
        300,
        datetime(2022, 12, 31, 23, 59, 59, 123000, tzinfo=JST),
        int(300 - datetime(2022, 12, 31, 23, 59, 59, 123000, tzinfo=JST).timestamp()),
    ),
    (
        390,
        30,
        datetime(2022, 12, 31, 23, 59, 59, 123000, tzinfo=JST),
        int(390 - datetime(2022, 12, 31, 23, 59, 59, 123000, tzinfo=JST).timestamp()),
    ),
]


@pytest.mark.parametrize(
    "interval, guard_time, now, expected", data_for_get_interval_to_next_check1
)
def test_get_interval_to_next_check1(freezer, interval, guard_time, now, expected):
    s = Hoshu5chStatus()
    assert s
    assert s.last_check is None
    assert s.last_post is None
    freezer.move_to(now)
    assert s.get_interval_to_next_check(interval, guard_time) == expected


data_for_get_interval_to_next_check2 = [
    (
        90,
        300,
        datetime(2022, 12, 31, 23, 59, 59, 123000, tzinfo=JST),
        90,
    ),
    (
        390,
        30,
        datetime(2022, 12, 31, 23, 59, 59, 123000, tzinfo=JST),
        390,
    ),
]


@pytest.mark.parametrize(
    "interval, guard_time, now, expected", data_for_get_interval_to_next_check2
)
def test_get_interval_to_next_check2(freezer, interval, guard_time, now, expected):
    s = Hoshu5chStatus()
    assert s
    assert s.last_check is None
    assert s.last_post is None
    freezer.move_to(now)
    s.update_last_check()
    assert s.last_check == now
    assert s.last_post is None
    assert s.get_interval_to_next_check(interval, guard_time) == expected


data_for_get_interval_to_next_check3 = [
    (
        90,
        300,
        datetime(2022, 12, 31, 23, 59, 59, 123000, tzinfo=JST),
        300,
    ),
    (
        390,
        30,
        datetime(2022, 12, 31, 23, 59, 59, 123000, tzinfo=JST),
        30,
    ),
]


@pytest.mark.parametrize(
    "interval, guard_time, now, expected", data_for_get_interval_to_next_check3
)
def test_get_interval_to_next_check3(freezer, interval, guard_time, now, expected):
    s = Hoshu5chStatus()
    assert s
    assert s.last_check is None
    assert s.last_post is None
    freezer.move_to(now)
    s.update_last_post()
    assert s.last_check is None
    assert s.last_post == now
    assert s.get_interval_to_next_check(interval, guard_time) == expected


data_for_get_interval_to_next_check4 = [
    (
        90,
        300,
        datetime(2022, 12, 31, 23, 59, 59, 123000, tzinfo=JST),
        300,
    ),
    (
        390,
        30,
        datetime(2022, 12, 31, 23, 59, 59, 123000, tzinfo=JST),
        390,
    ),
]


@pytest.mark.parametrize(
    "interval, guard_time, now, expected", data_for_get_interval_to_next_check4
)
def test_get_interval_to_next_check4(freezer, interval, guard_time, now, expected):
    s = Hoshu5chStatus()
    assert s
    assert s.last_check is None
    assert s.last_post is None
    freezer.move_to(now)
    s.update_last_check()
    s.update_last_post()
    assert s.last_check == now
    assert s.last_post == now
    assert s.get_interval_to_next_check(interval, guard_time) == expected
