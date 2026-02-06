# meas_grpc.py
from __future__ import annotations

import logging
import time

from aandd_reader_grpc_client import AanddReaderGrpcClient
from x_logger import XLogger


def main() -> None:
    # logging.basicConfig(level="INFO")
    # logger = logging.getLogger("aandd_meas_grpc")
    logger = XLogger(log_level="INFO", logger_name="aandd_meas_grpc")

    client = AanddReaderGrpcClient(
        server_ip="127.0.0.1",
        server_port=50051,
        logger=logger,
        log_level="INFO",
        timeout_sec=5.0,
    )

    client.reset()
    time.sleep(0.5)

    value = client.meas()
    logger.info(value)

    client.close()


if __name__ == "__main__":
    main()
