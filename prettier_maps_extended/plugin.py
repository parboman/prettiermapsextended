from typing import Optional

from qgis.PyQt.QtGui import QAction, QIcon

from .config import LOGO_PATH
from .interfaces import IQgisInterface
from .ui import MainDialog


class PrettierMapsPlugin:
    def __init__(self, iface: IQgisInterface) -> None:
        self.iface = iface
        self.action: Optional[QAction] = None

    def initGui(self) -> None:
        """Add the plugin's toolbar action to QGIS."""
        icon = QIcon(str(LOGO_PATH))

        self.action = QAction(icon, "Prettier Maps (Extended)", self.iface.mainWindow())
        self.action.setObjectName("prettierMapsExtendedAction")
        self.action.setWhatsThis(
            "Toggle individual sublayers of a MapTiler vector tile basemap, "
            "and style or save QuickOSM query results."
        )
        self.action.setStatusTip("Open Prettier Maps (Extended)")

        self.action.triggered.connect(self.open_dialog)
        self.iface.addWebToolBarIcon(self.action)

    def unload(self) -> None:
        """Remove the plugin's toolbar action from QGIS."""
        self.iface.removeWebToolBarIcon(self.action)

    def open_dialog(self) -> None:
        """Open the main plugin dialog."""
        dialog = MainDialog()
        dialog.exec()
