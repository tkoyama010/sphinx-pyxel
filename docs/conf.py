import os
import sys

sys.path.insert(0, os.path.abspath(".."))

project = "sphinx-pyxel"
author = "sphinx-pyxel contributors"
release = "0.1.0"

extensions = ["sphinx_pyxel"]
pyxel_root = "_pyxel"
master_doc = "index"
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
html_theme = "alabaster"
