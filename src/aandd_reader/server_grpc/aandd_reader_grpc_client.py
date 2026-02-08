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
            server_port = config.SERVER_PORT

        super().__init__(
            server_ip=str(server_ip),
            server_port=int(server_port),
            timeout_sec=timeout_sec,
            logger=logger,
            log_level=log_level,
        )
