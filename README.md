# AAndD_Reader

[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/ohara-lab-su/aandd_reader/blob/main/README.md)
[![ja](https://img.shields.io/badge/lang-ja-yellow.svg)](https://github.com/ohara-lab-su/aandd_reader/blob/main/README.ja.md)

[![GitHub](https://img.shields.io/badge/GitHub-ohara--lab--su%2Faandd_reader-181717?logo=github)](https://github.com/ohara-lab-su/aandd_reader/)
[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Documentation-222222?logo=githubpages&logoColor=white)](https://ohara-lab-su.github.io/aandd_reader/en/)
[![Ohara Lab](https://img.shields.io/badge/Ohara%20Lab-Home-4B5563?logo=homeassistant&logoColor=white)](https://ohara-lab-su.github.io/index.en.html)

## Information

- FX-200i balance
- https://www.aandd.co.jp/pdf_storage/manual/balance/m_fzi_fxi_fziwp_fxiwp.pdf

- USB-to-serial converter
  - RS-USB602F
  - https://www.ratocsystems.com/products/rs232c/
  - RATOC Systems, Inc.
    - Windows driver
    - https://www.ratocsystems.com/dlsoft/dlsoft_rs232c/dlsoft_232cusb/usb602f_win/

## Usage (Starting the Device Server)

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
        device_cls=AanddReader,  # Device control class
        router_cls=AanddReaderRouter,  # Router class
        config=Config,
        api_spec=aandd_reader_api_spec,
        device_kwargs={"port": Config.PORT},  # Constructor arguments for the device control class
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

# Set the httpx logging level to WARNING or higher (suppress INFO messages).
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

## Author
- Kengo NAKADA
