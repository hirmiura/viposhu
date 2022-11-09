#!/usr/bin/env -S python3
# SPDX-License-Identifier: MIT
# Copyright 2022 hirmiura <https://github.com/hirmiura>
import logging as lg
import random
import re
from datetime import datetime
from logging import getLogger
from logging.handlers import RotatingFileHandler
from typing import Optional

import lxml.html
from request5ch import Request5ch, Subject5ch, URL5ch

from . import event
from .exceptions import SubjectNotFetched, ThreadNotFound, ThreadOver1000, ThreadStopped
from .hoshu5ch_config import Hoshu5chConfig
from .hoshu5ch_status import JST, Hoshu5chStatus

logger = getLogger(__name__)
logger_sbj = getLogger("subject.txt")
logger_sbj.setLevel(lg.DEBUG)
handler_sbj = RotatingFileHandler("log/subject.txt", backupCount=5)
logger_sbj.addHandler(handler_sbj)
logger_sbj.propagate = False


class Hoshu5ch:
    DEFAULT_CONFIG_FILE_NAME = "hoshu5ch.json"

    def __init__(self, url: str = "") -> None:
        self.config = Hoshu5chConfig(Hoshu5ch.DEFAULT_CONFIG_FILE_NAME)
        self.status = Hoshu5chStatus()
        if url:
            self.set_url(url)
        self.init()

    def init(self) -> None:
        self.check_interval: int = 90
        self.guard_time: int = 5 * 60  # 5分
        self.rank_threshold: float = 0.8
        self.time_threshold: int = 45 * 60  # 45分
        self.subject: Optional[Subject5ch] = None
        self.last_post_in_thread = datetime.now(JST)

    def set_url(self, url: str) -> bool:
        urlobj = URL5ch.parse(url) if url else None
        self.config.url = urlobj
        return urlobj is not None

    evt_show_status_message = event.Event("ステータスメッセージを表示するイベント")

    def load_config(self, filename: str = "") -> Optional[Hoshu5chConfig]:
        return self.config.load(filename)

    def save_config(self, filename: str = "") -> None:
        self.config.save(filename)

    def is_in_interval_or_guard_time(self) -> bool:
        """インターバル内か、ガードタイム内かを調べる

        Returns:
            インターバル内またはガードタイム内であればTrueを返す。(保守不要)
        """
        assert self.status
        t = self.status.get_interval_to_next_check(self.check_interval, self.guard_time)
        if t > 0:
            return True
        return False

    evt_subject_fetched = event.Event("subject.txtを取得してランクを計算した後に呼ばれるイベント")

    def is_in_rank_threshold_by_checking_subject(self) -> bool:
        """subject.txtを取得して、スレの位置を調べる。

        Raises:
            SubjectNotFetched: subject.txtが取得できなかった。

        Returns:
            スレの位置が閾値内であればTrueを返す。(保守不要)
        """
        assert self.config.url
        urlobj = self.config.url
        req5ch = Request5ch(urlobj.thread_url)
        logger.debug("subject.txtを取得しています")
        subj, res = req5ch.get_subject()
        if not subj:
            # subject.txtが取得できなければ例外を投げる
            logger.error("subject.txtが見つかりませんでした")
            self.evt_show_status_message("subject.txtが見つかりませんでした")  # type: ignore
            raise SubjectNotFetched(urlobj.thread_url)
        logger.info("subject.txtを取得しました")
        self.subject = subj
        # デバッグ用にレスポンスを保存する
        logger_sbj.debug(res.text)
        handler_sbj.doRollover()

        # subject.txtが空であればPOSTと被っているのでスルーする
        if subj.total_count == 0:
            return True

        # subject.txt内で対象スレを検索する
        tindex = subj.search_index(urlobj.tid)
        if not tindex:
            # スレが見つからなければ例外を投げる
            logger.warn("subject.txtに目的のスレッドが見つかりませんでした")
            self.evt_show_status_message("subject.txtに目的のスレッドが見つかりませんでした")  # type: ignore
            raise ThreadNotFound(urlobj.thread_url)

        # スレの位置を総数から計算する
        rank: float = (tindex + 1) / subj.total_count
        self.status.update_last_check()  # 最終確認日時を更新する
        self.evt_subject_fetched()  # type: ignore
        if rank < self.rank_threshold:
            # 閾値未満であればTrueを返す
            return True
        return False

    evt_last_post_got_from_thread = event.Event("スレから最終投稿日時を取得した時に呼ばれるイベント")

    def is_in_time_threshold(self) -> bool:
        """スレの最終投稿日時を取得して、投稿間隔が閾値以内か調べる。

        Returns:
            閾値以内であればTrueを返す。(保守不要)
        """
        assert self.config.url
        urlobj = self.config.url
        req5ch = Request5ch(urlobj.thread_url)
        logger.debug("スレ({0}/{1}/{2})を取得しています".format(urlobj.domain_host, urlobj.bbs, urlobj.tid))
        res = req5ch.get_thread_l1()
        if not res.ok:
            # スレが取得できなければ例外を投げる
            text = "スレ({0}/{1}/{2})が取得できませんでした".format(urlobj.domain_host, urlobj.bbs, urlobj.tid)
            logger.error(text)
            self.evt_show_status_message(text)  # type: ignore
            raise ThreadNotFound(urlobj.thread_url)
        text = "スレ({0}/{1}/{2})を取得しました".format(urlobj.domain_host, urlobj.bbs, urlobj.tid)
        logger.info(text)
        self.evt_show_status_message(text)  # type: ignore

        # パースする
        html = lxml.html.fromstring(res.content)
        # スレストされているか取得する
        ret_stopdone = html.xpath("(//div[contains(@class,'stopdone')])[last()]")
        if ret_stopdone and len(ret_stopdone) > 0:
            b_stopped = True
        else:
            b_stopped = False
        # 最終投稿日時を取得する
        ret_date = html.xpath(
            "(//div[@class='thread']/div[@class='post']/div[@class='meta']/span[@class='date'])"
            "[last()]"
        )
        dstr = ret_date[0].text
        if dstr != "Over 1000":
            dstr = re.sub(r"\(.+\)", "", dstr) + " +0900"  # 曜日を消してUTCオフセットを付ける
            last_post_dt = datetime.strptime(dstr, "%Y/%m/%d %H:%M:%S.%f %z")
            self.status.update_last_post_in_thread(last_post_dt)
        else:
            self.status.update_last_post_in_thread(datetime.max)

        if dstr == "Over 1000":
            raise ThreadOver1000(urlobj.thread_url)
        if b_stopped:
            raise ThreadStopped(urlobj.thread_url)

        # 閾値を調べる
        now = datetime.now(JST)
        delta = now - last_post_dt
        self.status.update_last_check()  # 最終確認日時を更新する
        self.evt_last_post_got_from_thread()  # type: ignore
        if delta.total_seconds() < self.time_threshold:
            return True
        return False

    def post(self):
        """保守投稿を行う"""
        assert self.config.url
        urlobj = self.config.url
        req5ch = Request5ch(urlobj.thread_url)
        conf = self.config
        # 重み付きリストから1つ選ぶ
        mes = random.choices(conf.messages, weights=conf.weights)[0]
        logger.debug("保守投稿を行おうとしています")
        res = req5ch.post(mes, conf.name, conf.mail)
        text = "保守投稿を行いました"
        logger.info(text)
        self.evt_show_status_message(text)  # type: ignore
        self.status.update_last_post()  # 最終投稿日時を更新する
        return res

    def do_once(self) -> bool:
        # 時間間隔が充分に開いていなければ何もしない
        if self.is_in_interval_or_guard_time():
            return False

        # subject.txtを取得してスレの位置を調べる
        if self.is_in_rank_threshold_by_checking_subject():
            # 最終投稿日時の閾値を調べる
            if self.is_in_time_threshold():
                # 閾値内であれば何もしない
                return False
        # 保守投稿を行う
        self.post()
        return True
