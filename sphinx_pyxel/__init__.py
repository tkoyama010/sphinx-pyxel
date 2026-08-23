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
            next to the page, so root is "."; when ``pyxel_root`` is set,
            default is the relative path from the page to the shared dir)
    :name:  file name served (default: basename of the argument)
    :gamepad: enabled | disabled (only meaningful for ``play``)
    :assets: comma-separated extra files to copy next to the app
            (e.g. ``mygame.pyxres``)
    :script: URL of the Pyxel web runtime (default: the jsdelivr wasm build)

Config value:
    pyxel_root  -- directory under the HTML output where apps are collected
                   (e.g. ``_pyxel``). When set, each app is copied there once
                   instead of next to every page that references it, and the
                   emitted ``root`` points back at it from each page. Default:
                   unset (copy next to the page).

Only the HTML builder embeds the runtime; other builders emit a note pointing
at the app file name.
"""

from __future__ import annotations

import os
import shutil

from docutils import nodes
from sphinx.util import logging
from sphinx.util.docutils import SphinxDirective

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
        "height": str,
    }

    def run(self):
        rel_src, abs_src = self.env.relfn2path(self.arguments[0].strip())
        self.env.note_dependency(rel_src)

        if not os.path.isfile(abs_src):
            logger.warning(
                "pyxel: file not found: %s", abs_src, location=self.get_source_info()
            )
            return [
                self.state.document.reporter.warning(
                    "pyxel: file not found: %s" % self.arguments[0], line=self.lineno
                )
            ]

        basename = os.path.basename(abs_src)
        ext = os.path.splitext(basename)[1].lower()

        mode = self.options.get("mode")
        if mode is None:
            mode = "play" if ext == ".pyxapp" else "run"
        if mode not in ("run", "play"):
            logger.warning(
                "pyxel: :mode: must be 'run' or 'play', got %r",
                mode,
                location=self.get_source_info(),
            )
            mode = "play" if ext == ".pyxapp" else "run"

        page_dir = self._page_dir()
        pyxel_root = self.env.config.pyxel_root
        if pyxel_root:
            # Collect apps into one shared dir under the output; emit a root
            # relative to the page so the runtime can fetch them.
            shared_dir = os.path.join(self.env.app.builder.outdir, pyxel_root)
            os.makedirs(shared_dir, exist_ok=True)
            dest = os.path.join(shared_dir, basename)
            shutil.copyfile(abs_src, dest)
            default_root = os.path.relpath(shared_dir, page_dir).replace(os.sep, "/")
            asset_dir = shared_dir
        else:
            # Copy the app next to the generated HTML page so the runtime can
            # fetch it with a relative path.
            os.makedirs(page_dir, exist_ok=True)
            dest = os.path.join(page_dir, basename)
            shutil.copyfile(abs_src, dest)
            default_root = "."
            asset_dir = page_dir

        assets = [
            a.strip()
            for a in (self.options.get("assets") or "").split(",")
            if a.strip()
        ]
        for asset in assets:
            a_rel, a_abs = self.env.relfn2path(asset)
            self.env.note_dependency(a_rel)
            if os.path.isfile(a_abs):
                shutil.copyfile(a_abs, os.path.join(asset_dir, os.path.basename(a_abs)))
            else:
                logger.warning(
                    "pyxel: asset not found: %s", a_abs, location=self.get_source_info()
                )

        root = self.options.get("root", default_root)
        name = self.options.get("name", basename)
        script = self.options.get("script", DEFAULT_SCRIPT)

        attrs = f'\n      root="{root}"\n      name="{name}"'
        if mode == "play" and self.options.get("gamepad"):
            attrs += f'\n      gamepad="{self.options["gamepad"]}"'

        tag = "pyxel-" + mode
        # Emit the runtime <script> once per page per URL: the Pyxel runtime
        # declares module-level consts, so loading it twice redeclares them and
        # throws "Identifier 'PYODIDE_URL' has already been declared".
        if not hasattr(self.env, "_pyxel_scripts"):
            self.env._pyxel_scripts = {}
        emitted = self.env._pyxel_scripts.setdefault(self.env.docname, set())
        script_tag = "" if script in emitted else f'<script src="{script}"></script>'
        emitted.add(script)

        # Emit <div id="pyxel-screen"> once per page. The runtime's
        # _createScreenElements does querySelector("div#pyxel-screen") first and
        # only creates+appends-to-body if none exists, so placing it here makes
        # the app render inline at the directive's location instead of taking
        # over the whole page. The runtime only supports one screen per page,
        # so a second directive on the same page reuses this div.
        if not hasattr(self.env, "_pyxel_screens"):
            self.env._pyxel_screens = set()
        screen_div = (
            ""
            if self.env.docname in self.env._pyxel_screens
            else '<div id="pyxel-screen"></div>'
        )
        self.env._pyxel_screens.add(self.env.docname)

        # The runtime's own pyxel.css forces #pyxel-screen fullscreen. Override
        # with higher specificity (.pyxel-app div#pyxel-screen) so it sizes to
        # the container instead. Cascade order doesn't matter: specificity wins.
        height = self.options.get("height", "480px")
        style = (
            "<style>"
            ".pyxel-app{position:relative;width:100%;}"
            f".pyxel-app div#pyxel-screen{{position:relative;left:auto;top:auto;"
            f"width:100%;height:{height};background-color:#202224;}}"
            ".pyxel-app div#pyxel-screen canvas#canvas{position:relative;"
            "left:auto;top:auto;width:100%;height:100%;}"
            "</style>"
        )

        html = (
            f'<div class="pyxel-app">'
            f"{style}"
            f"{screen_div}"
            f"{script_tag}"
            f"<{tag}{attrs}\n    ></{tag}>"
            f"</div>"
        )

        container = nodes.container(classes=["pyxel"])
        container += nodes.raw("", html, format="html")
        # Fallback for non-HTML builders.
        container += nodes.paragraph(
            "",
            f"Pyxel app ({mode}): {name}. "
            "View this page in the HTML build to play it.",
        )
        return [container]

    def _page_dir(self):
        outdir = self.env.app.builder.outdir
        outname = self.env.app.builder.get_outfilename(self.env.docname)
        return os.path.dirname(outname) or outdir


def _purge_doc(app, env, docname):
    scripts = getattr(env, "_pyxel_scripts", None)
    if scripts:
        scripts.pop(docname, None)
    screens = getattr(env, "_pyxel_screens", None)
    if screens:
        screens.discard(docname)


def setup(app):
    app.add_directive("pyxel", PyxelDirective)
    app.add_node(nodes.container, override=True)
    app.add_config_value("pyxel_root", None, "html")
    app.connect("env-purge-doc", _purge_doc)
    return {
        "version": __version__,
        "parallel_read_safe": False,  # we copy files during read
        "parallel_write_safe": True,
    }
