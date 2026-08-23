# Add `pyxel_root` config to collect apps into one shared directory

## Summary

New `pyxel_root` config value. When set, the `pyxel` directive copies each app into a single shared directory under the HTML output (e.g. `_pyxel/`) instead of next to every page that references it, and emits a `root` relative to each page pointing back at that directory.

## Why

PR #1 copies the app file next to each page that embeds it. An app reused across many pages is duplicated once per page. `pyxel_root` stores it once.

## What it does

```python
# conf.py
pyxel_root = "_pyxel"
```

Then:
```rst
.. pyxel:: hello.py     # copied to _pyxel/hello.py, root="_pyxel"
```

- Default behavior unchanged when `pyxel_root` is unset (copy next to page, `root="."`).
- When set, `root` defaults to the relative path from the page to the shared dir.
- `:root:` still overrides; `:name:` disambiguates same-basename apps in the shared dir.
- Assets are copied into the shared dir too.

## How to test

```bash
pip install -e .
python -m sphinx -b html docs docs/_build
```

- `docs/_build/_pyxel/hello.py` exists (one copy).
- No `docs/_build/*.py` per-page copies.
- Both `index.html` and `shared.html` emit `root="_pyxel"`.
- `python test_sphinx_pyxel.py` prints `ok`.

## Files

- `sphinx_pyxel/__init__.py` — `pyxel_root` config value + shared-dir copy path
- `docs/conf.py` — sets `pyxel_root = "_pyxel"` for the example docs
- `docs/shared.rst` — second page embedding the same app
- `docs/index.rst` — documents the config value + toctree
- `README.md` — documents `pyxel_root`
- `test_sphinx_pyxel.py` — covers `setup()` registering `pyxel_root`

Builds on #1.
