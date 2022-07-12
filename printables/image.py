import os
from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPainter, QPixmap, QIcon
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QLabel, QSlider, QHBoxLayout, QPushButton, QFileDialog

from labelmaker import USABLE_HEIGHT
from margins import Margins
from printables.printable import Printable, PrintableData
from printables.propsedit import PropsEdit


class ImageData(PrintableData):
    source = ''
    threshold = 127

    def __init__(
            self, image_source: Optional[str] = None, 
            threshold: int = 127, margins: Optional[Margins] = None
    ):
        super().__init__(margins)
        self.source = image_source
        self.threshold = threshold

    def clone(self):
        return ImageData(self.source, self.threshold, self.margins)

    def set_from(self, source):
        self.source = source.source
        self.threshold = source.threshold


class ImagePropsEdit(PropsEdit):

    def __init__(self, data: ImageData, parent, printable):
        super().__init__(data, parent, printable)

        self.data = data

        layout = self.layout

        self.edit_text = QLineEdit('', self)
        self.edit_text.setText(data.source)
        self.open_image = QPushButton('Open image', self)
        self.open_image.clicked.connect(self.on_open_image)
        self.preview_image = QLabel()
        self.preview_image.setFixedHeight(USABLE_HEIGHT)
        self.preview_image.setMaximumWidth(USABLE_HEIGHT * 2)
        self.preview_image.setPixmap(QPixmap(data.source).scaledToHeight(USABLE_HEIGHT))

        layout.addWidget(self.preview_image)
        layout.addWidget(QLabel('Source:'))
        layout.addWidget(self.edit_text)
        layout.addWidget(self.open_image)
        layout.addSpacing(10)

        threshold = QHBoxLayout()
        layout.addLayout(threshold)
        threshold.addWidget(QLabel('Threshold:'))
        thresh_value = QLabel(str(data.threshold))
        thresh_value.setAlignment(Qt.AlignmentFlag.AlignRight)
        threshold.addWidget(thresh_value)
        self.thresh_value = thresh_value

        slider = QSlider(Qt.Orientation.Horizontal, self)
        slider.setMinimum(1)
        slider.setMaximum(254)
        slider.setValue(data.threshold)
        slider.valueChanged.connect(self.update_threshold)
        self.thresh_slider = slider

        # slider.setMinimumWidth(128)
        layout.addWidget(slider)
        slider.update()
        layout.addStretch()

    def on_open_image(self):
        user_home = os.path.expanduser('~')
        open_initial_path = os.path.join(user_home, 'Pictures')
        if not os.path.isdir(open_initial_path):
            open_initial_path = user_home
        image_path, _ = QFileDialog.getOpenFileName(
            directory=open_initial_path,
            caption='Open Image',
            filter='Image Files (*.png *.jpg *.bmp)')

        if len(image_path) > 0:
            self.edit_text.setText(image_path)
            self.data.source = image_path

        self.save()

    def update_threshold(self, value: int):
        self.thresh_value.setText(str(value))
        self.save()

    def serialize(self, clone=False):
        super().serialize(clone)
        if self.thresh_slider is None:
            return
        self.data.source = self.edit_text.text()
        self.data.threshold = self.thresh_slider.value()


class Image(Printable):
    def __init__(self, data: Optional[ImageData] = None):
        super().__init__()
        if data is None:
            data = ImageData()
        self.data = data

    def get_margins(self):
        return self.data.margins

    def get_props_editor(self, parent):
        return ImagePropsEdit(self.data, parent, self)

    def get_name(self):
        if self.data.source is None:
            return '<No image selected>'
        return os.path.basename(self.data.source)

    def get_icon(self):
        if self.data.source is None:
            return Image.get_generic_icon()
        elif not os.path.isfile(self.data.source):
            return Image.get_generic_icon(False)
        img_source = QImage(self.data.source)
        img = QImage(32, 32, QImage.Format.Format_ARGB32)
        img.fill(0xffffffff)

        p = QPainter(img)
        p.drawRect(0, 0, 30, 30)
        if img_source.width() > img_source.height():
            scaled = img_source.scaledToWidth(32)
            p.drawImage(0, 16 - (scaled.height() // 2), scaled)
        else:
            scaled = img_source.scaledToHeight(32)
            p.drawImage(16 - (scaled.width() // 2), 0, scaled)
        p.end()

        img = img.convertToFormat(QImage.Format.Format_Mono)

        return QIcon(QPixmap.fromImage(img))

    def render(self) -> Optional[QImage]:
        self.render_error = None
        d = self.data
        if d.source is None:
            self.render_error = UserWarning('No image selected')
            return QImage(0, USABLE_HEIGHT, QImage.Format.Format_Mono)
        if not os.path.isfile(d.source):
            self.render_error = FileNotFoundError(f'Source file not found: {d.source}')
            return QImage(0, USABLE_HEIGHT, QImage.Format.Format_Mono)
        img_src = QImage(d.source)
        if img_src.hasAlphaChannel():
            img = QImage(img_src.size(), QImage.Format.Format_ARGB32)
            img.fill(0xffffffff)
            p = QPainter(img)

            p.drawImage(0, 0, img_src)
            p.end()
        else:
            img = img_src
        # img.convertToFormat(QImage.Format_Mono)
        img = img.scaledToHeight(USABLE_HEIGHT, Qt.TransformationMode.FastTransformation)
        rect = img.rect() # .marginsAdded(d.margins.getQMargins())

        max_x = img.width()
        max_y = USABLE_HEIGHT

        bitmap = QImage(rect.width(), USABLE_HEIGHT, QImage.Format.Format_Mono)
        for x in range(0, rect.width()):
            for y in range(0, USABLE_HEIGHT):
                if x >= max_x or x <= 0 or y > max_y or y < 0:
                    bitmap.setPixel(x, y, 1)
                    continue

                oc = img.pixelColor(x, y)
                if oc.value() > d.threshold:
                    bitmap.setPixel(x, y, 1)
                else:
                    bitmap.setPixel(x, y, 0)
        return bitmap
