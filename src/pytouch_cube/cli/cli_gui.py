import asyncio
import sys
import os.path as path

from PyQt6.QtWidgets import QApplication
from qasync import QEventLoop

from pytouch_cube.gui import EditorWindow
from pytouch_cube.margins import Margins
from pytouch_cube.printables.barcode import BarcodeData, Barcode
from pytouch_cube.printables.spacing import Spacing, SpacingData
from pytouch_cube.printables.text import TextData, Text as TextItem
from pytouch_cube.printables.image import ImageData, Image as ImageItem

class CliGui:
    def run(self, seed=False):
        app = QApplication(sys.argv)
        editor = EditorWindow(app)
        editor.show()

        if seed:
            testdata = path.join(path.dirname(__file__) + '/testdata/')
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