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
        threshold: float,
        above: bool = True,
        once: bool = True,
    ) -> None:
        """
        Event 計測の用の煩雑な手続きを省略するメソッド

        Args:
            topic:
            threshold:
            above:
            once:

        Returns:

        """
        self.stream_start()

        self.event_set_config(
            threshold=threshold,
            above=above,
            topic=topic,
        )

        self.event_arm()

        self._event_topic = topic
        self._event_once = once

    def wait_event(self):
        """1イベント待つための薄いラッパー"""
        topic = getattr(self, "_event_topic", None)
        if topic is None:
            raise RuntimeError("event is not prepared")

        for event in self.subscribe(topic=topic, once=True):
            return event
