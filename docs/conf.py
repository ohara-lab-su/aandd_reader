#!/usr/bin/env python
"""
Kengo NAKADA:
https://github.com/shimane-dev, https://github.com/kengo-nakada
kengo.nakada@mat.shimane-u.ac.jp, kengo.nakada@gmail.com
"""

import os, sys

sys.path.insert(0, os.path.abspath("../src"))
sys.path.insert(0, os.path.abspath("../../x_logger/src"))

project = "Project"
language = "ja"

extensions = [
    "sphinx.ext.autodoc",  # autodoc: Pythonのdocstringから自動的にAPIドキュメントを生成
    "sphinx.ext.autosummary",  # autosummary: autodocを拡張し、API一覧表や要約を自動生成
    "sphinx.ext.napoleon",  # napoleon: Google/NumpyスタイルのdocstringをSphinxが解釈できるようにする
    "sphinx.ext.viewcode",  # viewcode: ドキュメントからソースコードへのリンクを自動生成
    "sphinx.ext.intersphinx",  # Projドキュメント間のリンク
    "myst_parser",  # Markdown を有効化
]

# 対応するファイル拡張子
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

# MyST のオプション(markdown ページ作成に必要な最小構成)
myst_enable_extensions = [
    "colon_fence",  # ::: フェンス
    "deflist",  # 定義リスト
    "attrs_block",  # 属性付与
    "substitution",  # 置換
    "linkify",  # URL 自動リンク
]
myst_linkify_fuzzy_links = True
myst_heading_anchors = 3

# autosummary で目録ページを自動生成
autosummary_generate = True

# 型ヒント参照で失敗した時の警告を抑制する
nitpick_ignore = [
    ("py:class", "ese774_frame.clients.async_device_client.AsyncDeviceClient"),
    ("py:class", "ese774_frame.clients.sync_device_client.SyncDeviceClient"),
    ("py:class", "ese774_frame.routers.device_router.DeviceRouter"),
    ("py:class", "x_logger.x_logger.XLogger"),
    ("py:class", "Path"),
    ("py:class", "pathlib.Path"),
    ("py:class", "direction"),
    ("py:class", "pydantic.main.BaseModel"),
    ("py:class", "ConfigDict"),
    ("py:class", "enum.Enum"),
]

autodoc_type_aliases = {
    "XLogger": "x_logger.x_logger.XLogger",
    "Path": "pathlib.Path",
    "BaseModel": "pydantic.main.BaseModel",
    "ConfigDict": "pydantic.config.ConfigDict",
    "Enum": "enum.Enum",
}

autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
    "private-members": True,
}

add_module_names = False
autodoc_typehints = "description"
autodoc_preserve_defaults = True
set_type_checking_flag = True

# パッケージ内でインポートしているモジュール関係を Sphinxで追いかけない
autodoc_mock_imports = [
    "win32com",
    "pythoncom",
    "x_logger",
    "ese774_frame",
    "grpc_frame",
    "grpc",
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "pydantic": ("https://docs.pydantic.dev/latest/", None),
    "fastapi": ("https://fastapi.tiangolo.com/", None),
}

html_theme = "sphinx_rtd_theme"
html_theme_options = {
    "collapse_navigation": False,
    "navigation_depth": 4,
    "titles_only": False,
}
html_static_path = ["_static"]
html_extra_path = ["robots.txt"]
