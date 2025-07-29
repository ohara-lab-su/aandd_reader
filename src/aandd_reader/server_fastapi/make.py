#!/usr/bin/env python
import os
from contextlib import contextmanager

# make
from fastapi_frame.routers.make_pyi_device_router import make_pyi_device_router
from fastapi_frame.clients.make_pyi_sync_device_client import (
    make_pyi_sync_device_client,
)
from fastapi_frame.clients.make_pyi_async_device_client import (
    make_pyi_async_device_client,
)

from aandd_reader.server_fastapi.spec_ctrl import aandd_reader_api_spec


@contextmanager
def chdir(path):
    prev_cwd = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(prev_cwd)


with chdir("clients"):
    # Async client
    make_pyi_async_device_client(
        filename="async_aandd_reader_client.pyi",
        api_spec=aandd_reader_api_spec,
        class_name="AsyncAanddReaderClient",
    )

    # Sync client
    make_pyi_sync_device_client(
        filename="sync_aandd_reader_client.pyi",
        api_spec=aandd_reader_api_spec,
        class_name="SyncAanddReaderClient",
    )

with chdir("routers"):
    # router Device
    make_pyi_device_router(
        filename="aandd_reader_router.pyi",
        api_spec=aandd_reader_api_spec,
        class_name="AanddReaderRouter",
    )
