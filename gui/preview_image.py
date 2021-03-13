from typing import Optional, List, Tuple

from PyQt5.QtCore import pyqtSignal, QRect, Qt
from PyQt5.QtGui import QPainter, QImage, QPixmap, QColor, QPalette, QBitmap, QRegion
from PyQt5.QtWidgets import QLabel, QWidget
from qasync import QtGui

from gui.types import Color
from labelmaker import USABLE_HEIGHT


class PreviewImage(QLabel):
    preview_item_clicked = pyqtSignal(int, name='preview_item_clicked')

    def __init__(self, parent: Optional[QWidget]):
        super().__init__('No items to preview', parent=parent)
        self.selected_index = -1
        self.item_offsets: List[int] = []
        self.setFixedHeight(USABLE_HEIGHT + 2)
        self.fg_color = Qt.black
        self.bg_color = Qt.white
        self.preview_bitmap = QPixmap()

    def update_colors(self, fg: Color, bg: Color, repaint=True):
        self.fg_color = QColor(*fg)
        self.bg_color = QColor(*bg)

    def repaint_preview(self):
        pixmap = self.pixmap()
        if pixmap is None:
            return
        painter = QPainter(pixmap)
        self.draw_preview(painter)
        painter.end()
        self.repaint(self.preview_bitmap.rect())

    def update_selected(self, selected_index: int):
        self.selected_index = selected_index
        pixmap = self.pixmap()
        if pixmap is None:
            return
        with QPainter(pixmap) as painter:
            self.draw_selection(painter)
        self.repaint(QRect(0, USABLE_HEIGHT-1, self.preview_bitmap.width(), 4))

    def draw_selection(self, painter: QPainter):
        select_rect = QRect(0, USABLE_HEIGHT, 0, 4)
        palette = self.palette()
        for index, offset in enumerate(self.item_offsets):
            select_rect.translate(select_rect.width(), 0)
            select_rect.setWidth(offset - select_rect.left())
            color = palette.color(QPalette.Highlight if self.selected_index == index else QPalette.Background)
            painter.fillRect(select_rect, color)

    def setPixmap(self, a0: QtGui.QPixmap) -> None:
        self.preview_bitmap = QBitmap(a0)
        img = QImage(a0.width(), a0.height() + 4, QImage.Format_RGB32)
        img.fill(self.palette().color(QPalette.Background))
        if a0.width() > 0:
            with QPainter(img) as painter:
                self.draw_preview(painter)
                self.draw_selection(painter)
        super().setPixmap(QPixmap(img))
        self.repaint()

    def draw_preview(self, painter: QPainter):
        painter.setBackgroundMode(Qt.OpaqueMode)
        painter.setBackground(self.bg_color)
        painter.setPen(self.fg_color)
        painter.drawPixmap(0, 0, self.preview_bitmap)

    def mousePressEvent(self, ev: QtGui.QMouseEvent) -> None:
        x = ev.x()
        for index, offset in enumerate(self.item_offsets):
            if x < offset:
                self.preview_item_clicked.emit(index)
                self.update_selected(index)
                break

    def set_item_offsets(self, offsets: List[int]):
        self.item_offsets = offsets
