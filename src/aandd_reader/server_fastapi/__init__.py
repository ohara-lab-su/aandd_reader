#!/usr/bin/env python
"""
aandd_reader FastAPI client / router / DeviceProxy registration.

このモジュールは FastAPI/DeviceProxy 層の公開インターフェースである。
ローカル制御クラス AanddReader には依存しない。
"""
from aandd_reader.server_fastapi.clients.async_aandd_reader_client import (
    AsyncAanddReaderClient,
)
from aandd_reader.server_fastapi.clients.sync_aandd_reader_client import (
    SyncAanddReaderClient,
)
from aandd_reader.server_fastapi.routers.aandd_reader_router import AanddReaderRouter
from aandd_reader.server_fastapi.spec_ctrl import aandd_reader_api_spec

from ese774_frame.clients import register_device_proxy


DEVICE_PROXY_NAME = "AanddReader"
DEVICE_PROXY_ALIASES = [
    "aandd",
    "AandDReader",
    "aandd_reader",
]


register_device_proxy(
    DEVICE_PROXY_NAME,
    async_client_cls=AsyncAanddReaderClient,
    sync_client_cls=SyncAanddReaderClient,
    api_spec=aandd_reader_api_spec,
    default_async_mode=True,
    aliases=DEVICE_PROXY_ALIASES,
)


__all__ = [
    "DEVICE_PROXY_NAME",
    "DEVICE_PROXY_ALIASES",
    "AsyncAanddReaderClient",
    "SyncAanddReaderClient",
    "AanddReaderRouter",
    "aandd_reader_api_spec",
]
