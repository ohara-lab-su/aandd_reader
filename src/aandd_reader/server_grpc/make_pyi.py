#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import pathlib
import grpc_frame
from grpc_frame.make_pyi import generate_client_pyi


def main() -> None:
    base = pathlib.Path(__file__).resolve().parent

    client_py = base / "aandd_reader_grpc_client.py"
    ctrl_py = base / "../aandd_reader.py"

    grpc_base = pathlib.Path(grpc_frame.__file__).resolve().parent
    base_py = grpc_base / "grpc_client.py"

    # sync
    out = base / "aandd_reader_grpc_client.pyi"

    generate_client_pyi(
        client_py=client_py,
        client_class="AanddReaderGrpcClient",
        ctrl_py=ctrl_py,
        ctrl_class="AanddReader",
        base_py=base_py,
        base_class="GrpcClient",
        out_path=out,
    )

    # async
    out_async = base / "async_aandd_reader_grpc_client.pyi"

    generate_client_pyi(
        client_py=base / "async_aandd_reader_grpc_client.py",
        client_class="AsyncAanddReaderGrpcClient",
        ctrl_py=ctrl_py,
        ctrl_class="AanddReader",
        base_py=base_py,
        base_class="AsyncGrpcClient",
        out_path=out_async,
        ctrl_async=True,
    )


if __name__ == "__main__":
    main()
