#!/usr/bin/env python
"""

Kengo NAKADA:
https://github.com/shimane-dev, https://github.com/kengo-nakada
kengo.nakada@mat.shimane-u.ac.jp, kengo.nakada@gmail.com
"""
import pytest


@pytest.mark.asyncio
async def test_fastapi_async_meas():
    import logging

    # httpx のログを WARNING レベル以上にする（INFO を抑制）
    logging.getLogger("httpx").setLevel(logging.WARNING)

    from aandd_reader.config import Config
    from aandd_reader.server_fastapi.clients import AsyncAanddReaderClient
    from x_logger import XLogger

    Config.load_yaml("config_server.yaml")

    logger = XLogger(log_level="info", logger_name=Config.CLIENT_LOGGER_NAME)
    client = AsyncAanddReaderClient(config=Config, logger=logger)
    assert client is not None, "Connect Error"

    ret = await client.get_serial_number()
    print(ret)
    assert "result" == "result"
    # send_command("unknown")  # これはエラーになる
