from sphinx_pyxel import PyxelDirective, __version__, setup


def test_version():
    assert __version__ == "0.1.0"


def test_directive_meta():
    assert PyxelDirective.required_arguments == 1
    assert PyxelDirective.has_content is False
    assert "mode" in PyxelDirective.option_spec
    assert "gamepad" in PyxelDirective.option_spec
    assert "assets" in PyxelDirective.option_spec


def test_setup_registers_pyxel_root():
    class _App:
        def __init__(self):
            self.directives = {}
            self.config_values = []
        def add_directive(self, name, cls):
            self.directives[name] = cls
        def add_node(self, node, override=False):
            pass
        def add_config_value(self, name, default, rebuild):
            self.config_values.append((name, default, rebuild))
    app = _App()
    setup(app)
    assert "pyxel" in app.directives
    assert ("pyxel_root", None, "html") in app.config_values


if __name__ == "__main__":
    test_version()
    test_directive_meta()
    test_setup_registers_pyxel_root()
    print("ok")
