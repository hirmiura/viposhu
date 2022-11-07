#!/usr/bin/env -S python3
# SPDX-License-Identifier: MIT
# Copyright 2022 hirmiura <https://github.com/hirmiura>
from pathlib import Path

import pytest

from viposhu.hoshu5ch import Hoshu5ch
from viposhu.hoshu5ch_config import Hoshu5chConfig


@pytest.fixture
def hoshu5ch_conf_1():
    FILENAME = "tests/" + Hoshu5ch.DEFAULT_CONFIG_FILE_NAME
    p = Path(FILENAME)
    p.write_text(
        '{"url": "https://mi.5ch.net/test/read.cgi/news4vip/1667574391/", "name": "名前", "mail": "hage", "messages": [["ほほ", 1]]}',
        encoding="utf-8",
    )
    yield FILENAME
    p.unlink(True)


def test_init():
    c = Hoshu5chConfig()
    assert c
    assert c.filename == ""
    assert c.url is None
    assert c.name == ""
    assert c.mail == ""
    assert c.messages == ["ほ"]
    assert c.weights == [1]

    c = Hoshu5chConfig(None)  # type: ignore
    assert c
    assert c.url is None
    assert c.name == ""
    assert c.mail == ""
    assert c.messages == ["ほ"]
    assert c.weights == [1]


def test_load(hoshu5ch_conf_1):
    c = Hoshu5chConfig(hoshu5ch_conf_1)
    assert c
    assert c.filename == hoshu5ch_conf_1
    assert c.url
    assert c.url.scheme == "https"
    assert c.url.domain_host == "mi"
    assert c.url.bbs == "news4vip"
    assert c.url.tid == "1667574391"
    assert c.name == "名前"
    assert c.mail == "hage"
    assert c.messages == ["ほほ"]
    assert c.weights == [1]


def test_save(hoshu5ch_conf_1):
    c = Hoshu5chConfig(hoshu5ch_conf_1)
    assert c.filename == hoshu5ch_conf_1
    c.save()
    p = Path(hoshu5ch_conf_1)
    saved = p.read_text(encoding="utf-8")
    assert (
        saved
        == """{
  "url": "https://mi.5ch.net/test/read.cgi/news4vip/1667574391/",
  "name": "名前",
  "mail": "hage",
  "messages": [
    [
      "ほほ",
      1
    ]
  ]
}"""
    )
