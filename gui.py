#!/usr/bin/env python3
import os
from enum import Enum, auto

from PyQt5.QtCore import Qt, pyqtSignal, QDir, QModelIndex, QSortFilterProxyModel
from PyQt5.QtGui import QPixmap, QImage, QStandardItemModel, QPainter, QColor, QDragEnterEvent, QDropEvent, \
    QStandardItem
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QHBoxLayout, \
    QTreeView, QGroupBox, QInputDialog, QMessageBox, QMainWindow, QMenuBar, QAction, QComboBox, QFileSystemModel

from printables.barcode import BarcodeData, Barcode
from printables.image import ImageData, Image
from printables.printable import Printable
from printables.text import TextData, Text

APP_NAME = 'PyTouch Cube Editor'
APP_VERSION = 'v0.1'

class ModelCol(Enum):
    TYPE = 0
    DATA = 1


class ItemType(Enum):
    IMAGE = auto()
    TEXT = auto()
    BARCODE = auto()

    __names__ = {
        IMAGE: 'Image',
        TEXT: 'Text',
        BARCODE: 'Barcode',
    }

    def name(self):
        return ItemType.__names__[self.value]


class ItemView(QTreeView):

    rowMoved = pyqtSignal(int, int, name='rowMoved')

    def itemFromIndex(self, index):
        return self.model().data(index)

    def dragEnterEvent(self, e: QDragEnterEvent) -> None:
        self.draggedItem = self.indexAt(e.pos())
        e.setDropAction(Qt.MoveAction)
        super().dragEnterEvent(e)

    def dropEvent(self, e: QDropEvent) -> None:
        dropped_index = self.indexAt(e.pos())
        if not dropped_index.isValid():
            return

        old_row = self.draggedItem.row()

        model: QStandardItemModel = self.model()
        item = model.takeRow(old_row)

        new_row = dropped_index.row()
        model.insertRow(new_row, item)

        self.setCurrentIndex(model.indexFromItem(item[0]))

        self.rowMoved.emit(old_row, new_row)

def make_props_empty(parent):
    widget = QLabel('No item selected', parent)
    widget.setMinimumWidth(128)
    return widget


