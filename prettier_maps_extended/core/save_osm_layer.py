from pathlib import Path
from typing import NamedTuple, Tuple

from qgis.core import (
    Qgis,
    QgsMessageLog,
    QgsProject,
    QgsVectorFileWriter,
    QgsVectorLayer,
)

from prettier_maps_extended.core.layers import is_quick_osm_layer


class SaveResult(NamedTuple):
    saved: int
    skipped: int
    failed: int

    @property
    def ok(self) -> bool:
        return self.skipped == 0 and self.failed == 0

    @property
    def total(self) -> int:
        return self.saved + self.skipped + self.failed


def is_to_be_saved(layer: QgsVectorLayer) -> bool:
    """
    Simple filter for selecting which layers will be saved.
    """
    return (
        isinstance(layer, QgsVectorLayer)
        and layer.isValid()
        and layer.dataProvider().name() == "memory"
    )


def get_file_paths(directory: str, name: str) -> Tuple[str, Path]:
    """
    Generates file path information given a directory and file name.

    :param directory: Location of file.
    :param name: File name.
    """

    output_file_str = str(Path(directory) / f"{name}.gpkg")
    qml_file = Path(directory) / f"{name}.qml"

    return output_file_str, qml_file


def add_permanent_layer(
    instance: QgsProject, qml: Path, output_file: str, name: str
) -> None:
    """
    Creates a permanent version of a layer and loads this into the current project.

    :param instance: Current project.
    :param qml: Path of the style file.
    :param output_file: Path of the output file.
    :param name: Name of the permanent layer.
    """
    permanent_layer = QgsVectorLayer(f"{output_file}|layername={name}", name, "ogr")
    instance.addMapLayer(permanent_layer)
    permanent_layer.loadNamedStyle(str(qml))


def save_quick_osm_layers(output_directory: str) -> SaveResult:
    """
    Saves all layers which are outputs of QuickOSM queries.

    Returns a SaveResult tallying saved / skipped / failed layers, so the
    caller can surface accurate status instead of always reporting success.
    """

    instance = QgsProject.instance()
    assert instance is not None

    quick_osm_geoms = {
        Qgis.GeometryType.Point: "point",
        Qgis.GeometryType.Line: "line",
        Qgis.GeometryType.Polygon: "polygon",
    }

    saved = 0
    skipped = 0
    failed = 0

    for layer in instance.mapLayers().values():
        if not is_to_be_saved(layer):
            continue

        geom_type = layer.geometryType()
        geom_type_str = quick_osm_geoms.get(geom_type)
        if geom_type_str is None:
            QgsMessageLog.logMessage(
                f"Skipping layer {layer.name()!r}: "
                f"unsupported geometry type {geom_type!r}",
                "PrettierMaps",
                Qgis.MessageLevel.Warning,
            )
            skipped += 1
            continue

        original_name = layer.name()
        new_layer_name = f"{original_name}_{geom_type_str}"

        output_file_str, qml_file = get_file_paths(output_directory, new_layer_name)

        # Save the temporary layer to a GeoPackage. Rename the source layer
        # only after a successful write so a failed save does not leave the
        # in-memory layer with an inflated name on retry.
        options = QgsVectorFileWriter.SaveVectorOptions()
        options.driverName = "GPKG"
        options.fileEncoding = "UTF-8"
        options.layerOptions = [
            "GEOMETRY_NAME=geom",
            f"layerName={new_layer_name}",
        ]
        result = QgsVectorFileWriter.writeAsVectorFormatV3(
            layer,
            output_file_str,
            instance.transformContext(),
            options,
        )
        error_code = result[0]
        if error_code != QgsVectorFileWriter.WriterError.NoError:
            error_message = result[1] if len(result) > 1 else ""
            QgsMessageLog.logMessage(
                f"Failed to save layer {original_name!r} to "
                f"{output_file_str}: {error_message}",
                "PrettierMaps",
                Qgis.MessageLevel.Critical,
            )
            failed += 1
            continue

        layer.setName(new_layer_name)
        layer.saveNamedStyle(str(qml_file))
        add_permanent_layer(instance, qml_file, output_file_str, new_layer_name)
        instance.removeMapLayer(layer.id())
        saved += 1

    return SaveResult(saved=saved, skipped=skipped, failed=failed)
