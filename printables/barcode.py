from PyQt5.QtCore import Qt, QRectF, QStringListModel
from PyQt5.QtGui import QFont, QFontMetrics, QImage, QPainter, QColor, QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QLabel, QComboBox
from barcode.writer import BaseWriter

from labelmaker import USABLE_HEIGHT
from printables.printable import Printable, PrintableData
import barcode

from printables.propsedit import PropsEdit


class BarcodeData(PrintableData):
    def set_from(self, source):
        self.text = source.text
        self.code_type = source.code_type

    def clone(self):
        return BarcodeData(self.text, self.code_type)

    def __init__(self, text='123456789012', code_type='ean13'):
        self.text = text
        self.code_type = code_type


class BarcodePropsEdit(PropsEdit):

    def __init__(self, data: BarcodeData, parent, printable):
        super().__init__(data, parent, printable)
        self.setMinimumWidth(256)
        layout = QVBoxLayout()

        self.combo_type = QComboBox()
        model = QStandardItemModel(0, 2)
        curr_index = 0
        for key in barcode.PROVIDED_BARCODES:
            bc = barcode.get(key)
            model.appendRow([QStandardItem(bc.name) ,QStandardItem(key)])
            if self.data.code_type == key:
                curr_index = model.rowCount() - 1

        self.combo_type.setModel(model)
        self.combo_type.setCurrentIndex(curr_index)
        self.combo_type.currentIndexChanged.connect(self.combo_type_changed)
        layout.addWidget(QLabel('Barcode type:'))
        layout.addWidget(self.combo_type)

        self.edit_text = QLineEdit(self.data.text, self)
        self.edit_text.textChanged.connect(self.edit_text_changed)
        layout.addWidget(QLabel('Value:'))
        layout.addWidget(self.edit_text)

        layout.addStretch()

        self.setLayout(layout)

    def combo_type_changed(self):
        model: QStandardItemModel = self.combo_type.model()
        item = model.item(self.combo_type.currentIndex(), 1)
        print(item.text(), item.data())
        self.data.code_type = item.text()
        self.save()
        pass

    def edit_text_changed(self):
        self.data.text = self.edit_text.text()
        self.save()



class BarcodeWriter(BaseWriter):
    dpi = 15
    text_size = 20

    def __init__(self):
        BaseWriter.__init__(self, self._init, self._create_module,
                            self._create_text, self._finish)


    def _init(self, code):
        print('init', code)
        width, height = self.calculate_size(len(code[0]), len(code), self.dpi * 25)
        print(width, height)
        image = QImage(width, USABLE_HEIGHT, QImage.Format_ARGB32)
        image.fill(0xffffffff)
        self._painter = QPainter(image)
        self._image = image

        pass

    first = True
    def _create_module(self, xpos, ypos, width, color):
        if self.first:
            print('_create_module', xpos, ypos, width, color)
            self.first = False
        p = self._painter
        p.setBrush(QColor(color))
        x1 = xpos * self.dpi
        y1 = 0
        x2 = width * self.dpi
        y2 = USABLE_HEIGHT
        p.drawRect(x1, y1, x2, y2)
        pass

    def _create_text(self, xpos, ypos):
        return
        print('_create_text', xpos, ypos)
        if self.human != '':
            barcodetext = self.human
        else:
            barcodetext = self.text
        p = self._painter

        font = p.font()
        font.setPixelSize(self.text_size)
        p.setFont(font)
        bounds = p.drawText(self._image.rect(), Qt.AlignBottom | Qt.AlignCenter, barcodetext)
        p.setBrush(QColor(0xffffffff))
        pen = p.pen()
        p.setPen(Qt.NoPen)
        p.drawRect(bounds)
        p.setPen(pen)

        bounds = p.drawText(self._image.rect(), Qt.AlignBottom | Qt.AlignCenter, barcodetext)

        pass

    def _finish(self):
        self._painter.end()
        return self._image
        pass

    def save(self, filename, output):
        print('save')
        pass


class Barcode(Printable):
    def __init__(self, data: BarcodeData):
        self.data = data

    def get_name(self):
        bc = barcode.get(self.data.code_type).name
        return "[{0}] {1}".format(bc, self.data.text)

    def get_props_editor(self, parent):
        return BarcodePropsEdit(self.data, parent, self)

    def render(self):
        d = self.data

        writer = BarcodeWriter()
        self.render_error = None
        try:
            img = barcode.generate(d.code_type, d.text, writer, pil=True)
        except Exception as x:
            self.render_error = x
            return QImage(0, 0, QImage.Format_ARGB32)

        return img