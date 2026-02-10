#!/usr/bin/env python3
"""
Kengo NAKADA
kengo.nakada@mat.shimane-u.ac.jp
kengo.nakada@gmail.com
"""

from __future__ import annotations

import time
from concurrent import futures
from typing import Any, Optional

import grpc
from grpc import channel_ready_future

from aandd_reader import Config
from aandd_reader.server_grpc import aandd_reader_server

from x_logger.x_logger import XLogger


# ------------------------------------------------------------
# main
# ------------------------------------------------------------
if __name__ == "__main__":
    Config.load_yaml("config_server1.yaml")

    DEVICE_PORT = Config.DEVICE_PORT
    GRPC_HOST = Config.SERVER_IP
    GRPC_PORT = Config.GRPC_PORT
    # DEVICE_PORT = "COM3"
    # GRPC_HOST = "10.170.10.38"
    # GRPC_PORT = 50051
    LOG_LEVEL = "INFO"

    LOGGER = XLogger(
        log_level=LOG_LEVEL,
        logger_name="JoypadServer",
    )

    aandd_reader_server(
        device_port=DEVICE_PORT,
        grpc_host=GRPC_HOST,
        grpc_port=GRPC_PORT,
        logger=LOGGER,
        log_level=LOG_LEVEL,
    )
