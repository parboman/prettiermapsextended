# Changelog

## Unreleased

Not yet released. Whoever cuts the next version: turn this into its version
heading and add a matching `changelog=` block to `metadata.txt`.

### Fixed

- **Two basemaps no longer share sublayer checkboxes.** With two MapTiler
  basemaps loaded, the dialog matched sublayer checkboxes by style name across
  both, so unchecking a sublayer in one basemap switched off the same-named
  style in the other, and the first basemap's checkbox kept showing the old
  state. Checkboxes and filtering are now scoped to each vector tile layer.
  This supersedes the 1.5.1 known limitation below.

### Known limitation

- Inside a single basemap, two styles that share a style name under different
  source layers (for example a `fill` under `water` and a `fill` under
  `landcover`) still share one entry: only the later checkbox switches both
  styles, and toggling the earlier one has no effect. This predates 1.5.1.

## 1.5.2 — 2026-09-10

Hardening release, from a Bandit scan of the 1.5.1 package (10 findings, all
B101 `assert_used`, all Low severity — no vulnerability, but two of the
asserts were load-bearing).

### Fixed

- **A vector tile layer with no renderer crashed the dialog.** `filter_layers`
  and `populate_layers` asserted that every discovered layer carried a
  `QgsVectorTileBasicRenderer`; a layer whose renderer is missing — a corrupt
  project, or a script that cleared it — raised `AssertionError` and the plugin
  window never opened. Such a layer is now logged to the PrettierMaps channel
  and skipped, and the remaining layers are still listed and filtered.

### Changed

- **No `assert` statements left in the shipped package.** They were type
  narrowing for mypy, but `python -O` strips them, which turned the guards
  above into an `AttributeError` instead of an `AssertionError`. Every one is
  now an explicit guard: a bad layer is skipped, and the paths that cannot
  reach a project instance return an empty result. Bandit reports no issues.

## 1.5.1 — 2026-09-10

Bug-fix release. Every defect below was reproduced headlessly against real
QGIS 4.0.2 bindings before the fix, and the suite that pins them grew from
7 to 23 tests.

### Fixed

- **The dialog crashed on nested groups.** A MapTiler group inside another
  group raised `AttributeError: 'QgsLayerTreeGroup' object has no attribute
  'layer'` and the window never opened.
- **Layers outside the first top-level group were invisible.** Any unrelated
  group above the MapTiler group produced "No MapTiler Layers Found"; a second
  basemap group was silently ignored; a vector tile layer at the project root
  was never listed, and `filter_layers` left its styles alone whatever the
  checkboxes said. Discovery now walks the whole layer tree, skips unresolved
  layer nodes and de-duplicates by layer id.
- **Opening the plugin could blank out a basemap.** Styles whose source layer
  is not in the `POSSIBLE_LAYERS` whitelist get no checkbox, yet were switched
  off as soon as the dialog opened, with no way to restore them. Styles the
  dialog cannot control are now left exactly as the user set them.
- **`Style QuickOSM Layer` did nothing for grouped layers.** Only root-level
  nodes were walked. QuickOSM layers are now found through the project's layer
  registry, so layers inside groups are styled too.
- **Styling crashed on unresolved layers and on non-single-symbol renderers.**
  A broken project reference raised `AttributeError: 'NoneType' object has no
  attribute 'customProperty'`; a categorized, graduated or rule-based renderer
  raised on `symbol()`. Both are now logged to the PrettierMaps channel and
  skipped.
- **`Save Quick OSM Layers` saved every in-memory layer**, including unrelated
  scratch layers, replacing each one in the project with a GeoPackage-backed
  copy. Only QuickOSM layers are exported now; everything else is left alone.
- **Every save logged a GDAL warning** — `does not support layer creation
  option layerName`. The GeoPackage layer name is passed through
  `SaveVectorOptions.layerName` instead.
- **"No layers saved" was reported when there was simply nothing to export**
  (the project's QuickOSM layers were already file-backed), pointing at an
  empty message log.

### Added

- `make test-macos` — runs the test suite against the QGIS app's bundled
  Python on macOS, where `qgis.core` actually exists. `make test` still needs
  a QGIS-provisioned environment; `make test-in-docker` is unchanged.

### Known limitation

- With two MapTiler basemaps loaded at once, sublayer checkboxes are matched by
  style name across both, so toggling one can affect the other. Before 1.5.1
  the second basemap was not listed at all, so this case was unreachable.
  *(Superseded: fixed on `par/per-layer-sublayers`, see Unreleased.)*

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
