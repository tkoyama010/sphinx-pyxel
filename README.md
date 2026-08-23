# sphinx-pyxel

A [Sphinx](https://www.sphinx-doc.org/) extension that embeds [Pyxel](https://github.com/kitao/pyxel) apps directly in your HTML documentation using the official Pyxel web runtime.

## Install

```bash
pip install sphinx-pyxel
```

Or from source:

```bash
pip install .
```

## Usage

Add the extension to your `conf.py`:

```python
extensions = ["sphinx_pyxel"]
```

Then use the `pyxel` directive in any reStructuredText document:

```rst
.. pyxel:: examples/01_hello_pyxel.py
```

For a packaged app (`.pyxapp`) with gamepad support:

```rst
.. pyxel:: examples/30sec_of_daylight.pyxapp
   :mode: play
   :gamepad: enabled
```

If your app loads external resources, copy them next to it:

```rst
.. pyxel:: my_game.py
   :assets: my_game.pyxres, my_game_bank.json
```

## Options

| Option     | Default                              | Description                                                       |
|------------|--------------------------------------|-------------------------------------------------------------------|
| `mode`     | `run` for `.py`, `play` for `.pyxapp`| `run` (just runs) or `play` (player controls, gamepad support).   |
| `root`     | `.` (or rel path to `pyxel_root`)    | Root path served relative to the HTML page.                       |
| `name`     | basename of the argument             | File name served by the runtime.                                  |
| `gamepad`  | unset                                | `enabled` or `disabled` (only meaningful for `play`).            |
| `assets`   | unset                                | Comma-separated extra files to copy next to the app.              |
| `script`   | jsdelivr wasm build                  | URL of the Pyxel web runtime script.                              |

## How it works

During the build, the directive copies the referenced app file (and any
`assets`) into the output directory next to the generated HTML page, then emits
a `<pyxel-run>` (or `<pyxel-play>`) custom element plus the Pyxel web runtime
script tag. The app runs entirely in the browser — no Python is executed by
Sphinx.

## Config value: `pyxel_root`

Set ``pyxel_root`` in ``conf.py`` to collect every app into one shared
directory under the HTML output instead of copying it next to each page that
references it. Each emitted ``root`` then points from the page back at the
shared directory, so an app reused across many pages is stored once.

```python
pyxel_root = "_pyxel"
```

## Limitations

- The embedded app only renders in the **HTML** builder. Other builders (LaTeX,
  man, text, etc.) emit a short note instead. This is expected: the Pyxel web
  runtime is JavaScript and only runs in a browser.
- One file is copied next to each page that references it **unless**
  ``pyxel_root`` is set, in which case apps are collected into one shared
  directory. Two apps with the same basename under ``pyxel_root`` would
  collide; give one a distinct ``:name:`` if that happens.

## License

MIT
