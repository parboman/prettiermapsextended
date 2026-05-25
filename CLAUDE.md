# prettiermapsextended

Public fork of [PrettierMaps/PrettierMaps](https://github.com/PrettierMaps/PrettierMaps) — a QGIS plugin for splitting MapTiler vector tile layers and working with QuickOSM queries. Forked May 2026 to add QGIS 4 / Qt 6 compatibility, since the upstream is no longer regularly maintained.

## Working model

- Claude Opus writes the code, Codex (GPT-5.5) reviews each step via `/cowork` before commit.
- Pär is the human in the loop — reviews diffs, approves, ships. Cannot code.
- The README is intentionally transparent about this. Don't dilute it.

## Stack

- Python 3.9+, `uv` for dependency management.
- Qt via `qgis.PyQt` shim (the QGIS-vendored compatibility wrapper for PyQt5/PyQt6). **Never import `PyQt5` or `PyQt6` directly** — always go through `qgis.PyQt`.
- Plugin metadata: `qgisMinimumVersion=3.30`, `qgisMaximumVersion=4.99`.

## Conventions

- All Qt enums must be scoped (`Qt.AlignmentFlag.AlignLeft`, `Qgis.MessageLevel.Critical`, `Qt.CheckState.Checked`, etc.) — Qt 6 enforces this.
- `QAction` lives in `qgis.PyQt.QtGui` (Qt 6 moved it from `QtWidgets`).
- Use `dialog.exec()`, never `dialog.exec_()`.
- For file writing, use `QgsVectorFileWriter.writeAsVectorFormatV3` with `SaveVectorOptions`. Always check the return tuple's error code before assuming success.

## Useful commands

- `make zip_plugin` — build the installable QGIS plugin zip
- `make test` — run pytest suite
- `make test-in-docker` — run tests in a containerized QGIS env

## Layout

- `prettier_maps/` — the actual QGIS plugin (loaded by QGIS)
- `main.py` — standalone dev entry point (not packaged into the plugin zip)
- `tests/core/` — pytest suite, runs against real QGIS bindings
- `docs/` — mkdocs site source
