from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGroupBox

from printables.printable import PrintableData
from qmargins_edit import QMarginsEdit


class PropsEdit(QWidget):
    data: PrintableData

    def __init__(self, data: PrintableData, parent: QWidget, printable, default_props=True):
        super().__init__(parent)

        self.data = data.clone()
        self.data_original = data
        self.parent = parent
        self.printable = printable
        self.layout = QVBoxLayout()

        if default_props:
            group = QGroupBox('Margins:', self)
            self.margin_editor = QMarginsEdit(self)
            self.margin_editor.setMargins(self.data.margins)
            self.margin_editor.valueChanged.connect(self.save)
            layout = QVBoxLayout(self)
            group.setLayout(layout)
            layout.addWidget(self.margin_editor)
            self.layout.addWidget(group)

        self.setLayout(self.layout)

    def serialize(self, clone=False):
        if clone:
            data = PrintableData()
        else:
            data = self.data
        data.margins = self.margin_editor.margins()

        return data

    def save(self):
        self.serialize()
        self.data_original.set_from(self.data)
        self.printable.data = self.data
        self.parent.update_preview()
        self.parent.update_items(True)