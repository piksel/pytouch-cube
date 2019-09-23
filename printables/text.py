from copy import copy

from PyQt5.QtCore import Qt, QMargins
from PyQt5.QtGui import QFont, QImage, QPainter, QFontMetrics
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QLabel, QPushButton, QFontDialog, QHBoxLayout, QSizePolicy, \
    QFontComboBox, QGroupBox, QSpinBox, QCheckBox

from labelmaker import USABLE_HEIGHT
from margins import Margins
from printables.printable import Printable, PrintableData
from printables.propsedit import PropsEdit
from settings import Settings


class TextData(PrintableData):

    def __init__(self, text='', font_string=None, margins: Margins = None):
        super().__init__(margins)
        self.text = text

        if font_string is None:
            font = QFont()
            font.setStyleHint(QFont.Helvetica)
            font.setFamily('Helvetica Neue')

            # font.Helvetica
            print('Default font:', font.family(), font.families(), font.toString())
            font.setPixelSize(USABLE_HEIGHT)
            self.font_string = font.toString()
        else:
            self.font_string = font_string

    def getQFont(self):
        font = QFont()
        font.fromString(self.font_string)
        return font

    def clone(self):
        return TextData(self.text, self.font_string, self.margins.clone())

    def set_from(self, source):
        super().set_from(source)
        self.text = source.text
        self.font_string = source.font_string

    def __str__(self):
        return '<TextData [{0}] "{1}" {2} {3} {4} {5}>'.format(self.font_string, self.text, self.margins.top(), self.margins.left(), self.margins.right(), self.margins.bottom())


class TextPropsEdit(PropsEdit):

    data: TextData
    adjusted_size = None

    def __init__(self, data: TextData, parent, printable):
        super().__init__(data, parent, printable)

        font = data.getQFont()

        self.setMinimumWidth(256)

        self.edit_text = QLineEdit(self.data.text, self)
        self.edit_text.textChanged.connect(self.text_changed)
        self.layout.addWidget(QLabel('Text:'))
        self.layout.addWidget(self.edit_text)

        self.button_font = QPushButton(self.get_font_name())
        self.button_font.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.button_font.clicked.connect(self.button_font_clicked)

        button_default = QPushButton('Set as default', self)
        button_default.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        button_default.clicked.connect(self.default_clicked)

        font_layout = QVBoxLayout()
        font_family = QFontComboBox(self)
        font_family.setCurrentFont(font)
        font_family.currentFontChanged.connect(self.font_changed)
        self.font_family = font_family
        font_layout.addWidget(font_family)
        font_group = QGroupBox('Font:', self)
        font_group.setLayout(font_layout)

        self.layout.addWidget(font_group)

        buttons = QHBoxLayout()
        buttons.setSpacing(0)
        font_size = QSpinBox(self)
        font_size.setValue(font.pixelSize())
        font_size.valueChanged.connect(self.size_changed)
        self.font_size = font_size
        buttons.addWidget(QLabel('Size:'))
        buttons.addWidget(font_size)
        buttons.addWidget(QLabel('px'))
        buttons.addStretch()
        # buttons.addWidget(self.button_font)

        adjusted_size = QLabel(self)
        self.adjusted_size_label = adjusted_size

        self.auto_size = QCheckBox('Automatically scale font', self)
        self.auto_size.stateChanged.connect(self.auto_size_changed)
        buttons.addWidget(self.auto_size)

        buttons2 = QHBoxLayout()

        buttons2.addWidget(adjusted_size)
        buttons2.addWidget(button_default)

        font_layout.addLayout(buttons)
        font_layout.addLayout(buttons2)

        # font_preview = QLabel(self.data.text)
        # font_preview.setFont(font)
        # self.layout.addWidget(font_preview)

        self.layout.addStretch()

    def get_font_name(self):
        f = self.data.getQFont()
        return "{0} {1}".format(f.family(), f.styleName())

    def serialize(self, clone=False) -> TextData:
        data = super().serialize(clone)

        data.text = self.edit_text.text()
        font = self.font_family.currentFont()
        target_font_size = self.font_size.value()
        data.auto_size = self.auto_size.isChecked()
        data.font_size = target_font_size

        if data.auto_size:
            font.setPixelSize(self.adjusted_size)
        else:
            font.setPixelSize(target_font_size)
        data.font_string = font.toString()

        return data

    def font_changed(self, font):
        self.update_adjusted(font)
        self.save()

    def auto_size_changed(self):
        self.update_adjusted()
        self.save()

    def size_changed(self):
        self.update_adjusted()
        self.save()

    def text_changed(self):
        self.save()

    def default_clicked(self):
        default = self.serialize(True)
        default.text = ''
        Settings.set_propsdata_default(default)

    def update_adjusted(self, font=None):
        if font is None:
            font = self.font_family.currentFont()

        if self.auto_size.isChecked():
            font_size = self.font_size.value()
            font.setPixelSize(font_size)
            metrics = QFontMetrics(font)
            rect = metrics.boundingRect(self.edit_text.text())
            print('Font:', font.family())
            print('Height:', rect.height(), rect.top(), '<->', rect.bottom(), 'CapHeight:', metrics.capHeight(),
                  'Ascent:', metrics.ascent(), 'FontSize:', font_size)
            over_ascent = metrics.ascent() - font_size
            print('OverAscent:', over_ascent)
            adjusted_size = font_size - over_ascent
            self.adjusted_size = adjusted_size
            self.adjusted_size_label.setText('Adjusted size: {0}px'.format(adjusted_size))
        else:
            self.adjusted_size_label.setText('')

    def button_font_clicked(self):
        font, ok = QFontDialog.getFont(self.data.getQFont(), self, "Select a font...")
        if not ok:
            return
        self.data.font_string = font.toString()
        self.button_font.setText(self.get_font_name())
        self.save()


class Text(Printable):

    def __init__(self, data: TextData = None):
        if data is None:
            data = Settings.get_propsdata_default(type(TextData))
            if data is None:
                data = TextData()

        self.data = data

    def get_name(self):
        return self.data.text

    def get_props_editor(self, parent):
        return TextPropsEdit(self.data, parent, self)

    def render(self):
        d = self.data
        font = QFont()
        font.fromString(d.font_string)
        width = QFontMetrics(font).width(d.text)
        print(width, font.toString(), d.text)
        img = QImage(width, USABLE_HEIGHT, QImage.Format_ARGB32)
        img.fill(0xffffffff)
        p = QPainter(img)
        p.setFont(font)
        rect = img.rect().marginsRemoved(d.margins.getQMargins())
        p.drawText(rect, Qt.AlignLeft | Qt.AlignHCenter, d.text)
        p.end()
        del p
        return img
