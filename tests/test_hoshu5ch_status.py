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
