import tempfile
from pathlib import Path
from typing import List

import pytest
from qgis.core import (
    Qgis,
    QgsCategorizedSymbolRenderer,
    QgsLayerTreeGroup,
    QgsLayerTreeLayer,
    QgsMapLayer,
    QgsProject,
    QgsRendererCategory,
    QgsSingleSymbolRenderer,
    QgsSymbol,
    QgsVectorLayer,
    QgsVectorTileBasicRenderer,
    QgsVectorTileBasicRendererStyle,
    QgsVectorTileLayer,
)
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QColor
from qgis.testing import start_app

from prettier_maps_extended.core.layers import (
    filter_layers,
    get_layers_from_group,
    get_vector_tile_layers,
    is_quick_osm_layer,
)
from prettier_maps_extended.core.save_osm_layer import save_quick_osm_layers
from prettier_maps_extended.core.style_osm_layer import (
    apply_style_to_quick_osm_layers,
    style_single_layer,
)
from prettier_maps_extended.ui.dialog import MainDialog


@pytest.fixture
def rendererless_and_healthy_layers():
    start_app()
    project = QgsProject.instance()
    group = project.layerTreeRoot().addGroup("Renderer regression")
    broken = QgsVectorTileLayer()
    broken.setName("Rendererless tiles")
    broken.setRenderer(None)
    healthy = QgsVectorTileLayer()
    healthy.setName("Healthy tiles")
    renderer = QgsVectorTileBasicRenderer()
    water = QgsVectorTileBasicRendererStyle()
    water.setLayerName("water")
    water.setStyleName("water fill")
    water.setEnabled(False)
    building = QgsVectorTileBasicRendererStyle()
    building.setLayerName("building")
    building.setStyleName("building fill")
    building.setEnabled(True)
    renderer.setStyles([water, building])
    healthy.setRenderer(renderer)
    group.addLayer(broken)
    group.addLayer(healthy)
    try:
        yield project, broken, healthy
    finally:
        project.layerTreeRoot().removeChildNode(group)


def test_filter_layers_skips_rendererless_and_filters_healthy(
    rendererless_and_healthy_layers,
) -> None:
    project, broken, healthy = rendererless_and_healthy_layers

    filter_layers({"water fill"}, project)

    assert broken.renderer() is None
    assert [style.isEnabled() for style in healthy.renderer().styles()] == [True, False]


def test_dialog_opens_with_rendererless_layer(rendererless_and_healthy_layers) -> None:
    _, broken, _ = rendererless_and_healthy_layers

    dialog = MainDialog()
    try:
        assert broken.name() not in dialog.layer_checkboxes
        all_layers = dialog.tree_widget.topLevelItem(0)
        assert all_layers.childCount() == 1
        assert all_layers.child(0).text(0) == "Healthy tiles"
    finally:
        dialog.close()


def test_dialog_keeps_healthy_checkboxes_alongside_rendererless_layer(
    rendererless_and_healthy_layers,
) -> None:
    _, _, healthy = rendererless_and_healthy_layers

    dialog = MainDialog()
    try:
        parent = dialog.layer_checkboxes[healthy.name()]
        assert parent.childCount() == 2
        water = dialog.layer_checkboxes["water fill"]
        building = dialog.layer_checkboxes["building fill"]
        assert water.parent().parent() is parent
        assert building.parent().parent() is parent
        assert water.checkState(0) == Qt.CheckState.Unchecked
        assert building.checkState(0) == Qt.CheckState.Checked
        assert [style.isEnabled() for style in healthy.renderer().styles()] == [
            False,
            True,
        ]
    finally:
        dialog.close()


def test_get_layers_from_group_with_empty_group() -> None:
    group = QgsLayerTreeGroup("empty_group")
    result = get_layers_from_group(group)
    assert result == []


def test_get_layers_from_group() -> None:
    group = QgsLayerTreeGroup("test_group")

    # Create valid QgsVectorTileLayer objects
    v1 = QgsVectorTileLayer(
        "type=xyz&url=http://tile.stamen.com/toner/{z}/{x}/{y}.png",
        "vector_tile_1",
    )
    v2 = QgsVectorTileLayer(
        "type=xyz&url=http://tile.stamen.com/toner/{z}/{x}/{y}.png",
        "vector_tile_2",
    )

    # Create QgsLayerTreeLayer objects with valid QgsVectorTileLayer objects
    layer1 = QgsLayerTreeLayer(v1)
    layer2 = QgsLayerTreeLayer(v2)
    non_layer = QgsLayerTreeLayer(QgsVectorLayer("Point?crs=EPSG:4326"))

    group.addChildNode(layer1)
    group.addChildNode(layer2)
    group.addChildNode(non_layer)
    result = get_layers_from_group(group)
    assert len(result) == 2
    assert result[0] == layer1.layer()
    assert result[1] == layer2.layer()


