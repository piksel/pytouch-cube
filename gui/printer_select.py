from pprint import pprint

from PyQt6.QtCore import QDir, Qt
from PyQt6.QtWidgets import QComboBox
from qasync import asyncSlot

from labelmaker.comms import list_printer_devices
from util import *
from .types import *


class PrinterSelect(QComboBox):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        #self.setPlaceholderText('Select Bluetooth Device...')
        self.setModel(PrinterDevicesModel(self))

    @asyncSlot()
    async def update(self) -> None:
        self.clear()
#        if is_win:
        candidate = await self.update_win()
#        else:
#            candidate = await self.update_devfs()

        #if candidate is not None:
        index = self.findText('PT-P3', Qt.MatchFlag.MatchContains)
        if index > 0:
            self.setCurrentIndex(index)

        self.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        self.adjustSize()
        # self.setMinimumWidth(self.minimumSizeHint().width())



    async def update_devfs(self) -> Optional[str]:
        candidate = None

        # TODO: Evaluate fsmodel vs custom
        # fs_model = QFileSystemModel(self)
        # model_proxy = QSortFilterProxyModel(self)
        # model_proxy.setSourceModel(fs_model)
        # fs_model.setNameFilters(['tty.PT-P3*'])
        #
        # fs_model.setRootPath('/dev/')
        # fs_model.setFilter(QDir.System)
        #
        # dev_index = fs_model.index('/dev')

        # print(printers.entryList())

        # model_proxy.setRecursiveFilteringEnabled(True)
        # model_proxy.setFilterKeyColumn(0)
        # proxy_dev = model_proxy.mapFromSource(dev_index)

        # printer_select.setRootModelIndex(dev_index)
        # printer_select.setRootIndex(dev_index)
        # printer_select.setExpanded(dev_index, True)
        # model_proxy.setFilterWildcard('tty*')

        for p in QDir('/dev').entryList(['tty*', 'rfcomm*'], QDir.Filter.System, QDir.SortFlag.Name):
            if p.startswith('tty.') or p.startswith('rfcomm'):
                device = '/dev/' + p

                self.addItem(device, device)
                #row = printers.add(device, device)

                if p.startswith('tty.PT-P3'):
                    candidate = device

        return candidate

    async def update_win(self) -> Optional[str]:
        candidate = None

        for item in await list_printer_devices():
            name, device = item
            # pprint(device.port_info.__dict__, depth=10)
            self.addItem(name, device)

        return candidate
