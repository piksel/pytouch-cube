from sys import argv

from PyQt5.QtWidgets import QApplication
from qasync import QEventLoop

from gui import PyTouchCubeGUI

if __name__ == '__main__':
    PyTouchCubeGUI(QApplication([])).run(seed='--seed' in argv)