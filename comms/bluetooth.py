from __future__ import annotations
import asyncio

import logging
from pprint import pprint
from typing import *

from qasync import QThreadExecutor
from gui import icons
from . import PrinterDevice
from util import *
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPainter, QColor, QIcon, QPixmap
import bluetooth as bt

log = logging.getLogger(__name__)

class BluetoothStream(IO[bytes]):
    def __init__(self, socket: bt.BluetoothSocket, name: str):
        self._name = name
        self.socket = socket

    def write(self, payload: Union[bytes, bytearray]) -> int:
        return self.socket.send(payload)

    def read(self, n: int = -1) -> bytes:
        return self.socket.recv(n)

    @property
    def in_waiting(self):
        return 'n/a'

    @property
    def out_waiting(self):
        return 'n/a'

    @property
    def name(self):
        return self._name

    def reset_input_buffer(self):
        pass

class BluetoothPrinterDevice(PrinterDevice):
    def __init__(self, address: str, name=None):
        if name is None:
            name = bt.lookup_name(address)
        super().__init__(address, name)

    @classmethod
    async def list_devices(cls) -> List[Tuple[str, PrinterDevice]]:
        with QThreadExecutor(1) as exec:
            return await asyncio.get_event_loop().run_in_executor(exec, cls.list_devices_sync)

    @classmethod
    def list_devices_sync(cls) -> List[Tuple[str, PrinterDevice]]:

        devices = bt.discover_devices(3, flush_cache=False, lookup_names=True, lookup_class=True)
        sd = filter(lambda d: len(bt.find_service(address=d[0], uuid=bt.SERIAL_PORT_CLASS)) > 0, devices)
        return [(name, BluetoothPrinterDevice(addr, name=name))
            for addr, name, _ in sd]

        # service lookup, more efficient, but uses too short duration
        #services = bt.find_service(uuid=bt.SERIAL_PORT_CLASS)
        # sd = [(bt.lookup_name(s["host"]), s) for s in services]

        # return [(name, BluetoothPrinterDevice(s["host"], name=name))
        #     for name, s in sd]

    @classmethod
    def get_icon(cls) -> QIcon:
        return icons.get_generic_icon(cls.__name__[0])

    def test(self):
        log.info(f'Scanning {self.address} for services...')
        service_matches = bt.find_service(address=self.address)

        first_match = service_matches[0]

        port = first_match["port"]
        name = first_match["name"]
        host = first_match["host"]

    def open(self) -> IO[bytes]:
        attempt = 1
        while attempt < 10:
            service_matches = bt.find_service(address=self.address,uuid=bt.SERIAL_PORT_CLASS)
            if len(service_matches) > 0:
                first_match = service_matches[0]

                port = first_match["port"]
                host = first_match["host"]

                socket = bt.BluetoothSocket()
                socket.connect((host, port))
                return BluetoothStream(socket, self.name)
            log.warn(f"No service candidate found, re-querying... ({attempt}/10)")
            attempt += 1
            
        raise Exception("Could not find device serial service")

    def __str__(self) -> str:
        return f"[{self.address}]: {self.name}"