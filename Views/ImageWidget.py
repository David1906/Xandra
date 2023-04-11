from PyQt5 import QtGui, QtWidgets


class ImageWidget(QtWidgets.QLabel):
    def __init__(self, imagePath: str, parent=None):
        super(ImageWidget, self).__init__(parent)
        pixMap = QtGui.QPixmap(imagePath)
        self.setPixmap(pixMap.scaledToHeight(16))
        self.setMargin(3)
