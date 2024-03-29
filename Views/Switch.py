from PyQt5.QtCore import (
    Qt,
    pyqtSignal,
    QPropertyAnimation,
    QPoint,
    QAbstractAnimation,
    QParallelAnimationGroup,
)

from PyQt5.QtWidgets import QWidget, QPushButton, QGridLayout, QHBoxLayout


class Switch(QWidget):
    toggled = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.__checked = False
        self._initVal()
        self._initUi()

    def _initVal(self):
        self.__circle_diameter = 20
        self.__animationEnabledFlag = False
        self.__pointAnimation = ""
        self.__colorAnimation = ""

    def _initUi(self):
        self.__circle = QPushButton()
        self.__circle.setCheckable(True)
        self.__circle.toggled.connect(self._toggled)

        self.__layForBtnAlign = QHBoxLayout()
        self.__layForBtnAlign.setAlignment(Qt.AlignLeft)
        self.__layForBtnAlign.addWidget(self.__circle)
        self.__layForBtnAlign.setContentsMargins(0, 0, 0, 0)

        innerWidgetForStyle = QWidget()
        innerWidgetForStyle.setLayout(self.__layForBtnAlign)

        lay = QGridLayout()
        lay.addWidget(innerWidgetForStyle)
        lay.setContentsMargins(0, 0, 0, 0)

        self.setLayout(lay)

        self._setStyle()

    def setChecked(self, value):
        self.__circle.setChecked(value)
        self._toggled(value, emitEvent=False)

    def getChecked(self):
        return self.__checked

    def setEnabled(self, value: bool) -> None:
        super().setEnabled(value)
        self._setStyle()

    def _setStyle(self):
        self.__circle.setFixedSize(self.__circle_diameter, self.__circle_diameter)
        color = "#36A355" if self.isEnabled() else "#A2B0A6"
        if not self.__checked:
            color = "#A34646" if self.isEnabled() else "#A88585"
        self.setStyleSheet(
            f"QWidget {{ border: {self.__circle_diameter // 20}px solid #AAAAAA; "
            f"border-radius: {self.__circle_diameter // 2}px;"
            f"background-color: {color}; }}"
        )
        self.setFixedSize(self.__circle_diameter * 2, self.__circle_diameter)

    def setAnimation(self, f: bool):
        self.__animationEnabledFlag = f
        if self.__animationEnabledFlag:
            self.__colorAnimation = QPropertyAnimation(self, b"point")
            self.__colorAnimation.valueChanged.connect(self.__circle.move)
            self.__colorAnimation.setDuration(100)
            self.__colorAnimation.setStartValue(QPoint(0, 0))
            self.__colorAnimation.setEndValue(QPoint(self.__circle_diameter, 0))

            self.__pointAnimation = QPropertyAnimation(self, b"color")
            self.__pointAnimation.valueChanged.connect(self._setColor)
            self.__pointAnimation.setDuration(100)
            self.__pointAnimation.setStartValue(255)
            self.__pointAnimation.setEndValue(200)

            self.__animationGroup = QParallelAnimationGroup()
            self.__animationGroup.addAnimation(self.__colorAnimation)
            self.__animationGroup.addAnimation(self.__pointAnimation)

    def mousePressEvent(self, e):
        self.__circle.toggle()
        return super().mousePressEvent(e)

    def _toggled(self, f, emitEvent=True):
        self.__checked = f
        if self.__animationEnabledFlag:
            if f:
                self.__animationGroup.setDirection(QAbstractAnimation.Forward)
                self.__animationGroup.start()
            else:
                self.__animationGroup.setDirection(QAbstractAnimation.Backward)
                self.__animationGroup.start()
        else:
            if f:
                self.__circle.move(self.__circle_diameter, 0)
                self.__layForBtnAlign.setAlignment(Qt.AlignRight)
                self._setColor(200)
            else:
                self.__circle.move(0, 0)
                self.__layForBtnAlign.setAlignment(Qt.AlignLeft)
                self._setColor(255)
        if emitEvent:
            self.toggled.emit(f)

    def _setColor(self, f: int):
        self.__circle.setStyleSheet(
            f"QPushButton {{ background-color: rgb({f}, {f}, 255); }}"
        )
        self._setStyle()

    def setCircleDiameter(self, diameter: int):
        self.__circle_diameter = diameter
        self._setStyle()
        self.__colorAnimation.setEndValue(QPoint(self.__circle_diameter, 0))
