# Copyright (c) 2025 sphinx-pyxel contributors
"""Command-line interface for sphinx-pyxel.

Usage::

    sphinx-pyxel banner --save docs/_static/banner.png --scale 4
    sphinx-pyxel banner            # run the banner as a live Pyxel app

The ``banner`` subcommand renders the Sphinx-logo banner (see
:mod:`sphinx_pyxel.banner`) either to a PNG file (``--save``) or as a live
Pyxel window. The banner background (palette 7) is remapped to pure white so
the PNG blends into GitHub's README body color.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pyxel

from sphinx_pyxel import banner


def _run_banner(args: argparse.Namespace) -> None:
    """Render the banner to a PNG (``--save``) or launch it live."""
    save = Path(args.save).resolve() if args.save else None

    pyxel.init(banner.W, banner.H)

    # Match the banner background (palette 7) to pure white so it blends
    # into GitHub's README body color.
    pyxel.colors[7] = 0xFFFFFF

    font = banner.load_font()

    if save:
        img = pyxel.Image(banner.W, banner.H)
        banner.draw_banner(img, font)
        img.save(str(save), args.scale)
        print(f"saved {save}")  # noqa: T201
        return

    pyxel.run(lambda: None, lambda: banner.draw_banner(pyxel, font))


def build_parser() -> argparse.ArgumentParser:
    """Build the top-level argument parser."""
    parser = argparse.ArgumentParser(prog="sphinx-pyxel")
    sub = parser.add_subparsers(dest="command", required=True)

    banner_p = sub.add_parser(
        "banner",
        help="Render the Sphinx-logo banner (PNG or live Pyxel app).",
    )
    banner_p.add_argument(
        "--save",
        metavar="PATH",
        help="Save the banner to this PNG path instead of opening a window.",
    )
    banner_p.add_argument(
        "--scale",
        type=int,
        default=4,
        help="PNG scale factor (default: 4). Only used with --save.",
    )
    banner_p.set_defaults(func=_run_banner)

    return parser


def main() -> None:
    """Entry point for the ``sphinx-pyxel`` console script."""
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
