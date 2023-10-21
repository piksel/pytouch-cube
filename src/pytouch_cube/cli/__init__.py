import sys, logging

from .arguments import get_parser
from .cli_print import CliPrint
from .cli_gui import CliGui

def run():
    if not sys.gettrace() is None:
        logging.basicConfig(level=logging.DEBUG)

    parser = get_parser()
    args = parser.parse_args()
    match args.runtime:
        case "print":
            CliPrint.run(args)
        case "gui" | "":
            CliGui.run("seed" in args and args.seed)
        case _:
            raise RuntimeError(f"Invalid action {args.runtime}")