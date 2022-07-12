import abc
from typing import Optional
import logging
from PyQt6.QtCore import Qt, QLineF, QPointF
from PyQt6.QtGui import QImage, QPainter, QColor, QIcon, QPixmap, QStandardItem, QPainterPath, QAction
from PyQt6.QtWidgets import QLabel

from margins import Margins

log = logging.getLogger(__name__)

class PrintableData:
    margins = Margins()

    def __init__(self, margins: Optional[Margins] = None):
        if margins is None:
            margins = Margins()
        self.margins = margins

    def clone(self):
        raise NotImplementedError

    def set_from(self, source):
        self.margins = source.margins.clone()


class Printable(abc.ABC):
    render_error: Optional[Exception] = None

    @classmethod
    def get_add_add_action(cls, parent):
        action = QAction('Add ' + cls.__name__, parent)
        action.triggered.connect(cls.add_new(parent))
        return action

    @classmethod
    def add_new(cls, parent):
        def add():
            log.debug(f'Adding new "{cls.__name__}" printable')
            parent.add_item(cls())

        return add

    def get_render_error(self):
        return self.render_error

    @classmethod
    def get_letter(cls):
        return cls.__name__[0]

    def get_name(self):
        return hex(self.__hash__() & ((1 << 32) - 1))

    @abc.abstractmethod
    def render(self) -> QImage:
        raise NotImplementedError

    def get_margins(self):
        return Margins(0, 0, 0, 1)

    def get_props_editor(self, parent):
        widget = QLabel('Item props cannot be edited', parent)
        widget.setMinimumWidth(128)
        return widget

    @classmethod
    def get_generic_icon(cls, valid: bool = True) -> QIcon:
        img = QImage(32, 32, QImage.Format.Format_ARGB32)
        img.fill(QColor(200, 200, 200))
        with QPainter(img) as p:
            pen = p.pen()
            pen.setColor(QColor(0, 0, 0) if valid else QColor(255, 0, 0))
            p.setPen(pen)

            p.drawRect(1, 1, 30, 30)

            font = p.font()
            font.setPixelSize(32)
            p.setFont(font)

            p.drawText(img.rect(), Qt.AlignmentFlag.AlignCenter, cls.get_letter())

        return QIcon(QPixmap.fromImage(img))

    @classmethod
    def get_error_icon(cls) -> QIcon:
        img = QImage(32, 32, QImage.Format.Format_ARGB32)
        img.fill(Qt.GlobalColor.white)
        with QPainter(img) as p:
            pen = p.pen()
            pen.setColor(QColor(0, 0, 0))
            p.setPen(pen)

            mn, md, mx = 1, 15.5, 30
            triangle = QPainterPath(QPointF(mn, mx))
            triangle.lineTo(QPointF(md, mn))
            triangle.lineTo(QPointF(mx, mx))
            triangle.lineTo(QPointF(mn, mx))

            p.fillPath(triangle, QColor(255, 197, 74))
            p.drawPath(triangle)

            font = p.font()
            font.setPixelSize(26)
            p.setFont(font)

            p.drawText(img.rect(), Qt.AlignmentFlag.AlignCenter, '!')

        return QIcon(QPixmap.fromImage(img))

    def get_icon(self) -> QIcon:
        return self.__class__.get_generic_icon()

    def get_type(self):
        return self.__class__.__name__

    def get_list_item(self):
        name = self.get_name()
        icon = self.get_icon()
        return QStandardItem(icon, self.get_type()), QStandardItem(name)
