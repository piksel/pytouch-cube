from wmi import WMI # type: ignore
from serial.tools.list_ports_windows import comports
import logging

log = logging.getLogger(__name__)

def fix_port(wmi: WMI, port: str):
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

def list_comports():
    wmi = WMI()
    return [fix_port(wmi, it) for it in comports(include_links=True) if it.hwid.startswith('BTH')]