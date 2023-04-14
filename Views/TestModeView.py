from Core.Enums.FixtureMode import FixtureMode
from PyQt5 import QtWidgets
from Utils.PathHelper import PathHelper
from Views.ImageWidget import ImageWidget


class TestModeView(QtWidgets.QWidget):
    def __init__(self, fixtureMode: FixtureMode) -> None:
        super().__init__()
        self.fixtureMode = fixtureMode

        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setSpacing(0)

        img = self._get_image()
        if img != None:
            layout.addWidget(img)
        layout.addWidget(QtWidgets.QLabel(fixtureMode.description))

        self.setLayout(layout)

    def _get_image(self) -> ImageWidget:
        imagePath = PathHelper().join_root_path("/Static/unknown.png")
        if self.fixtureMode == FixtureMode.ONLINE:
            imagePath = PathHelper().join_root_path("/Static/online.png")

        if self.fixtureMode == FixtureMode.RETEST:
            imagePath = PathHelper().join_root_path("/Static/retest.png")

        if self.fixtureMode == FixtureMode.OFFLINE:
            imagePath = PathHelper().join_root_path("/Static/offline.png")

        return ImageWidget(imagePath, self)
