#!/usr/bin/env python
"""
Kengo NAKADA:
https://github.com/shimane-dev, https://github.com/kengo-nakada
kengo.nakada@mat.shimane-u.ac.jp, kengo.nakada@gmail.com
"""
import re
import asyncio
import nest_asyncio
from pathlib import Path
from typing import Union, Optional, Set

from aandd_reader.config import Config
from aandd_reader.server_fastapi.spec_ctrl import aandd_reader_api_spec
from aandd_reader.server_fastapi.models.comman import ResultResponse

from fastapi_frame.clients.async_device_client import AsyncDeviceClient


class AsyncAanddReaderClient(AsyncDeviceClient):
    def __init__(
        self,
        config: Config = None,
        server_ip: str = None,
        server_port: int = None,
        logger=None,
    ):
        """
        旧版との互換インターフェース（引数）を保ったまま
        AsyncDeviceClient に api_spec, base_url を自動設定して渡すラッパ
        """
        if config is not None:
            server_ip = config.SERVER_IP
            server_port = config.SERVER_PORT

        base_url = f"http://{server_ip}:{server_port}"
        self._base_url = base_url

        logger.info(f"[CLIENT] server_ip = {server_ip}")
        logger.info(f"[CLIENT] server_port = {server_port}")
        logger.info(f"[CLIENT] base_url = {base_url}")

        super().__init__(
            server_ip=server_ip,
            server_port=server_port,
            api_spec=aandd_reader_api_spec,
            base_url=base_url,
            logger=logger,
        )

    #
    # property style で一部メソッドを使えるようにする
    #

    @staticmethod
    def _sync_await(coro):
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            import nest_asyncio

            nest_asyncio.apply()
            return loop.run_until_complete(coro)
        else:
            return asyncio.run(coro)

    # def __getattr__(self, name):
    #     m = re.match(r"^(P|F|I|IO)(\d+)$", name)
    #     if m:
    #         kind, id_num = m.group(1), int(m.group(2))
    #         # 1. 一番堅実：「P", 110 で渡す
    #         print("==getattr==", kind, id_num)
    #         return self._sync_await(self.get_var(kind, id_num))
    #         # 2. もしget_var("P110")しかAPI specで対応してなければ↓
    #         # return self._sync_await(self.get_var(f"{kind}{id_num}"))
    #     raise AttributeError(
    #         f"'{type(self).__name__}' object has no attribute '{name}'"
    #     )

    # def __setattr__(self, name, value):
    #     if isinstance(name, str):
    #         m = re.match(r"^(P|F|I|IO)(\d+)$", name)
    #         if m:
    #             kind, id_num = m.group(1), int(m.group(2))
    #             self._sync_await(self.set_var(kind, id_num, value))
    #             return
    #     super().__setattr__(name, value)
