from .interfaces import IQgisInterface
from .plugin import PrettierMapsPlugin

__version__ = "1.5.0"


def classFactory(iface: IQgisInterface) -> PrettierMapsPlugin:
    return PrettierMapsPlugin(iface)  # pragma: no cover
