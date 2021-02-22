#!/usr/bin/env python
import ctypes
import os
import struct
import sys
from pprint import pprint

import serial
from serial.tools.list_ports_common import ListPortInfo

if os.name == 'nt':  # sys.platform == 'win32':
    from serial.tools.list_ports_windows import comports as list_comports
elif os.name == 'posix':
    from serial.tools.list_ports_posix import comports as list_comports

from labelmaker_encode import encode_raster_transfer, read_png



STATUS_OFFSET_BATTERY = 6
STATUS_OFFSET_EXTENDED_ERROR = 7
STATUS_OFFSET_ERROR_INFO_1 = 8
STATUS_OFFSET_ERROR_INFO_2 = 9
STATUS_OFFSET_STATUS_TYPE = 18
STATUS_OFFSET_PHASE_TYPE = 19
STATUS_OFFSET_NOTIFICATION = 22

BUFFER_HEIGHT = 128
PRINT_MARGIN = 30
USABLE_HEIGHT = BUFFER_HEIGHT - (PRINT_MARGIN * 2)

STATUS_REPLY = 0x00
STATUS_PRINT_DONE = 0x01
STATUS_ERROR = 0x02
STATUS_PHASE_CH = 0x06

STATUS_TYPE = [
    "Reply to status request",
    "Printing completed",
    "Error occured",
    "IF mode finished",
    "Power off",
    "Notification",
    "Phase change",
]

STATUS_BATTERY = [
    "Full",
    "Half",
    "Low",
    "Change batteries",
    "AC adapter in use"
]

PHASE_RECEIVING = 0x00
PHASE_PRINTING = 0x01

ERROR1_NO_MEDIA = 0x01
ERROR1_END_OF_MEDIA = 0x02
ERROR1_TAPE_CUT_JAM = 0x04

ERROR2_REPLACE_MEDIA = 0x01 # Replace the media.
ERROR2_EXP_BUFFER_FULL = 0x02 # Expansion buffer is full.
ERROR2_TRANS_ERROR = 0x04 # Transmission error
ERROR2_TRANS_BUFF_FULL = 0x08 # Transmission buffer is full.
ERROR2_COVER_OPEN = 0x10 # The cover is open

MODE_PTCBP =1

MEDIA_UNKNOWN = 0x00
MEDIA_LAMINATED = 0x01      # Laminated tape, stamp tape and security tape (tape for sealing)
MEDIA_LETTERING = 0x02      # Instant lettering tape and iron-on transfer tape
MEDIA_NONLAMINATED = 0x03   # Non-laminated tape/rolls and thermal tape
MEDIA_AV_TAPE = 0x08        # AV Tape
MEDIA_HG_TAPE = 0x09        # HG Tape

# TZ tape/HG tape
# Paper Media Width Media Length
# 6 mm 6 0
# 9 mm 9 0
# 12 mm 12 0
# 18 mm 18 0
# 24 mm 24 0
# 36 mm 36 0

# AV tape
# Paper Media Width Media Length
# AV1789 17 89
# AV1957 19 57
# AV2067 20 67

class Status:
    def __init__(self, raw: bytes):

        if len(raw) != 32:
            self.parse_error = "Error: status must be 32 bytes. Got " + str(len(raw))
            return

        header = raw[:8]
        if header != b'\x80\x20B0J0\x00\x00':
            self.parse_error = 'Header mismatch! Got ' + header

        self.error1 = raw[STATUS_OFFSET_ERROR_INFO_1]
        self.error2 = raw[STATUS_OFFSET_ERROR_INFO_2]
        self.battery = raw[STATUS_OFFSET_BATTERY]
        self.media_width = raw[10]
        self.media_type = raw[11]
        self.media_length = raw[17]
        self.status_type = raw[STATUS_OFFSET_STATUS_TYPE]
        self.phase_type = raw[19]
        self.phase_number = raw[20:1]
        self.notif_number = raw[22]

    def error_text(self):
        if self.error1 == ERROR1_NO_MEDIA: return 'No media'
        if self.error1 == ERROR1_END_OF_MEDIA: return 'End of media'
        if self.error1 == ERROR1_TAPE_CUT_JAM: return 'Tape cut jam'

        if self.error2 == ERROR2_REPLACE_MEDIA: return 'Replace the media.'
        if self.error2 == ERROR2_EXP_BUFFER_FULL: return 'Expansion buffer is full'
        if self.error2 == ERROR2_TRANS_ERROR: return 'Transmission error'
        if self.error2 == ERROR2_TRANS_BUFF_FULL: return 'Transmission buffer is full'
        if self.error2 == ERROR2_COVER_OPEN: return 'The cover is open'

        return 'Unknown error (E1: 0x{0} E2: 0x{1})'.format(hex(self.error1), hex(self.error2))

    def __str__(self):
        if self.status_type == STATUS_ERROR:
            return 'Status: {0}, Error: '.format(STATUS_TYPE[self.status_type], self.error_text())
        else:
            return 'Status: {0}'.format(STATUS_TYPE[self.status_type])

