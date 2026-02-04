#!/usr/bin/env python
import os
from contextlib import contextmanager

# make
from fastapi_frame.routers.make_pyi_device_router import (
    make_pyi_device_router,
)

from fastapi_frame.clients.make_pyi_device_client import (
    make_pyi_device_client,
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


def _patch_pyi_inheritance_and_extras(
    *,
    filename: str,
    base_import_line: str,
    class_name: str,
    base_class_name: str,
    extra_method_lines: list[str],
) -> None:
    with open(filename, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()

    out: list[str] = []

    # 1) base import を入れる（重複は避ける）
    already_has_base_import = False
    for line in lines:
        if line.strip() == base_import_line.strip():
            already_has_base_import = True
            break

    inserted = False
    for line in lines:
        # import ブロックの末尾あたりに挿入（class より前）
        if inserted is False:
            if line.startswith("class "):
                if already_has_base_import is False:
                    out.append(base_import_line)
                inserted = True

        # 2) class 定義を継承付きに置換
        if line.startswith(f"class {class_name}:"):
            out.append(f"class {class_name}({base_class_name}):")
            continue

        out.append(line)

    # 3) 自前メソッド（API spec 外）を末尾に足す
    #    pyi が .py を隠すので、ここに無いメソッドは「存在しない」扱いになる
    if extra_method_lines:
        # 末尾に空行を入れて追記
        if len(out) > 0:
            if out[-1].strip() != "":
                out.append("")
        out.extend(extra_method_lines)

    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")


# Normal
# with chdir("clients"):
#     # Async client
#     make_pyi_device_client(
#         filename="async_aandd_reader_client.pyi",
#         api_spec=aandd_reader_api_spec,
#         class_name="AsyncAanddReaderClient",
#         async_mode=True,
#     )
#
#     # Sync client
#     make_pyi_device_client(
#         filename="sync_aandd_reader_client.pyi",
#         api_spec=aandd_reader_api_spec,
#         class_name="SyncAanddReaderClient",
#         async_mode=False,
#     )


# === 変更: make.py の make_pyi 呼び出し部（差し替え） ===
with chdir("clients"):
    # Async client
    make_pyi_device_client(
        filename="async_aandd_reader_client.pyi",
        api_spec=aandd_reader_api_spec,
        class_name="AsyncAanddReaderClient",
        async_mode=True,
    )

    _patch_pyi_inheritance_and_extras(
        filename="async_aandd_reader_client.pyi",
        base_import_line="from fastapi_frame.clients.async_device_client import AsyncDeviceClient",
        class_name="AsyncAanddReaderClient",
        base_class_name="AsyncDeviceClient",
        extra_method_lines=[
            "    # --- methods defined in .py (pyi が .py を隠すため明示) ---",
            "    @staticmethod",
            "    def _sync_await(coro) -> Any: ...",
            "    async def start_watch_listener(self, threshold: float, hysteresis: float, on_event: Any, timeout_sec: float = ...) -> Any: ...",
            "    async def stop_watch_listener(self, watch_id: str) -> Any: ...",
        ],
    )

    # Sync client
    make_pyi_device_client(
        filename="sync_aandd_reader_client.pyi",
        api_spec=aandd_reader_api_spec,
        class_name="SyncAanddReaderClient",
        async_mode=False,
    )

    _patch_pyi_inheritance_and_extras(
        filename="sync_aandd_reader_client.pyi",
        base_import_line="from fastapi_frame.clients.sync_device_client import SyncDeviceClient",
        class_name="SyncAanddReaderClient",
        base_class_name="SyncDeviceClient",
        extra_method_lines=[],
    )

with chdir("routers"):
    # router Device
    make_pyi_device_router(
        filename="aandd_reader_router.pyi",
        api_spec=aandd_reader_api_spec,
        class_name="AanddReaderRouter",
    )
