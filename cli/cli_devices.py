# BluetoothPrinterDevice
import asyncio
from argparse import Namespace
from typing import List, Tuple, Any, Optional
import logging
from comms.bluetooth import BluetoothPrinterDevice
from comms.serial import SerialPrinterDevice

class CliDevices:
    def __init__(self, type: str):
        self.type = type

        logging.root.addHandler(logging.StreamHandler())
        logging.root.setLevel(logging.INFO)

    async def list(self):
        if self.type == 'all' or self.type == 'serial':
            print("Serial devices:")
            for name, device in await SerialPrinterDevice.list_devices():
                print("-", device)
            print()

        if self.type == 'all' or self.type == 'bluetooth':
            print("Bluetooth devices:")
            for name, device in await BluetoothPrinterDevice.list_devices():
                print("-", device)
            print()

    @classmethod
    def create(cls, args: Namespace) -> 'CliDevices':
        cli = cls(args.type)

        return cli

    @classmethod
    def run(cls, args: Namespace):
        cli = cls.create(args)
        asyncio.run(cli.list())