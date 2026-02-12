#!/usr/bin/env python
"""
Kengo NAKADA:
https://github.com/shimane-dev, https://github.com/kengo-nakada
kengo.nakada@mat.shimane-u.ac.jp, kengo.nakada@gmail.com
"""
# meas_grpc.py
from __future__ import annotations
import asyncio

import time
import logging
from pathlib import Path

# meas_grpc.py

from aandd_reader import Config

# from aandd_reader.server_grpc import AanddReaderGrpcClient
from aandd_reader.server_grpc import AsyncAanddReaderGrpcClient
from x_logger import XLogger

# logging.basicConfig(level="INFO")
# logger = logging.getLogger("aandd_meas_grpc")


async def main() -> None:
    HERE = Path(__file__).parent
    Config.load_yaml(HERE / "config_server1.yaml")

    log_level = "info"

    logger = XLogger(
        log_level=log_level,
        logger_name=Config.CLIENT_LOGGER_NAME,
    )

    client = AsyncAanddReaderGrpcClient(
        config=Config,
        # server_ip="10.170.10.38",
        # server_port=50051,  # gRPC
        # timeout_sec=0.5,  # 入力しなければ、None がデフォでNonだと 0.5 になる
        logger=logger,
        log_level=log_level,
    )

    # client.reset()
    # time.sleep(0.5)

    ret = await client.meas()
    print(ret)

    client.close()


if __name__ == "__main__":
    asyncio.run(main())
