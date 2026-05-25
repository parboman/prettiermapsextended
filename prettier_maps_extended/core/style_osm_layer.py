from qgis.core import (
    QgsFillSymbol,
    QgsLayerTreeLayer,
    QgsLineSymbol,
    QgsMarkerSymbol,
    QgsVectorLayer,
)
from qgis.PyQt.QtGui import QColor
from qgis.utils import iface

from prettier_maps_extended.core.layers import get_groups, is_quick_osm_layer


def apply_style_to_quick_osm_layers(colour: QColor) -> None:
    """
    Main styling function, linked to styling button. Styles all QuickOSM layers.
    """
    for child in get_groups():
        if not isinstance(child, QgsLayerTreeLayer):
            continue
        layer = child.layer()

        if is_quick_osm_layer(layer):
            style_single_layer(layer, colour)
            update_styled_layer(layer)


def style_single_layer(layer: QgsVectorLayer, colour: QColor) -> None:
    """Apply a uniform fill/line/marker style to a single QuickOSM layer."""
    symbol_renderer = layer.renderer()
    cur_symbol = symbol_renderer.symbol()

    basic_symbols = (QgsFillSymbol, QgsLineSymbol, QgsMarkerSymbol)
    symbol = None
    for symbol_type in basic_symbols:
        if isinstance(cur_symbol, symbol_type):
            symbol = symbol_type.createSimple({})

    # If the current symbol is not a basic type we can recreate, just recolour it.
    if symbol is None:
        symbol = cur_symbol

    # Fall back to purple if the user cancelled the colour picker.
    symbol.setColor(colour if colour.isValid() else QColor.fromRgb(155, 0, 155))
    symbol_renderer.setSymbol(symbol)


def update_styled_layer(layer: QgsVectorLayer) -> None:
    """
    Makes QGIS show the new style.
    """

    layer.triggerRepaint()
    iface.layerTreeView().refreshLayerSymbology(layer.id())
