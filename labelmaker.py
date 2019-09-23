#!/usr/bin/env python

from labelmaker_encode import encode_raster_transfer, read_png, unsigned_char

import binascii
import packbits
import serial
import sys
import time

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

    def print_status(self, raw: bytes):
        n = 0
        for byte in raw:
            #if byte != 0xffffffff:
            #    print(hex(n), hex(byte))
            #n += 1
            pass
        if len(raw) != 32:
            self.log("Error: status must be 32 bytes. Got " + str(len(raw)))
            return

        if raw[STATUS_OFFSET_STATUS_TYPE] < len(STATUS_TYPE):
            self.log("Status: " + STATUS_TYPE[raw[STATUS_OFFSET_STATUS_TYPE]])
        else:
            self.log("Status: " + hex(raw[STATUS_OFFSET_STATUS_TYPE]))

        if raw[STATUS_OFFSET_BATTERY] < len(STATUS_BATTERY):
            self.log("Battery: " + STATUS_BATTERY[raw[STATUS_OFFSET_BATTERY]])
        else:
            self.log("Battery: " + hex(raw[STATUS_OFFSET_BATTERY]))

        self.log("Error info 1: " + hex(raw[STATUS_OFFSET_ERROR_INFO_1]))
        self.log("Error info 2: " + hex(raw[STATUS_OFFSET_ERROR_INFO_2]))
        self.log("Extended error: " + hex(raw[STATUS_OFFSET_EXTENDED_ERROR]))
        self.log('')

    def print_label(self, data):
        ser = self.ser

        print('Input:', ser.in_waiting)
        print('Output:', ser.out_waiting)
        ser.reset_input_buffer()

        self.log('Using serial device: ' + ser.name)

        self.log("Entering raster graphics (PTCBP) mode...")
        ser.write(b"\x1b\x69\x61\x01")

        self.log("Initialize...")
        ser.write(b"\x1b\x40")

        self.log("Query status...")
        ser.write(b"\x1b\x69\x53")
        status = ser.read(size=32)
        self.print_status(status)

        self.log("Flushing print buffer...")
        for i in range(64):
            ser.write(b"\x00")

        self.log("Initialize...")
        ser.write(b"\x1b\x40")

        self.log("Entering raster graphics (PTCBP) mode...")
        ser.write(b"\x1b\x69\x61\x01")

        # Found docs on http://www.undocprint.org/formats/page_description_languages/brother_p-touch
        self.log("Setting media format...")
        ser.write(b"\x1B\x69\x7A") # Set media & quality
        ser.write(b"\xC4\x01") # print quality, continuous roll
        ser.write(b"\x0C") # Tape width in mm
        ser.write(b"\x00") # Label height in mm (0 for continuous roll)

        # Number of raster lines in image data
        raster_lines = int(len(data) / 16)
        raster_lines_bytes = raster_lines.to_bytes(2, 'little')
        self.log('Setting raster lines: ' + str(raster_lines) + ' => ' + str(raster_lines_bytes))
        ser.write(raster_lines_bytes)
        # ser.write( bytes( int(raster_lines / 256) ) )

        # Unused data bytes in the "set media and quality" command
        ser.write(b"\x00\x00\x00\x00")

        # Set print chaining off (0x8) or on (0x0)
        ser.write(b"\x1B\x69\x4B\x08")

        # Set no mirror, no auto tape cut
        ser.write(b"\x1B\x69\x4D\x00")

        # Set margin amount (feed amount)
        ser.write(b"\x1B\x69\x64\x00\x00")

        # Set compression mode: TIFF
        ser.write(b"\x4D\x02")

        # Send image data
        self.log("Sending image data")
        ser.write( encode_raster_transfer(data) )
        self.log("Done")

        # Print and feed
        ser.write(b"\x1A")

        # Dump status that the printer returns
        self.print_status( ser.read(size=32) )

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