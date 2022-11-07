#!/usr/bin/env -S python3
# SPDX-License-Identifier: MIT
# Copyright 2022 hirmiura <https://github.com/hirmiura>
import tkinter as tk
from logging import getLogger

from . import event
from .exceptions import SubjectNotFetched, ThreadNotFound, ThreadStopped
from .hoshu5ch import Hoshu5ch

VERSION = "0.0.1"
logger = getLogger(__name__)


class VIPoshu(tk.Frame):
    TIMER_INTERVAL = 1000
    btn_lable_start = "保守開始"
    btn_lable_stop = "保守終了"

    def __init__(self, master=None) -> None:
        super().__init__(master)
        self.master.title(f"VIPoshu {VERSION}")  # type: ignore
        self.master.protocol("WM_DELETE_WINDOW", self.on_delete_window)  # type: ignore
        self.hoshu_timer_end = False
        self.update_title = True
        self.hoshu5ch: Hoshu5ch = Hoshu5ch()
        self.hoshu5ch.evt_show_status_message += self.eh_show_status_message  # type: ignore
        self.evt_before_hoshu_start += self.hoshu5ch.status.clear_datetime  # type: ignore
        self.init_url_frame()
        self.init_status_frame1()
        self.init_status_frame2()
        self.master.resizable(False, False)  # type: ignore
        self.pack()

    def init_url_frame(self):
        url_frame = tk.Frame(self.master)

        tk.Label(url_frame, text="URL:").pack(anchor=tk.W, side=tk.LEFT)
        conf = self.hoshu5ch.config
        url = conf.url.thread_url if conf.url else ""
        self.urlStrVar = tk.StringVar(value=url)
        self.urlEntry = tk.Entry(url_frame, textvariable=self.urlStrVar, width=55)
        self.urlEntry.pack(anchor=tk.CENTER, side=tk.LEFT, expand=True, fill=tk.X)

        self.btnStrVar = tk.StringVar(value=VIPoshu.btn_lable_start)
        tk.Button(
            url_frame, textvariable=self.btnStrVar, command=self.on_start_stop_btn_click
        ).pack(anchor=tk.E, side=tk.LEFT)

        url_frame.pack(anchor=tk.N, side=tk.TOP, fill=tk.X)

    def init_status_frame1(self):
        status_frame1 = tk.Frame(self.master)

        tk.Label(status_frame1, text="Rank:").pack(anchor=tk.W, side=tk.LEFT)
        self.rankStrVar = tk.StringVar(value="000/000")
        label_rank = tk.Label(status_frame1, textvariable=self.rankStrVar, anchor=tk.E, width=6)
        label_rank.propagate(False)
        label_rank.pack(anchor=tk.W, side=tk.LEFT)

        tk.Label(status_frame1, text="Next:").pack(anchor=tk.W, side=tk.LEFT, padx=(4, 0))
        self.nextStrVar = tk.StringVar(value="0000秒")
        label_next = tk.Label(status_frame1, textvariable=self.nextStrVar, anchor=tk.E, width=5)
        label_next.propagate(False)
        label_next.pack(anchor=tk.W, side=tk.LEFT)

        tk.Label(status_frame1, text="最終投稿:").pack(anchor=tk.W, side=tk.LEFT, padx=(4, 0))
        # dtstr = self.hoshu5ch.last_post_in_thread.strftime("%Y-%m-%d %H:%M:%S")
        self.lpdtStrVar = tk.StringVar(value="0000-00-00 00:00:00")
        label_lpdt = tk.Label(status_frame1, textvariable=self.lpdtStrVar, anchor=tk.E, width=15)
        label_lpdt.propagate(False)
        label_lpdt.pack(anchor=tk.W, side=tk.LEFT)

        status_frame1.pack(anchor=tk.N, side=tk.TOP, fill=tk.X)

    def init_status_frame2(self):
        status_frame2 = tk.Frame(self.master, relief=tk.SUNKEN, bd=1)

        self.statusStrVar = tk.StringVar(value="")
        label_rank = tk.Label(status_frame2, textvariable=self.statusStrVar, anchor=tk.W)
        label_rank.pack(anchor=tk.W, side=tk.LEFT)

        status_frame2.pack(anchor=tk.N, side=tk.TOP, fill=tk.X)

    def show_status_message(self, text: str = ""):
        self.statusStrVar.set(text)

    def eh_show_status_message(self, sender, earg):
        self.show_status_message(earg)

    evt_before_hoshu_start = event.Event("保守開始の直前に呼ばれるイベント")
    evt_after_hoshu_end = event.Event("保守終了の直後に呼ばれるイベント")

    def on_start_stop_btn_click(self) -> None:
        btn_label_now = self.btnStrVar.get()
        ho5 = self.hoshu5ch
        if btn_label_now == VIPoshu.btn_lable_start:
            self.urlEntry.configure(state="readonly")
            self.btnStrVar.set(VIPoshu.btn_lable_stop)
            # URLを取得してパースする
            url = self.urlStrVar.get()
            ret = ho5.set_url(url)
            if not ret:
                text = "URLのパースに失敗しました"
                logger.warn(text + f"({url})")
                self.show_status_message(text)
                self.btnStrVar.set(VIPoshu.btn_lable_start)
                self.urlEntry.configure(state=tk.NORMAL)
                return
            # 設定を保存する
            ho5.save_config()
            # イベントハンドラを登録する
            ho5.evt_subject_fetched += self.eh_subject_fetched  # type: ignore
            ho5.evt_last_post_got_from_thread += self.eh_last_post_got_from_thread  # type: ignore
            # 保守ループを開始する
            self.hoshu_timer_end = False
            self.update_title = True
            self.evt_before_hoshu_start()  # type: ignore
            self.hoshu_timer()
        else:
            self.btnStrVar.set(VIPoshu.btn_lable_start)
            self.urlEntry.configure(state=tk.NORMAL)
            # 保守ループを終了する
            self.hoshu_timer_end = True
            self.master.title(f"VIPoshu {VERSION}")  # type: ignore
            self.evt_after_hoshu_end()  # type: ignore
            # イベントハンドラを削除する
            ho5.evt_subject_fetched -= self.eh_subject_fetched  # type: ignore
            ho5.evt_last_post_got_from_thread -= self.eh_last_post_got_from_thread  # type: ignore

    def end_processing(self) -> None:
        self.hoshu_timer_end = True
        # TODO: 終了処理
        pass

    def on_delete_window(self):
        self.end_processing()
        self.master.destroy()

    def hoshu_timer(self):
        ho5 = self.hoshu5ch
        if self.hoshu_timer_end:
            return
        try:
            ho5.do_once()
        except (SubjectNotFetched, ThreadNotFound, ThreadStopped) as e:
            self.hoshu_timer_end = True
            logger.error(e)
            self.on_start_stop_btn_click()
            return
        # TODO: 保守状況の描画
        # 次のチェックまでの時間
        nsec = ho5.status.get_interval_to_next_check(ho5.check_interval, ho5.guard_time)
        self.nextStrVar.set(str(nsec) + "秒")

        # タイマー設定
        self.after(VIPoshu.TIMER_INTERVAL, self.hoshu_timer)

    def eh_subject_fetched(self, sender, earg):
        tid = self.hoshu5ch.config.url.tid
        index, title, _ = self.hoshu5ch.subject.search_tuple(tid)

        # ランク
        sbj = self.hoshu5ch.subject
        total = sbj.total_count if sbj else -1
        rank = "{0:03d}/{1:03d}".format(index, total)
        self.rankStrVar.set(rank)

        # タイトル
        if self.update_title:
            self.update_title = False
            self.master.title(title)  # type: ignore

    def eh_last_post_got_from_thread(self, sender, earg):
        # 最終投稿
        ho5 = sender
        dtstr = ho5.last_post_in_thread.strftime("%Y-%m-%d %H:%M:%S")
        self.lpdtStrVar.set(dtstr)
