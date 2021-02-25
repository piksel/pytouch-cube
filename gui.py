#!/usr/bin/env python3
import datetime
import os
import pickle
from enum import Enum, auto
from pprint import pprint

from PyQt5.QtCore import Qt, pyqtSignal, QDir, QModelIndex, QSortFilterProxyModel
from PyQt5.QtGui import QPixmap, QImage, QStandardItemModel, QPainter, QColor, QDragEnterEvent, QDropEvent, \
    QStandardItem, QFont, QKeySequence, QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QHBoxLayout, \
    QTreeView, QGroupBox, QInputDialog, QMessageBox, QMainWindow, QMenuBar, QAction, QComboBox, QFileSystemModel, QMenu, \
    QButtonGroup, QDialog, QTextEdit, QScrollArea, QBoxLayout, QSizePolicy

from app import APP_NAME, APP_VERSION
from labelmaker import LabelMaker, USABLE_HEIGHT, PRINT_MARGIN, BUFFER_HEIGHT
from labelmaker_encode import unsigned_char
from print_thread import PrintThread
from printables.barcode import BarcodeData, Barcode
from printables.image import ImageData, Image
from printables.printable import Printable, PrintableData
from printables.propsedit import PropsEdit
from printables.qrcode import QrCode
from printables.spacing import Spacing, SpacingData
from printables.text import TextData, Text
from settings import Settings

if os.name == 'nt':
    is_win = True
    is_linux = False
    is_mac = False
