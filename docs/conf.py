"""Sphinx configuration shared by independently built language trees."""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("AANDD_READER_REPO_ROOT", Path(__file__).resolve().parent.parent)).resolve()
sys.path.insert(0, str(ROOT / "src"))

project = "aandd_reader"
root_doc = "index"
language = "en"
source_suffix = {".md": "markdown", ".rst": "restructuredtext"}
extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]
myst_enable_extensions = ["colon_fence"]
autosummary_generate = True
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
}
autodoc_typehints = "description"
autodoc_preserve_defaults = True
autodoc_mock_imports = ["win32com", "pythoncom", "x_logger", "ese774_frame", "grpc_frame", "grpc"]
html_theme = "sphinx_rtd_theme"
html_theme_options = {
    "collapse_navigation": False,
    "navigation_depth": 4,
    "titles_only": False,
}
exclude_patterns = ["_build", "_generated"]
