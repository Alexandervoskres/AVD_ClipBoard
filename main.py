import sys
import os
import threading
import keyboard
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (QWidget, QPushButton,
                             QHBoxLayout, QVBoxLayout, QListWidget,
                             QSplitter, QFileDialog, QInputDialog,
                             QLineEdit, QMenu, QAbstractItemView, QLabel,
                             QMessageBox,QGroupBox)
from PyQt5.QtCore import Qt, QEvent,QRect
from PyQt5.Qt import QApplication
import sqlite3
import pyautogui
import avd

class Clipboard(QWidget):

    def __init__(self):

        super().__init__()
        self.font_size = 14
        self.color_even ="#2b143b"
        self.color_even2 = "#1a0c24"
        self.font_family = "Roboto"
        self.color = "white"
        self.font_weight = "bold"
        self.hotkey = 'ctrl + space'
        self.minimizeAfterPasting = False
        self.initDB()
        self.initUI()
        screen_resolution = app.desktop().screenGeometry()
        self.screenH = screen_resolution.height()
        keyboard.add_hotkey(self.hotkey, self.onHotKeyPressed)
    # метод для создания базы данных, в ктр хран. элементы.
    def initDB(self):

        self.db = sqlite3.connect("database.db")
        self.cursor = self.db.cursor()

        self.cursor.execute("""SELECT count(name) FROM sqlite_master
        WHERE type='table' AND name='clipboard'""")

    # Если таблица не существует, то создаём.

        if self.cursor.fetchone()[0] != 1:
            self.cursor.execute("""CREATE TABLE clipboard(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT,
                image BLOB
            )""")

            values = [
                ("Hello!", "NULL"),
                ("Нажмите на элемент в таблице,  и он сработает в аналогии ctrl+v", "NULL"),
                ("Данные Буфера можно сбросить нажав на кнопку", "NULL"),
                ("А так же сохранить ", "NULL"),
                ("Масштабировать текст вы также можете", "NULL")
            ].__reversed__()

            self.cursor.executemany("INSERT INTO clipboard(text, image) VALUES(?, ?)", values)
            self.db.commit()
    # метод для создания интерфейса пользователя.
    # устанавливает их параметры и соединяет их с методами.

    def initUI(self):
        self.lastClip = ''
        self.setWindowTitle('AVD ClipBoard')

        # ставим позиционирование
        screen_resolution = app.desktop().screenGeometry()
        self.screenW, self.screenH = screen_resolution.width(), screen_resolution.height()
        self.setGeometry(0, 0,
                         int(self.screenH * 0.06), int(self.screenH * 0.4))
        self.move(self.screenW // 2 - self.width() * 2, self.screenH // 2 - self.height() // 2)
        self.setWindowTitle('AVD ClipBoard')
        # добавляем виджеты

        settingsBtn = QPushButton("Настройки")
        settingsBtn.setStyleSheet("""QPushButton {background-color: #1f0e2b;padding: 6px;
        color:#FFFFFF;font-family:Roboto;font-weight:900;
        border-radius: 15px;cursor: pointer;}
        QPushButton:hover {background-color:#1a0c24 ;}
        QPushButton:pressed {background-color:#0d0612;}""")
        settingsBtn.setMinimumHeight(70)
        settingsBtn.setMaximumWidth(90)
        saveButton = QPushButton("Сохранить")
        saveButton.setMinimumHeight(70)
        saveButton.setMaximumWidth(90)
        saveButton.setStyleSheet("""QPushButton {background-color: #1f0e2b;padding: 6px;
        color:#FFFFFF;font-family:Roboto;font-weight:900;
        border-radius: 15px;cursor: pointer;}
        QPushButton:hover {background-color:#1a0c24 ;}
        QPushButton:pressed {background-color:#0d0612;}""")
        clrButton = QPushButton("Сбросить")
        clrButton.setMinimumHeight(70)
        clrButton.setMaximumWidth(90)
        clrButton.setStyleSheet("""QPushButton {background-color: #1f0e2b;padding: 6px;
        color:#FFFFFF;font-family:Roboto;font-weight:900;
        border-radius: 15px;cursor: pointer;}
        QPushButton:hover {background-color:#1a0c24 ;}
        QPushButton:pressed {background-color:#0d0612;}""")
        plusButton = QPushButton("+")
        plusButton.setMinimumHeight(70)
        plusButton.setMaximumWidth(90)
        plusButton.setStyleSheet("""QPushButton {background-color: #1f0e2b;padding: 6px;
        color:#FFFFFF;font-family:Roboto;font-weight:900;
        border-radius: 15px;cursor: pointer;}
        QPushButton:hover {background-color:#1a0c24 ;}
        QPushButton:pressed {background-color:#0d0612;}""")
        minButton = QPushButton("-")
        minButton.setMinimumHeight(70)
        minButton.setMaximumWidth(90)
        minButton.setStyleSheet("""QPushButton {background-color: #1f0e2b;padding: 6px;
        color:#FFFFFF;font-family:Roboto;font-weight:900;
        border-radius: 15px;cursor: pointer;}
        QPushButton:hover {background-color:#1a0c24 ;}
        QPushButton:pressed {background-color:#0d0612;}""")
        self.clipboard = QListWidget()
        self.clipboard.setMinimumHeight(int(self.screenH * 0.05))
        self.clipboard.setMinimumWidth(int(self.screenW * 0.3))
        self.clipboard.setDragDropMode(QAbstractItemView.DragDrop)
        self.clipboard.setDefaultDropAction(Qt.MoveAction)
        self.clipboard.setAutoScroll(True)
        self.clipboard.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.clipboard.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.clipboard.setWordWrap(True)
        self.clipboard.setStyleSheet(
            "color: {}; font-family: {}; font-weight: {}; font-size: {}".format(
                self.color, self.font_family, self.font_weight, self.font_size))
        self.clipboard.viewport().installEventFilter(self)

        # Подгрузка того  ,что уже есть в бд
        for data in list(self.cursor.execute("SELECT * FROM clipboard")):
            if data[2] == "NULL":
                self.addItem(newClip=data[1])

        self.clipboard.viewport().installEventFilter(self)

        self.bin = QListWidget()
        self.bin.setMaximumHeight(int(self.screenH * 0.05))
        self.bin.setMinimumWidth(int(self.screenW * 0.1))
        self.bin.setDragDropMode(QAbstractItemView.DragDrop)
        self.bin.setDefaultDropAction(Qt.MoveAction)
        self.bin.viewport().installEventFilter(self)

        # define layout: a horizontal box with three buttons in it
        hbox = QHBoxLayout()
        v1box = QVBoxLayout()
        v1box.addWidget(saveButton)
        v1box.addWidget(clrButton)
        v1box.addWidget(plusButton)
        v1box.addWidget(minButton)
        v1box.setSpacing(12)
        v1box.setContentsMargins(0, 0, 0, 0)
        v1box.addWidget(settingsBtn)
        # a vertical box with the clipboard and the horizontal box in it

        self.titlebar = QLabel('AVD ClipBoard', self)
        self.titlebar.setPixmap(QtGui.QPixmap("img/logo2.png"))
        self.titlebar.setAlignment(Qt.AlignHCenter)

        v2box = QVBoxLayout()
        v2box.addWidget(self.titlebar)
        v2box.addWidget(self.clipboard)
        v2box.setSpacing(0)
        v2box.setContentsMargins(0, 0, 0, 0)
        hbox.addLayout(v2box)
        hbox.addLayout(v1box)
        self.setLayout(hbox)
        # connect button to methods on_click
        settingsBtn.clicked.connect(self.settings)
        clrButton.clicked.connect(self.clearList)
        saveButton.clicked.connect(self.saveList)
        self.clipboard.clicked.connect(self.selectItem)

        plusButton.clicked.connect(self.increase_font)
        minButton.clicked.connect(self.decrease_font)

        # create instance of system clipboard
        self.CB = QApplication.clipboard()

        self.CB.dataChanged.connect(self.addItem)

        self.show()

# Метод eventFilter() перехватывает и фильтрует события, генерируемые виджетом.

    def eventFilter(self, obj, event):
        if obj is self.bin.viewport() and event.type() == QtCore.QEvent.Drop:
            super().eventFilter(obj, event)
            threading.Timer(0.01, self.bin.clear).start()
        if obj is self.clipboard.viewport() and event.type() == QtCore.QEvent.Drop:
            super().eventFilter(obj, event)
            threading.Timer(0.01, self.draw_rows).start()
        if obj is self.clipboard.viewport() and event.type() == QEvent.MouseButtonRelease:
            if len(self.clipboard.selectedItems()) != 0 and event.button() == Qt.RightButton:
                self.editItem()
        return False
# метод, который увеличивает размер шрифта элементов в списке

    def increase_font(self):
        if self.font_size < 36:
            self.font_size += 2
        self.clipboard.setStyleSheet(
            "font-size: {}pt; color: {}; font-family: {}; font-weight: {};".format(
                self.font_size, self.color, self.font_family, self.font_weight))
# метод, который уменьшает размер шрифта элементов

    def decrease_font(self):
        if self.font_size > 6:
            self.font_size -= 2
        self.clipboard.setStyleSheet(
            "font-size: {}pt; color: {}; font-family: {}; font-weight: {};".format(
                self.font_size, self.color, self.font_family, self.font_weight))
# метод, который сохраняет элементы списка в текстовый файл.

# Метод settings() вызывается при нажатии кнопки "Настройки"
    # позволяет пользователю изменить горячую клавишу для вызова приложения.
    def settings(self):
        text, okPressed = QInputDialog.getText(self, "Settings", "Edit Hotkey:", QLineEdit.Normal, self.hotkey)

        if okPressed:
            keyboard.remove_hotkey(self.hotkey)
            self.hotkey = text
            keyboard.add_hotkey(self.hotkey, self.onHotKeyPressed)

    def toggleMinimizeAfterPasting(self):
        self.minimizeAfterPasting = not self.minimizeAfterPasting
# метод, который сохраняет элементы списка в текстовый файл.

    def saveList(self):
        fileName, _ = QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()", "",
                                                  "All Files (*);;Text Files (*.txt)")
        if fileName:
            text_file = open(fileName, "w")
            n = self.clipboard.count()
            text2save = ''
            for i in range(n):
                text2save += self.clipboard.item(i).text()
                text2save += '\n'
            text_file.write(text2save)
            text_file.close()