class LabelMaker:
    log = lambda s: s

    def __init__(self, logger, serial_device):
        self.log = logger
        self.log('Opening serial device connection...')
        self.ser = serial.Serial(
            serial_device,
            baudrate=9600,
            stopbits=serial.STOPBITS_ONE,
            parity=serial.PARITY_NONE,
            bytesize=8,
            timeout=10,
            write_timeout=10,
            dsrdtr=True
        )

    @classmethod
    def list_serial_ports(cls):
        plat = sys.platform.lower()
        if os.name == 'posix' and plat[:6] == 'darwin':
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
            return list_comports()

    def query_status(self):
        self.log("Query status...")
        self.ser.write(b"\x1b\x69\x53")
        raw = self.ser.read(size=32)
        status = Status(raw)


    def print_status(self, raw: bytes):

        if raw[STATUS_OFFSET_STATUS_TYPE] < len(STATUS_TYPE):
            self.log("Status: " + STATUS_TYPE[raw[STATUS_OFFSET_STATUS_TYPE]])
        else:
            self.log("Status: " + hex(raw[STATUS_OFFSET_STATUS_TYPE]))

        if raw[STATUS_OFFSET_BATTERY] < len(STATUS_BATTERY):
            self.log("Battery: " + STATUS_BATTERY[raw[STATUS_OFFSET_BATTERY]])
        else:
            self.log("Battery: " + hex(raw[STATUS_OFFSET_BATTERY]))


        self.log("Extended error: " + hex(raw[STATUS_OFFSET_EXTENDED_ERROR]))
        self.log('')

    # The print buffer is cleared, and the arrangement position is returned to the origin on the page.
    def inititialize(self):
        self.log("Initialize...")
        self.ser.write(b"\x1b\x40")

    def set_graphics_mode(self, graphics_mode=MODE_PTCBP):
        self.log("Entering raster graphics (PTCBP) mode...")
        self.ser.write(bytes([0x1b, 0x69, 0x61, graphics_mode]))

    def set_modes(self, mirror_printing=False, auto_tape_cut=False):
        mode = 0
        if mirror_printing:
            mode |= (1 << 7)
        if auto_tape_cut:
            mode |= (1 << 6)
        self.log("Setting mode flags MirrorPrinting: {0} AutoTapeCut: {1}...".format(mirror_printing, auto_tape_cut))
        self.ser.write(b"\x1b\x69\x4d" + bytes(mode))

    def set_media_format(self, line_count, fast=False, continuous=True, width=0x0c, length=0):
        # Found docs on http://www.undocprint.org/formats/page_description_languages/brother_p-touch
        self.log("Setting media format...")
        self.ser.write(b"\x1B\x69\x7A")  # Set media & quality

        # 1, bit 6: Print quality: 0=fast, 1=high
        if fast:
            self.ser.write(bytes([0x00]))
        else:
            self.ser.write(bytes([0xC4]))

        # 2, bit 0: Media type: 0=continuous roll, 1=pre-cut labels
        if continuous:
            self.ser.write(bytes([0x00]))
            length = 0
        else:
            self.ser.write(bytes([0x01]))

        # 3: Tape width in mm
        self.ser.write(bytes([width]))

        # 4: Label height in mm (0 for continuous roll)
        self.ser.write(bytes([length]))

        # 5 #6: Page consists of N=#5+256*#6 pixel lines
        self.log('Setting raster lines: ' + str(line_count))
        self.ser.write(line_count.to_bytes(2, 'little'))

        # Unused data bytes in the "set media and quality" command
        self.ser.write(b"\x00\x00\x00\x00")

    def set_print_chaining(self, enabled=False):
        b = 0
        if enabled:
            b = 0x8

        # Set print chaining off (0x8) or on (0x0)
        self.ser.write(bytes([0x1B, 0x69, 0x4B, b]))

    # Set margin amount (feed amount)
    def set_margin(self, margin=0):
        self.ser.write(bytes([ 0x1b, 0x69, 0x64, margin & 0xff, (margin >> 8)&0xff]))

    # Set expanded mode
    def set_expanded_mode(self, half_cut=False, chain_print=False, label_end_cut=False, high_res_print=False, clear_buf=True):
        mode = 0

        # Bit 2 Half cut (multiple half cut)
        #  Half cut is effective only with laminated tape.
        if half_cut:
            mode |= (1 << 2)

        # Bit 3 No chain printing (inverted)
        # When printing multiple copies, the labels are fed after the last one is printed.
        # ON: No chain printing (feeding and cutting the last label); default
        # OFF:Chain printing (no feeding and cutting of the last label)
        if not chain_print:
            mode |= (1 << 3)

        # Bit 5 Label end cut
        # When printing multiple copies, the end of the last label is cut.
        # ON: Cutting the end of the label
        # OFF:No cutting the end of the label
        if label_end_cut:
            mode |= (1 << 5)

        # Bit 6 High-resolution printing
        # ON: High-resolution printing (360 dpi × 720 dpi)
        # OFF:Normal printing (360 dpi × 360 dpi)
        if high_res_print:
            mode |= (1 << 6)

        # Bit7 No buffer clearing when printing (inverted)
        # Copy printing function
        # The expansion buffer of the P-touch is not cleared with the “no buffer clearing when printing” command. If this
        # command is sent when the data of the first label is printed (it is specified between the “initialize” command
        # and the print data), printing is possible only if a print command is sent with the second or later label. However,
        # this is possible only when printing extremely small labels.
        if not clear_buf:
            mode |= (1 << 7)

        self.ser.write(bytes([0x1B, 0x69, 0x4B, mode]))

    def print_label(self, data):
        ser = self.ser

        print('Input:', ser.in_waiting)
        print('Output:', ser.out_waiting)
        ser.reset_input_buffer()

        self.log('Using serial device: ' + ser.name)

        self.set_graphics_mode()

        self.inititialize();

        status = self.query_status()
        self.print_status(status)

        self.log("Flushing print buffer...")
        for i in range(64):
            ser.write(b"\x00")

        self.inititialize()

        self.set_graphics_mode(MODE_PTCBP)

        self.set_media_format(int(len(data) / 16), width=0xc0, length=0)

        self.set_expanded_mode(chain_print=False)

        # Set no mirror, no auto tape cut
        self.set_modes(False, False)

        self.set_margin()

        # Set compression mode: TIFF
        ser.write(b"\x4D\x02")

        # Send image data
        self.log("Sending image data")
        ser.write(encode_raster_transfer(data))
        self.log("Done")

        # Print and feed
        ser.write(b"\x1A")

        # Dump status that the printer returns
        self.print_status(ser.read(size=32))

        # Initialize
        ser.write(b"\x1b\x40")

        ser.close()


if __name__ == '__main__':
    # Check for input image
    if len(sys.argv) < 2:
        print("Usage:", sys.argv[0], "<path-to-image>")
        sys.exit(1)

    print('Labelmaker CLI')

    # Read input image into memory
    data = read_png(sys.argv[1])

    label_maker = LabelMaker(lambda s: print(s))
    label_maker.print_label(data)
