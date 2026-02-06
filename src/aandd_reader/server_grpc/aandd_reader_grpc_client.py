# aandd_reader_grpc_client.py
from __future__ import annotations

from typing import Any, Optional

import grpc_frame.events_pb2 as events_pb2
import grpc_frame.grpc_client as grpc_client_module
from grpc_frame.grpc_client import GrpcClient


class AanddReaderGrpcClient(GrpcClient):
    def __init__(
        self,
        config: Any = None,
        server_ip: Optional[str] = None,
        server_port: Optional[int] = None,
        logger: Any = None,
        log_level: str = "INFO",
        timeout_sec: Optional[float] = None,
    ) -> None:
        grpc_client_module.events_pb2 = events_pb2

        if config is not None:
            server_ip = config.SERVER_IP
            server_port = config.SERVER_PORT

        super().__init__(
            server_ip=str(server_ip),
            server_port=int(server_port),
            logger=logger,
            log_level=log_level,
            timeout_sec=timeout_sec,
        )
