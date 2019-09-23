from PyQt5.QtCore import Qt, QRect, QMargins
from PyQt5.QtGui import QImage, QPainter, QColor, QIcon, QPixmap, QStandardItem
from PyQt5.QtWidgets import QLabel, QAction

from margins import Margins


class PrintableData:

    margins = Margins()

    def __init__(self, margins: Margins=None):
        if margins is None:
            margins = Margins()
        self.margins = margins

    def clone(self):
        raise NotImplementedError

    def set_from(self, source):
        self.margins = source.margins.clone()


class Printable:

    render_error = None

    @classmethod
    def get_add_add_action(cls, parent):
        action = QAction('Add ' + cls.__name__, parent)
        action.triggered.connect(cls.add_new(parent))
        return action

    @classmethod
    def add_new(cls, parent):
        def add():
            print('Add, class:', cls, 'parent:', parent)
            parent.add_item(cls())
        return add

    def get_render_error(self):
        return self.render_error

    @classmethod
    def get_letter(cls):
        return cls.__name__[0]

    def get_name(self):
        return hex(self.__hash__() & ((1 << 32) - 1))

    def render(self):
        raise NotImplementedError

    def get_props_editor(self, parent):
        widget = QLabel('Item props cannot be edited', parent)
        widget.setMinimumWidth(128)
        return widget

    @classmethod
    def get_generic_icon(cls) -> QIcon:
        img = QImage(32, 32, QImage.Format_ARGB32)
        img.fill(QColor(200, 200, 200))
        with QPainter(img) as p:
            pen = p.pen()
            pen.setColor(QColor(0, 0, 0))
            p.setPen(pen)

            p.drawRect(1, 1, 30, 30)

            font = p.font()
            font.setPixelSize(32)
            p.setFont(font)

            p.drawText(img.rect(), Qt.AlignCenter, cls.get_letter())

        return QIcon(QPixmap.fromImage(img))

    def get_icon(self) -> QIcon:
        return self.__class__.get_generic_icon()

    def get_list_item(self):
        name = self.get_name()
        icon = self.get_icon()
        return QStandardItem(icon, self.__class__.__name__), QStandardItem(name)