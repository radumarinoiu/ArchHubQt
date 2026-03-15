from typing import Callable
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QSizePolicy, QVBoxLayout

from archhub.ui.styles import PAGE_BUTTON_STYLE, SQUARE_LABEL_STYLE, SUB_PAGE_BUTTON_STYLE


class QSquareLabel(QFrame):
    def __init__(self, title: str, value: str):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setFixedWidth(80)
        self.setFixedHeight(80)
        
        self.setStyleSheet(SQUARE_LABEL_STYLE)

        self.value_label = QLabel(value)
        self.value_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(self.value_label, alignment=Qt.AlignCenter)
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("font-size: 12px;")
        layout.addWidget(self.title_label, alignment=Qt.AlignCenter)
        self.setLayout(layout)

class QPageButton(QPushButton):
    STYLESHEET = PAGE_BUTTON_STYLE
    def __init__(self, text: str, page: str, on_click: Callable[[str], None]):
        super().__init__(text)
        self.page = page
        self.setFlat(True)
        self.setCheckable(True)
        self.setStyleSheet(self.STYLESHEET)
        self.clicked.connect(lambda: on_click(page))

class QSubPageButton(QPageButton):
    STYLESHEET = SUB_PAGE_BUTTON_STYLE
