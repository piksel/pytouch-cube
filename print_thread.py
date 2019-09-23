from PyQt5.QtCore import QThread, pyqtSignal

from labelmaker import LabelMaker, BUFFER_HEIGHT, PRINT_MARGIN


class PrintThread(QThread):
    done = pyqtSignal('PyQt_PyObject')
    log = pyqtSignal('PyQt_PyObject')

    def __init__(self, print_image, print_device):
        QThread.__init__(self)
        self.print_image = print_image
        self.print_device = print_device

    # run method gets called when we start the thread
    def run(self):
        try:
            buf = bytearray()

            self.log.emit('Building bit map from image...')

            # State for bit packing
            bit_cursor = 8
            byte = 0
            for x in range(0, self.print_image.width()):
                for y in range(0, BUFFER_HEIGHT):
                    if y < PRINT_MARGIN or y >= (BUFFER_HEIGHT - PRINT_MARGIN):
                        pixel = 0xffffffff
                    else:
                        pixel = self.print_image.pixel(x, y - PRINT_MARGIN)

                    bit_cursor -= 1

                    if pixel <= 0xff000000:
                        # print('#', end='')
                        byte |= (1 << bit_cursor)
                    else:
                        pass
                        # print(' ', end='')

                    if bit_cursor == 0:
                        # packed = unsigned_char.pack(byte)
                        buf.append(byte)
                        byte = 0
                        bit_cursor = 8

                # print()
            self.log.emit('Printing label, width: {0} height: {1}'.format(self.print_image.width(), self.print_image.height()))

            lm = LabelMaker(lambda s: self.log.emit(s), self.print_device)
            print('wat2')
            lm.print_label(buf)
            print('wat3')
            self.done.emit(None)
        except Exception as x:
            self.done.emit(x)

        print('wat4')