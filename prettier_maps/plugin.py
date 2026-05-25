from typing import Optional

from qgis.PyQt.QtGui import QAction, QIcon, QPainter

from .config import LOGO_PATH
from .interfaces import IQgisInterface
from .ui import MainDialog


class PrettierMapsPlugin:
    def __init__(self, iface: IQgisInterface) -> None:
        self.iface = iface
        self.action: Optional[QAction] = None

    def initGui(self) -> None:
        """Initializes the GUI"""

        # Get the icon
        icon = QIcon(str(LOGO_PATH))

        self.action = QAction(icon, "PrettierMaps", self.iface.mainWindow())
        self.action.setObjectName("prettierMapsAction")
        self.action.setWhatsThis("Configuration for PrettierMaps")
        self.action.setStatusTip("This is status tip")

        # Connect the open_dialog function to the button
        self.action.triggered.connect(self.open_dialog)
        self.iface.addWebToolBarIcon(self.action)

    def unload(self) -> None:
        """Removes the icon from the toolbar"""

        self.iface.removeWebToolBarIcon(self.action)

    def open_dialog(self) -> None:
        """Opens the main dialog"""

        dialog = MainDialog()
        dialog.exec()
