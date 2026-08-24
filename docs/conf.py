# Copyright (c) 2025 sphinx-pyxel contributors
"""Sphinx configuration for the sphinx-pyxel example site."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

project = "sphinx-pyxel"
author = "sphinx-pyxel contributors"
release = "0.1.0"

extensions = ["sphinx_pyxel"]
pyxel_root = "_pyxel"
master_doc = "index"
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
html_theme = "alabaster"
