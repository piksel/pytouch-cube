from typing import Dict, Tuple, List

BUFFER_HEIGHT = 128
PRINT_MARGIN = 30
USABLE_HEIGHT = BUFFER_HEIGHT - (PRINT_MARGIN * 2)

from ._types import Color

labels = [
    ("TZe-S631", "Black", "Yellow"),
    ("TZe-S221", "Black", "White"),
    ("TZe-S211", "Black", "White"),
    ("TZe-S131", "Black", "Clear"),
    ("TZe-N201", "Black", "White"),
    ("TZe-MQP35", "White", "Berry Pink"),
    ("TZe-MQG35", "White", "Lime Green"),
    ("TZe-MQF31", "Black", "Pastel Purple"),
    ("TZe-MQE31", "Black", "Pastel Pink"),
    ("TZe-MQ934", "Gold", "Satin Silver"),
    ("TZe-MQ835", "White", "Satin Gold"),
    ("TZe-MQ531", "Black", "Pastel Blue"),
    ("TZe-FX631", "Black", "Yellow"),
    ("TZe-FA3", "Navy Blue", "White Fabric"),
    ("TZe-AF231", "Black", "White"),
    ("TZe-AF131", "Black", "Clear"),
    ("TZe-631", "Black", "Yellow"),
    ("TZe-421", "Black", "Red"),
    ("TZe-335", "White", "Black"),
    ("TZe-334", "Gold", "Black"),
    ("TZe-325", "White", "Black"),
    ("TZe-315", "White", "Black"),
    ("TZe-232", "Red", "White"),
    ("TZe-2312PK", "Black", "White"),
    ("TZe-231", "Black", "White"),
    ("TZe-221", "Black", "White"),
    ("TZe-211", "Black", "White"),
    ("TZe-135", "White", "Clear"),
    ("TZe-1312PK", "Black", "Clear"),
    ("TZe-131", "Black", "Clear"),
    ("TZe-121", "Black", "Clear"),
    ("TZe-111", "Black", "Clear"),
    ("TZe-M31", "Black", "Clear"),
    ("TZe-ML35", "White", "Gray"),
    ("TZe-PR234", "Gold", "White"),
    ("TZe-PR831", "Black", "Glitter Gold"),
    ("TZe-PR935", "White", "Glitter Silver"),
    ("TZe-S621", "Black", "Yellow"),
    ("TZe-S231", "Black", "White"),
    ("TZe-S135", "White", "Clear"),
    ("TZe-S121", "Black", "Clear"),
    ("TZe-FX231", "Black", "White"),
]

colors: Dict[str, Color] = {
    'Black': (0, 0, 0),
    'Clear': (128, 128, 128),
    'Gray': (128, 128, 128),
    'Red': (255, 0, 0),
    'Yellow': (255, 255, 0),
    'White': (255, 255, 255),
    'Gold': (200, 180, 128),
    'Berry Pink': (221, 91, 151),
    'Lime Green': (185, 209, 89),
    'Pastel Purple': (199, 179, 214),
    'Pastel Pink': (229, 200, 222),
    'Satin Silver': (187, 187, 187),
    'Satin Gold': (230, 201, 73),
    'Pastel Blue': (196, 212, 235),
    'Navy Blue': (23, 29, 75),
    'White Fabric': (240, 240, 240),
    'Glitter Silver': (187, 187, 187),
    'Glitter Gold': (230, 201, 73),
}

tapes: List[Tuple[str, Color, Color]] = [(f'{sku}, {fg} on {bg}', colors[fg], colors[bg]) for sku, fg, bg in labels]
