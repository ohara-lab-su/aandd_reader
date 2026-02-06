#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import ast
import pathlib
from dataclasses import dataclass
from typing import Any, List, Optional


@dataclass(frozen=True)
class _Param:
    name: str
    type_str: str
    has_default: bool


@dataclass(frozen=True)
class _Method:
    name: str
    params: List[_Param]
    return_type: str


def _type_str(annotation: Optional[ast.AST]) -> str:
    if annotation is None:
        return "Any"
    try:
        return ast.unparse(annotation)
    except Exception:
        return "Any"


def _extract_method(func: ast.FunctionDef) -> _Method:
    params: List[_Param] = []

    defaults = list(func.args.defaults)
    total = len(func.args.args)
    default_start = total - len(defaults)
    if default_start < 0:
        default_start = 0

    index = 0
    for arg in func.args.args:
        if arg.arg == "self":
            index += 1
            continue

        has_default = index >= default_start
        params.append(
            _Param(
                name=arg.arg,
                type_str=_type_str(arg.annotation),
                has_default=has_default,
            )
        )
        index += 1

    if func.name == "__init__":
        return_type = "None"
    else:
        return_type = _type_str(func.returns)

    return _Method(
        name=func.name,
        params=params,
        return_type=return_type,
    )


def _parse_class(
    py_file: pathlib.Path,
    class_name: str,
) -> List[_Method]:

    src = py_file.read_text(encoding="utf-8")
    tree = ast.parse(src)

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            if node.name == class_name:
                methods: List[_Method] = []
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        methods.append(_extract_method(item))
                return methods

    return []


def generate_pyi(
    class_name: str,
    ctor: _Method,
    methods: List[_Method],
) -> str:

    lines: List[str] = []

    lines.append("from typing import Any, Optional")
    lines.append("")
    lines.append(f"class {class_name}:")

    def _fmt(m: _Method) -> str:
        args: List[str] = ["self"]
        for p in m.params:
            if p.has_default:
                args.append(f"{p.name}: {p.type_str} = ...")
            else:
                args.append(f"{p.name}: {p.type_str}")
        sig = ", ".join(args)
        return f"    def {m.name}({sig}) -> {m.return_type}: ..."

    lines.append(_fmt(ctor))

    seen: set[str] = set()
    for m in methods:
        if m.name.startswith("_"):
            continue
        if m.name in seen:
            continue
        seen.add(m.name)
        lines.append(_fmt(m))

    return "\n".join(lines)


def main() -> None:
    base = pathlib.Path(__file__).parent

    client_py = base / "aandd_reader_grpc_client.py"
    ctrl_py = base / "../aandd_reader.py"

    client_methods = _parse_class(client_py, "AanddReaderGrpcClient")
    ctrl_methods = _parse_class(ctrl_py, "AanddReader")

    ctor: Optional[_Method] = None
    for m in client_methods:
        if m.name == "__init__":
            ctor = m
            break

    if ctor is None:
        raise RuntimeError("AanddReaderGrpcClient.__init__ not found")

    pyi_text = generate_pyi(
        class_name="AanddReaderGrpcClient",
        ctor=ctor,
        methods=ctrl_methods,
    )

    out = base / "aandd_reader_grpc_client.pyi"
    out.write_text(pyi_text, encoding="utf-8")


if __name__ == "__main__":
    main()
