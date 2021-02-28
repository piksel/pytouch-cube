from PyQt5.QtCore import QMargins


class Margins:

    def __init__(self, vert=0, left=0, right=0, scale: float = 1):
        self.vert: int = vert
        self.left: int = left
        self.right: int = right
        self.scale: float = scale

    def clone(self):
        return Margins(self.vert, self.left, self.right, self.scale)

    def getQMargins(self) -> QMargins:
        m = QMargins()
        m.setTop(self.vert)
        m.setLeft(self.left)
        m.setRight(self.right)
        m.setBottom(0 - self.vert)
        return m
