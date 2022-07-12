import logging
from typing import Optional

from PyQt5.QtCore import pyqtSignal, pyqtBoundSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QTextEdit, QVBoxLayout, QWidget, QDialog, QPushButton


class LogConsole(QTextEdit):
    log_signal = pyqtSignal(str)

    def __init__(self, parent: Optional[QWidget]):
        super().__init__(parent)
        self.setReadOnly(True)
        font = QFont('Fira')
        font.setStyleHint(QFont.Monospace, QFont.PreferDefault)
        if hasattr(font, 'setFamilies'):
            font.setFamilies(['Fira', 'Source Code Pro', 'Monaco', 'Consolas', 'Monospaced', 'Courier'])
        self.setFont(font)

        self.log_signal.connect(self.print_message)
        
        logging.root.addHandler(LogConsoleHandler(self.log_signal))
        logging.root.setLevel(logging.INFO)

    def print_message(self, message: str):
        self.textCursor().insertText(message + "\n")
        self.ensureCursorVisible()

    # def fmt_log(message):
    #     now = datetime.datetime.now()
    #     return '{0} {1}'.format(now.isoformat(), message)


class LogConsoleModal(QDialog):

    def __init__(self, parent: Optional[QWidget]):
        super().__init__(parent)
        modal_layout = QVBoxLayout(self)
        log_console = LogConsole(self)
        modal_layout.addWidget(log_console)

        self.setLayout(modal_layout)
        self.setFixedWidth(int(parent.width() * .9))
        self.setFixedHeight(int(parent.height() * .9))

        close = QPushButton('close')
        close.setDisabled(True)
        close.clicked.connect(self.on_close)
        modal_layout.addWidget(close)

        self.log_console = log_console
        self.close_button = close

    def enable_close(self):
        self.close_button.setDisabled(False)

    def log_message(self, message: str):
        self.log_console.log_signal.emit(message)

    def on_close(self):
        self.close()


class LogConsoleHandler(logging.Handler):
    def __init__(self, log_handler: pyqtBoundSignal):
        super(LogConsoleHandler, self).__init__()
        self.log_handler = log_handler

    def emit(self, record: logging.LogRecord):
        self.log_handler.emit(record.getMessage())
