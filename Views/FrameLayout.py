from PyQt5 import QtCore, QtWidgets, QtGui


class FrameLayout(QtWidgets.QFrame):
    def __init__(self, parent=None, tooltip=None):
        super().__init__(parent)

        self._is_collasped = False
        self._title_frame = TitleFrame(self, tooltip, self._is_collasped)
        self._content, self._content_layout = (None, None)

        self._main_layout = QtWidgets.QHBoxLayout(self)
        self._main_layout.addWidget(self._title_frame, 1)
        self._main_layout.addWidget(self.initContent(self._is_collasped))
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet(
            """
            FrameLayout{  
               border: 1px solid #c0c2ce;
               background-color: #f8f8fa;
               border-radius: 3px;
            }
               
            TitleFrame:hover{
                background-color: #c0c2ce;
            }
               """
        )

    def initContent(self, collapsed):
        self._content = QtWidgets.QWidget()
        self._content.setContentsMargins(0, 0, 0, 0)
        self._content_layout = QtWidgets.QVBoxLayout()
        self._content_layout.setContentsMargins(0, 0, 0, 0)

        self._content.setLayout(self._content_layout)
        self._content.setVisible(not collapsed)

        return self._content

    def addWidget(self, widget):
        self._content_layout.addWidget(widget)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.toggleCollapsed()

    def toggleCollapsed(self):
        self._content.setVisible(self._is_collasped)
        self._is_collasped = not self._is_collasped
        self._title_frame._arrow.setArrow(int(self._is_collasped))

    def expand(self):
        if self._is_collasped:
            self.toggleCollapsed()

    def collapse(self):
        if not self._is_collasped:
            self.toggleCollapsed()


class TitleFrame(QtWidgets.QFrame):
    def __init__(self, parent=None, tooltip="", collapsed=False):
        super().__init__(parent)

        self.setMinimumWidth(25)
        self.setStyleSheet("background-color: #e5e6eb;")
        self.setToolTip(tooltip)

        self._layout = QtWidgets.QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        self._arrow = None
        self._title = None

        self._layout.addWidget(self.initArrow(collapsed))
        # self._layout.addWidget(self.initTitle(title))

    def initArrow(self, collapsed):
        self._arrow = Arrow(self, collapsed)
        self._arrow.setStyleSheet("border:0px")
        return self._arrow

    def initTitle(self, title=None):
        self._title = VerticalLabel(title)
        self._title.setMinimumWidth(24)
        self._title.setStyleSheet("border:0px;")
        return self._title

    def mousePressEvent(self, event):
        return super(TitleFrame, self).mousePressEvent(event)


class VerticalLabel(QtWidgets.QWidget):
    def __init__(self, text=None):
        super(self.__class__, self).__init__()
        self.text = text

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setPen(QtCore.Qt.black)
        painter.translate(20, 100)
        painter.rotate(-90)
        if self.text:
            painter.drawText(0, 0, self.text)
        painter.end()


class Arrow(QtWidgets.QFrame):
    def __init__(self, parent=None, collapsed=False):
        super().__init__(parent)

        self.setMaximumSize(24, 24)

        self._arrow_right = (
            QtCore.QPointF(13.0, 7.0),
            QtCore.QPointF(8.0, 12.0),
            QtCore.QPointF(13.0, 17.0),
        )
        self._arrow_left = (
            QtCore.QPointF(8.0, 7.0),
            QtCore.QPointF(13.0, 12.0),
            QtCore.QPointF(8.0, 17.0),
        )
        self._arrow = None
        self.setArrow(int(collapsed))

    def setArrow(self, arrow_dir):
        if arrow_dir:
            self._arrow = self._arrow_left
        else:
            self._arrow = self._arrow_right

    def paintEvent(self, event):
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setBrush(QtGui.QColor(192, 192, 192))
        painter.setPen(QtGui.QColor(64, 64, 64))
        painter.drawPolygon(*self._arrow)
        painter.end()
