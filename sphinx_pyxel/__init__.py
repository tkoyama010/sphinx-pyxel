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
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar

from docutils import nodes
from sphinx.util import logging
from sphinx.util.docutils import SphinxDirective

if TYPE_CHECKING:
    from collections.abc import Callable

    from sphinx.application import Sphinx
    from sphinx.environment import BuildEnvironment

__version__ = "0.1.0"

logger = logging.getLogger(__name__)

DEFAULT_SCRIPT = "https://cdn.jsdelivr.net/gh/kitao/pyxel/wasm/pyxel.js"

# ponytail: store per-env dedup state on the env object under these names.
# Accessed via getattr/setattr so the private-member (SLF010) and constant
# setattr (B010) rules don't fight each other.
_SCRIPTS_ATTR = "_pyxel_scripts"
_SCREENS_ATTR = "_pyxel_screens"


class PyxelDirective(SphinxDirective):
    """Embed a Pyxel app via the web runtime."""

    has_content = False
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec: ClassVar[dict[str, Callable[[str], str | None]]] = {
        "mode": str,
        "root": str,
        "name": str,
        "gamepad": str,
        "assets": str,
        "script": str,
        "height": str,
    }

    def run(self) -> list[nodes.Node]:
        """Build the node tree for a ``.. pyxel::`` directive."""
        rel_src, abs_src = self.env.relfn2path(self.arguments[0].strip())
        self.env.note_dependency(rel_src)

        src_path = Path(abs_src)
        if not src_path.is_file():
            logger.warning(
                "pyxel: file not found: %s",
                abs_src,
                location=self.get_source_info(),
            )
            return [
                self.state.document.reporter.warning(
                    f"pyxel: file not found: {self.arguments[0]}",
                    line=self.lineno,
                ),
            ]

        basename = src_path.name
        ext = src_path.suffix.lower()
        mode = self._resolve_mode(ext)

        page_dir = self._page_dir()
        pyxel_root = self.env.config.pyxel_root
        if pyxel_root:
            shared_dir = Path(self.env.app.builder.outdir) / pyxel_root
            shared_dir.mkdir(parents=True, exist_ok=True)
            dest = shared_dir / basename
            shutil.copyfile(abs_src, dest)
            default_root = os_relpath(shared_dir, page_dir)
            asset_dir = shared_dir
        else:
            page_dir.mkdir(parents=True, exist_ok=True)
            dest = page_dir / basename
            shutil.copyfile(abs_src, dest)
            default_root = "."
            asset_dir = page_dir

        self._copy_assets(asset_dir)

        root = self.options.get("root", default_root)
        name = self.options.get("name", basename)
        script = self.options.get("script", DEFAULT_SCRIPT)
        html = self._build_html(mode, root, name, script)

        container = nodes.container(classes=["pyxel"])
        container += nodes.raw("", html, format="html")
        container += nodes.paragraph(
            "",
            f"Pyxel app ({mode}): {name}. "
            "View this page in the HTML build to play it.",
        )
        return [container]

    def _resolve_mode(self, ext: str) -> str:
        """Pick ``run`` or ``play`` from :mode: or the file extension."""
        mode = self.options.get("mode")
        default = "play" if ext == ".pyxapp" else "run"
        if mode is None:
            return default
        if mode not in ("run", "play"):
            logger.warning(
                "pyxel: :mode: must be 'run' or 'play', got %r",
                mode,
                location=self.get_source_info(),
            )
            return default
        return mode

    def _copy_assets(self, asset_dir: Path) -> None:
        """Copy any ``:assets:`` files next to the app."""
        assets = [
            a.strip()
            for a in (self.options.get("assets") or "").split(",")
            if a.strip()
        ]
        for asset in assets:
            a_rel, a_abs = self.env.relfn2path(asset)
            self.env.note_dependency(a_rel)
            a_path = Path(a_abs)
            if a_path.is_file():
                shutil.copyfile(a_abs, asset_dir / a_path.name)
            else:
                logger.warning(
                    "pyxel: asset not found: %s",
                    a_abs,
                    location=self.get_source_info(),
                )

    def _build_html(self, mode: str, root: str, name: str, script: str) -> str:
        """Assemble the embedded runtime HTML for one directive."""
        attrs = f'\n      root="{root}"\n      name="{name}"'
        if mode == "play" and self.options.get("gamepad"):
            attrs += f'\n      gamepad="{self.options["gamepad"]}"'

        tag = "pyxel-" + mode
        # Emit the runtime <script> once per page per URL: the Pyxel runtime
        # declares module-level consts, so loading it twice redeclares them and
        # throws "Identifier 'PYODIDE_URL' has already been declared".
        scripts: dict[str, set[str]] = getattr(self.env, _SCRIPTS_ATTR, None)  # type: ignore[assignment]
        if scripts is None:
            scripts = {}
            setattr(self.env, _SCRIPTS_ATTR, scripts)
        emitted = scripts.setdefault(self.env.docname, set())
        script_tag = "" if script in emitted else f'<script src="{script}"></script>'
        emitted.add(script)

        # Emit <div id="pyxel-screen"> once per page. The runtime's
        # _createScreenElements does querySelector("div#pyxel-screen") first and
        # only creates+appends-to-body if none exists, so placing it here makes
        # the app render inline at the directive's location instead of taking
        # over the whole page. The runtime only supports one screen per page,
        # so a second directive on the same page reuses this div.
        screens: set[str] = getattr(self.env, _SCREENS_ATTR, None)  # type: ignore[assignment]
        if screens is None:
            screens = set()
            setattr(self.env, _SCREENS_ATTR, screens)
        screen_div = (
            "" if self.env.docname in screens else '<div id="pyxel-screen"></div>'
        )
        screens.add(self.env.docname)

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

        return (
            f'<div class="pyxel-app">'
            f"{style}"
            f"{screen_div}"
            f"{script_tag}"
            f"<{tag}{attrs}\n    ></{tag}>"
            f"</div>"
        )

    def _page_dir(self) -> Path:
        """Return the output directory for the current page."""
        outdir = Path(self.env.app.builder.outdir)
        outname = self.env.app.builder.get_outfilename(self.env.docname)
        return Path(outname).parent or outdir


def os_relpath(target: Path, start: Path) -> str:
    """Cross-platform ``os.path.relpath`` as a POSIX string."""
    return os.path.relpath(target, start).replace(os.sep, "/")


def _purge_doc(_app: Sphinx, env: BuildEnvironment, docname: str) -> None:
    """Drop cached script/screen state for a removed/changed doc."""
    scripts: dict[str, set[str]] | None = getattr(env, _SCRIPTS_ATTR, None)
    if scripts:
        scripts.pop(docname, None)
    screens: set[str] | None = getattr(env, _SCREENS_ATTR, None)
    if screens:
        screens.discard(docname)


def setup(app: Sphinx) -> dict[str, object]:
    """Register the extension with Sphinx."""
    app.add_directive("pyxel", PyxelDirective)
    app.add_node(nodes.container, override=True)
    app.add_config_value("pyxel_root", None, "html")
    app.connect("env-purge-doc", _purge_doc)
    return {
        "version": __version__,
        "parallel_read_safe": False,  # we copy files during read
        "parallel_write_safe": True,
    }
