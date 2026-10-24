[![en](https://img.shields.io/badge/lang-en-red.svg)](https://ohara-lab-su.github.io/aandd_reader/en/tutorials/intro.html) [![ja](https://img.shields.io/badge/lang-ja-yellow.svg)](https://ohara-lab-su.github.io/aandd_reader/ja/tutorials/intro.html)

# チュートリアル

このセクションでは AandD の電子天秤制御 aandd_reader の使い方を段階的に説明します。

A or B のどちらかでお使いください

## A. サーバーの起動 (ese774互換)

- A(ese774) or B(gRPC) のどちらかでお使いください
 
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
```

## B. サーバーの起動 (Event駆動での利用の場合)

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

## 基本的なクライアントの使い方(ese774)共通)
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

    # COMポートを選ぶ
    # aandd_reader = AanddReader(port="COM4", logger=logger)
    aandd_reader = AanddReader(port="COM3", logger=logger)

    # Reset
    aandd_reader.reset()
    time.sleep(0.5)
    
    # 測定
    ret = aandd_reader.meas()
    if ret is False:
        logger.error("Error measuring.")
        logger.error(ret)
        sys.exit(1)
        
    logger.info(ret)

```

## 基本的なクライアントの使い方(gRPC) sync版

実質的には使い方が同じ(呼び出すクラス名が一つだけ異なる)

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
        # timeout_sec=0.5,  # 入力しなければ、None がデフォでNonだと 0.5 になる
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

## 基本的なクライアントの使い方(gRPC) async版

ese774版と使い方が同じ(呼び出すクラス名が一つだけ異なる)

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
        # timeout_sec=0.5,  # 入力しなければ、None がデフォでNonだと 0.5 になる
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


## イベント起動

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

    # --- Event 測定の準備（順番はクライアント内部に閉じ込める） ---
    client.prepare_event_measurement(
        topic="weight_threshold",
        threshold_g=10.0,  # 閾値g
        above=True,
        once=True,
        # trigger_mode="mean",
        trigger_mode="raw",
        # trigger_window=3,
        # trigger_min_samples=3,
    )

    # --- 1イベント待つ ---
    event = client.wait_event()
    on_weight_event(event)

    # --- 後始末 ---
    client.stream_stop()
    time.sleep(0.1)


if __name__ == "__main__":
    main()

```

---
## 作者
- Kengo NAKADA