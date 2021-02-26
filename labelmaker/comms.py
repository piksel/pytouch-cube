from __future__ import annotations

import logging
from pprint import pprint
from typing import *
from util import *

import abc
import serial
import bluetooth
from serial.tools.list_ports_common import ListPortInfo

BluetoothDeviceInfo = Tuple[str, str, str]

log = logging.getLogger(__name__)


class PrinterDevice(abc.ABC):
    def __init__(self, name):
        self.name = name
        self.baudrate = 9600
        self.stopbits = serial.STOPBITS_ONE,
        self.parity = serial.PARITY_NONE,
        self.timeout = 10

    @abc.abstractmethod
    def open(self):
        pass

    @classmethod
    @abc.abstractmethod
    async def list_devices(cls) -> List[Tuple[str, PrinterDevice]]:
        pass


class BluetoothPrinterDevice(PrinterDevice):
    def __init__(self, address: str, service=None, name=None):
        if name is None:
            name = address
        super().__init__(name)
        self.address = address

    @classmethod
    async def list_devices(cls) -> List[Tuple[str, PrinterDevice]]:
        devices = bluetooth.discover_devices(1, flush_cache=False, lookup_names=True, lookup_class=True)

        for d in devices:
            pprint(d)

        return [(name if not None else address, BluetoothPrinterDevice(address, service)) for address, name, service in
                devices]

    def test(self):
        log.info(f'Scanning {self.address} for services...')
        service_matches = bluetooth.find_service(address=self.address)
        for d in service_matches:
            pprint(d)

        first_match = service_matches[0]

        port = first_match["port"]
        name = first_match["name"]
        host = first_match["host"]

    def open(self):
        service_matches = bluetooth.find_service(address=self.address)
        for d in service_matches:
            pprint(d)

        first_match = service_matches[0]

        port = first_match["port"]
        name = first_match["name"]
        host = first_match["host"]

        socket = bluetooth.BluetoothSocket()
        socket.connect((host, port))
        return socket


class SerialPrinterDevice(PrinterDevice):

    def __init__(self, port_info: ListPortInfo, name=None):
        if name is None:
            name = port_info.name
        super().__init__(name)
        self.port_info = port_info

    def open(self):
        serial.Serial(
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
        return [(it.name if it.name is not None else it.device, SerialPrinterDevice(it)) for it in cls.list_comports()]

    @classmethod
    def list_comports(cls) -> List[ListPortInfo]:
        if is_mac:
            from serial.tools.list_ports_osx import GetIOServicesByType, GetParentDeviceByType, get_string_property
            from mac_bt import get_bytes_property, IOBluetooth

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
                            print('Device:', tty, 'Address:', address)
                            print('Name:', dev_name)
                            info = ListPortInfo(tty)
                            info.name = dev_name
                            ports.append(info)
                            break
            return ports
        else:
            if is_win:
                from wmi import WMI
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


async def list_printer_devices() -> List[Tuple[str, PrinterDevice]]:
    # return await BluetoothPrinterDevice.list_devices()
    return await SerialPrinterDevice.list_devices()