else:
    import sys
    is_win = False
    plat = sys.platform.lower()
    is_mac = plat[:6] == 'darwin'
    is_linux = not is_mac


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
    print('####################### CREATING EMPTY ######################')
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

        add_menu = QMenu()
        add_menu.addAction(Text.get_add_add_action(self))
        add_menu.addAction(Image.get_add_add_action(self))
        add_menu.addAction(Barcode.get_add_add_action(self))
        add_menu.addAction(QrCode.get_add_add_action(self))

        add_menu.addSeparator()
        add_menu.addAction(Spacing.get_add_add_action(self))

        add_button = QPushButton('Add')
        add_button.setMenu(add_menu)
        buttons.addWidget(add_button)

        # buttons.addWidget(add_text_button)
        # buttons.addWidget(add_barcode_button)
        buttons.addStretch()
        buttons.setSpacing(1)

        b_down = QPushButton('⬇︎')
        b_down.clicked.connect(lambda _: self.move_item(1))
        b_up = QPushButton('⬆︎')
        b_up.clicked.connect(lambda _: self.move_item(-1))
        b_delete = QPushButton('Delete')
        b_delete.clicked.connect(self.delete_item)

        b_clone = QPushButton('Copy')
        b_clone.clicked.connect(self.on_clone)

        buttons.addWidget(b_clone)
        buttons.addSpacing(10)
        buttons.addWidget(b_up)
        buttons.addWidget(b_down)
        buttons.addSpacing(10)
        buttons.addWidget(b_delete)

        layout.addLayout(buttons)
        group.setLayout(layout)
        items_layout.addWidget(group)

        self.property_group = QGroupBox('Item properties:')
        self.props_layout = QVBoxLayout()

        self.property_group.setLayout(self.props_layout)

        self.props_current = QLabel()
        self.props_layout.addWidget(self.props_current)
        self.save_printable_button = QPushButton('Save Changes')
        self.save_printable_button.clicked.connect(self.save_props)
        self.props_layout.addWidget(self.save_printable_button)
        self.update_props()

        items_layout.addWidget(self.property_group)

        root.addLayout(items_layout)

        group = QGroupBox('Preview:')
        layout = QVBoxLayout()

        preview_wrapper = QScrollArea(self)

        # prev_layout = QHBoxLayout()
        preview_wrapper.setWidget(self.preview_image)
        preview_wrapper.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        preview_wrapper.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        preview_wrapper.setWidgetResizable(True)
        preview_wrapper.setFixedHeight(USABLE_HEIGHT)
        layout.addWidget(preview_wrapper)

        # layout.addWidget(self.save_image_button)
        group.setLayout(layout)
        group.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed))

        root.addWidget(group)

        self.printer_select = QComboBox(self)
        fs_model = QFileSystemModel(self)
        # model_proxy = QSortFilterProxyModel(self)
        # model_proxy.setSourceModel(fs_model)
        # fs_model.setNameFilters(['tty.PT-P3*'])

        potential_printer = None
        printers = QStandardItemModel()

        # for p in QDir('/dev').entryList(['tty*'], QDir.System, QDir.Name):
        #    if p.startswith('tty.'):
        for p in LabelMaker.list_serial_ports():
            pprint(p.__dict__)
            # p.description
            item = [QStandardItem(p.device), QStandardItem(p.device)]
            printers.appendRow(item)
            '''
            item = QStandardItem('/dev/' + p)
            printers.appendRow(item)
            if p.startswith('tty.PT-P3'):
                potential_printer = item
            '''

        # print(printers.entryList())

        # model_proxy.setRecursiveFilteringEnabled(True)
        # model_proxy.setFilterKeyColumn(0)

        fs_model.setRootPath('/dev/')  # /Users/nilsmasen')
        fs_model.setFilter(QDir.System)

        dev_index = fs_model.index('/dev')
        # proxy_dev = model_proxy.mapFromSource(dev_index)

        self.printer_select.setModel(printers)

        if potential_printer is not None:
            index = printers.indexFromItem(potential_printer)
            self.printer_select.setCurrentIndex(index.row())
        # printer_select.setRootModelIndex(dev_index)
        # printer_select.setRootIndex(dev_index)
        # printer_select.setExpanded(dev_index, True)
        # model_proxy.setFilterWildcard('tty*')

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
        root_widget.setFixedWidth(800)
        root_widget.setLayout(root)
        self.setCentralWidget(root_widget)
        menu = QMenuBar()
        self.setMenuBar(menu)

        about = QAction('About ' + APP_NAME, self)
        about.triggered.connect(self.on_about)
        about.setMenuRole(QAction.AboutRole)

        if is_mac:
            menu.setWindowTitle(APP_NAME)
            tools_menu = menu.addMenu(APP_NAME)
            prefs = QAction('&Preferences', self)
            prefs.triggered.connect(self.on_prefs)
            tools_menu.addAction(prefs)
            tools_menu.addAction(about)

        file_menu = menu.addMenu('Label')
        act_new = QAction('&New', self)
        act_new.triggered.connect(self.on_new)
        file_menu.addAction(act_new)
        file_menu.addSeparator()
        act_open = QAction('&Open', self)
        act_open.triggered.connect(self.on_open)
        act_open.setShortcut(QKeySequence('Ctrl+O'))
        file_menu.addAction(act_open)
        file_menu.addSeparator()
        act_save = QAction('&Save', self)
        act_save.triggered.connect(self.on_save)
        act_save.setShortcut(QKeySequence("Ctrl+S"))
        file_menu.addAction(act_save)
        act_save_as = QAction('Save &as...', self)
        act_save_as.triggered.connect(self.on_save_as)
        act_save_as.setShortcut(QKeySequence("Ctrl+Shift+S"))
        file_menu.addAction(act_save_as)
        file_menu.addSeparator()
        file_menu.addAction(QAction('&Export image', self))

        if not is_mac:
            help_menu = menu.addMenu('Help')
            help_menu.addAction(about)

        # menu.setNativeMenuBar(False)

    def on_new(self):
        self.item_data = []
        self.items.clear()
        self.update_items()
        self.update_preview()

    def on_about(self):
        QMessageBox.information(self,
                                "Info",
                                f"{APP_NAME} v{APP_VERSION}\n\nhttps://github.com/piksel/pytouch-cube")

    def on_prefs(self):
        QMessageBox.information(self, "Info", "Not implemented")

    def run(self):

        self.show()
        # self.add_item(Text(TextData('foo')))
        # self.add_item(Text(TextData('Bar1')))
        # self.add_item(Text(TextData('Bar2')))
        # self.add_item(Spacing(SpacingData(10)))
        # self.add_item(Text(TextData('baz')))
        # self.add_item(Barcode(BarcodeData('123456789012')))
        # self.add_item(Barcode(BarcodeData('ACE222', 'code128')))

        self.app.exec_()

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
        file_path, format = QFileDialog.getSaveFileName(
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
        file_path, format = QFileDialog.getOpenFileName(
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
            pickler.dump(self.item_data)

    def open(self):
        with open(self.current_file, 'rb') as file:
            unpickler = pickle.Unpickler(file)
            self.item_data = unpickler.load()
            self.update_items()
            self.update_preview()

    def print_clicked(self):

        log_console = QTextEdit(self)
        log_console.setReadOnly(True)
        font = QFont('Fira')
        font.setStyleHint(QFont.Monospace, QFont.PreferDefault)
        font.setFamilies(['Fira', 'Source Code Pro', 'Monaco', 'Consolas', 'Monospaced', 'Courier'])
        log_console.setFont(font)
        modal = QDialog(self)
        modal_layout = QVBoxLayout(self)
        modal_layout.addWidget(log_console)

        close = QPushButton('close')
        close.setDisabled(True)
        close.clicked.connect(lambda _: modal.close())
        modal_layout.addWidget(close)

        modal.setLayout(modal_layout)
        modal.setFixedWidth(int(self.width() * .9))
        modal.setFixedHeight(int(self.height() * .9))
        modal.open()

        def fmt_log(message):
            now = datetime.datetime.now()
            return '{0} {1}'.format(now.isoformat(), message)

        def log(message):
            log_console.insertPlainText('\n' + fmt_log(message))
            log_console.ensureCursorVisible()

        def done(exception: Exception):
            if exception is not None:
                log('Failed to print due to the following error:\n')
                print(exception)
                log_console.insertHtml('<pre style="color:red">{0}</pre>'.format(exception))
            else:
                log('Printing completed without any errors!\n')
            close.setDisabled(False)

        log_console.insertPlainText(fmt_log('Starting print thread...'))

        print_device = self.printer_select.currentText()
        # print_device = self.printer_select.currentData(1)
        print(print_device)
        self.print_thread = PrintThread(QImage(self.print_image), print_device)
        self.print_thread.log.connect(log)
        self.print_thread.done.connect(done)

        self.print_thread.start()

    def tree_view_clicked(self, index):
        self.item_selected = index.row()
        self.update_props()

    def move_item(self, direction):

        current = self.tree_view.currentIndex()
        print(direction, current)
        if not current.isValid() or current.row() < 0:
            print('invalid index', current.row())
            self.tree_view.repaint()
            return
        old = current.row()
        new = current.row() + direction
        if new < 0 or new >= self.items.rowCount():
            print('cannot move from', old, 'to', new)
            return
        # self.items.moveRow(current.parent(), old, current.parent(), new)
        self.tree_view_reorder(old, new)
        self.update_items()

        self.tree_view.setCurrentIndex(current.sibling(new, 0))
        self.tree_view.repaint()

    def delete_item(self):
        current = self.tree_view.currentIndex()
        if not current.isValid() or current.row() < 0:
            return
        self.item_data.remove(self.item_data[current.row()])

        self.items.removeRow(current.row())
        self.update_items()
        self.update_preview()

    def on_clone(self):
        current = self.tree_view.currentIndex()
        if not current.isValid() or current.row() < 0:
            return

        original = self.item_data[current.row()]
        copy = original.__class__(original.data.clone())
        new_index = current.row() + 1
        self.item_data.insert(new_index, copy)

        self.update_items()
        self.update_preview()

        self.tree_view.setCurrentIndex(self.items.index(new_index, 0))
        self.tree_view.repaint()

        self.item_selected = new_index
        self.update_props()

    def tree_view_reorder(self, old, new):
        item = self.item_data.pop(old)
        self.item_data.insert(new, item)
        self.update_preview()
        print(old, '=>', new)
        return item

    def create_model(self):
        model = QStandardItemModel(0, 2, self)
        model.setHeaderData(ModelCol.TYPE.value, Qt.Horizontal, 'Type')
        model.setHeaderData(ModelCol.DATA.value, Qt.Horizontal, 'Data')
        return model

    def add_item(self, item: Printable):
        current = self.tree_view.currentIndex()
        row = self.items.rowCount()
        if current.isValid():
            row = current.row()
        self.items.insertRow(row, item.get_list_item())
        self.item_data.insert(row, item)
        if current.isValid():
            self.tree_view.setCurrentIndex(current)
        else:
            self.tree_view.setCurrentIndex(self.items.createIndex(row, 0))
        self.item_selected = row
        self.update_preview()
        self.update_props()

    def save_props(self):
        if isinstance(self.props_current, PropsEdit):
            self.props_current.save()
            current = self.tree_view.currentIndex()
            self.update_items()
            self.tree_view.setCurrentIndex(current)

    def update_items(self, keep_index=False):
        current = self.tree_view.currentIndex()
        for row in range(0, len(self.item_data)):
            item = self.item_data[row].get_list_item()
            for col in range(0, len(item)):
                self.items.setItem(row, col, item[col])

        if keep_index:
            self.tree_view.setCurrentIndex(current)

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

    def update_props(self):

        if self.item_selected is None:
            if self.props_empty:
                return
            new_widget = make_props_empty(self)
            if self.save_printable_button is not None:
                self.save_printable_button.setEnabled(False)
            self.props_empty = True
        else:
            item: Printable = self.item_data[self.item_selected]
            new_widget = item.get_props_editor(self)
            self.save_printable_button.setEnabled(True)

        self.props_layout.replaceWidget(self.props_current, new_widget)
        self.props_current.close()
        self.props_current = new_widget


if __name__ == '__main__':
    PyTouchCubeGUI(QApplication([])).run()
