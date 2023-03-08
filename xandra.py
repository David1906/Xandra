from PyQt5.QtWidgets import QApplication
from Utils.PathHelper import PathHelper
from Utils.qtexceptiohook import QtExceptHook
from Views.ExitSingleInstanceWindow import ExitSingleInstanceWindow
from Views.MainWindow import MainWindow
import fcntl
import os
import sys

fh = 0
app = QApplication(sys.argv)


def start():
    os.environ["XANDRA_VERSION"] = "1.0.3"
    os.environ["HALT"] = "Az3E4ur"
    QtExceptHook().enable()
    with open(PathHelper().get_root_path() + "/Static/styles.css", "r") as fh:
        app.setStyleSheet(fh.read())
    window = MainWindow()
    window.showMaximized()
    app.exec()


def run_once():
    global fh
    fh = open(os.path.realpath(__file__), "r")
    print(os.path.realpath(__file__))
    try:
        fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
        start()
    except Exception as e:
        ExitSingleInstanceWindow().exec(str(e))
        os._exit(0)


run_once()
