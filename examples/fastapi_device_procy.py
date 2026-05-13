#!/usr/bin/env python
"""
Kengo NAKADA:
https://github.com/shimane-dev, https://github.com/kengo-nakada
kengo.nakada@mat.shimane-u.ac.jp, kengo.nakada@gmail.com
"""

# import pytest
import asyncio

import time
import logging
from pathlib import Path

from ese774_frame import DeviceProxy
from aandd_reader import Config

# from aandd_reader import AsyncAanddReaderClient
from x_logger import XLogger

# httpx のログを WARNING レベル以上にする（INFO を抑制）
logging.getLogger("httpx").setLevel(logging.WARNING)


# @pytest.mark.asyncio
# async def test_fastapi_async_meas():
async def main():
    # HERE = Path(__file__).parent
    # Config.load_yaml(HERE / "config_aandd1_server1.yaml")

    # Config.load_yaml("config_aandd1_server1.yaml")
    Config.load_yaml("config_aandd2_server4.yaml")

    log_level = "info"

    logger = XLogger(
        log_level="info",
        logger_name=Config.CLIENT_LOGGER_NAME,
    )
    # client = AsyncAanddReaderClient(
    #     config=Config,
    #     logger=logger,
    #     log_level=log_level,
    # )
    client = DeviceProxy(
        "AanddReader",
        config=Config,
        logger=logger,
        log_level=log_level,
    )
    ret = await client.meas()
    print(ret)


if __name__ == "__main__":
    asyncio.run(main())
