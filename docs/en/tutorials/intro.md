[![en](https://img.shields.io/badge/lang-en-red.svg)](https://ohara-lab-su.github.io/aandd_reader/en/tutorials/intro.html) [![ja](https://img.shields.io/badge/lang-ja-yellow.svg)](https://ohara-lab-su.github.io/aandd_reader/ja/tutorials/intro.html)

# Tutorial

This tutorial explains how to use `aandd_reader` to control A&D electronic balances, step by step.

Choose either server option A or B.

## A. Starting the server (ese774-compatible / FastAPI)

- Use either A (ese774/FastAPI) or B (gRPC).
 
```python
#!/usr/bin/env python
from pathlib import Path

from aandd_reader.config import Config
from aandd_reader.aandd_reader import AanddReader
from aandd_reader.server_fastapi.routers import AanddReaderRouter
from aandd_reader.server_fastapi.spec_ctrl import aandd_reader_api_spec

from ese774_frame.api_server import FastApiServer
from x_logger.x_logger import XLogger


if __name__ == "__main__":
    HERE = Path(__file__).parent

    Config.load_yaml(HERE / "config_server1.yaml")
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
        device_cls=AanddReader,  # control class
        router_cls=AanddReaderRouter,  # router class
        config=Config,
        api_spec=aandd_reader_api_spec,
        device_kwargs={
            "port": Config.DEVICE_PORT
        },  # constructor arguments for the control class)
        logger=logger,
        logger_name=Config.SERVER_LOGGER_NAME,  # LOGGER_NAME
        lifespan_msg_prefix="AANDD",
    )
    server.run(host=Config.SERVER_IP, port=Config.FASTAPI_PORT)
```

## B. Starting the server (gRPC / event-driven use)

```python
#!/usr/bin/env python3
from __future__ import annotations

import time
from concurrent import futures
from typing import Any, Optional

import grpc
from grpc import channel_ready_future

from aandd_reader import Config
from aandd_reader.server_grpc import aandd_reader_server

from x_logger.x_logger import XLogger


if __name__ == "__main__":
    Config.load_yaml("config_server1.yaml")

    # DEVICE_PORT = Config.DEVICE_PORT
    GRPC_HOST = Config.SERVER_IP
    GRPC_PORT = Config.GRPC_PORT
    DEVICE_PORT = "COM4"
    # GRPC_HOST = "10.170.10.38"
    # GRPC_PORT = 50051
    LOG_LEVEL = "INFO"

    LOGGER = XLogger(
        log_level=LOG_LEVEL,
        logger_name="JoypadServer",
    )

    aandd_reader_server(
        device_port=DEVICE_PORT,
        grpc_host=GRPC_HOST,
        grpc_port=GRPC_PORT,
        logger=LOGGER,
        log_level=LOG_LEVEL,
    )

```

## Basic direct-control client (also applicable to ese774)
```python

#!/usr/bin/env python
import sys
import time
from aandd_reader import AanddReader
from x_logger import XLogger


if __name__ == "__main__":

    log_mode = "file"
    logger = XLogger(
        log_level="info",
        log_mode=log_mode,
        log_name="aandd.log",
        logger_name="aandd_reader",
    )

    # Select the COM port
    # aandd_reader = AanddReader(port="COM4", logger=logger)
    aandd_reader = AanddReader(port="COM3", logger=logger)

    # Reset
    aandd_reader.reset()
    time.sleep(0.5)
    
    # Measurement
    ret = aandd_reader.meas()
    if ret is False:
        logger.error("Error measuring.")
        logger.error(ret)
        sys.exit(1)
        
    logger.info(ret)

```

## Basic gRPC client (synchronous)

The calling pattern is essentially the same; the client class differs.

```python
#!/usr/bin/env python
from __future__ import annotations

import time
import logging
from pathlib import Path

# meas_grpc.py

from aandd_reader import Config
from aandd_reader.server_grpc import AanddReaderGrpcClient
from x_logger import XLogger

# logging.basicConfig(level="INFO")
# logger = logging.getLogger("aandd_meas_grpc")


def main() -> None:
    HERE = Path(__file__).parent
    Config.load_yaml(HERE / "config_server1.yaml")

    log_level = "info"

    logger = XLogger(
        log_level=log_level,
        logger_name=Config.CLIENT_LOGGER_NAME,
    )

    client = AanddReaderGrpcClient(
        config=Config,
        # server_ip="10.170.10.38",
        # server_port=50051,  # gRPC
        # timeout_sec=0.5,  # if omitted, defaults to None (see implementation for effective timeout)
        logger=logger,
        log_level=log_level,
    )

    # client.reset()
    # time.sleep(0.5)

    ret = client.meas()
    print(ret)

    client.close()


if __name__ == "__main__":
    main()
```

## Basic gRPC client (asynchronous)

The usage is similar to the ese774 version, but asynchronous calls must be awaited.

```python
#!/usr/bin/env python
from __future__ import annotations
import asyncio

import time
import logging
from pathlib import Path

# meas_grpc.py

from aandd_reader import Config

# from aandd_reader.server_grpc import AanddReaderGrpcClient
from aandd_reader.server_grpc import AsyncAanddReaderGrpcClient
from x_logger import XLogger

# logging.basicConfig(level="INFO")
# logger = logging.getLogger("aandd_meas_grpc")


async def main() -> None:
    HERE = Path(__file__).parent
    Config.load_yaml(HERE / "config_server1.yaml")

    log_level = "info"

    logger = XLogger(
        log_level=log_level,
        logger_name=Config.CLIENT_LOGGER_NAME,
    )

    client = AsyncAanddReaderGrpcClient(
        config=Config,
        # server_ip="10.170.10.38",
        # server_port=50051,  # gRPC
        # timeout_sec=0.5,  # if omitted, defaults to None (see implementation for effective timeout)
        logger=logger,
        log_level=log_level,
    )

    # client.reset()
    # time.sleep(0.5)

    ret = await client.meas()
    print(ret)

    client.close()


if __name__ == "__main__":
    asyncio.run(main())
```


## Event-driven measurement

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import time
from typing import Any

from aandd_reader import Config
from aandd_reader.server_grpc import AanddReaderGrpcClient
from x_logger import XLogger


def on_weight_event(payload: Any) -> None:
    print("=== EVENT RECEIVED ===")
    print(payload)
    print("=======================")


def main() -> None:
    Config.load_yaml("config_server1.yaml")

    log_level = "info"

    logger = XLogger(
        log_level=log_level,
        logger_name="aandd_reader",
    )

    client = AanddReaderGrpcClient(
        config=Config,
        logger=logger,
        log_level=log_level,
    )

    # --- Prepare event measurement (the client handles the sequence internally) ---
    client.prepare_event_measurement(
        topic="weight_threshold",
        threshold_g=10.0,  # threshold in grams
        above=True,
        once=True,
        # trigger_mode="mean",
        trigger_mode="raw",
        # trigger_window=3,
        # trigger_min_samples=3,
    )

    # --- Wait for one event ---
    event = client.wait_event()
    on_weight_event(event)

    # --- Cleanup ---
    client.stream_stop()
    time.sleep(0.1)


if __name__ == "__main__":
    main()

```

---
## Author
- Kengo NAKADA