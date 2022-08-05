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

STOPBITS_ONE = serial.STOPBITS_ONE
PARITY_NONE = serial.PARITY_NONE

log = logging.getLogger(__name__)

class SerialPrinterDevice(PrinterDevice):

    def __init__(self, port_info: ListPortInfo, name=None):
        if name is None:
            name = port_info.product
        super().__init__(port_info.name, name)
        self.port_info = port_info

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
            from serial.tools.list_ports_osx import GetIOServicesByType, GetParentDeviceByType, get_string_property
            from mac.bluetooth import get_bytes_property, IOBluetooth

            services = GetIOServicesByType('IOSerialBSDClient')
            ports = []
            bt_devices = IOBluetooth.IOBluetoothDevice.pairedDevices()
            for service in services:
                tty = get_string_property(service, "IODialinDevice")
                bt_device = GetParentDeviceByType(service, "IOBluetoothSerialClient")
                dev_name = tty
                if bt_device is not None:
                    address_bytes = get_bytes_property(bt_device, "BTAddress")

                    if address_bytes is not None:
                        address = '-'.join(list('%02.x' % b for b in address_bytes))
                        for dev in bt_devices:
                            if not address.startswith(dev.addressString()):
                                continue

                            disp_name = dev.getDisplayName()
                            name = dev.getName()

                            if disp_name is not None:
                                dev_name = '{0} - {1} ({2})'.format(disp_name, name, tty)
                            else:
                                dev_name = '{0} ({1})'.format(name, tty)
                            info = ListPortInfo(tty)
                            info.name = dev_name
                            ports.append(info)
                            break
            return ports
        else:
            if is_win:
                from wmi import WMI # type: ignore
                from serial.tools.list_ports_windows import comports

                wmi = WMI()

                def fix_port(port):
                    parts = port.hwid.split('&')
                    hw_address, _ = parts[len(parts) - 1].split('_')
                    log.debug(f"Found potential Bluetooth device address: {hw_address}")
                    wql = f"SELECT Name FROM Win32_PNPEntity WHERE DeviceID LIKE '%BTHENUM\\Dev_{hw_address}%'"
                    log.debug(f"Fetching device name using WQL: {wql}")
                    for entity in wmi.query(wql):
                        port.name = f'{entity.Name} ({port.device})'
                        return port
                    # No entity found, use BT address
                    port.name = f'Unknown device 0x{hw_address} ({port.device})'
                    return port

                return [fix_port(it) for it in comports(include_links=True) if it.hwid.startswith('BTH')]

            else:
                from serial.tools.list_ports_posix import comports as list_comports
                return list_comports()

    def __str__(self) -> str:
        return f"[{self.address}]: {self.name}"

    @classmethod
    def get_icon(cls) -> QIcon:
        # return icons.get_bluetooth_icon()
        return icons.get_generic_icon(cls.__name__[0])