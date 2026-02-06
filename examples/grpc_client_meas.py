#!/usr/bin/env python
"""
Kengo NAKADA:
https://github.com/shimane-dev, https://github.com/kengo-nakada
kengo.nakada@mat.shimane-u.ac.jp, kengo.nakada@gmail.com
"""
# meas_grpc.py
from __future__ import annotations

import time
import logging
from pathlib import Path

from aandd_reader import Config
from aandd_reader.server_grpc import AanddReaderGrpcClient
from x_logger import XLogger

# logging.basicConfig(level="INFO")
# logger = logging.getLogger("aandd_meas_grpc")


def main() -> None:
    HERE = Path(__file__).parent
    Config.load_yaml(HERE / "config_server1.yaml")

    log_level = "info"

    logger = XLogger(
        log_level="INFO",
        logger_name=Config.CLIENT_LOGGER_NAME,
    )

    client = AanddReaderGrpcClient(
        server_ip="10.170.10.38",
        server_port=50051,  # gRPC
        logger=logger,
        log_level="INFO",
        timeout_sec=5.0,
    )

    # client.reset()
    # time.sleep(0.5)

    ret = client.meas()
    print(ret)

    client.close()


if __name__ == "__main__":
    main()
