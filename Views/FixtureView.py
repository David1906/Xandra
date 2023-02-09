from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt5 import QtCore
from Controllers.FixtureController import FixtureController
from Views.Switch import Switch


class FixtureView(QFrame):
    def __init__(self, fixture):
        super().__init__()

        self.fixture = fixture
        self._fixtureController = FixtureController()

        self.setProperty("cssClass", "large")
        layout = QVBoxLayout()

        self.lblId = QLabel("Id:")
        self.lblId.setObjectName("h1")
        self.lblId.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.lblId)

        self.btnStart = QPushButton("Start")
        self.btnStart.clicked.connect(self.on_btnStart_clicked)
        layout.addWidget(self.btnStart)

        self.lblIp = QLabel("IP:")
        self.lblIp.setObjectName("h2")
        self.lblIp.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.lblIp)

        self.lblYield = QLabel("Yield:")
        self.lblYield.setObjectName("h2")
        self.lblYield.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.lblYield)

        hBoxSwitch = QHBoxLayout()
        hBoxSwitch.addWidget(QLabel("Traceability"))
        self.swTraceability = Switch()
        self.swTraceability.setChecked(True)
        hBoxSwitch.addWidget(self.swTraceability)
        layout.addLayout(hBoxSwitch)

        hBoxSwitch = QHBoxLayout()
        hBoxSwitch.addWidget(QLabel("Skip Low Yield Lock"))
        self.swSkip = Switch()
        self.swSkip.toggled.connect(self.onswSkipChange)
        hBoxSwitch.addWidget(self.swSkip)
        layout.addLayout(hBoxSwitch)

        self.setLayout(layout)
        self.__update()

    def onswSkipChange(self, checked):
        self.fixture.isSkipped = checked
        self._fixtureController.update_yield_lock_skipped(self.fixture)
        self.__update()

    def set_fixture(self, fixture):
        self.fixture = fixture
        self.__update()

    def __update(self):
        self.lblId.setText(f"Fixture {self.fixture.id}")
        self.lblYield.setText(f"Yield: {self.fixture.yieldRate}%")
        self.lblIp.setText(f"Ip: {self.fixture.ip}")
        self.btnStart.setEnabled(self.fixture.isDisabled() == False)
        self.swSkip.setEnabled(self.fixture.isDisabled() or self.fixture.isSkipped)
        self.swSkip.setChecked(self.fixture.isSkipped)

        objectName = ""
        if self.fixture.isDisabled():
            objectName = "error"
        elif self.fixture.isWarning():
            objectName = "warning"
        self.setObjectName(objectName)
        self.__setStyle()

    def __setStyle(self):
        self.setStyleSheet(
            """
            QWidget:disabled{
                opacity: 0.5;
            }
            QFrame[cssClass="large"] {
                padding: 4px;
                margin: 4px;
                color: black;
                border-radius: 5px;
                border: 1px solid gray;
            }
            QFrame#error {
                background-color: lightcoral;
            }
            QFrame#warning {
                background-color: yellow;
            }
            QLabel#h1{
                margin: 16px 0x;
                font-size: 24px;
                font-weight: bold;
            }
            QLabel#h2{
                margin: 8px 0px;
                font-size: 16px;
            }
         """
        )

    def on_btnStart_clicked(self):
        self._fixtureController.launch_fct_host_control(
            self.fixture, self.swTraceability.getChecked()
        )
        self.swTraceability.setChecked(True)

    def equals(self, fixture):
        return fixture.id == self.fixture.id
