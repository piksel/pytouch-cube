import math

import qrcode
from PyQt5.QtGui import QImage, QPainter, QColor
from PyQt5.QtWidgets import QLineEdit, QLabel

from labelmaker import USABLE_HEIGHT
from printables.printable import PrintableData, Printable
from printables.propsedit import PropsEdit


class QrCodeData(PrintableData):
    def set_from(self, source):
        self.text = source.text

    def clone(self):
        return QrCodeData(self.text)

    def __init__(self, text='123456789012'):
        self.text = text


class QrCodePropsEdit(PropsEdit):

    def __init__(self, data: QrCodeData, parent, printable):
        super().__init__(data, parent, printable)

        self.edit_text = QLineEdit(self.data.text, self)
        # self.edit_text.textChanged.connect(self.edit_text_changed)
        self.layout.addWidget(QLabel('Value:'))
        self.layout.addWidget(self.edit_text)

    def serialize(self, clone=False):
        super().serialize(clone)
        self.data.text = self.edit_text.text()


class QrCode(Printable):
    def __init__(self):
        super().__init__()
        self.data = QrCodeData()

    def get_props_editor(self, parent):
        return QrCodePropsEdit(self.data, parent, self)

    def render(self):
        d = self.data

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=USABLE_HEIGHT,
            border=4,
        )
        qr.add_data(d.text)
        qr.make(fit=True)

        img = QImage(USABLE_HEIGHT, USABLE_HEIGHT, QImage.Format_Mono)
        img.fill(0xffffffff)
        with QPainter(img) as p:

            modcount = qr.modules_count
            M = math.floor(USABLE_HEIGHT / modcount)
            padding = ((USABLE_HEIGHT - (modcount * M))/2)

            black = QColor(0, 0, 0)

            for r in range(modcount):
                for c in range(modcount):
                    if qr.modules[r][c]:
                        p.fillRect(padding + (r*M), padding + (c*M), M, M, black)

        return img
