#!/usr/bin/env -S python3
# SPDX-License-Identifier: MIT
# Copyright 2022 hirmiura <https://github.com/hirmiura>
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional

JST = timezone(timedelta(hours=+9), "JST")


@dataclass
class Hoshu5chStatus:
    """自身が行ったスレ保守の日時を保持しサポートするクラス"""

    last_check: Optional[datetime] = None
    """最終確認日時"""

    last_post: Optional[datetime] = None
    """自身による最終投稿日時"""

    last_post_in_thread: Optional[datetime] = None
    """スレ内の最終投稿日時"""

    def _update_X(self, varname: str, now: Optional[datetime] = None) -> datetime:
        if not now:
            now = datetime.now(JST)
        exec("self.{} = now".format(varname))
        return now

    def update_last_check(self, now: Optional[datetime] = None) -> datetime:
        return self._update_X("last_check", now)

    def update_last_post(self, now: Optional[datetime] = None) -> datetime:
        return self._update_X("last_post", now)

    def update_last_post_in_thread(self, now: Optional[datetime] = None) -> datetime:
        return self._update_X("last_post_in_thread", now)

    def get_interval_to_next_check(self, interval: int, guard_time: int) -> int:
        """次にチェックする時間を秒で返す

        Args:
            interval_needed: 通常のチェック間隔(秒)
            guard_time_needed: 投稿防止時間(秒)
        """
        ts_lc = self.last_check.timestamp() if self.last_check else 0
        ts_lp_m = self.last_post.timestamp() if self.last_post else 0
        ts_lp_t = self.last_post_in_thread.timestamp() if self.last_post_in_thread else 0
        next_lc = ts_lc + interval
        next_lp_m = ts_lp_m + guard_time
        next_lp_t = ts_lp_t + guard_time
        ts_now = datetime.now(JST).timestamp()
        delta_lc = next_lc - ts_now
        delta_lp_m = next_lp_m - ts_now
        delta_lp_t = next_lp_t - ts_now
        delta_to_next = max(delta_lc, delta_lp_m, delta_lp_t)
        return int(delta_to_next)

    def clear_datetime(self, sender, earg):
        self.last_check = None
        self.last_post = None