# метод, который добавляет новый элемент в конец списка.
    # Если элемент уже был скопирован ранее, то он пропускается

    def addItem(self, newClip=0):
        if newClip == 0:
            newClip = self.CB.text()

        if newClip == self.lastClip:
            pass
        else:
            self.clipboard.insertItem(0, newClip)
            self.draw_rows()
            self.lastClip = newClip


# метод, который выделяет выбранный пользователем элемент списка и копирует его в буфер обмена.

    def selectItem(self):
        print("select")
        items = self.clipboard.selectedItems()
        text2clip = ''

        for item in items:
            text2clip += item.text()
            self.CB.setText(text2clip, 0)
        self.lastClip = text2clip
        self.paste()

# метод, который устанавливает цвет фона у каждого элемента списка
    # в соответствии с его порядковым номером.

    def draw_rows(self):
        for row_num in range(self.clipboard.count()):
            if row_num % 2:
                color = QtGui.QColor(self.color_even)
                self.clipboard.item(row_num).setBackground(color)
            else:
                color = QtGui.QColor(self.color_even2)
                self.clipboard.item(row_num).setBackground(color)

# метод, который очищает список.

    def clearList(self):
        self.clipboard.clear()
        self.bin.clear()
# метод, который вызывается при закрытии окна. В нем происходит сохранение элементов списка в базу данных.

    def closeEvent(self, event):
        ex.cursor.execute("DELETE FROM clipboard")
        ex.cursor.executemany("INSERT INTO clipboard(text, image) VALUES(?, ?)",
                              [(ex.clipboard.item(x).text(), "NULL")
                               for x in range(ex.clipboard.count())].__reversed__())
        ex.db.commit()
        ex.db.close()
# метод, который вставляет выбранный пользователем элемент из буфера обмена.

    def paste(self):
        self.showMinimized()
        pyautogui.hotkey('ctrl', 'v')
        if not self.minimizeAfterPasting:
            self.showNormal()

# метод, который вызывается при нажатии горячей клавиши.
    # Если окно свернуто, то оно разворачивается, иначе - сворачивается.

    def onHotKeyPressed(self):
        if self.isMinimized():
            self.move(pyautogui.position().x,
                      pyautogui.position().y) + int(self.screenH * 0.01)
            self.showNormal()
        else:
            self.showMinimized()
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton  and not self.isMinimized():
            self.offset = event.pos()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.offset is not None and event.buttons() == QtCore.Qt.LeftButton and not self.isMinimized():
            self.move(self.pos() + event.pos() - self.offset)
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.offset = None
        super().mouseReleaseEvent(event)
if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = Clipboard()
    menu = QMenu()
    ui = avd.Ui_MainWindow()
    ui.setupUi(ex)
    minimizeAfterPasting = menu.addAction("Minimize after pasting (toggle)")
    minimizeAfterPasting.triggered.connect(ex.toggleMinimizeAfterPasting)
    sys.exit(app.exec_())