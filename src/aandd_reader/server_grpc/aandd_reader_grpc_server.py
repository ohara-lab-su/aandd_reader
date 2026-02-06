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

# --- gRPC-frame (new: ctrl.Control/Describe, ctrl.Control/Call) ---
# import grpc_frame.ctrl_pb2 as ctrl_pb2
import grpc_frame.ctrl_pb2_grpc as ctrl_pb2_grpc
from grpc_frame.grpc_server import _ControlServicer
from x_logger.x_logger import XLogger


# ============================================================
# Servicer クラス を用いた、server の起動
# ============================================================
def aandd_reader_server(
    port: str,
    logger: Optional[Any] = None,
    log_level: str = "INFO",
) -> None:
    """ """
    # XLogger が存在しない時に仕方がないのでデフォルトの logging を使う
    if logger is None:
        import logging

        # from x_logger.util import *

        logging.basicConfig(level=log_level.upper())
        logger = logging.getLogger(__name__)

    logger = logger

    # ========================================================
    # gRPC server を先に作る（旧版と同一）
    # ========================================================
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10),
    )

    bind_addr: str = f"{grpc_host}:{grpc_port}"
    ret: int = server.add_insecure_port(bind_addr)
    if ret == 0:
        raise RuntimeError(f"bind failed: {bind_addr}")

    logger.info(f"gRPC bind OK: {bind_addr}")

    # ========================================================
    # server.start() を先に呼ぶ（最重要）
    # ========================================================
    server.start()

    # self-check（旧版と同一）
    ch = grpc.insecure_channel(bind_addr)
    channel_ready_future(ch).result(timeout=2.0)
    logger.info("gRPC self-check OK")

    ctrl = AanddReader(
        port="COM3",
        logger=logger,
        log_level=log_level,
    )

    servicer = _ControlServicer(
        ctrl_obj=ctrl,
        logger=logger,
        log_level=log_level,
    )

    ctrl_pb2_grpc.add_ControlServicer_to_server(
        servicer,
        server,
    )

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt")

    finally:
        server.stop(grace=None)
        logger.info("gRPC server stopped")


# ------------------------------------------------------------
# main
# ------------------------------------------------------------
if __name__ == "__main__":
    PORT = "COM3"
    LOG_LEVEL = "INFO"

    LOGGER = XLogger(log_level=LOG_LEVEL, logger_name="JoypadServer")

    aandd_reader_server(
        port=PORT,
        logger=LOGGER,
        log_level=LOG_LEVEL,
    )
