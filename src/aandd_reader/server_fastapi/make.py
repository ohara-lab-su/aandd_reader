#!/usr/bin/env python
"""
server_fastapi 用の生成スクリプトである。

このスクリプトは次を行う。

1. API spec から client / router の pyi を生成する。
2. 生成された client pyi を、実際の Python クラス構造に合わせて補正する。
3. server_fastapi/__init__.py を生成し、DeviceProxy 用の登録を行う。
4. server_fastapi/__init__.pyi を生成し、DeviceProxy 登録後の公開 API を型補完へ反映する。

pyi は同名の .py を型検査上は上書きするため、生成された pyi に継承関係や
.py 側で定義された補助メソッドが書かれていない場合、それらは存在しないものとして
扱われる。このため、API spec から機械生成した pyi をそのまま使わず、実装クラスの
実態に合わせて後処理する。

DeviceProxy 登録は server_fastapi 層に閉じ込める。デバイス本体クラスや config は
ここでは import しない。ローカル制御層と FastAPI/DeviceProxy 層の依存方向を分離するためである。
"""
import os
import re
from contextlib import contextmanager

from ese774_frame.clients.make_pyi_device_client import make_pyi_device_client
from ese774_frame.routers.make_pyi_device_router import make_pyi_device_router

from aandd_reader.server_fastapi.spec_ctrl import aandd_reader_api_spec


CLIENT_DIR = "clients"
ROUTER_DIR = "routers"

ASYNC_CLIENT_PYI = "async_aandd_reader_client.pyi"
SYNC_CLIENT_PYI = "sync_aandd_reader_client.pyi"
ROUTER_PYI = "aandd_reader_router.pyi"
INIT_PY = "__init__.py"
INIT_PYI = "__init__.pyi"

ASYNC_CLIENT_CLASS = "AsyncAanddReaderClient"
SYNC_CLIENT_CLASS = "SyncAanddReaderClient"
ROUTER_CLASS = "AanddReaderRouter"

DEVICE_PROXY_NAME = "AanddReader"
DEVICE_PROXY_ALIASES = [
    "aandd",
    "AandDReader",
    "aandd_reader",
]


@contextmanager
def chdir(path):
    prev_cwd = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(prev_cwd)


def _read_lines(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return f.read().splitlines()


def _write_lines(filename, lines):
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def _ensure_import(lines, import_line):
    """
    import_line を class 定義より前に一度だけ挿入する。
    生成器の import 順序に強く依存しないよう、最初の class の直前を挿入位置にする。
    """
    if any(line.strip() == import_line.strip() for line in lines):
        return lines

    out = []
    inserted = False
    for line in lines:
        if not inserted and line.startswith("class "):
            out.append(import_line)
            inserted = True
        out.append(line)

    if not inserted:
        out.append(import_line)

    return out


def _replace_class_base(lines, class_name, base_class_name):
    """
    class ClassName: と class ClassName(...): の両方を受け、基底クラスを明示する。
    """
    out = []
    pattern = re.compile(r"^(class\s+" + re.escape(class_name) + r")\s*(?:\([^)]*\))?:\s*$")
    target = "class {}({}):".format(class_name, base_class_name)

    for line in lines:
        if pattern.match(line):
            out.append(target)
        else:
            out.append(line)

    return out


def _find_class_block(lines, class_name):
    start = None
    pattern = re.compile(r"^class\s+" + re.escape(class_name) + r"(?:\(|:)")

    for i, line in enumerate(lines):
        if pattern.match(line):
            start = i
            break

    if start is None:
        raise RuntimeError("class not found in generated pyi: {}".format(class_name))

    end = len(lines)
    for i in range(start + 1, len(lines)):
        line = lines[i]
        if line and not line.startswith((" ", "\t", "#")):
            end = i
            break

    return start, end


def _member_signature_key(member_line):
    stripped = member_line.strip()
    if stripped.startswith("def "):
        return stripped.split("(", 1)[0]
    if stripped.startswith("async def "):
        return stripped.split("(", 1)[0]
    if stripped.startswith("@"):
        return stripped
    return stripped


def _ensure_class_members(lines, class_name, member_lines):
    """
    API spec 外の .py 実装メソッドを pyi の class ブロック内に一度だけ追加する。
    単純なファイル末尾追記ではなく class ブロックの末尾へ挿入するため、後続の
    トップレベル定義が増えた場合でも壊れにくい。
    """
    if not member_lines:
        return lines

    start, end = _find_class_block(lines, class_name)
    class_lines = lines[start:end]
    existing_keys = set(_member_signature_key(line) for line in class_lines)

    missing = []
    for member in member_lines:
        key = _member_signature_key(member)
        if key in existing_keys:
            continue
        missing.append(member)

    if not missing:
        return lines

    out = list(lines[:end])
    if out and out[-1].strip() != "":
        out.append("")
    out.extend(missing)
    out.extend(lines[end:])
    return out


def _patch_pyi_inheritance_and_extras(
    filename,
    base_import_line,
    class_name,
    base_class_name,
    extra_method_lines,
):
    lines = _read_lines(filename)
    lines = _ensure_import(lines, base_import_line)
    lines = _ensure_import(lines, "from typing import Any")
    lines = _replace_class_base(lines, class_name, base_class_name)
    lines = _ensure_class_members(lines, class_name, extra_method_lines)
    _write_lines(filename, lines)


def _make_string_list_literal(items, indent="    "):
    if not items:
        return "[]"

    lines = ["["]
    for item in items:
        lines.append('{}"{}",'.format(indent, item))
    lines.append("]")
    return "\n".join(lines)


def _write_device_proxy_init_py(filename):
    """
    server_fastapi/__init__.py を生成する。

    ここでは server_fastapi 層の公開物だけを扱う。AanddReader 本体や Config は
    ローカル制御層の責務であり、DeviceProxy 登録には不要なので import しない。
    """
    aliases_text = _make_string_list_literal(DEVICE_PROXY_ALIASES, indent="    ")

    text = '''#!/usr/bin/env python
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


DEVICE_PROXY_NAME = "{device_proxy_name}"
DEVICE_PROXY_ALIASES = {aliases}


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
'''.format(
        device_proxy_name=DEVICE_PROXY_NAME,
        aliases=aliases_text,
    )

    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)


