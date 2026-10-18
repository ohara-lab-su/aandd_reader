#!/usr/bin/env python
# coding: utf-8
"""aandd_reader server_fastapi の DeviceProxy 用 .pyi 生成スクリプト。"""

from pathlib import Path

from ese774_frame.clients.make_pyi_device_proxy import make_pyi_device_proxy


def main():
    """server_fastapi/__init__.pyi の DeviceProxy 型定義を生成する。"""
    root = Path(__file__).resolve().parent

    make_pyi_device_proxy(
        filename=str(root / "__init__.pyi"),
        device_names=[
            "AanddReader",
            "aandd",
            "AandDReader",
            "aandd_reader",
        ],
        async_client_module=(
            "aandd_reader.server_fastapi.clients.async_aandd_reader_client"
        ),
        async_client_class="AsyncAanddReaderClient",
        sync_client_module=(
            "aandd_reader.server_fastapi.clients.sync_aandd_reader_client"
        ),
        sync_client_class="SyncAanddReaderClient",
        default_async_mode=True,
    )


if __name__ == "__main__":
    main()
