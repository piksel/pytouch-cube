import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPainter, QPixmap, QIcon
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QLabel

from labelmaker import USABLE_HEIGHT
from printables.printable import Printable, PrintableData


class ImageData(PrintableData):
    def __init__(self, image_source: str):
        self.source = image_source


class ImagePropsEdit(QWidget):

    def __init__(self, parent):
        super().__init__(parent)

        layout = QVBoxLayout()

        self.edit_text = QLineEdit('', self)
        self.preview_image = QLabel()
        self.preview_image.setFixedHeight(USABLE_HEIGHT)
        self.preview_image.setMaximumWidth(USABLE_HEIGHT * 2)

        layout.addWidget(self.preview_image)
        layout.addWidget(QLabel('Source:'))
        layout.addWidget(self.edit_text)
        layout.addStretch()

        self.setLayout(layout)

    def setData(self, data: ImageData):
        self.preview_image.setPixmap(QPixmap(data.source).scaledToHeight(USABLE_HEIGHT))
        self.edit_text.setText(data.source)


class Image(Printable):
    def __init__(self, data: ImageData):
        super().__init__()
        self.data = data

    def get_props_editor(self, parent):
        editor = ImagePropsEdit(parent)
        editor.setData(self.data)
        return editor

    def get_name(self):
        return os.path.basename(self.data.source)

    def get_icon(self):
        img_source = QImage(self.data.source)
        img = QImage(32, 32, QImage.Format_ARGB32)
        img.fill(0xffffffff)

        p = QPainter(img)
        p.drawRect(0,0,30,30)
        if img_source.width() > img_source.height():
            scaled = img_source.scaledToWidth(32)
            p.drawImage(0, 16 - (scaled.height() / 2), scaled)
        else:
            scaled = img_source.scaledToHeight(32)
            p.drawImage(16 - (scaled.width() / 2), 0, scaled)
        p.end()

        img = img.convertToFormat(QImage.Format_Mono)

        return QIcon(QPixmap.fromImage(img))

    def render(self):
        d = self.data
        img_src = QImage(d.source)
        if img_src.hasAlphaChannel():
            img = QImage(img_src.size(), QImage.Format_ARGB32)
            img.fill(0xffffffff)
            p = QPainter(img)
            p.drawImage(0, 0, img_src)
            p.end()
        else:
            img = img_src
        # img.convertToFormat(QImage.Format_Mono)
        return img.scaledToHeight(USABLE_HEIGHT, Qt.FastTransformation)