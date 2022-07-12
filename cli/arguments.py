from argparse import ArgumentParser, _ArgumentGroup as ArgumentGroup
import argparse
from typing import List, Tuple
import re
from dataclasses import fields, MISSING


from labelmaker.config import LabelMakerConfig


class OrderArguments(argparse.Action):
    def __call__(self, _parser, namespace, values, _option_string=None):
        if not 'ordered_printables' in namespace:
            setattr(namespace, 'ordered_printables', [])
        previous = namespace.ordered_printables
        previous.append((self.dest, values))


def tuple_type_factory(types: List, delimiter: str = ":"):
    import csv
    def tuple_parser(text: str) -> Tuple:
        data = next(csv.reader(
            [text], delimiter=delimiter, quotechar='"', 
            doublequote=True,strict=True, escapechar="\\"))
        assert len(types) == len(data), f"{text} (parsed: {data}) doesn't have {len(types)} arguments"
        for i, t in enumerate(types):
            data[i] = t(data[i])
        return tuple(data)
    return tuple_parser


def sanitize_python(name: str) -> str:
    return name.replace("_", "-")


def cli_setup_labelmakerconfig(parser: ArgumentGroup, dataclass):
    for field in fields(dataclass):
        assert field.default_factory == MISSING, f"{field.name} should not use a default factory"

        further_args = {
            "dest": f"{dataclass.__name__}|{field.name}",
            "type": str if type(field.type) != type else field.type,
            "required": field.default == MISSING,
        }

        if field.default != MISSING:

            if field.type == bool:
                further_args["action"] = "store_" + ("true" if not field.default else "false")
                del further_args["type"]
            else:
                further_args["default"] = field.default 

        parser.add_argument(
            f"--{sanitize_python(field.name)}", **further_args)


def get_parser():
    parser = ArgumentParser(description="Utility to print to the Brother P-Touch Cube system")
    runtime = parser.add_subparsers(title="Runtime mode", dest="runtime", required=False)
    runtime.default = "gui"
    gui = runtime.add_parser("gui", help="Use the utlity in GUI mode")
    cli = runtime.add_parser("print", help="Print using suplied arguments")

    ## configure gui parser
    gui.add_argument("--seed", help="Setup the GUI with example printables", action="store_true")
    
    ## configure cli
    ### setup possible configuration parameters
    config = cli.add_argument_group('config')
    cli_setup_labelmakerconfig(config, LabelMakerConfig)
    config.add_argument("--default-font", type=str, default="auto")
    config.add_argument("--device", type=str, default="auto")
    config.add_argument("--output", type=str, help="don't print just write the output to a png")

    ### define the print modes
    print_modes = cli.add_subparsers(title="Print mode", dest="print_mode", required=True)
    label = print_modes.add_parser(
        "label", help="Configure printables. Order is preserved", 
        argument_default=argparse.SUPPRESS)
    label_file = print_modes.add_parser(
        "file", help="Open predefined label file that was generate from the UI")

    ### the printables arguments
    label.add_argument(
        "-t", "--text", help="Text to write. Font is taken from --default-font",
        type=str, action=OrderArguments)
    label.add_argument(
        "-q", "--qr-code", help="Argument is the qr-code data",
        type=str, action=OrderArguments)
    label.add_argument(
        "-s", "--spacing", help="Adds spacing. Argument should be int",
        type=int, action=OrderArguments)
    label.add_argument(
        "-b", "--barcode", help="Add barcode delimited with ':' in the format DATA:BARCODE_TYPE"
        type=tuple_type_factory([str,str]), action=OrderArguments)
    label.add_argument(
        "-l", "--labeled-barcode", help="Add barcode with label. See --barcode",
        type=tuple_type_factory([str,str]), action=OrderArguments)
    label.add_argument(
        "-i", "--image", help="Adds an image with format IMAGE_PATH:THRESHOLD. Where threshold is an int",
        type=tuple_type_factory([str, int]), action=OrderArguments)

    ## add argument for label file
    label_file.add_argument(
        "label_file_name", help="File path to label project file",
        type=str)


    return parser


##############
## Parsers  ##
##############

def dataclass_from_args(args: argparse.Namespace, dataclass):
    dc_args = {
        s[1]: getattr(args, k) for k in dir(args) 
        if (s := k.split("|"))[0] == dataclass.__name__
    }

    return dataclass(**dc_args)

