from __future__ import annotations

import logging
from typing import *
from gui import icons
from comms import PrinterDevice
from util import *
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPainter, QColor, QIcon, QPixmap
import serial
from serial.tools.list_ports_common import ListPortInfo

log = logging.getLogger(__name__)

class SerialPrinterDevice(PrinterDevice):

    def __init__(self, port_info: ListPortInfo, name=None):
        if name is None:
            name = port_info.product
        super().__init__(port_info.name, name)
        self.port_info = port_info
        self.baudrate = 9600
        self.stopbits = serial.STOPBITS_ONE
        self.parity = serial.PARITY_NONE

    def open(self) -> IO[bytes]:
        return serial.Serial(
            self.port_info.device,
            baudrate=self.baudrate,
            stopbits=self.stopbits,
            parity=self.parity,
            bytesize=8,
            timeout=self.timeout,
            write_timeout=self.timeout,
            dsrdtr=True
        )

    @classmethod
    def find(cls, query: str) -> Optional[PrinterDevice]:
        for name, device in cls.list_devices():
            if device.port_info.device == query:
                return device
        return None

    @classmethod
    async def list_devices(cls) -> List[Tuple[str, SerialPrinterDevice]]:
        nd = [(f"{it.product if it.product is not None else it.name} ({it.device})", it) 
            for it in cls.list_comports()]
        return [(name, SerialPrinterDevice(it, name)) for name, it in nd]

    @classmethod
    def list_comports(cls) -> List[ListPortInfo]:
        if is_mac:
            from mac.serial import list_comports
        elif is_win:
            from win.serial import list_comports
        else:
            from serial.tools.list_ports_posix import comports as list_comports
        return list_comports()

    def __str__(self) -> str:
        return f"[{self.address}]: {self.name}"

    @classmethod
    def get_icon(cls) -> QIcon:
        # return icons.get_bluetooth_icon()
        return icons.get_generic_icon(cls.__name__[0])