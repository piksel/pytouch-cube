import asyncio
import logging
import sys
import os.path as path
from sys import argv

from PyQt6.QtWidgets import QApplication
from qasync import QEventLoop

from gui import EditorWindow
from margins import Margins
from printables.barcode import BarcodeData, Barcode
from printables.spacing import Spacing, SpacingData
from printables.text import TextData, Text as TextItem
from printables.image import ImageData, Image as ImageItem

testdata = path.join(path.dirname(__file__) + '/testdata/')

if not sys.gettrace() is None:
    logging.basicConfig(level=logging.DEBUG

                        )


def run(seed=False):
    app = QApplication(sys.argv)
    editor = EditorWindow(app)
    editor.show()

    if seed:
        editor.sources.add_item(TextItem(TextData('foo')))
        editor.sources.add_item(TextItem(TextData('Bar1')))
        # editor.sources.add_item(TextItem(TextData('Bar2')))
        # editor.sources.add_item(Spacing(SpacingData(10)))
        # editor.sources.add_item(TextItem(TextData('baz')))
        # editor.sources.add_item(Barcode(BarcodeData(text='123456789012')))
        # editor.sources.add_item(Barcode(BarcodeData(text='ACE222', code_type='code128')))
        editor.sources.add_item(ImageItem(ImageData(image_source=path.join(testdata, 'whodat3.png'),
                                                    margins=Margins(vert=0,
                                                                    left=15,
                                                                    right=15,
                                                                    scale=1))))

    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    asyncio.create_task(editor.init_async())

    with loop:
        loop.run_forever()


if __name__ == '__main__':
    run(seed='--seed' in argv)
