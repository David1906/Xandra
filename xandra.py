import sys
from Views.MainWindow import MainWindow
from PyQt5.QtWidgets import QApplication

app = QApplication(sys.argv)
styleSheet="Resources/styles.css"
with open(styleSheet,"r") as fh:
    app.setStyleSheet(fh.read())
window = MainWindow()
window.show()
app.exec()