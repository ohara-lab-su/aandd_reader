#!/usr/bin/env python
"""
Kengo NAKADA:
https://github.com/shimane-dev, https://github.com/kengo-nakada
kengo.nakada@mat.shimane-u.ac.jp, kengo.nakada@gmail.com
"""
from aandd_reader.config import Config
from aandd_reader.aandd_reader import AanddReader
from aandd_reader.server_fastapi.routers import AanddReaderRouter
from aandd_reader.server_fastapi.spec_ctrl import aandd_reader_api_spec

from fastapi_frame.api_server import FastApiServer
from x_logger.x_logger import XLogger


if __name__ == "__main__":
    Config.load_yaml("config_server.yaml")
    logger = XLogger(log_level="debug", logger_name=Config.SERVER_LOGGER_NAME)

    logger.info(f"PORT = {Config.PORT}")

    server = FastApiServer(
        device_cls=AanddReader,  # 制御クラス
        router_cls=AanddReaderRouter,  # routerクラス
        config=Config,
        api_spec=aandd_reader_api_spec,
        device_kwargs={"port": Config.PORT},  # COBOTTA制御Classのコンストラクタ引数)
        logger=logger,
        logger_name=Config.SERVER_LOGGER_NAME,  # LOGGER_NAME
        lifespan_msg_prefix="AANDD",
    )
    server.run(host=Config.SERVER_IP, port=Config.SERVER_PORT)
