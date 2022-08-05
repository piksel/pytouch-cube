from __future__ import annotations

import logging
from pprint import pprint
from typing import *
from util import *
from PyQt6.QtCore import Qt, QLineF, QPointF
from PyQt6.QtGui import QImage, QPainter, QColor, QIcon, QPixmap, QPainterPath
import abc
import serial

from serial.tools.list_ports_common import ListPortInfo

BluetoothDeviceInfo = Tuple[str, str, str]

log = logging.getLogger(__name__)


class PrinterDevice(abc.ABC):
    def __init__(self, address, name=None):
        self.address = address
        if name is None:
            name = address
        self.name = name
        self.baudrate = 9600
        self.stopbits = serial.STOPBITS_ONE
        self.parity = serial.PARITY_NONE
        self.timeout = 10

    @abc.abstractmethod
    def open(self) -> IO[bytes]:
        pass

    @abc.abstractclassmethod
    def get_icon(cls) -> QIcon:
        pass

    @classmethod
    @abc.abstractmethod
    async def list_devices(cls) -> List[Tuple[str, PrinterDevice]]:
        pass

def find_device(device_type: str, device_address: str) -> PrinterDevice | None:
    from .bluetooth import BluetoothPrinterDevice
    from .serial import SerialPrinterDevice
    if device_type == "bluetooth" or device_type == "bt":
        # This skips the lookup, as it will be performed when connecting anyway
        return BluetoothPrinterDevice(device_address)
    elif device_type == "serial" or device_type == "":
        return SerialPrinterDevice.find(device_address)
    else:
        log.error(f'Invalid device type "{device_type}"')
        return None

async def find_default_device() -> PrinterDevice | None:
    from .bluetooth import BluetoothPrinterDevice
    from .serial import SerialPrinterDevice

    log.info("Querying for serial device...")
    for name, dev in await SerialPrinterDevice.list_devices():
        if name.startswith('PT-P300'):
            log.info(f"Found serial device: {dev}")
            return dev
    
    for name, dev in await BluetoothPrinterDevice.list_devices():
        if name.startswith('PT-P300'):
            log.info(f"Found bluetooth device: {dev}")
            return dev

    return None

async def list_printer_devices() -> List[Tuple[str, PrinterDevice]]:
    from .bluetooth import BluetoothPrinterDevice
    from .serial import SerialPrinterDevice
    # return await SerialPrinterDevice.list_devices()
    return await BluetoothPrinterDevice.list_devices() + await SerialPrinterDevice.list_devices()
