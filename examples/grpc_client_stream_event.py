#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import time
from typing import Any

from aandd_reader_grpc_client import AandDReaderGrpcClient


# --- イベント受信時に起動したい処理 ---
def on_weight_event(payload: Any) -> None:
    # payload は adapter.unpack_result() 済み
    print("=== EVENT RECEIVED ===")
    print(payload)
    print("=======================")


def main() -> None:
    client = AandDReaderGrpcClient(
        host="10.170.10.38",
        port=50051,
    )

    # --- stream 測定開始（サーバ側でスレッド起動） ---
    # 閾値・条件はサーバ側 ctrl 実装に委ねる
    client.stream_start()

    # --- event 待機 ---
    # topic 名はサーバ側 publish と一致させる
    for event in client.subscribe(
        topic="weight_threshold",
        once=True,
    ):
        on_weight_event(event)
        break

    # --- 必要なら再度待機可能 ---
    # client.stream_wait()
    # for event in client.subscribe(topic="weight_threshold", once=True):
    #     on_weight_event(event)

    # --- 終了 ---
    client.stream_stop()
    time.sleep(0.1)


if __name__ == "__main__":
    main()