def test_get_layers_from_group_with_only_non_vector_tile_layers() -> None:
    group = QgsLayerTreeGroup("non_vector_tile_group")

    non_layer1 = QgsLayerTreeLayer(
        QgsVectorLayer("Point?crs=EPSG:4326", "non_vector_tile_layer_1", "memory")
    )
    non_layer2 = QgsLayerTreeLayer(
        QgsVectorLayer("LineString?crs=EPSG:4326", "non_vector_tile_layer_2", "memory")
    )

    group.addChildNode(non_layer1)
    group.addChildNode(non_layer2)

    result = get_layers_from_group(group)
    assert result == []


def test_filter_layers() -> None:
    instance = QgsProject()
    assert instance is not None
    root = instance.layerTreeRoot()
    assert root is not None

    group = QgsLayerTreeGroup("test_group")
    root.addChildNode(group)

    layer = QgsVectorTileLayer()
    tree_layer = QgsLayerTreeLayer(layer)
    group.addChildNode(tree_layer)

    renderer = QgsVectorTileBasicRenderer()
    style1 = QgsVectorTileBasicRendererStyle()
    style1.setStyleName("water")
    style1.setLayerName("water")
    style2 = QgsVectorTileBasicRendererStyle()
    style2.setStyleName("building")
    style2.setLayerName("building")
    renderer.setStyles([style1, style2])
    layer.setRenderer(renderer)

    filter_layers({"water"}, instance)

    renderer = layer.renderer()
    assert isinstance(renderer, QgsVectorTileBasicRenderer)
    styles = renderer.styles()

    assert styles[0].isEnabled() is True
    assert styles[1].isEnabled() is False


def test_get_vector_tile_layers_at_project_root() -> None:
    project = QgsProject()
    layer = QgsVectorTileLayer()
    project.layerTreeRoot().addLayer(layer)

    assert get_vector_tile_layers(project) == [layer]


def test_get_vector_tile_layers_in_nested_subgroup() -> None:
    project = QgsProject()
    group = project.layerTreeRoot().addGroup("Basemaps")
    nested = group.addGroup("MapTiler").addGroup("Tiles")
    layer = QgsVectorTileLayer()
    nested.addLayer(layer)

    assert get_vector_tile_layers(project) == [layer]
    assert get_layers_from_group(group) == [layer]


def test_get_vector_tile_layers_in_sibling_groups() -> None:
    project = QgsProject()
    root = project.layerTreeRoot()
    root.addGroup("Unrelated")
    first = root.addGroup("A")
    second = root.addGroup("B")
    layer_a = QgsVectorTileLayer()
    layer_b = QgsVectorTileLayer()
    first.addLayer(layer_a)
    second.addLayer(layer_b)
    second.addLayer(layer_a)

    assert get_vector_tile_layers(project) == [layer_a, layer_b]
    assert get_layers_from_group(root) == [layer_a, layer_b]


def test_get_vector_tile_layers_skips_unresolved_node() -> None:
    project = QgsProject()
    group = project.layerTreeRoot().addGroup("Basemaps")
    missing = QgsLayerTreeLayer("missing-id", "missing", "/nonexistent.gpkg", "ogr")
    assert missing.layer() is None
    group.addChildNode(missing)
    layer = QgsVectorTileLayer()
    group.addLayer(layer)

    assert get_vector_tile_layers(project) == [layer]
    assert get_layers_from_group(group) == [layer]


def test_filter_layers_at_project_root() -> None:
    project = QgsProject()
    layer = QgsVectorTileLayer()
    project.layerTreeRoot().addLayer(layer)
    renderer = QgsVectorTileBasicRenderer()
    water = QgsVectorTileBasicRendererStyle()
    water.setStyleName("water")
    water.setLayerName("water")
    water.setEnabled(False)
    building = QgsVectorTileBasicRendererStyle()
    building.setStyleName("building")
    building.setLayerName("building")
    building.setEnabled(True)
    renderer.setStyles([water, building])
    layer.setRenderer(renderer)

    filter_layers({"water"}, project)

    styles = layer.renderer().styles()
    assert [(style.styleName(), style.isEnabled()) for style in styles] == [
        ("water", True),
        ("building", False),
    ]


