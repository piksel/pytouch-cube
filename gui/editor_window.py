#!/usr/bin/env python3
import asyncio
import logging
import pickle

from PyQt5.QtGui import QPixmap, QImage, QPainter, QColor, QIcon
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QPushButton, QLabel, QFileDialog, QHBoxLayout, \
    QGroupBox, QMessageBox, QMainWindow, QScrollArea, QSizePolicy
from qasync import QEventLoop

from app import APP_NAME, APP_VERSION
from labelmaker import USABLE_HEIGHT
from print_thread import PrintThread
from printables.barcode import BarcodeData, Barcode
from printables.propsedit import PropsEdit
from printables.spacing import Spacing, SpacingData
from printables.text import TextData, Text as TextItem
from settings import Settings
from util import *
from .item_view import ItemView
from .log_console import LogConsoleModal
from .printer_select import PrinterSelect
from .source_items import SourceItems
from .top_menu import TopMenu
from .types import *

log = logging.getLogger(__name__)


def make_props_empty(parent):
    log.debug('Creating empty props view')
    widget = QLabel('No item selected', parent)
    widget.setMinimumWidth(128)
    return widget


class PyTouchCubeGUI(QMainWindow):
    item_selected = None
    props_current = None
    printer_select = None
    save_printable_button = None

    def __init__(self, app: QApplication):
        super().__init__()

        self.print_image = None
        self.current_file = None
        self.current_item = None
        self.print_thread = None

        Settings.load()

        self.setWindowTitle(APP_NAME)
        self.setWindowIcon(QIcon('pytouch3.png'))

        self.app = app

        app.setApplicationName(APP_NAME)
        app.setApplicationDisplayName(APP_NAME)

        self.preview_image = QLabel('No items to preview')
        self.preview_image.setFixedHeight(USABLE_HEIGHT)

        self.props_empty = False

        self.save_image_button = QPushButton('Save image')
        self.save_image_button.setDisabled(True)

        sources = SourceItems(self)
        self.sources = sources

        root = QVBoxLayout()
        items_layout = QHBoxLayout()
        items_layout.addWidget(sources)
        items_layout.setAlignment(Qt.AlignLeft)

        sources.item_selected.connect(self.selected_item_changed)
        sources.items_changed.connect(self.update_preview)

        self.property_group = QGroupBox('Item properties:')
        self.props_layout = QVBoxLayout()

        self.property_group.setLayout(self.props_layout)

        self.props_current = QLabel()
        self.props_layout.addWidget(self.props_current)
        self.save_printable_button = QPushButton('Save Changes')
        self.save_printable_button.clicked.connect(self.save_props)
        self.props_layout.addWidget(self.save_printable_button)
        self.update_props()

        self.property_group.setMaximumWidth(400)
        items_layout.addWidget(self.property_group)

        root.addLayout(items_layout)

        group = QGroupBox('Preview:')
        layout = QVBoxLayout()

        preview_wrapper = QScrollArea(self)

        preview_container = QWidget(self)

        container_layout = QHBoxLayout()
        container_layout.addWidget(self.preview_image)
        preview_container.setLayout(container_layout)
        container_layout.setContentsMargins(0, 0, 0, 0)

        preview_wrapper.setWidget(preview_container)

        # prev_layout = QHBoxLayout()

        preview_container.setContentsMargins(0, 0, 0, 0)
        preview_container.setFixedHeight(USABLE_HEIGHT)
        preview_wrapper.setContentsMargins(0, 0, 0, 0)

        preview_wrapper.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        preview_wrapper.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        preview_wrapper.setWidgetResizable(True)
        layout.addWidget(preview_wrapper)

        # layout.addWidget(self.save_image_button)
        group.setLayout(layout)
        group.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed))

        root.addWidget(group)

        self.printer_select = PrinterSelect(self)

        bottom_box = QGroupBox('Print label: ')
        bottom_bar = QHBoxLayout()
        bottom_bar.addWidget(QLabel('Print device:'))
        bottom_bar.addWidget(self.printer_select)
        bottom_bar.addStretch()
        # /dev/tty.PT-P300BT0607-Serial
        print_button = QPushButton('Print')
        print_button.setFixedWidth(100)
        bottom_bar.addWidget(print_button)
        print_button.clicked.connect(self.print_clicked)

        bottom_box.setLayout(bottom_bar)
        root.addWidget(bottom_box)

        root_widget = QWidget()
        # root_widget.setFixedWidth(800)
        root_widget.setLayout(root)
        self.setCentralWidget(root_widget)
        menu = TopMenu(self)
        menu.about.triggered.connect(self.on_about)
        menu.prefs.triggered.connect(self.on_prefs)
        menu.label_new.triggered.connect(self.on_new)
        menu.label_open.triggered.connect(self.on_open)
        menu.label_save.triggered.connect(self.on_save)
        menu.label_save_as.triggered.connect(self.on_save_as)
        self.setMenuBar(menu)

        # TODO: Mac top bar?
        # menu.setNativeMenuBar(False)

    async def init_async(self):
        await self.printer_select.update()

    def on_new(self):
        self.item_data = []
        self.items.clear()
        self.update_items()
        self.update_preview()

    def on_about(self):
        QMessageBox.information(self, APP_NAME, f" v{APP_VERSION}\n\nhttps://github.com/piksel/pytouch-cube")

    def on_prefs(self):
        QMessageBox.information(self, "Info", "Not implemented")

    def run(self, seed=False):

        self.show()
        if seed and True:
            self.sources.add_item(TextItem(TextData('foo')))
            self.sources.add_item(TextItem(TextData('Bar1')))
            self.sources.add_item(TextItem(TextData('Bar2')))
            self.sources.add_item(Spacing(SpacingData(10)))
            self.sources.add_item(TextItem(TextData('baz')))
            self.sources.add_item(Barcode(BarcodeData(text='123456789012')))
            self.sources.add_item(Barcode(BarcodeData(text='ACE222', code_type='code128')))

        loop = QEventLoop(self.app)
        asyncio.set_event_loop(loop)

        asyncio.create_task(self.init_async())

        with loop:
            loop.run_forever()

    def on_save(self):
        if self.current_file is None:
            self.on_save_as()
        else:
            self.save()

    def on_save_as(self):
        user_home = os.path.expanduser('~')
        save_initial_path = os.path.join(user_home, 'Documents')
        if not os.path.isdir(save_initial_path):
            save_initial_path = user_home
        file_path, file_format = QFileDialog.getSaveFileName(
            self,
            caption='Save Label',
            directory=save_initial_path,
            filter='Label Files (*.p3label)')

        if len(file_path) <= 0:
            return

        self.current_file = file_path
        self.save()

    def on_open(self):
        user_home = os.path.expanduser('~')
        open_initial_path = os.path.join(user_home, 'Documents')
        if not os.path.isdir(open_initial_path):
            open_initial_path = user_home
        file_path, file_format = QFileDialog.getOpenFileName(
            self,
            caption='Open Label',
            directory=open_initial_path,
            filter='Label Files (*.p3label)')

        if len(file_path) <= 0:
            return

        self.current_file = file_path
        self.open()

    def save(self):
        with open(self.current_file, 'wb') as file:
            pickler = pickle.Pickler(file)
            pickler.dump(self.sources.items.items)

    def open(self):
        with open(self.current_file, 'rb') as file:
            unpickler = pickle.Unpickler(file)
            items = unpickler.load()

            self.sources.items.clear()

            for item in items:
                self.sources.items.add(item)
            self.update_preview()
            self.item_selected = None
            self.update_props()

    def print_clicked(self):

        modal = LogConsoleModal(self)
        modal.show()

        def done(exception: Exception):
            if exception is not None:
                log.error('Failed to print due to the following error:\n' + str(exception))
                print(str(exception))
                # log_console.insertHtml('<pre style="color:red">{0}</pre>'.format(exception))
            else:
                modal.log_message('Printing completed without any errors!\n')
            modal.enable_close()

        log.info('Starting print thread...')
        # modal.log_message(')

        print_device = self.printer_select.currentData()

        # print_device = self.printer_select.currentData(1)
        log.debug(f'Using device: {print_device}')
        self.print_thread = PrintThread(QImage(self.print_image), print_device)
        # self.print_thread.log.connect(log)
        self.print_thread.done.connect(done)

        self.print_thread.start()

    def save_props(self):
        if isinstance(self.props_current, PropsEdit):
            self.props_current.save()

    def update_current_item(self):
        self.sources.update_current_item()

    def update_preview(self):
        item_renders = []
        width_needed = 0

        for item in self.sources.items.items:
            render = item.render()
            render_error = item.get_render_error()
            if render_error is not None:
                QMessageBox.warning(self, 'Failed to render item', 'Failed to render item:\n' + str(render_error))
            item_renders.append(render)
            width_needed += render.width()

        x = 0
        image = QImage(width_needed, USABLE_HEIGHT, QImage.Format_Mono)
        image.fill(QColor(255, 255, 255))
        painter = QPainter(image)
        for render in iter(item_renders):
            painter.drawImage(x, 0, render)
            x += render.width()
        painter.end()
        del painter

        self.print_image = image
        self.preview_image.setPixmap(QPixmap.fromImage(image))
        self.preview_image.repaint()

    def selected_item_changed(self, item: Optional[Printable]):
        self.current_item = item
        self.update_props()

    def update_props(self):

        if self.current_item is None:
            if self.props_empty:
                return
            new_widget = make_props_empty(self)
            if self.save_printable_button is not None:
                self.save_printable_button.setEnabled(False)
            self.props_empty = True
        else:
            new_widget = self.current_item.get_props_editor(self)
            self.save_printable_button.setEnabled(True)

        self.props_layout.replaceWidget(self.props_current, new_widget)
        self.props_current.close()
        self.props_current = new_widget
