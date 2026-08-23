# Add `pyxel` directive to embed Pyxel apps in HTML docs

## Summary

New Sphinx extension `sphinx_pyxel` that embeds [Pyxel](https://github.com/kitao/pyxel) apps in HTML documentation using the official Pyxel web runtime (`<pyxel-run>` / `<pyxel-play>` custom elements + the wasm build from jsdelivr).

## Why

Pyxel ships a web runtime that runs `.py` and `.pyxapp` apps directly in the browser. There is currently no Sphinx integration — authors have to hand-write the `<script>` tag and custom element into raw HTML blocks. This extension turns that into one directive so Pyxel apps can live next to the prose that documents them.

## What it does

- Adds the `pyxel` directive:
  ```rst
  .. pyxel:: examples/hello.py
  ```
- Auto-selects `run` for `.py` and `play` for `.pyxapp`; overridable with `:mode:`.
- Copies the app file (and any `:assets:`) next to the generated HTML page during the build, so the runtime can fetch them with a relative path.
- Emits `<pyxel-run>` / `<pyxel-play>` with `root` / `name` / `gamepad` attributes.
- Non-HTML builders get a short text fallback (the runtime is JS, only runs in a browser).

## Options

| Option | Default | Description |
|---|---|---|
| `mode` | `run` for `.py`, `play` for `.pyxapp` | `run` or `play` |
| `root` | `.` | Root path served relative to the HTML page |
| `name` | basename of the argument | File name served by the runtime |
| `gamepad` | unset | `enabled` / `disabled` (only for `play`) |
| `assets` | unset | Comma-separated extra files to copy next to the app |
| `script` | jsdelivr wasm build | URL of the Pyxel web runtime script |

## How to test

```bash
pip install -e .
python -m sphinx -b html docs docs/_build
open docs/_build/index.html   # Pyxel app runs in the browser
```

A self-check is included:
```bash
python test_sphinx_pyxel.py   # prints "ok"
```

## Files

- `sphinx_pyxel/__init__.py` — the directive + `setup()`
- `pyproject.toml` — packaging metadata
- `docs/` — example docs that embed a sample app (`docs/hello.py`)
- `test_sphinx_pyxel.py` — minimal self-check
- `README.md`, `LICENSE`

## Limitations / next steps

- One copy of the app per page that references it. A future PR could add a shared `pyxel_root` config value to avoid duplication across many pages.
- No tests against a real browser; only the emitted HTML is verified.

Closes #1.
