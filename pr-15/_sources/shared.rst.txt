Multiple pages, one shared app
==============================

This page and :doc:`index` both embed the same app. With ``pyxel_root = _pyxel``
in ``conf.py``, the app is copied into ``_pyxel/`` once and each page points its
``root`` at that directory.

.. pyxel:: hello.py
