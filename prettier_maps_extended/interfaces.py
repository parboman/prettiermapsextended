from abc import abstractmethod
from typing import Optional

from qgis.PyQt.QtCore import QObject
from qgis.PyQt.QtGui import QAction
from qgis.PyQt.QtWidgets import QWidget


class IQgisInterface(QObject):  # type: ignore[misc]
    @abstractmethod
    def mainWindow(self) -> Optional[QWidget]:
        """Return the QGIS main window."""

    @abstractmethod
    def addWebToolBarIcon(self, qAction: Optional[QAction]) -> int:  # noqa: N803
        """Add a QAction to the Web toolbar; returns the icon index."""

    @abstractmethod
    def removeWebToolBarIcon(self, qAction: Optional[QAction]) -> None:  # noqa: N803
        """Remove a previously-added QAction from the Web toolbar."""
