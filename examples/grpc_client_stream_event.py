#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import time
from typing import Any

from aandd_reader_grpc_client import AandDReaderGrpcClient


def on_weight_event(payload: Any) -> None:
    print("=== EVENT RECEIVED ===")
    print(payload)
    print("=======================")


def main() -> None:
    client = AandDReaderGrpcClient(
        host="10.170.10.38",
        port=50051,
    )

    # 1) サーバ側で stream を開始（スレッド起動）
    client.stream_start()

    # 2) 閾値条件を設定（ctrl 側 AanddReader.event_set_config）
    #    topic は Subscribe(topic=...) と一致させます。
    client.event_set_config(
        threshold=10.0,
        above=True,
        topic="weight_threshold",
    )

    # 3) 1回分だけイベント待機状態にする（ctrl 側 AanddReader.event_arm）
    client.event_arm()

    # 4) サーバからのイベントを待つ（polling ではなく Subscribe のストリーム）
    for event in client.subscribe(
        topic="weight_threshold",
        once=True,
    ):
        on_weight_event(event)
        break

    # 5) 後始末
    client.stream_stop()
    time.sleep(0.1)


if __name__ == "__main__":
    main()
