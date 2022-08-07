from enum import Enum, auto
from typing import *

Color = Tuple[int, int, int]

class ItemType(Enum):
    Image = auto()
    Text = auto()
    Barcode = auto()