sphinx-pyxel
============

A Sphinx extension that embeds Pyxel apps in HTML documentation.

Installation
------------

::

    pip install sphinx-pyxel

Enable it in ``conf.py``::

    extensions = ["sphinx_pyxel"]

Directive
---------

``.. pyxel::`` copies a Pyxel app (``.py`` or ``.pyxapp``) into the build output
and renders it with the official Pyxel web runtime.

Run a Python app
----------------

.. pyxel:: hello.py

Play a packaged app
-------------------

.. pyxel:: hello.py
   :mode: play
   :gamepad: enabled

Options
-------

``mode``
    ``run`` (default for ``.py``) or ``play`` (default for ``.pyxapp``).

``root`` / ``name``
    Path served relative to the HTML page. Default copies the file next to the
    page (``root="."``, ``name`` = basename).

``gamepad``
    ``enabled`` or ``disabled``. Only meaningful for ``play``.

``assets``
    Comma-separated extra files copied next to the app (e.g. ``game.pyxres``).

``script``
    URL of the Pyxel web runtime. Defaults to the jsdelivr wasm build.
