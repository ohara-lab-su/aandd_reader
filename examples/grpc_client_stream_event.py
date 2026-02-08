#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import time
from typing import Any

from aandd_reader import Config
from aandd_reader.server_grpc import AanddReaderGrpcClient
from x_logger import XLogger


def on_weight_event(payload: Any) -> None:
    print("=== EVENT RECEIVED ===")
    print(payload)
    print("=======================")


def main() -> None:
    Config.load_yaml("config_server1.yaml")

    log_level = "info"

    logger = XLogger(
        log_level=log_level,
        logger_name="aandd_reader",
    )

    client = AanddReaderGrpcClient(
        config=Config,
        logger=logger,
        log_level=log_level,
    )

    # --- Event 測定の準備（順番はクライアント内部に閉じ込める） ---
    client.prepare_event_measurement(
        topic="weight_threshold",
        threshold=10.0,  # 閾値g
        above=True,
        once=True,
    )

    # --- 1イベント待つ ---
    event = client.wait_event()
    on_weight_event(event)

    # --- 後始末 ---
    client.stream_stop()
    time.sleep(0.1)


if __name__ == "__main__":
    main()
