# Changelog

## 1.5.0 — 2026-05-25

First release of **Prettier Maps (Extended)**, a public fork of [PrettierMaps/PrettierMaps](https://github.com/PrettierMaps/PrettierMaps) v1.4.4.

### Added

- **QGIS 4.0 / Qt 6 support.** Plugin metadata declares `qgisMinimumVersion=3.30` and `qgisMaximumVersion=4.99`, so the same build installs on both QGIS 3.30+ and QGIS 4.x.
- **Accurate save-result reporting.** `save_quick_osm_layers()` now returns a `SaveResult` tuple with per-layer saved/skipped/failed counts; the dialog reports success, partial success, or failure accordingly instead of always showing "All OSM layers have been saved successfully."
- **Writer error surfacing.** `QgsVectorFileWriter` failures and unsupported geometry types are logged to the `PrettierMaps` channel in the QGIS message log instead of being silently swallowed.
- `CHANGELOG.md` and project-level `CLAUDE.md` documenting the fork's working model.

### Changed

- **Plugin directory renamed** `prettier_maps/` → `prettier_maps_extended/` so the fork is a distinct, co-installable plugin in QGIS — the directory name is the registry identifier, not the metadata display name.
- All `PyQt5.*` imports replaced with `qgis.PyQt.*` (the QGIS-vendored Qt 5/6 compatibility shim).
- `QAction` moved to its Qt 6 location: `qgis.PyQt.QtGui` (was `QtWidgets`).
- `dialog.exec_()` → `dialog.exec()`.
- `Qt.ItemFlag.ItemIsTristate` → `Qt.ItemFlag.ItemIsAutoTristate` (Qt 6 rename).
- All `Qgis.*` enums scoped: `Qgis.Critical/Warning/Success/Info` → `Qgis.MessageLevel.*`.
- Geometry-type lookup switched from `("point", "line", "polygon")[geom_type]` to a dict keyed on `Qgis.GeometryType` — Qt 6 enums are no longer int-indexable.
- Deprecated `QgsVectorFileWriter.writeAsVectorFormat` replaced with `writeAsVectorFormatV3` + `SaveVectorOptions`.
- Layer rename now happens **after** a successful write, not before, so a failed save no longer leaves the in-memory layer with an inflated name on retry.
- Warning text "no OSM layers" → "no QuickOSM layers" to disambiguate from MapTiler/OpenMapTiles (which also derives from OSM but is a different layer category).
- Plugin window title shows "Prettier Maps (Extended)" matching the registry name.

### Removed

- Direct `pyqt5` dependency from `pyproject.toml`. QGIS ships its own Qt bindings.
- Dead `show_message` method on `MainDialog` (referenced a non-existent `message_label` attribute).
- Duplicate `QgsMessageBar` creation in `init_ui`.
- Unused imports (`QPainter`, `QMessageBox`).

### Credits

See [README.md](README.md#credits). Original plugin by the University of Glasgow team. This fork: code by Claude Opus 4.7, reviewed by OpenAI Codex (GPT-5.5) via the `/cowork` pattern, shipped by Pär Boman.
