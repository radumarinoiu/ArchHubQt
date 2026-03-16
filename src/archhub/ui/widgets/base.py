"""Common base component helpers.
`BaseWidget` centralizes a few common patterns:
- optional automatic addition to a parent layout
- optional objectName and \"class\" property for use in QSS selectors
"""

from __future__ import annotations

from typing import Sequence

from PySide6.QtWidgets import QLayout, QWidget


class BaseWidgetMixin:
    """Base widget with shared setup and optional auto-attach to a parent layout.

    This base focuses on ergonomics, not styling:
    - Use a global QSS applied to the QApplication.
    - Use `object_name` and `classes` to target widgets from QSS.
    - Use `parent_layout` to automatically add the widget to a layout in `__init__`.
    """
    CLASSES: Sequence[str] = ()

    def init(
        self,
        parent_layout: QLayout | None = None,
        object_name: str | None = None,
    ) -> None:
        """
        Args:
            parent_layout: If provided, this widget is added to that layout.
            object_name: Optional `objectName` for QSS / testing / lookup.
            classes: Optional \"class\" property values for QSS
                     (e.g. [\"card\", \"primary\"]) applied as space-separated string.
        """
        if not isinstance(self, QWidget):
            raise TypeError("BaseWidgetMixin can only be used with QWidget subclasses")
        
        if object_name:
            self.setObjectName(object_name)

        # if self.CLASSES:
        #     # e.g. in QSS: QWidget[class~=\"card\"] { ... }
        #     self.setProperty("class", " ".join(self.CLASSES))

        if parent_layout is not None:
                parent_layout.addWidget(self)
