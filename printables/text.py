from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QImage, QPainter, QFontMetrics
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QLabel, QPushButton, QFontDialog

from printables.printable import Printable, PrintableData
from printables.propsedit import PropsEdit


class TextData(PrintableData):

    def __init__(self, text='', font_string=None):
        self.text = text

        font = QFont()
        if font_string is None:
            font.setPixelSize(128)
        else:
            font.fromString(font_string)
        self.font = font

    def clone(self):
        return TextData(self.text, self.font.toString())

    def set_from(self, source):
        self.text = source.text
        self.font.fromString(source.font.toString())


class TextPropsEdit(PropsEdit):

    data: TextData

    def __init__(self, data: TextData, parent, printable):
        super().__init__(data, parent, printable)

        self.setMinimumWidth(256)
        layout = QVBoxLayout()

        self.edit_text = QLineEdit(self.data.text, self)
        layout.addWidget(QLabel('Text:'))
        layout.addWidget(self.edit_text)

        self.button_font = QPushButton(self.get_font_name())
        self.button_font.clicked.connect(self.button_font_clicked)
        layout.addWidget(QLabel('Font:'))
        layout.addWidget(self.button_font)

        layout.addStretch()

        self.setLayout(layout)

    def get_font_name(self):
        f = self.data.font
        return "{0} {1}".format(f.family(), f.styleName())

    def button_font_clicked(self):
        font, ok = QFontDialog.getFont(self.data.font, self, "Select a font...")
        if not ok:
            return
        self.data.font = font
        self.button_font.setText(self.get_font_name())
        self.save()




class Text(Printable):

    def __init__(self, data: TextData):
        self.data = data

    def get_name(self):
        return self.data.text

    def get_props_editor(self, parent):
        return TextPropsEdit(self.data, parent, self)

    def render(self):
        d = self.data
        font = d.font
        width = QFontMetrics(font).width(d.text)
        print(width, font.toString())
        img = QImage(width, 128, QImage.Format_ARGB32)
        img.fill(0xffffffff)
        p = QPainter(img)
        p.setFont(font)
        p.drawText(img.rect(), Qt.AlignLeft, d.text)
        p.end()
        del p
        return img