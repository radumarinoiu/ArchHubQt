from typing import Callable
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QLayout, QPushButton, QVBoxLayout, QWidget
from .base import BaseWidgetMixin


class VSeparatorWidget(BaseWidgetMixin, QFrame):
    def __init__(
        self,
        parent_layout: QLayout | None = None,
        object_name: str | None = None,
    ):
        super().__init__()
        self.setFixedWidth(1)
        self.init(parent_layout=parent_layout, object_name=object_name)


class HSeparatorWidget(BaseWidgetMixin, QFrame):
    def __init__(
        self,
        parent_layout: QLayout | None = None,
        object_name: str | None = None,
    ):
        super().__init__()
        self.setFixedHeight(1)
        self.init(parent_layout=parent_layout, object_name=object_name)


class LabelWidget(BaseWidgetMixin, QLabel):
    def __init__(
        self,
        text: str,
        alignment: Qt.Alignment = Qt.AlignmentFlag.AlignCenter,
        parent_layout: QLayout | None = None,
        object_name: str | None = None,
    ):
        super().__init__(text)
        self.setAlignment(alignment)
        self.init(parent_layout=parent_layout, object_name=object_name)

class SquareIndicatorWidget(BaseWidgetMixin, QFrame):
    def __init__(
        self,
        value: str,
        title: str,
        parent_layout: QLayout | None = None,
        object_name: str | None = None,
    ):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setFixedWidth(80)
        self.setFixedHeight(80)

        self.value_label = LabelWidget(value, alignment=Qt.AlignmentFlag.AlignCenter, parent_layout=layout, object_name="value-label")
        self.title_label = LabelWidget(title, alignment=Qt.AlignmentFlag.AlignCenter, parent_layout=layout, object_name="title-label")
        self.setLayout(layout)
        self.init(parent_layout=parent_layout, object_name=object_name)

    def setValue(self, value: str) -> None:
        self.value_label.setText(value)


class CountersCardWidget(BaseWidgetMixin, QWidget):
    def __init__(
        self,
        total_packages: int,
        aur_packages: int,
        updates_count: int,
        parent_layout: QLayout | None = None,
        object_name: str | None = None,
    ):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.installed_label = SquareIndicatorWidget(
            str(total_packages), "Installed", parent_layout=layout
        )
        self.aur_label = SquareIndicatorWidget(
            str(aur_packages), "AUR", parent_layout=layout
        )
        self.updates_label = SquareIndicatorWidget(
            str(updates_count), "Updates", parent_layout=layout
        )
        self.setLayout(layout)
        self.init(parent_layout=parent_layout)


class PageButtonWidget(BaseWidgetMixin, QPushButton):
    def __init__(
        self,
        text: str,
        page: str,
        on_click: Callable[[str], None],
        parent_layout: QLayout | None = None,
        object_name: str | None = None,
    ):
        super().__init__(text)
        self.page = page
        self.setFlat(True)
        self.setCheckable(True)
        self.clicked.connect(lambda: on_click(page))
        self.init(parent_layout=parent_layout, object_name=object_name)

class SubPageButtonWidget(PageButtonWidget):
    pass