class PyTouchCubeGUI(QMainWindow):

    item_selected = None
    props_current = None

    def __init__(self, app: QApplication):
        super().__init__()

        self.setWindowTitle(APP_NAME)

        self.app = app
        app.setApplicationName(APP_NAME)
        app.setApplicationDisplayName(APP_NAME)

        self.preview_image = QLabel('No image selected')
        self.preview_image.setFixedHeight(128)

        add_image_button = QPushButton('Add image')
        add_image_button.clicked.connect(self.add_image)

        add_text_button = QPushButton('Add text')
        add_text_button.clicked.connect(self.on_add_text)

        add_barcode_button = QPushButton('Add barcode')
        add_barcode_button.clicked.connect(self.add_barcode)

        self.save_image_button = QPushButton('Save image')
        self.save_image_button.setDisabled(True)

        self.tree_view = ItemView()
        self.items = self.create_model()
        self.item_data = []
        self.tree_view.setRootIsDecorated(False)
        # self.tree_view.setAlternatingRowColors(True)
        self.tree_view.setModel(self.items)
        self.tree_view.clicked.connect(self.tree_view_clicked)
        self.tree_view.rowMoved.connect(self.tree_view_reorder)
        self.tree_view.setDragEnabled(True)
        self.tree_view.setDragDropMode(QTreeView.InternalMove)
        self.tree_view.setItemsExpandable(False)
        self.tree_view.setDragDropOverwriteMode(False)



        root = QVBoxLayout()

        items_layout = QHBoxLayout()

        group = QGroupBox('Source items:')
        layout = QVBoxLayout()
        layout.addWidget(self.tree_view)
        buttons = QHBoxLayout()
        buttons.addWidget(add_image_button)
        buttons.addWidget(add_text_button)
        buttons.addWidget(add_barcode_button)
        layout.addLayout(buttons)
        group.setLayout(layout)
        items_layout.addWidget(group)

        self.property_group = QGroupBox('Item properties:')
        self.props_layout = QVBoxLayout()

        self.property_group.setLayout(self.props_layout)
        self.update_props()

        items_layout.addWidget(self.property_group)

        root.addLayout(items_layout)

        group = QGroupBox('Preview:')
        layout = QVBoxLayout()
        layout.addWidget(self.preview_image)
        layout.addWidget(self.save_image_button)
        group.setLayout(layout)
        root.addWidget(group)

        printer_select = QComboBox(self)
        fs_model = QFileSystemModel(self)
        #model_proxy = QSortFilterProxyModel(self)
        #model_proxy.setSourceModel(fs_model)
        # fs_model.setNameFilters(['tty.PT-P3*'])


        printers = QStandardItemModel()
        for p in QDir('/dev').entryList(['tty*'], QDir.System, QDir.Name):
            printers.appendRow(QStandardItem('/dev/' + p))
        #print(printers.entryList())


        #model_proxy.setRecursiveFilteringEnabled(True)
        #model_proxy.setFilterKeyColumn(0)

        fs_model.setRootPath('/dev/')#/Users/nilsmasen')
        fs_model.setFilter( QDir.System  )
        dev_index = fs_model.index('/dev')
        #proxy_dev = model_proxy.mapFromSource(dev_index)



        printer_select.setModel(printers)
        #printer_select.setRootModelIndex(dev_index)
        #printer_select.setRootIndex(dev_index)
        #printer_select.setExpanded(dev_index, True)
        #model_proxy.setFilterWildcard('tty*')


        bottom_bar = QHBoxLayout()
        #bottom_bar.addStretch()
        bottom_bar.addWidget(printer_select)
        # /dev/tty.PT-P300BT0607-Serial
        bottom_bar.addWidget(QPushButton('Print'))

        root.addLayout(bottom_bar)

        root_widget = QWidget()
        root_widget.setLayout(root)
        self.setCentralWidget(root_widget)
        menu = QMenuBar()
        self.setMenuBar(menu)

        menu.setWindowTitle(APP_NAME)
        tools_menu = menu.addMenu('Python')
        prefs = QAction('&Preferences', self)
        prefs.triggered.connect(self.on_prefs)
        tools_menu.addAction(prefs)
        about = QAction('About ' + APP_NAME, self)
        about.triggered.connect(self.on_prefs)
        about.setMenuRole(QAction.AboutRole)
        tools_menu.addAction(about)

        file_menu = menu.addMenu('Label')
        file_menu.addAction(QAction('&New', self))
        file_menu.addSeparator()
        file_menu.addAction(QAction('&Open', self))
        file_menu.addSeparator()
        file_menu.addAction(QAction('Save &as...', self))
        file_menu.addAction(QAction('&Export image', self))

        # menu.setNativeMenuBar(False)

    def on_prefs(self):
        QMessageBox.information(self,
                                "Info",
                                "{0} {1}\n\nhttps://github.com/piksel/pytouch-cube".format(APP_NAME, APP_VERSION))

    def run(self):

        self.show()
        self.add_item(Text(TextData('Foo')))
        self.add_item(Text(TextData('Bar')))
        self.add_item(Barcode(BarcodeData('123456789012')))
        self.add_item(Barcode(BarcodeData('ACE222', 'code128')))

        self.app.exec_()

    def add_image(self):
        user_home = os.path.expanduser('~')
        open_initial_path = os.path.join(user_home, 'Pictures')
        if not os.path.isdir(open_initial_path):
            open_initial_path = user_home
        image_path, _ = QFileDialog.getOpenFileName(
            directory=open_initial_path,
            caption='Open Image',
            filter='Image Files (*.png *.jpg *.bmp)')

        if len(image_path) > 0:
            data = ImageData(image_path)
            self.add_item(Image(data))

    def on_add_text(self):
        text, etc = QInputDialog.getText(self, 'Add text', 'Enter text:')
        print(text, etc)
        if len(text) < 1:
            return
        self.add_item(Text(TextData(text)))

    def add_barcode(self):
        text, etc = QInputDialog.getText(self, 'Add barcode', 'Enter text:')
        print(text, etc)
        if len(text) < 1:
            return

        self.add_item(Barcode(BarcodeData(text)))

    def tree_view_clicked(self, index):
        self.item_selected = index.row()
        self.update_props()

    def tree_view_reorder(self, old, new):
        item = self.item_data.pop(old)
        self.item_data.insert(new, item)
        self.update_preview()
        print(old, '=>', new)

    def create_model(self):
        model = QStandardItemModel(0, 2, self)
        model.setHeaderData(ModelCol.TYPE.value, Qt.Horizontal, 'Type')
        model.setHeaderData(ModelCol.DATA.value, Qt.Horizontal, 'Data')
        return model

    def add_item(self, item: Printable):
        self.items.appendRow(item.get_list_item())
        self.item_data.append(item)
        self.update_preview()

    def update_preview(self):

        item_renders = []
        width_needed = 0

        for i in range(0, len(self.item_data)):
            render = self.item_data[i].render()
            render_error = self.item_data[i].get_render_error()
            if render_error is not None:
                QMessageBox.warning(self, 'Failed to render item', 'Failed to render item:\n' + str(render_error))
            item_renders.append(render)
            width_needed += render.width()

        x = 0
        image = QImage(width_needed, 128, QImage.Format_Mono)
        image.fill(QColor(255, 255, 255))
        painter = QPainter(image)
        for render in iter(item_renders):
            painter.drawImage(x, 0, render)
            x += render.width()
        painter.end()
        del painter

        self.preview_image.setPixmap(QPixmap.fromImage(image))

    def update_props(self):

        if self.item_selected is None:
            new_widget = make_props_empty(self)
        else:
            item: Printable = self.item_data[self.item_selected]
            new_widget = item.get_props_editor(self)
        if self.props_current is None:
            self.props_layout.addWidget(new_widget)
        else:
            self.props_layout.replaceWidget(self.props_current, new_widget)
            self.props_current.close()
        self.props_current = new_widget


if __name__ == '__main__':
    PyTouchCubeGUI(QApplication([])).run()
