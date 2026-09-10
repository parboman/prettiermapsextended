# prettiermapsextended

Public fork of [PrettierMaps/PrettierMaps](https://github.com/PrettierMaps/PrettierMaps) — a QGIS plugin for splitting MapTiler vector tile layers and working with QuickOSM queries. Forked May 2026 to add QGIS 4 / Qt 6 compatibility, since the upstream is no longer regularly maintained.

## Working model

- Claude Opus writes the code, Codex (GPT-5.5) reviews each step via `/cowork` before commit —
  or the inverse (`/reversecowork`: Claude specs and reviews, Codex builds), which is what the
  1.5.1 defect sweep used. The Codex-headroom gate in global CLAUDE.md picks the lane.
- Pär is the human in the loop — reviews diffs, approves, ships. Cannot code.
- The README is intentionally transparent about this. Don't dilute it.

## Stack

- Python 3.9+, `uv` for dependency management.
- Qt via `qgis.PyQt` shim (the QGIS-vendored compatibility wrapper for PyQt5/PyQt6). **Never import `PyQt5` or `PyQt6` directly** — always go through `qgis.PyQt`.
- Plugin metadata: `qgisMinimumVersion=3.30`, `qgisMaximumVersion=4.99`.

## Conventions

- All Qt enums must be scoped (`Qt.AlignmentFlag.AlignLeft`, `Qgis.MessageLevel.Critical`, `Qt.CheckState.Checked`, etc.) — Qt 6 enforces this.
- `QAction` lives in `qgis.PyQt.QtGui` (Qt 6 moved it from `QtWidgets`).
- `Qt.ItemFlag.ItemIsTristate` was removed in Qt 6 — use `ItemIsAutoTristate`. Other Qt 5→6 renamed enum members are similar one-off gotchas; static review won't catch them, only launching the plugin in QGIS 4 will.
- Use `dialog.exec()`, never `dialog.exec_()`.
- For file writing, use `QgsVectorFileWriter.writeAsVectorFormatV3` with `SaveVectorOptions`. Always check the return tuple's error code before assuming success.
- Never disable a style the dialog does not show. `filter_layers` only touches styles whose
  **source** layer (`style.layerName()`, e.g. `water`) is in `config/layers.py`'s
  `POSSIBLE_LAYERS`; `populate_layers` builds checkboxes on the same test. Widen one without the
  other and merely opening the plugin switches off styles the user has no control to restore.
  Note the two look-alikes: `layerName()` is the vector tile source layer, `styleName()` is the
  label shown in the tree.
- Layer discovery walks the **whole** layer tree (`core.layers.get_vector_tile_layers`), not just
  top-level groups: a node's `.layer()` can be `None`, groups nest, and vector tile layers also sit
  at the project root. QuickOSM layers are found through the project's layer registry instead
  (`get_quick_osm_layers`), which sees inside groups for free.

## Before uploading to plugins.qgis.org

The QGIS plugin registry runs **flake8** against uploads with `W503` and `E704` enabled — both of which modern PEP 8 (and therefore `ruff`) consider acceptable. So `uv run ruff check` passing is **not enough**. Run:

```bash
uv run --with flake8 flake8 --max-line-length=100 prettier_maps_extended/
```

and fix any output before building the zip. Specifically avoid `from .x import *` (use explicit `__all__`), multi-line `and`/`or`/`|` chains where the operator leads the line (refactor to short-circuit if-returns or intermediate variables), and one-line `def x(): ...` abstract methods (use a docstring body instead). Don't reach for `# noqa` — restructure instead so it survives the next `ruff format` pass.

The `LICENSE` file must live inside `prettier_maps_extended/` (not just at repo root) for the registry validator to accept the upload. The Makefile keeps both copies in sync via the build.

The upload form's checklist asks you to confirm the repo matches the ZIP **excluding compiled
files** — and running the test suite leaves `__pycache__` inside the plugin package, which
`zip -r` used to sweep into the upload (21 files → 37). `make zip_plugin` now excludes bytecode
and `make test-macos` sets `PYTHONDONTWRITEBYTECODE`. Sanity-check a built zip with:

```bash
unzip -Z1 prettier_maps_extended.zip | grep -c pycache   # want 0
diff <(unzip -Z1 prettier_maps_extended.zip | grep -v '/$' | sort) \
     <(git ls-tree -r --name-only HEAD -- prettier_maps_extended | sort)
```

Run **Bandit** too — Pär scans uploads with one, and B101 (`assert_used`) fires on every
`assert` in the package:

```bash
uv run --with bandit bandit -r prettier_maps_extended/     # want: No issues identified
```

Keep it at zero by writing real guards, never `# nosec`. That rule has already paid for itself:
the asserts it flagged were the only thing between a rendererless `QgsVectorTileLayer` and a
crashed dialog, and `python -O` strips them anyway. Type-narrowing for mypy is not worth a
control-flow statement the interpreter is allowed to delete.

Add a `changelog=` block to `metadata.txt` for each release — the plugin page renders it and the
upload form pre-fills its description box from it (1.5.0 shipped without one).

## Useful commands

- `make zip_plugin` — build the installable QGIS plugin zip
- `make test` — run pytest suite
- `make test-macos` — run tests using the macOS QGIS app's bundled Python
- `make test-in-docker` — run tests in a containerized QGIS env

## Layout

- `prettier_maps_extended/` — the actual QGIS plugin (loaded by QGIS). The directory name **is** the plugin identifier in the QGIS plugin registry — renamed from `prettier_maps` so this fork can coexist with the upstream plugin.
- `main.py` — standalone dev entry point (not packaged into the plugin zip)
- `tests/core/` — pytest suite, runs against real QGIS bindings
- `docs/` — mkdocs site source
