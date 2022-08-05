import asyncio
from pprint import pprint

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QComboBox
from qasync import asyncSlot

from comms import list_printer_devices
from util import *
from .types import *


class PrinterSelect(QComboBox):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setModel(PrinterDevicesModel(self))


    @asyncSlot()
    async def update(self) -> None:
        self.setPlaceholderText("loading devices...")
        self.clear()
        self.setDisabled(True)

        # yield to the qt loop to update UI
        await asyncio.sleep(.1)

        devices = await list_printer_devices()

        for name, device in devices:
            self.addItem(device.get_icon(), name, device)

        self.setPlaceholderText("")
        self.setDisabled(False)

        index = self.findText('PT-P3', Qt.MatchFlag.MatchContains)
        if index > 0:
            self.setCurrentIndex(index)

        self.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        self.adjustSize()


