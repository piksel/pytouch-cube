from typing import Optional, List

from PyQt5.QtCore import pyqtSignal, QRect, Qt
from PyQt5.QtGui import QPainter, QImage, QPixmap, QColor, QPalette
from PyQt5.QtWidgets import QLabel, QWidget
from qasync import QtGui

from labelmaker import USABLE_HEIGHT


class PreviewImage(QLabel):
    preview_item_clicked = pyqtSignal(int, name='preview_item_clicked')

    def __init__(self, parent: Optional[QWidget]):
        super().__init__('No items to preview', parent=parent)
        self.selected_index = -1
        self.item_offsets: List[int] = []
        self.setFixedHeight(USABLE_HEIGHT + 2)

    def update_selected(self, selected_index: int):
        self.selected_index = selected_index
        pixmap = self.pixmap()
        if pixmap is None:
            return
        painter = QPainter(pixmap)
        self.draw_selection(painter)
        painter.end()
        self.repaint()

    def draw_selection(self, painter: QPainter):
        select_rect = QRect(0, USABLE_HEIGHT, 0, 4)
        palette = self.palette()
        for index, offset in enumerate(self.item_offsets):
            select_rect.translate(select_rect.width(), 0)
            select_rect.setWidth(offset - select_rect.left())
            color = palette.color(QPalette.Highlight if self.selected_index == index else QPalette.Background)
            painter.fillRect(select_rect, color)

    def setPixmap(self, a0: QtGui.QPixmap) -> None:
        img = QImage(a0.width(), a0.height() + 4, QImage.Format_RGB32)
        img.fill(self.palette().color(QPalette.Background))
        painter = QPainter(img)
        painter.drawImage(0, 0, a0.toImage())
        self.draw_selection(painter)
        painter.end()
        super().setPixmap(QPixmap(img))
        self.repaint()

    def mousePressEvent(self, ev: QtGui.QMouseEvent) -> None:
        x = ev.x()
        for index, offset in enumerate(self.item_offsets):
            if x < offset:
                self.preview_item_clicked.emit(index)
                self.update_selected(index)
                break

    def set_item_offsets(self, offsets: List[int]):
        self.item_offsets = offsets
