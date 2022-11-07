#!/usr/bin/env -S python3
# SPDX-License-Identifier: MIT
# Copyright 2022 hirmiura <https://github.com/hirmiura>
import json
from pathlib import Path
from typing import Optional

from request5ch import URL5ch


class Hoshu5chConfig:
    def __init__(self, filename: str = "") -> None:
        self.filename = filename
        self.url: Optional[URL5ch] = None
        self.name = ""
        self.mail = ""
        self.messages: list[str] = ["ほ"]
        self.weights: list[int] = [1]
        if filename:
            self.load(filename)

    def load(self, filename: str = ""):
        if filename:
            self.filename = filename
        else:
            filename = self.filename
        p = Path(filename)
        if not p.is_file():
            return None
        with p.open(encoding="utf-8") as f:
            json_obj = json.load(f)

        if "url" in json_obj:
            self.url = URL5ch.parse(json_obj["url"])
        for varname in ["name", "mail"]:
            if varname in json_obj:
                exec("self.{0} = json_obj['{0}']".format(varname))
        if "messages" in json_obj:
            mess_and_wgts = json_obj["messages"]
            # messagesから重み付けを分離する
            self.messages = [m[0] for m in mess_and_wgts]
            self.weights = [m[1] for m in mess_and_wgts]
        return self

    def save(self, filename: str = "") -> None:
        assert self.url
        if filename:
            self.filename = filename
        else:
            filename = self.filename
        json_obj = {}
        if self.url:
            json_obj["url"] = self.url.thread_url
        if self.name:
            json_obj["name"] = self.name
        if self.mail:
            json_obj["mail"] = self.mail
        mess_and_wgts = list(zip(self.messages, self.weights))
        json_obj["messages"] = mess_and_wgts
        p = Path(filename)
        with p.open("w", encoding="utf-8") as f:
            json.dump(json_obj, f, ensure_ascii=False, indent=2)
