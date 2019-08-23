from PyQt5.QtWidgets import QWidget

from printables.printable import PrintableData


class PropsEdit(QWidget):
    def __init__(self, data: PrintableData, parent, printable):
        super().__init__(parent)

        self.data = data.clone()
        self.data_original = data
        self.parent = parent
        self.printable = printable

    def save(self):
        self.data_original.set_from(self.data)
        self.parent.update_preview()