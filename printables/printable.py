from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPainter, QColor, QIcon, QPixmap, QStandardItem
from PyQt5.QtWidgets import QLabel


class PrintableData:
    def clone(self):
        raise NotImplementedError

    def set_from(self, source):
        raise NotImplementedError


class Printable:

    render_error = None

    def get_render_error(self):
        return self.render_error

    def get_letter(self):
        return self.__class__.__name__[0]

    def get_name(self):
        return hex(self.__hash__() & ((1 << 32) - 1))

    def render(self):
        raise NotImplementedError

    def get_props_editor(self, parent):
        widget = QLabel('Item props cannot be edited', parent)
        widget.setMinimumWidth(128)
        return widget

    def get_icon(self):
        img = QImage(32, 32, QImage.Format_ARGB32)
        img.fill(QColor(200, 200, 200))
        p = QPainter(img)

        pen = p.pen()
        pen.setColor(QColor(0, 0, 0))
        p.setPen(pen)

        p.drawRect(1, 1, 30, 30)

        font = p.font()
        font.setPixelSize(32)
        p.setFont(font)

        p.drawText(img.rect(), Qt.AlignCenter, self.get_letter())
        p.end()
        del p
        return QIcon(QPixmap.fromImage(img))

    def get_list_item(self):
        name = self.get_name()
        icon = self.get_icon()
        return QStandardItem(icon, self.__class__.__name__), QStandardItem(name)