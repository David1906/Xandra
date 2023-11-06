from PyQt5 import QtWidgets, QtCore


class BadgeView(QtWidgets.QFrame):
    def __init__(
        self,
        text: str,
        parent=None,
        color: str = "#E5E6EB",
        isBold: bool = False,
        prefix: str = "",
    ):
        super().__init__(parent)
        self._isBold = isBold
        self._color = color
        self._prefix = prefix
        self._text = text

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        self.lbl = QtWidgets.QLabel(self)
        self.lbl.setTextInteractionFlags(
            QtCore.Qt.TextInteractionFlag.TextSelectableByMouse
        )
        self.lbl.mousePressEvent = self.mousePressEvent
        layout.addWidget(self.lbl)
        self.setText(text)
        self._update_style()

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self._copy_text_to_clipboard()

    def _copy_text_to_clipboard(self):
        QtWidgets.QApplication.clipboard().setText(self._text)

    def set_color(self, color: str):
        self._color = color
        self._update_style()

    def _update_style(self):
        self.setStyleSheet(
            f"""
                background-color: {self._color};
                border-radius: 3px;
                font-size: 10px; 
                {"font-weight: bold;" if self._isBold else ""}
            """
        )

    def setText(self, text: str):
        if self._text != text:
            self.lbl.setText(self._prefix + text)
            self._text = text
