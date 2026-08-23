sphinx-pyxel
============

A Sphinx extension that embeds Pyxel apps in HTML documentation.

.. toctree::
   :maxdepth: 1

   shared

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

::

    .. pyxel:: hello.py

.. pyxel:: hello.py

Play a packaged app
-------------------

Use ``:mode: play`` with a ``.pyxapp`` file (packaged with the Pyxel CLI ``pyxel
package``). The ``play`` command only accepts ``.pyxapp`` files::

    .. pyxel:: my_game.pyxapp
       :mode: play
       :gamepad: enabled

One app per page
----------------

The Pyxel web runtime uses a single shared global context, so place at most one
``.. pyxel::`` directive per page. Two apps on one page conflict and neither
runs cleanly.

Options
-------

``mode``
    ``run`` (default for ``.py``) or ``play`` (default for ``.pyxapp``).

``root`` / ``name``
    Path served relative to the HTML page. Default copies the file next to the
    page (``root="."``, ``name`` = basename); when ``pyxel_root`` is set, the
    default ``root`` is the relative path from the page to the shared dir.

``gamepad``
    ``enabled`` or ``disabled``. Only meaningful for ``play``.

``assets``
    Comma-separated extra files copied next to the app (e.g. ``game.pyxres``).

``script``
    URL of the Pyxel web runtime. Defaults to the jsdelivr wasm build.

``height``
    CSS height of the inline app window (e.g. ``480px``, ``60vh``). Default
    ``480px``. The app renders inline where the directive is written.

Config value
------------

Set ``pyxel_root`` in ``conf.py`` to collect every app into one directory under
the HTML output (e.g. ``_pyxel``) instead of copying it next to each page that
references it::

    pyxel_root = "_pyxel"

See :doc:`shared` for an example where two pages embed the same app from the
shared directory.
