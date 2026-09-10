from typing import Iterator, List, Optional

from qgis.core import (
    Qgis,
    QgsLayerTreeGroup,
    QgsLayerTreeLayer,
    QgsLayerTreeNode,
    QgsMessageLog,
    QgsProject,
    QgsVectorLayer,
    QgsVectorTileBasicRenderer,
    QgsVectorTileBasicRendererStyle,
    QgsVectorTileLayer,
)

from prettier_maps_extended.config.layers import POSSIBLE_LAYERS


def _iter_vector_tile_layers(node: QgsLayerTreeNode) -> Iterator[QgsVectorTileLayer]:
    for child in node.children():
        if isinstance(child, QgsLayerTreeLayer):
            layer = child.layer()
            if isinstance(layer, QgsVectorTileLayer):
                yield layer
        else:
            yield from _iter_vector_tile_layers(child)


def get_layers_from_group(group: QgsLayerTreeGroup) -> List[QgsVectorTileLayer]:
    layers = []
    seen = set()
    for layer in _iter_vector_tile_layers(group):
        if layer.id() not in seen:
            seen.add(layer.id())
            layers.append(layer)
    return layers


def get_vector_tile_layers(
    project: Optional[QgsProject] = None,
) -> List[QgsVectorTileLayer]:
    instance = project or QgsProject.instance()
    if instance is None:
        return []
    root = instance.layerTreeRoot()
    if root is None:
        return []
    return get_layers_from_group(root)


def refresh_layer(
    layer: QgsVectorTileLayer, renderer: QgsVectorTileBasicRenderer
) -> None:
    """
    Refreshes a given layer.
    """

    layer.setRenderer(renderer.clone())
    layer.setBlendMode(layer.blendMode())
    layer.setOpacity(layer.opacity())


def get_groups(project: Optional[QgsProject] = None) -> list[QgsLayerTreeNode]:
    """Superseded by get_vector_tile_layers; kept for compatibility."""
    instance = project or QgsProject.instance()
    if instance is None:
        return []
    root = instance.layerTreeRoot()
    if root is None:
        return []

    return root.children()


def filter_layers(
    layers_to_turn_on: set[str], instance_to_filter: Optional[QgsProject] = None
) -> None:
    """
    Given a set of layers, shows only those layers while hiding others.

    :param layers_to_turn_on: Set of layers to be shown
    :param instance_to_filter: Instance of a QGISProject to filter on.
        If none is provided, the current QGIS project is used instead.
    """

    for layer in get_vector_tile_layers(instance_to_filter):
        renderer = layer.renderer()
        if not isinstance(renderer, QgsVectorTileBasicRenderer):
            QgsMessageLog.logMessage(
                f"Skipping layer {layer.name()!r}: "
                "missing or unsupported tile renderer",
                "PrettierMaps",
                Qgis.MessageLevel.Warning,
            )
            continue

        styles = renderer.styles()
        new_styles: list[QgsVectorTileBasicRendererStyle] = []
        for style in styles:
            if style.layerName() in POSSIBLE_LAYERS:
                style.setEnabled(style.styleName() in layers_to_turn_on)
            new_styles.append(style)

        renderer.setStyles(new_styles)
        refresh_layer(layer, renderer)


def has_layers() -> bool:
    """Superseded by get_vector_tile_layers; kept for compatibility."""
    instance = QgsProject.instance()
    if instance is None:
        return False
    layers = instance.mapLayers()
    return bool(layers)


def is_quick_osm_layer(layer: QgsVectorLayer) -> bool:
    """
    Simple filter for identifying which layers are the results of QuickOSM queries.
    """
    if layer is None:
        return False
    variable_names = layer.customProperty("variableNames")
    if variable_names is None:
        return False
    if "quickosm_query" not in variable_names:
        return False
    return True


def get_quick_osm_layers(
    project: Optional[QgsProject] = None,
) -> List[QgsVectorLayer]:
    """Return every QuickOSM vector layer registered in the project."""
    instance = project or QgsProject.instance()
    if instance is None:
        return []
    return [
        layer
        for layer in instance.mapLayers().values()
        if isinstance(layer, QgsVectorLayer) and is_quick_osm_layer(layer)
    ]


def has_quick_osm_layers() -> bool:
    """
    Simple check that there is at least one QuickOSM layer.
    """
    return bool(get_quick_osm_layers())
