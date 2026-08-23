import pyxel


class App:
    def __init__(self):
        pyxel.init(160, 120, title="Hello from sphinx-pyxel")
        self.x = 0
        pyxel.run(self.update, self.draw)

    def update(self):
        self.x = (self.x + 1) % pyxel.width

    def draw(self):
        pyxel.cls(0)
        pyxel.text(self.x, 60, "Hello, Pyxel!", 7)


App()
