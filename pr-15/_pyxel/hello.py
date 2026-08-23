"""Minimal Pyxel app embedded by the sphinx-pyxel example docs."""
import pyxel


class App:
    """A Pyxel app that bounces text across the screen."""

    def __init__(self) -> None:
        """Initialize and launch the app."""
        pyxel.init(160, 120, title="Hello from sphinx-pyxel")
        self.x = 0
        pyxel.run(self.update, self.draw)

    def update(self) -> None:
        """Advance the bouncing text one frame."""
        self.x = (self.x + 1) % pyxel.width

    def draw(self) -> None:
        """Render the current frame."""
        pyxel.cls(0)
        pyxel.text(self.x, 60, "Hello, Pyxel!", 7)


App()
