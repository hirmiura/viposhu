#!/usr/bin/env -S python3
# SPDX-License-Identifier: MIT
# Copyright 2022 hirmiura <https://github.com/hirmiura>
import pytest

from viposhu.exceptions import ThreadOver1000
from viposhu.hoshu5ch import Hoshu5ch


def test_over1000():
    h = Hoshu5ch("https://mi.5ch.net/test/read.cgi/news4vip/1667619945/l1")
    assert h
    with pytest.raises(ThreadOver1000) as e:
        b = h.is_in_time_threshold()
    assert e


def test_KakoLog():
    h = Hoshu5ch("https://mi.5ch.net/test/read.cgi/news4vip/1667714909/")
    assert h
    b = h.is_in_time_threshold()
