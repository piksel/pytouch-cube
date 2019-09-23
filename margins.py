from PyQt5.QtCore import QMargins


class Margins:

    def __init__(self, top=0, left=0, right=0, bottom=0):
        self.top = top
        self.left = left
        self.right = right
        self.bottom = bottom

    def clone(self):
        return Margins(self.top, self.left, self.right, self.bottom)

    def getQMargins(self) -> QMargins:
        m = QMargins()
        m.setTop(self.top)
        m.setLeft(self.left)
        m.setRight(self.right)
        m.setBottom(self.bottom)
        return m