@pytest.fixture
def mixed_source_styles():
    project = QgsProject()
    layer = QgsVectorTileLayer()
    project.layerTreeRoot().addLayer(layer)
    renderer = QgsVectorTileBasicRenderer()
    uncontrolled = QgsVectorTileBasicRendererStyle()
    uncontrolled.setLayerName("custom_source")
    uncontrolled.setStyleName("water")
    uncontrolled.setEnabled(True)
    controlled = QgsVectorTileBasicRendererStyle()
    controlled.setLayerName("water")
    controlled.setStyleName("water fill")
    controlled.setEnabled(True)
    renderer.setStyles([uncontrolled, controlled])
    layer.setRenderer(renderer)
    return project, layer


def test_filter_layers_preserves_enabled_unlisted_source(mixed_source_styles) -> None:
    project, layer = mixed_source_styles

    filter_layers(set(), project)

    assert layer.renderer().styles()[0].isEnabled() is True


def test_filter_layers_preserves_disabled_unlisted_source(mixed_source_styles) -> None:
    project, layer = mixed_source_styles
    renderer = layer.renderer()
    styles = renderer.styles()
    styles[0].setEnabled(False)
    renderer.setStyles(styles)

    filter_layers({"water"}, project)

    assert layer.renderer().styles()[0].isEnabled() is False


def test_filter_layers_disables_unselected_whitelisted_source(
    mixed_source_styles,
) -> None:
    project, layer = mixed_source_styles

    filter_layers(set(), project)

    styles = layer.renderer().styles()
    assert styles[0].isEnabled() is True
    assert styles[1].isEnabled() is False


def all_elements_equal(iterable) -> bool:
    return iterable.count(iterable[0]) == len(iterable)


def test_single_layer_styling() -> None:
    instance = QgsProject.instance()
    assert instance is not None

    geom_type_names = {
        Qgis.GeometryType.Point: "point",
        Qgis.GeometryType.Line: "line",
        Qgis.GeometryType.Polygon: "polygon",
    }
    layers = []
    for geom_type, current_geom_type in geom_type_names.items():
        layer = QgsVectorLayer(
            f"{current_geom_type}?crs=EPSG:4326",
            f"{current_geom_type}_layer",
            "memory",
        )
        symbol = QgsSymbol.defaultSymbol(geom_type)
        renderer = QgsSingleSymbolRenderer(symbol)
        layer.setRenderer(renderer)

        layers.append(layer)

    # Use a predefined color for testing
    test_color = QColor(255, 0, 0)  # Red color

    for layer in layers:
        style_single_layer(layer, test_color)

    colors = [layer.renderer().symbol().color() for layer in layers]
    assert all_elements_equal(colors)
    assert all(color == test_color for color in colors)


@pytest.mark.parametrize("depth", [1, 3])
def test_grouped_quick_osm_layer_is_styled(depth) -> None:
    project = QgsProject.instance()
    group = project.layerTreeRoot().addGroup("QuickOSM results")
    layer = QgsVectorLayer("Point?crs=EPSG:4326", "quickosm", "memory")
    layer.setCustomProperty("variableNames", ["quickosm_query"])
    layer.renderer().symbol().setColor(QColor(255, 0, 0))
    project.addMapLayer(layer, False)
    nested = group
    for _ in range(depth - 1):
        nested = nested.addGroup("Nested results")
    nested.addLayer(layer)
    try:
        apply_style_to_quick_osm_layers(QColor(0, 255, 0))
        assert layer.renderer().symbol().color() == QColor(0, 255, 0)
    finally:
        project.removeMapLayer(layer.id())
        project.layerTreeRoot().removeChildNode(group)


def test_quick_osm_styling_skips_unresolved_node() -> None:
    root = QgsProject.instance().layerTreeRoot()
    missing = QgsLayerTreeLayer("missing-id-123", "missing", "/nonexistent.gpkg", "ogr")
    assert missing.layer() is None
    root.addChildNode(missing)
    try:
        apply_style_to_quick_osm_layers(QColor(0, 255, 0))
    finally:
        root.removeChildNode(missing)


def test_categorized_quick_osm_layer_is_unchanged() -> None:
    layer = QgsVectorLayer("Point?crs=EPSG:4326", "categorized", "memory")
    layer.setCustomProperty("variableNames", ["quickosm_query"])
    symbol = QgsSymbol.defaultSymbol(Qgis.GeometryType.Point)
    symbol.setColor(QColor(255, 0, 0))
    layer.setRenderer(
        QgsCategorizedSymbolRenderer(
            "kind", [QgsRendererCategory("a", symbol, "Category A")]
        )
    )
    renderer = layer.renderer()

    style_single_layer(layer, QColor(0, 255, 0))

    assert layer.renderer() is renderer
    assert renderer.classAttribute() == "kind"
    category = renderer.categories()[0]
    assert category.value() == "a"
    assert category.label() == "Category A"
    assert category.symbol().color() == QColor(255, 0, 0)


