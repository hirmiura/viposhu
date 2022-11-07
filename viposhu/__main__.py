#!/usr/bin/env -S python3
# SPDX-License-Identifier: MIT
# Copyright 2022 hirmiura <https://github.com/hirmiura>
import json
import logging as lg
import sys
from logging import getLogger
from logging.config import dictConfig

from .viposhu import VIPoshu

LOG_CONF = "log_config.json"
logger = getLogger(__name__)


def init_logger():
    with open(LOG_CONF) as f:
        log_conf = json.load(f)
    dictConfig(log_conf)
    logger.info(f"{LOG_CONF}を読み込みました")


def init_app():
    poshu = VIPoshu()
    poshu.mainloop()


def main() -> int:
    init_logger()
    init_app()
    lg.shutdown()
    return 0


if __name__ == "__main__":
    sys.exit(main())
