# AAndD_Reader

[ohara-lab-su](https://ohara-lab-su.github.io/)/[aandd_reader](https://ohara-lab-su.github.io/aandd_reader/)

## info

- FX-200i 天秤
- https://www.aandd.co.jp/pdf_storage/manual/balance/m_fzi_fxi_fziwp_fxiwp.pdf

- USB シリアルコンバータ
  - RS-USB602F
  - https://www.ratocsystems.com/products/rs232c/
  - RATOC Systems, Inc
    - windows-driver
    - https://www.ratocsystems.com/dlsoft/dlsoft_rs232c/dlsoft_232cusb/usb602f_win/

## 使い方(デバイスサーバーの起動)

```python
from aandd_reader.config import Config
from aandd_reader.aandd_reader import AanddReader
from aandd_reader.server_fastapi.routers import AanddReaderRouter
from aandd_reader.server_fastapi.spec_ctrl import aandd_reader_api_spec

from ese774_frame.api_server import FastApiServer
from x_logger.x_logger import XLogger


if __name__ == "__main__":
    Config.load_yaml("config_server.yaml")
    logger = XLogger(
        log_level="debug",
        logger_name=Config.SERVER_LOGGER_NAME,
        log_mode="rotate",
        # log_mode="file",
        log_name="c:/opt/log/aandd.log",
    )
    logger.info(f"log_mode = {logger.log_mode}")
    logger.info(f"log_name = {logger.log_name}")
    logger.info(f"PORT = {Config.PORT}")

    server = FastApiServer(
        device_cls=AanddReader,  # 制御クラス
        router_cls=AanddReaderRouter,  # routerクラス
        config=Config,
        api_spec=aandd_reader_api_spec,
        device_kwargs={"port": Config.PORT},  # 制御Classのコンストラクタ引数)
        logger=logger,
        logger_name=Config.SERVER_LOGGER_NAME,  # LOGGER_NAME
        lifespan_msg_prefix="AANDD",
    )
    server.run(host=Config.SERVER_IP, port=Config.SERVER_PORT)

```
## Client

```python
import asyncio
import logging

# httpx のログを WARNING レベル以上にする（INFO を抑制）
logging.getLogger("httpx").setLevel(logging.WARNING)

from aandd_reader.config import Config
from aandd_reader.server_fastapi.clients import AsyncAanddReaderClient
from x_logger import XLogger

async def main():
    Config.load_yaml("config_server.yaml")
    
    logger = XLogger(log_level="info", logger_name=Config.CLIENT_LOGGER_NAME)
    client = AsyncAanddReaderClient(config=Config, logger=logger)
    
    ret = await client.meas()
    logger.info(ret)

if __name__ == '__main__':
    asyncio.run(main())
```
