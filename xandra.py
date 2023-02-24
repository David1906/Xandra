from datetime import datetime
import sys
from Models.DTO.TestDTO import TestDTO
from Utils.qtexceptiohook import QtExceptHook
from Views.MainWindow import MainWindow
from PyQt5.QtWidgets import QApplication
from Utils.FileWatchdog import FileWatchdog
from Utils.SfcEventHandler import SfcEventHandler
from DataAccess.SqlAlchemyBase import Base, engine, Session

Base.metadata.create_all(engine)
session = Session()

test = TestDTO(
    serialNumber="serialNumber",
    project="project",
    startTime=datetime.now(),
    endTime=datetime.now(),
    codeVersion="codeVersion",
    fixtureIp="fixtureIp",
    status=True,
    stepLabel="stepLabel",
    operator="operator",
)
session.add(test)
session.commit()
session.close()

FileWatchdog(SfcEventHandler()).start()

app = QApplication(sys.argv)
QtExceptHook().enable()
styleSheet = "Resources/styles.css"
with open(styleSheet, "r") as fh:
    app.setStyleSheet(fh.read())
window = MainWindow()
window.showMaximized()
app.exec()
