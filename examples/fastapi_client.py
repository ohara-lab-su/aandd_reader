#!/usr/bin/env python
"""

Kengo NAKADA:
https://github.com/shimane-dev, https://github.com/kengo-nakada
kengo.nakada@mat.shimane-u.ac.jp, kengo.nakada@gmail.com
"""
# import pytest
import asyncio

# @pytest.mark.asyncio
# async def test_fastapi_async_meas():
async def main():
    import logging
    from pathlib import Path

    # httpx のログを WARNING レベル以上にする（INFO を抑制）
    logging.getLogger("httpx").setLevel(logging.WARNING)

    from aandd_reader import Config
    from aandd_reader import AsyncAanddReaderClient
    from x_logger import XLogger

    HERE = Path(__file__).parent
    Config.load_yaml("config_server1.yaml")

    logger = XLogger(log_level="info", logger_name=Config.CLIENT_LOGGER_NAME)
    client = AsyncAanddReaderClient(config=Config, logger=logger)
    assert client is not None, "Connect Error"

    ret = await client.meas()
    print(ret)
    assert "result" == "result"
    # send_command("unknown")  # これはエラーになる

if __name__ == "__main__":
    asyncio.run(main())