# sphinx-pyxel: Pyxel app embedding for Sphinx

## Summary

New Sphinx extension `sphinx_pyxel` that embeds [Pyxel](https://github.com/kitao/pyxel) apps inline in HTML documentation using the official Pyxel web runtime. Apps render at the location of the `.. pyxel::` directive (not fullscreen), run entirely in the browser via Pyodide/wasm, and are copied into the build output automatically.

Supersedes #1 (folded in). All work of both PRs is here on one branch against `main`.

## The directive

```rst
.. pyxel:: examples/hello.py

.. pyxel:: examples/my_game.pyxapp
   :mode: play
   :gamepad: enabled
   :height: 600px
```

## Options

| Option    | Default                              | Description                                                       |
|-----------|--------------------------------------|-------------------------------------------------------------------|
| `mode`    | `run` for `.py`, `play` for `.pyxapp`| `run` (just runs) or `play` (player controls, gamepad support).   |
| `root`    | `.` (or rel path to `pyxel_root`)    | Root path served relative to the HTML page.                       |
| `name`    | basename of the argument             | File name served by the runtime.                                  |
| `gamepad` | unset                                | `enabled` or `disabled` (only meaningful for `play`).            |
| `assets`  | unset                                | Comma-separated extra files to copy next to the app.              |
| `script`  | jsdelivr wasm build                  | URL of the Pyxel web runtime script.                              |
| `height`  | `480px`                              | CSS height of the inline app window.                              |

## Config value

```python
# conf.py
extensions = ["sphinx_pyxel"]
pyxel_root = "_pyxel"   # collect apps into one shared dir, one copy per app
```

When `pyxel_root` is set, each app is copied into one directory under the HTML
output instead of next to every page that references it, and the emitted `root`
points back at it from each page.

## How it works

During the build, the directive copies the referenced app file (and any
`assets`) into the output, then emits:

- a `<div id="pyxel-screen">` inside its `.pyxel-app` container — the runtime's
  `_createScreenElements` does `querySelector("div#pyxel-screen")` first and
  only falls back to `document.body` if none exists, so placing it here makes
  the app render **inline at the directive's location**;
- a higher-specificity CSS override (`.pyxel-app div#pyxel-screen`) that beats
  the runtime's own fullscreen `pyxel.css` rule, so the canvas fills the
  container instead of the whole page;
- the runtime `<script>` tag (deduplicated per page per URL);
- a `<pyxel-run>` / `<pyxel-play>` custom element with `root` / `name` /
  `gamepad` attributes.

Non-HTML builders get a short text fallback (the runtime is JS, browser-only).

## Key fixes baked in

- **Runtime script dedup.** The Pyxel runtime declares module-level consts
  (`PYODIDE_URL`, etc.), so loading `pyxel.js` twice on one page throws
  `Identifier 'PYODIDE_URL' has already been declared` and breaks every app.
  The `<script>` tag is now emitted once per page per URL (env-scoped set,
  cleared on `env-purge-doc`).
- **Inline rendering.** Without a local `#pyxel-screen`, the runtime's own CSS
  forces fullscreen. The directive places the screen inside its container and
  overrides the fullscreen rule via specificity.
- **One app per page.** The runtime shares one global context per page, so the
  docs note this and the demo keeps one directive per page.

## How to test

```bash
uv venv
uv pip install -e .
uv run python -m sphinx -b html docs docs/_build
uv run python -m http.server --bind 127.0.0.1 8001 --directory docs/_build
# open http://127.0.0.1:8001/index.html  (file:// won't run the wasm fetch)
```

A Playwright capture script verifies the app boots inline:

```bash
uv pip install playwright
uv run playwright install chromium
uv run python capture.py http://127.0.0.1:8001/index.html screenshot.png
# RESULT: OK — canvas inside .pyxel-app, 'Hello, Pyxel!' rendered, 0 page errors
```

Self-check:
```bash
python test_sphinx_pyxel.py   # prints "ok"
```

## Files

- `sphinx_pyxel/__init__.py` — directive + `setup()` + purge hook
- `pyproject.toml` — packaging (`Framework :: Sphinx :: Extension`)
- `docs/` — example docs embedding `docs/hello.py` (`pyxel_root = "_pyxel"`)
- `test_sphinx_pyxel.py` — self-check for directive metadata + `setup()`
- `capture.py` — Playwright verification tool
- `README.md`, `LICENSE`, `.gitignore`

## Limitations / next steps

- One app per page (Pyxel runtime shares one global `window.pyxelContext`).
  A future PR could detect a second directive on a page and warn.
- `pyxel_root` apps with the same basename collide; give one a `:name:`.
- No real `.pyxapp` in the demo (no Pyxel CLI in this env); the `play` example
  is documentation-only.

Closes #1.
