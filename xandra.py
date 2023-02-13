import sys
from Utils.qtexceptiohook import QtExceptHook
from Views.MainWindow import MainWindow
from PyQt5.QtWidgets import QApplication

app = QApplication(sys.argv)
QtExceptHook().enable()
styleSheet = "Resources/styles.css"
with open(styleSheet, "r") as fh:
    app.setStyleSheet(fh.read())
window = MainWindow()
window.showMaximized()
app.exec()
