#!/usr/bin/env python
"""
Kengo NAKADA:
https://github.com/shimane-dev, https://github.com/kengo-nakada
kengo.nakada@mat.shimane-u.ac.jp, kengo.nakada@gmail.com
"""

from pathlib import Path

from aandd_reader.config import Config
from aandd_reader.aandd_reader import AanddReader
from aandd_reader.server_fastapi.routers import AanddReaderRouter
from aandd_reader.server_fastapi.spec_ctrl import aandd_reader_api_spec

from ese774_frame.api_server import FastApiServer
from x_logger.x_logger import XLogger

if __name__ == "__main__":
    # HERE = Path(__file__).parent
    # Config.load_yaml(HERE / "config_aandd1_server1.yaml")
    # Config.load_yaml("config_aandd1_server1.yaml")
    Config.load_yaml("config_aandd2_server4.yaml")

    logger = XLogger(
        log_level="debug",
        logger_name=Config.SERVER_LOGGER_NAME,
        log_mode="rotate",
        # log_mode="file",
        log_name="c:/opt/log/aandd.log",
    )
    logger.info(f"log_mode = {logger.log_mode}")
    logger.info(f"log_name = {logger.log_name}")
    logger.info(f"PORT = {Config.DEVICE_PORT}")

    server = FastApiServer(
        device_cls=AanddReader,  # 制御クラス
        router_cls=AanddReaderRouter,  # routerクラス
        config=Config,
        api_spec=aandd_reader_api_spec,
        device_kwargs={
            "port": Config.DEVICE_PORT
        },  # COBOTTA制御Classのコンストラクタ引数)
        logger=logger,
        logger_name=Config.SERVER_LOGGER_NAME,  # LOGGER_NAME
        lifespan_msg_prefix="AANDD",
    )
    server.run(host=Config.SERVER_IP, port=Config.FASTAPI_PORT)
