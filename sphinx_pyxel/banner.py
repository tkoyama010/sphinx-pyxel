"""Sphinx-logo banner drawn with Pyxel.

The Sphinx-docs logo (a black sphinx silhouette, traced from
https://sphinx-immaterial.readthedocs.io/en/latest/_images/sphinx_logo.svg)
redrawn as Pyxel pixel art, with the project title beside it in the bundled
PixelMplus12 pixel font.

``draw_banner(g, font)`` is the single draw routine used by both the live
Pyxel app and the headless PNG export in :mod:`sphinx_pyxel.cli`, so the
committed banner stays in sync with the app.
"""

from __future__ import annotations

from pathlib import Path

import pyxel

W, H = 64, 20

# Pyxel default palette indices.
BG = 7          # banner background (remapped to pure white by the CLI)
BLACK = 0       # sphinx silhouette + title fill

# Bundled pixel font (PixelMplus12, shipped with Pyxel's example assets).
FONT_PATH = Path(__file__).parent / "assets" / "PixelMplus12-Regular.ttf"
FONT_SIZE = 5
TITLE = "sphinx-pyxel"

# 25x19 trace of the Sphinx-docs logo SVG, one string per row.
# '0' = black silhouette, '7' = palette 7 (matches the banner background) so
# the silhouette sits directly on the white banner with no framing square.
LOGO_X, LOGO_Y = 2, 1
LOGO_W, LOGO_H = 25, 19
LOGO_DATA = [
    "7777777777777777777777777",
    "7777777770000000007777777",
    "7777700000007700000000777",
    "7000000077777777777000000",
    "7000777777777777777777777",
    "7777777770000000077777777",
    "7777700000000000000007777",
    "7000007777700000777770000",
    "7000777777700007777777000",
    "7770000007777777777000077",
    "7777777000000000000007777",
    "7777777777777000000077777",
    "7700077777777770070077777",
    "7000077777777700770007777",
    "0070077777770007770077777",
    "0077777777700777770077777",
    "7007777770007777770777777",
    "7700000000777777700777777",
    "7777000077777777707777777",
]


TITLE_X = 32
TITLE_Y = (H - FONT_SIZE) // 2


def draw_banner(g: pyxel.Image, font: pyxel.Font | None = None) -> None:
    """Draw the banner onto ``g`` (the Pyxel screen or an image bank)."""
    g.cls(BG)
    g.set(LOGO_X, LOGO_Y, LOGO_DATA)
    g.text(TITLE_X, TITLE_Y, TITLE, BLACK, font)


def load_font() -> pyxel.Font:
    """Load the bundled PixelMplus12 font at the banner size."""
    return pyxel.Font(str(FONT_PATH), FONT_SIZE)
