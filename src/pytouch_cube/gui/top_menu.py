from PyQt6.QtGui import QKeySequence, QAction
from PyQt6.QtWidgets import QMenuBar, QWidget

from pytouch_cube.util import *
from pytouch_cube import APP_NAME, __version__ as APP_VERSION
from typing import *


class TopMenu(QMenuBar):

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        about = QAction('About ' + APP_NAME, self)
        about.setMenuRole(QAction.MenuRole.AboutRole)

        prefs = QAction('&Preferences', self)

        if is_mac:
            self.setWindowTitle(APP_NAME)
            tools_menu = self.addMenu(APP_NAME)

            tools_menu.addAction(prefs)
            tools_menu.addAction(about)

        file_menu = self.addMenu('Label')
        label_new = QAction('&New', self)

        file_menu.addAction(label_new)
        file_menu.addSeparator()
        label_open = QAction('&Open', self)

        label_open.setShortcut(QKeySequence('Ctrl+O'))
        file_menu.addAction(label_open)
        file_menu.addSeparator()
        label_save = QAction('&Save', self)

        label_save.setShortcut(QKeySequence("Ctrl+S"))
        file_menu.addAction(label_save)
        label_save_as = QAction('Save &as...', self)

        label_save_as.setShortcut(QKeySequence("Ctrl+Shift+S"))
        file_menu.addAction(label_save_as)
        file_menu.addSeparator()
        label_export = QAction('&Export image', self)
        file_menu.addAction(label_export)
        file_menu.addSeparator()
        self.quit = QAction('Exit')
        file_menu.addAction(self.quit)

        if not is_mac:
            help_menu = self.addMenu('Help')
            help_menu.addAction(about)

        self.about = about
        self.prefs = prefs
        self.label_new = label_new
        self.label_open = label_open
        self.label_save = label_save
        self.label_save_as = label_save_as
        self.label_export = label_export
