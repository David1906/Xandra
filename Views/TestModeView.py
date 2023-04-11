from Core.Enums.TestMode import TestMode
from PyQt5 import QtWidgets
from Utils.PathHelper import PathHelper
from Views.ImageWidget import ImageWidget


class TestModeView(QtWidgets.QWidget):
    def __init__(self, testMode: TestMode) -> None:
        super().__init__()
        self.testMode = testMode

        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setSpacing(0)

        img = self._get_image()
        if img != None:
            layout.addWidget(img)
        layout.addWidget(QtWidgets.QLabel(testMode.description))

        self.setLayout(layout)

    def _get_image(self) -> ImageWidget:
        imagePath = PathHelper().join_root_path("/Static/unknown.png")
        if self.testMode == TestMode.ONLINE:
            imagePath = PathHelper().join_root_path("/Static/online.png")

        if self.testMode == TestMode.RETEST:
            imagePath = PathHelper().join_root_path("/Static/retest.png")

        if self.testMode == TestMode.OFFLINE:
            imagePath = PathHelper().join_root_path("/Static/offline.png")

        return ImageWidget(imagePath, self)
