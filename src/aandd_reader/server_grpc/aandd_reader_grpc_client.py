# aandd_reader_grpc_client.py
from __future__ import annotations

from typing import Any, Optional

import grpc_frame.events_pb2 as events_pb2
import grpc_frame.grpc_client as grpc_client_module
from grpc_frame.grpc_client import GrpcClient


class AanddReaderGrpcClient(GrpcClient):
    def __init__(
        self,
        config: Optional[Any] = None,
        server_ip: Optional[str] = None,
        server_port: Optional[int] = None,
        timeout_sec: Optional[float] = None,
        logger: Optional[Any] = None,
        log_level: Optional[str] = None,
    ) -> None:
        """

        Args:
            config (Any):
            server_ip (str):  gRPC ではなくて、Device Ctrl 側に食わせる
            server_port (int):  gRPC ではなくて、Device Ctrl 側に食わせる
            timeout_sec (float): Device Ctrl 側 (None だとデフォの 0.5)
            logger (Any):
            log_level (str):
        """
        grpc_client_module.events_pb2 = events_pb2

        if config is not None:
            server_ip = config.SERVER_IP
            server_port = config.GRPC_PORT

        super().__init__(
            server_ip=str(server_ip),
            server_port=int(server_port),
            timeout_sec=timeout_sec,
            logger=logger,
            log_level=log_level,
        )

        # for gRPC Event
        self._event_topic: Optional[str] = None
        self._event_once: bool = True

    def prepare_event_measurement(
        self,
        *,
        topic: str,
        threshold_g: float,
        above: bool = True,
        once: bool = True,
        # --- trigger mode ---
        trigger_mode: str = "raw",
        trigger_window: int = 3,
        trigger_min_samples: Optional[int] = None,
        trigger_alpha: float = 0.3,
        trigger_stable_only: bool = False,
    ) -> None:
        """
        Event 計測の用の煩雑な手続きを省略するメソッド

        Args:
            topic (str): gRPC-Event につける名前
            threshold_g (float): 閾値
            above (bool): 閾値の上(True) or した(False)
            once (bool): Event が一回終わったら Arm 終わるか？(true) そのまま続けるか？

            trigger_mode (str): raw / mean / median / ema
            trigger_window (int): 平均/中央値の窓サイズ
            trigger_min_samples (Optional[int]): 判定に必要な最小サンプル数
            trigger_alpha (float): EMA 係数
            trigger_stable_only (bool): True の場合 ST のみを判定に使う

        Returns:
        """
        self.stream_start()

        self.event_set_config(
            threshold_g=threshold_g,
            above=above,
            topic=topic,
        )

        # --- trigger mode 設定 ---
        self.set_trigger_mode(
            mode=trigger_mode,
            window=trigger_window,
            min_samples=trigger_min_samples,
            alpha=trigger_alpha,
            stable_only=trigger_stable_only,
        )

        self.event_arm(once=once)

        self._event_topic = topic
        self._event_once = once

    def wait_event(self):
        """1イベント待つための薄いラッパー"""
        topic = getattr(self, "_event_topic", None)
        if topic is None:
            raise RuntimeError("event is not prepared")

        for event in self.subscribe(topic=topic, once=True):
            return event
