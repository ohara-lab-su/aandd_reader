#!/usr/bin/env python
"""
Kengo NAKADA:
https://github.com/shimane-dev, https://github.com/kengo-nakada
kengo.nakada@mat.shimane-u.ac.jp, kengo.nakada@gmail.com
"""
from typing import Any
from aandd_reader.config import Config
from aandd_reader.server_fastapi.spec_ctrl import aandd_reader_api_spec
from fastapi_frame.clients.sync_device_client import SyncDeviceClient


class SyncAanddReaderClient(
    SyncDeviceClient,
):
    def __init__(
        self,
        config: Config = None,
        server_ip: str = None,
        server_port: int = None,
        logger: Any = None,
        log_level: str = "INFO",
    ):
        """
        旧版との互換インターフェース（引数）を保ったまま
        AsyncDeviceClient に api_spec, base_url を自動設定して渡すラッパ
        """
        if logger is None:
            import logging

            logging.basicConfig(level="INFO")
            logger = logging.getLogger(__name__)

        self._logger = logger
        if config is not None:
            server_ip = config.SERVER_IP
            server_port = config.SERVER_PORT

        base_url = f"http://{server_ip}:{server_port}"
        self._base_url = base_url

        self._logger.info(f"[CLIENT] server_ip = {server_ip}")
        self._logger.info(f"[CLIENT] server_port = {server_port}")
        self._logger.info(f"[CLIENT] base_url = {base_url}")

        super().__init__(
            server_ip=server_ip,
            server_port=server_port,
            api_spec=aandd_reader_api_spec,
            base_url=base_url,
            logger=logger,
            log_level=log_level,
        )
