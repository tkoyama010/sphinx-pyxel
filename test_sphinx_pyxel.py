from sphinx_pyxel import PyxelDirective, __version__


def test_version():
    assert __version__ == "0.1.0"


def test_directive_meta():
    assert PyxelDirective.required_arguments == 1
    assert PyxelDirective.has_content is False
    assert "mode" in PyxelDirective.option_spec
    assert "gamepad" in PyxelDirective.option_spec
    assert "assets" in PyxelDirective.option_spec


if __name__ == "__main__":
    test_version()
    test_directive_meta()
    print("ok")
