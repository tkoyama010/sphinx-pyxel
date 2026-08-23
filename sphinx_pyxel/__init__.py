"""Sphinx extension to embed Pyxel apps in HTML documentation.

Provides the ``pyxel`` directive, which copies a Pyxel app (a ``.py`` file or a
packaged ``.pyxapp``) into the build output and renders it with the official
Pyxel web runtime::

    .. pyxel:: examples/01_hello_pyxel.py

    .. pyxel:: examples/30sec_of_daylight.pyxapp
       :mode: play
       :gamepad: enabled

Options:
    :mode: run | play  (auto-detected from extension; ``run`` for .py,
                       ``play`` for .pyxapp)
    :root:  root path served relative to the HTML page (default: copied
            next to the page, so root is ".")
    :name:  file name served (default: basename of the argument)
    :gamepad: enabled | disabled (only meaningful for ``play``)
    :assets: comma-separated extra files to copy next to the app
            (e.g. ``mygame.pyxres``)
    :script: URL of the Pyxel web runtime (default: the jsdelivr wasm build)

Only the HTML builder embeds the runtime; other builders emit a note pointing
at the app file name.
"""

from __future__ import annotations

import os
import shutil

from docutils import nodes
from sphinx.util.docutils import SphinxDirective
from sphinx.util import logging

__version__ = "0.1.0"

logger = logging.getLogger(__name__)

DEFAULT_SCRIPT = "https://cdn.jsdelivr.net/gh/kitao/pyxel/wasm/pyxel.js"


class PyxelDirective(SphinxDirective):
    """Embed a Pyxel app via the web runtime."""

    has_content = False
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {
        "mode": str,
        "root": str,
        "name": str,
        "gamepad": str,
        "assets": str,
        "script": str,
    }

    def run(self):
        rel_src, abs_src = self.env.relfn2path(self.arguments[0].strip())
        self.env.note_dependency(rel_src)

        if not os.path.isfile(abs_src):
            logger.warning("pyxel: file not found: %s", abs_src, location=self.get_source_info())
            return [self.state.document.reporter.warning(
                "pyxel: file not found: %s" % self.arguments[0], line=self.lineno)]

        basename = os.path.basename(abs_src)
        ext = os.path.splitext(basename)[1].lower()

        mode = self.options.get("mode")
        if mode is None:
            mode = "play" if ext == ".pyxapp" else "run"
        if mode not in ("run", "play"):
            logger.warning("pyxel: :mode: must be 'run' or 'play', got %r", mode,
                           location=self.get_source_info())
            mode = "play" if ext == ".pyxapp" else "run"

        # Copy the app (and any assets) next to the generated HTML page so the
        # runtime can fetch them with a relative path.
        page_dir = self._page_dir()
        os.makedirs(page_dir, exist_ok=True)
        dest = os.path.join(page_dir, basename)
        shutil.copyfile(abs_src, dest)

        assets = [a.strip() for a in (self.options.get("assets") or "").split(",") if a.strip()]
        for asset in assets:
            a_rel, a_abs = self.env.relfn2path(asset)
            self.env.note_dependency(a_rel)
            if os.path.isfile(a_abs):
                shutil.copyfile(a_abs, os.path.join(page_dir, os.path.basename(a_abs)))
            else:
                logger.warning("pyxel: asset not found: %s", a_abs, location=self.get_source_info())

        root = self.options.get("root", ".")
        name = self.options.get("name", basename)
        script = self.options.get("script", DEFAULT_SCRIPT)

        attrs = f'\n      root="{root}"\n      name="{name}"'
        if mode == "play" and self.options.get("gamepad"):
            attrs += f'\n      gamepad="{self.options["gamepad"]}"'

        tag = "pyxel-" + mode
        html = (
            f'<div class="pyxel-app">'
            f'<script src="{script}"></script>'
            f'<{tag}{attrs}\n    ></{tag}>'
            f'</div>'
        )

        container = nodes.container(classes=["pyxel"])
        container += nodes.raw("", html, format="html")
        # Fallback for non-HTML builders.
        container += nodes.paragraph(
            "", f"Pyxel app ({mode}): {name}. "
            "View this page in the HTML build to play it."
        )
        return [container]

    def _page_dir(self):
        outdir = self.env.app.builder.outdir
        outname = self.env.app.builder.get_outfilename(self.env.docname)
        return os.path.dirname(outname) or outdir


def setup(app):
    app.add_directive("pyxel", PyxelDirective)
    app.add_node(nodes.container, override=True)
    return {
        "version": __version__,
        "parallel_read_safe": False,  # we copy files during read
        "parallel_write_safe": True,
    }
