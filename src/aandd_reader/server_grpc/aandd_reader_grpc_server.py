#!/usr/bin/env python3
"""
Kengo NAKADA
kengo.nakada@mat.shimane-u.ac.jp
kengo.nakada@gmail.com
"""

from __future__ import annotations

import time
from typing import Any, Optional

import grpc
from grpc import channel_ready_future

from grpc_frame.grpc_server import create_grpc_server

from aandd_reader.aandd_reader import AanddReader
from x_logger import XLogger


# ============================================================
# Servicer クラス を用いた、server の起動
# ============================================================
def aandd_reader_server(
    *,
    device_port: str,
    grpc_host: str,
    grpc_port: int,
    logger: Optional[Any] = None,
    log_level: Optional[str] = None,
) -> None:
    """"""
    # XLogger が存在しない時に仕方がないのでデフォルトの logging を使う
    if logger is None:
        import logging

        log_level = log_level or "INFO"
        logging.basicConfig(level=log_level.upper())
        logger = logging.getLogger(__name__)

    # ========================================================
    # 制御class
    # ========================================================
    ctrl = AanddReader(
        port=device_port,
        logger=logger,
        log_level=log_level,
    )

    # ========================================================
    # gRPC server
    # ========================================================
    server = create_grpc_server(
        ctrl_obj=ctrl,
        logger=logger,
        log_level=log_level,
        max_workers=10,
    )

    bind_addr: str = f"{grpc_host}:{grpc_port}"
    ret: int = server.add_insecure_port(bind_addr)
    if ret == 0:
        raise RuntimeError(f"bind failed: {bind_addr}")

    logger.info(f"gRPC bind OK: {bind_addr}")

    server.start()

    ch = grpc.insecure_channel(bind_addr)
    channel_ready_future(ch).result(timeout=2.0)
    logger.info("gRPC self-check OK")

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt")

    finally:
        server.stop(grace=None)
        logger.info("gRPC server stopped")
        try:
            ctrl.close()
        except Exception as e:
            pass


if __name__ == "__main__":
    DEVICE_PORT = "COM3"
    GRPC_HOST = "10.170.10.38"
    GRPC_PORT = 50051
    LOG_LEVEL = "INFO"

    LOGGER = XLogger(
        log_level=LOG_LEVEL,
        logger_name="AanddReaderServer",
    )

    aandd_reader_server(
        device_port=DEVICE_PORT,
        grpc_host=GRPC_HOST,
        grpc_port=GRPC_PORT,
        logger=LOGGER,
        log_level=LOG_LEVEL,
    )
