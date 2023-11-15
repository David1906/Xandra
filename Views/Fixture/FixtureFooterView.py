from PyQt5 import QtCore, QtGui, QtWidgets
from Models.TestAnalysis import TestAnalysis
from Views.BadgeView import BadgeView
from Views.TempView import TempView
from Utils.Translator import Translator

_ = Translator().gettext


class FixtureFooterView(QtWidgets.QFrame):
    def __init__(self, parent: QtWidgets.QWidget):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        # ************* Status *************
        self._bdgResult = BadgeView(_("Status: IDLE"), self, isBold=True)

        # ************* Badges *************
        self._tempView = TempView()
        self._bdgSerialNumber = BadgeView(_("Serial Number"), self, prefix="SN: ")
        self._bdgMac = BadgeView(_("Mac"), self, prefix="MAC: ")

        self._badgesLayout = QtWidgets.QHBoxLayout()
        self._badgesLayout.setContentsMargins(0, 0, 0, 0)
        self._badgesLayout.addWidget(self._tempView, 0)
        self._badgesLayout.addWidget(self._bdgSerialNumber, 0)
        self._badgesLayout.addWidget(self._bdgMac, 0)

        self._badgesInfoFrame = QtWidgets.QFrame()
        self._badgesInfoFrame.setContentsMargins(0, 0, 0, 0)
        self._badgesInfoFrame.setLayout(self._badgesLayout)
        self._badgesInfoFrame.hide()

        # ************* Layout *************
        self._layout = QtWidgets.QHBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.addWidget(self._bdgResult, 0)
        self._layout.addStretch()
        self._layout.addWidget(self._badgesInfoFrame)

        self.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self._layout)

    def update_status(self, status: str, setTooltip: bool):
        self._bdgResult.setText(status)
        self._bdgResult.setToolTip(status if setTooltip else "")
        self._bdgResult.set_color(self._get_status_color(status))

    def set_status_color(self, isError: bool = False):
        self._bdgResult.set_color("FAIL" if isError else "")

    def _get_status_color(self, status: str):
        color = "#D2D4DC"
        if "PASS" in status:
            color = "#5EAC24"
        elif "FAIL" in status:
            color = "#C44D56"
        return color

    def start(self, testAnalysis: TestAnalysis):
        self._bdgSerialNumber.setText(testAnalysis.serialNumber)
        self._bdgMac.setText(testAnalysis.mac)
        self.set_badges_setVisible(True)

    def start_temp(self, toolPath: str, testAnalysis: TestAnalysis):
        if self._can_start_temp_view(testAnalysis):
            self._tempView.start(
                toolPath,
                testAnalysis.bmcIp,
            )

    def _can_start_temp_view(self, testAnalysis: TestAnalysis):
        return (
            testAnalysis.bmcIp != ""
            and testAnalysis.bmcIp != None
            and not self._tempView.is_started()
        )

    def stop(self):
        self.set_badges_setVisible(False)
        self._tempView.pause()

    def set_badges_setVisible(self, setVisible: bool):
        self._badgesInfoFrame.setVisible(setVisible)
