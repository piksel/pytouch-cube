from argparse import Namespace
from typing import List, Tuple, Any, Optional
import logging

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QImage, QFont, QFontMetrics

from .arguments import dataclass_from_args
from printables.printable import Printable
import comms
from labelmaker.config import LabelMakerConfig
from gui.editor_window import EditorWindow
from gui.print_thread import PrintThread

from margins import Margins
from printables.printable import Printable
from printables.text import TextData, Text, TextPropsEdit
from printables.qrcode import QrCode, QrCodeData
from printables.spacing import Spacing, SpacingData
from printables.barcode import Barcode, BarcodeData
from printables.image import Image, ImageData

class CliPrint:
    def __init__(self, device: str, device_type: str):
        self.device_name = device
        self.device_type = device_type
        self.app = QApplication([])
        self.editor = EditorWindow(self.app)
        self.label_config = None
        self.output = None
        self.ignore_printer = False

        logging.root.addHandler(logging.StreamHandler())
        logging.root.setLevel(logging.INFO)

    def get_device(self) -> comms.PrinterDevice | None:
        dev = None
        if self.device_name == "auto":
            dev = comms.find_default_device()
        else:
            dev = comms.find_device(self.device_type, self.device_name)
        return dev

    def set_label_maker_config(self, config: LabelMakerConfig):
        self.label_config = config

    def add_printable(self, printable: Printable):
        self.editor.sources.add_item(printable)

    def print(self):
        self.editor.update_preview()

        assert self.editor.print_image is not None, "Unable to generate printable image"
       
        if not self.ignore_printer:
            device = self.get_device()
            assert device is not None, f"Could not find device '{self.device_name}'"

            thread = PrintThread(
                QImage(self.editor.print_image), device, 
                self.label_config)
            thread.run()
        if self.output is not None:
            self.editor.print_image.save(self.output)

    def set_output_only(self, output: Optional[str]):
        self.output = output
        self.ignore_printer = output is not None

    def open_file(self, file: str):
        self.editor.current_file = file
        self.editor.open()

    @staticmethod
    def _calculate_text_properties(font_name):
        """Method to calculate text properties so that the text is fully visible
        This means that the text is center vertically in accordance to the cap height"""

        font = QFont(font_name)
        font_size = 68

        adjusted_font_size = TextPropsEdit.calc_adjusted_size_for_font(font, font_size)
        font.setPixelSize(adjusted_font_size)

        # calculate top margin
        font_metric = QFontMetrics(font)
        # as text is rendered so that the heighest position the font can reach
        # is visible (ascent), we need to remove the space between that and 
        # the heighest position a normal capital letter would reach. (capHeight)
        top_margin = font_metric.capHeight() - font_metric.ascent()

        # without this line the font is glued to the top of all capitals
        # so now we can calculate the margin that would center the capHeight
        top_margin += (68 - font_metric.capHeight()) // 2
    
        return font, top_margin

    def printables_from_args(self, cli_args: Namespace):
        printable_args: List[Tuple[str, Any]] = cli_args.ordered_printables
        font = cli_args.default_font

        for (name, args) in printable_args:
            tmp = None
            match name:
                case "text":
                    font, vert_margin = self._calculate_text_properties(font)
                    margin = Margins(vert=vert_margin)
                    tmp = Text(TextData(args, font.toString(), margin))
                case "qr_code":
                    tmp = QrCode(QrCodeData(args))
                case "spacing":
                    tmp = Spacing(SpacingData(args))
                case name if "barcode" in name:
                    has_label = "label" in name
                    text, code_type = args
                    tmp = Barcode(BarcodeData(None, text, code_type, has_label))
                case "image":
                    image_source, threshold = args
                    tmp = Image(ImageData(image_source, int(threshold)))

            assert tmp != None
            self.add_printable(tmp)
            

    @classmethod
    def create(cls, args: Namespace) -> 'CliPrint':
        cli = cls(args.device, args.device_type)

        config = dataclass_from_args(args, LabelMakerConfig)
        cli.set_label_maker_config(config)
        cli.set_output_only(args.output)

        match args.print_mode:
            case "label":
                cli.printables_from_args(args)
            case "file":
                cli.open_file(args.label_file_name)
            case _:
                raise NotImplementedError(f"{args.print_mode}")

        return cli

    @classmethod
    def run(cls, args: Namespace):
        cli = cls.create(args)
        cli.print()

