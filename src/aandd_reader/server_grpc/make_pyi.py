#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import pathlib
import grpc_frame
from grpc_frame.make_pyi import generate_client_pyi


def main() -> None:
    # 現在のディレクトリ
    base = pathlib.Path(__file__).resolve().parent

    # Package 内の GrpcFrame の場所
    grpc_base = pathlib.Path(grpc_frame.__file__).resolve().parent

    # sync
    out = base / "aandd_reader_grpc_client.pyi"

    generate_client_pyi(
        ### client
        client_py=base / "aandd_reader_grpc_client.py",
        client_class="AanddReaderGrpcClient",
        ### Ctrl
        ctrl_py=base / "../aandd_reader.py",
        ctrl_class="AanddReader",
        ### Grpc
        base_py=grpc_base / "grpc_client.py",
        base_class="SyncGrpcClient",
        ### Output
        out_path=out,
        ctrl_async=False,
    )

    # async
    out_async = base / "async_aandd_reader_grpc_client.pyi"

    generate_client_pyi(
        ### client
        client_py=base / "async_aandd_reader_grpc_client.py",
        client_class="AsyncAanddReaderGrpcClient",
        ### Ctrl
        ctrl_py=base / "../aandd_reader.py",
        ctrl_class="AanddReader",
        ### Grpc
        base_py=grpc_base / "grpc_client.py",
        base_class="AsyncGrpcClient",
        ### Output
        out_path=out_async,
        ctrl_async=True,
    )


if __name__ == "__main__":
    main()
