from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QMenuBar, QAction, QWidget

from util import *
from app import *
from typing import *


class TopMenu(QMenuBar):

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        about = QAction('About ' + APP_NAME, self)
        about.setMenuRole(QAction.AboutRole)

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
        file_menu.addAction(QAction('&Export image', self))

        if not is_mac:
            help_menu = self.addMenu('Help')
            help_menu.addAction(about)

        self.about = about
        self.prefs = prefs
        self.label_new = label_new
        self.label_open = label_open
        self.label_save = label_save
        self.label_save_as = label_save_as