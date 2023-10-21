#!/usr/bin/env python
import logging
import sys
from typing import Optional

from .encode import encode_raster_transfer, read_png
from .config import LabelMakerConfig
from .comms import PrinterDevice, SerialPrinterDevice
from .format import Mode
from .status import Status
from pytouch_cube.labels import BUFFER_HEIGHT, PRINT_MARGIN, USABLE_HEIGHT

log = logging.getLogger(__name__)


class LabelMaker:

    def log(self, m: str):
        log.info(m)

    def __init__(self, serial_device: PrinterDevice, config: Optional[LabelMakerConfig] = None):
        self.log('Opening serial device connection...')

        self.config = config
        if config is None:
            self.config = LabelMakerConfig()

        self.ser = serial_device.open()

    def set_config(self, config: LabelMakerConfig):
        self.config = config

    def query_status(self):
        self.log("Query status...")
        self.ser.write(b"\x1b\x69\x53")
        raw = self.ser.read(size=32)
        return raw

    def print_status(self, raw: bytes):
        s = Status(raw)
        self.log(str(s))
        self.log(f"Battery: {s.battery}")
        if s.extended_error != 0:
            self.log(f"Extended error: 0x{hex(s.extended_error)}")

    # The print buffer is cleared, and the arrangement position is returned to the origin on the page.
    def initialize(self):
        self.log("Initialize...")
        self.ser.write(b"\x1b\x40")

    def set_graphics_mode(self, graphics_mode=Mode.PTCBP):
        self.log("Entering raster graphics (PTCBP) mode...")
        self.ser.write(bytes([0x1b, 0x69, 0x61, graphics_mode]))

    def set_modes(self, mirror_printing=False, auto_tape_cut=False):
        mode = 0
        if mirror_printing:
            mode |= (1 << 7)
        if auto_tape_cut:
            mode |= (1 << 6)
        self.log(f"Setting mode flags MirrorPrinting: {mirror_printing} AutoTapeCut: {auto_tape_cut}...")
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
        self.ser.write(bytes([0x1b, 0x69, 0x64, margin & 0xff, (margin >> 8) & 0xff]))

    # Set expanded mode
    def set_expanded_mode(self, half_cut=False, chain_print=False,
                          label_end_cut=False, high_res_print=False, clear_buf=True):
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
        # The expansion buffer of the P-touch is not cleared with the “no buffer clearing when printing” command.
        # If this command is sent when the data of the first label is printed (it is specified between the “initialize”
        # command and the print data), printing is possible only if a print command is sent with the second or later
        # label. However, this is possible only when printing extremely small labels.
        if not clear_buf:
            mode |= (1 << 7)

        self.ser.write(bytes([0x1B, 0x69, 0x4B, mode]))

    def print_label(self, data: bytearray):
        ser = self.ser

        print('Input:', ser.in_waiting)
        print('Output:', ser.out_waiting)
        ser.reset_input_buffer()

        self.log('Using serial device: ' + ser.name)

        self.set_graphics_mode()

        self.initialize()

        status_raw = self.query_status()
        self.print_status(status_raw)

        self.log("Flushing print buffer...")
        for i in range(64):
            ser.write(b"\x00")

        self.initialize()

        self.set_graphics_mode(Mode.PTCBP)

        self.set_media_format(int(len(data) / 16), width=0xc0, length=0)

        self.config.apply(self.set_expanded_mode)

        # Set no mirror, no auto tape cut
        self.config.apply(self.set_modes)

        self.config.apply(self.set_margin)

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
    image_data = read_png(sys.argv[1])
    device = sys.argv[2]

    label_maker = LabelMaker(SerialPrinterDevice.find(device))
    label_maker.print_label(image_data)