def test_is_quick_osm_layer_with_none() -> None:
    assert is_quick_osm_layer(None) is False


def test_non_quick_osm_layer_is_not_styled() -> None:
    project = QgsProject.instance()
    layer = QgsVectorLayer("Point?crs=EPSG:4326", "ordinary", "memory")
    layer.renderer().symbol().setColor(QColor(255, 0, 0))
    project.addMapLayer(layer)
    try:
        apply_style_to_quick_osm_layers(QColor(0, 255, 0))
        assert layer.renderer().symbol().color() == QColor(255, 0, 0)
    finally:
        project.removeMapLayer(layer.id())


def test_save_quick_osm_layers():
    project = QgsProject.instance()

    layer1 = QgsVectorLayer("Point?crs=EPSG:4326", "test_layer1", "memory")
    layer1.setCustomProperty("variableNames", ["quickosm_query"])
    project.addMapLayer(layer1)
    layer2 = QgsVectorLayer("LineString?crs=EPSG:4326", "test_layer2", "memory")
    layer2.setCustomProperty("variableNames", ["quickosm_query"])
    project.addMapLayer(layer2)

    with tempfile.TemporaryDirectory() as temp_dir:
        save_quick_osm_layers(temp_dir)

        output_file1 = Path(temp_dir) / "test_layer1_point.gpkg"
        output_file2 = Path(temp_dir) / "test_layer2_line.gpkg"
        assert output_file1.exists()
        assert output_file2.exists()

        # Close the layers to release the file handles
        layer1 = None
        layer2 = None

        qml_file1 = Path(temp_dir) / "test_layer1_point.qml"
        qml_file2 = Path(temp_dir) / "test_layer2_line.qml"
        assert qml_file1.exists()
        assert qml_file2.exists()

        new_layer1 = QgsProject.instance().mapLayersByName("test_layer1_point")
        new_layer2 = QgsProject.instance().mapLayersByName("test_layer2_line")
        assert len(new_layer1) == 1
        assert len(new_layer2) == 1
        assert new_layer1[0].isValid()
        assert new_layer2[0].isValid()

        # Remove the new layers from the project to release the file handles
        QgsProject.instance().removeMapLayer(new_layer1[0].id())
        QgsProject.instance().removeMapLayer(new_layer2[0].id())


def test_save_quick_osm_layers_leaves_scratch_layer_untouched(tmp_path):
    project = QgsProject.instance()
    scratch = QgsVectorLayer("Point?crs=EPSG:4326", "my_scratch_notes", "memory")
    scratch_id = scratch.id()
    project.addMapLayer(scratch)
    try:
        result = save_quick_osm_layers(str(tmp_path))

        assert result.saved == 0
        assert result.skipped == 0
        assert result.failed == 0
        assert list(tmp_path.iterdir()) == []
        assert project.mapLayers() == {scratch_id: scratch}
        assert scratch.name() == "my_scratch_notes"
        assert scratch.isValid()
        assert scratch.providerType() == "memory"
    finally:
        project.removeAllMapLayers()


def test_save_quick_osm_layers_in_mixed_project(tmp_path):
    project = QgsProject.instance()
    scratch = QgsVectorLayer("Point?crs=EPSG:4326", "my_scratch_notes", "memory")
    scratch_id = scratch.id()
    quick_osm = QgsVectorLayer("Point?crs=EPSG:4326", "quickosm", "memory")
    quick_osm.setCustomProperty("variableNames", ["quickosm_query"])
    quick_osm_id = quick_osm.id()
    project.addMapLayer(scratch)
    project.addMapLayer(quick_osm)
    try:
        result = save_quick_osm_layers(str(tmp_path))

        assert result.saved == 1
        assert result.skipped == 0
        assert result.failed == 0
        assert {path.name for path in tmp_path.iterdir()} == {
            "quickosm_point.gpkg",
            "quickosm_point.qml",
        }
        assert project.mapLayer(scratch_id) is scratch
        assert scratch.name() == "my_scratch_notes"
        assert scratch.isValid()
        assert scratch.providerType() == "memory"
        assert project.mapLayer(quick_osm_id) is None
        saved_layers = project.mapLayersByName("quickosm_point")
        assert len(saved_layers) == 1
        assert saved_layers[0].isValid()
        assert saved_layers[0].providerType() == "ogr"
        assert len(project.mapLayers()) == 2
    finally:
        project.removeAllMapLayers()
