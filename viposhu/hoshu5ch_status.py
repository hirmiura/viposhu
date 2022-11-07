#!/usr/bin/env -S python3
# SPDX-License-Identifier: MIT
# Copyright 2022 hirmiura <https://github.com/hirmiura>
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

JST = timezone(timedelta(hours=+9), "JST")


@dataclass
class Hoshu5chStatus:
    """自身が行ったスレ保守の日時を保持しサポートするクラス"""

    last_check: Optional[datetime] = None
    """最終確認日時"""

    last_post: Optional[datetime] = None
    """自身による最終投稿日時"""

    def _update_X(self, varname: str, now: Optional[datetime] = None) -> datetime:
        if not now:
            now = datetime.now(JST)
        exec("self.{} = now".format(varname))
        return now

    def update_last_check(self, now: Optional[datetime] = None) -> datetime:
        return self._update_X("last_check", now)

    def update_last_post(self, now: Optional[datetime] = None) -> datetime:
        return self._update_X("last_post", now)

    def _is_in_X(self, varname: str, num: int) -> bool:
        assert num >= 0
        dt: Optional[datetime] = None
        exec_local: dict[Any, Any] = {"self": self, "dt": dt}
        exec("dt = self.{0}".format(varname), globals(), exec_local)
        dt = exec_local["dt"]
        if not dt:
            return False
        now = datetime.now(JST)
        delta = now - dt
        if delta.total_seconds() < num:
            return True
        return False

    def is_in_check_interval(self, interval_needed: int) -> bool:
        return self._is_in_X("last_check", interval_needed)

    def is_in_guard_time(self, guard_time_needed: int) -> bool:
        return self._is_in_X("last_post", guard_time_needed)

    def get_interval_to_next_check(self, interval: int, guard_time: int) -> int:
        """次にチェックする時間を秒で返す

        Args:
            interval_needed: 通常のチェック間隔(秒)
            guard_time_needed: 投稿防止時間(秒)
        """
        ts_itv = self.last_check.timestamp() if self.last_check else 0
        ts_grd = self.last_post.timestamp() if self.last_post else 0
        next_itv = ts_itv + interval
        next_grd = ts_grd + guard_time
        ts_now = datetime.now(JST).timestamp()
        delta_itv = next_itv - ts_now
        delta_grd = next_grd - ts_now
        delta_to_next = max(delta_itv, delta_grd)
        return int(delta_to_next)

    def clear_datetime(self, sender, earg):
        self.last_check = None
        self.last_post = None
