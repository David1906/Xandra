from PyQt5.QtWidgets import QApplication
from Utils.qtexceptiohook import QtExceptHook
from Views.MainWindow import MainWindow
import sys

app = QApplication(sys.argv)
QtExceptHook().enable()
with open("Resources/styles.css", "r") as fh:
    app.setStyleSheet(fh.read())
window = MainWindow()
window.showMaximized()
app.exec()
