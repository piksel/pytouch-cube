from serial.tools.list_ports_osx import GetIOServicesByType, GetParentDeviceByType, get_string_property
from mac.bluetooth import get_bytes_property, IOBluetooth
from serial.tools.list_ports_common import ListPortInfo

def list_comports():
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