def _write_device_proxy_init_pyi(filename):
    """
    server_fastapi/__init__.pyi を生成する。

    __init__.py が DeviceProxy 登録の実行場所であるため、同じ公開名を pyi にも明示する。
    ここに書かない公開名は型検査・補完上は存在しない扱いになる。
    """
    text = '''from typing import Any, List

from aandd_reader.server_fastapi.clients.async_aandd_reader_client import (
    AsyncAanddReaderClient,
)
from aandd_reader.server_fastapi.clients.sync_aandd_reader_client import (
    SyncAanddReaderClient,
)
from aandd_reader.server_fastapi.routers.aandd_reader_router import AanddReaderRouter

DEVICE_PROXY_NAME: str
DEVICE_PROXY_ALIASES: List[str]
aandd_reader_api_spec: Any

__all__: List[str]
'''

    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)


def make_client_pyi():
    with chdir(CLIENT_DIR):
        make_pyi_device_client(
            filename=ASYNC_CLIENT_PYI,
            api_spec=aandd_reader_api_spec,
            class_name=ASYNC_CLIENT_CLASS,
            async_mode=True,
        )
        _patch_pyi_inheritance_and_extras(
            filename=ASYNC_CLIENT_PYI,
            base_import_line="from ese774_frame.clients.async_device_client import AsyncDeviceClient",
            class_name=ASYNC_CLIENT_CLASS,
            base_class_name="AsyncDeviceClient",
            extra_method_lines=[
                "    # --- methods defined in .py, not in api_spec ---",
                "    @staticmethod",
                "    def _sync_await(coro) -> Any: ...",
                "    async def start_watch_listener(self, threshold: float, hysteresis: float, on_event: Any, timeout_sec: float = ...) -> Any: ...",
                "    async def stop_watch_listener(self, watch_id: str) -> Any: ...",
            ],
        )

        make_pyi_device_client(
            filename=SYNC_CLIENT_PYI,
            api_spec=aandd_reader_api_spec,
            class_name=SYNC_CLIENT_CLASS,
            async_mode=False,
        )
        _patch_pyi_inheritance_and_extras(
            filename=SYNC_CLIENT_PYI,
            base_import_line="from ese774_frame.clients.sync_device_client import SyncDeviceClient",
            class_name=SYNC_CLIENT_CLASS,
            base_class_name="SyncDeviceClient",
            extra_method_lines=[],
        )


def make_router_pyi():
    with chdir(ROUTER_DIR):
        make_pyi_device_router(
            filename=ROUTER_PYI,
            api_spec=aandd_reader_api_spec,
            class_name=ROUTER_CLASS,
        )


def make_device_proxy_init_files():
    _write_device_proxy_init_py(INIT_PY)
    _write_device_proxy_init_pyi(INIT_PYI)


def main():
    make_client_pyi()
    make_router_pyi()
    make_device_proxy_init_files()


if __name__ == "__main__":
    main()
