<h1 align="center">Prettier Maps (Extended) 1.5.0</h1>

<p align="center">
  <img src="prettier_maps_extended/assets/logo.png" alt="Prettier Maps logo" width="350">
</p>
<p align="center">
    <em>Style and work with maps easily in QGIS — now with QGIS 4 / Qt 6 support</em>
</p>

---

This is a public, AI-maintained fork of [PrettierMaps/PrettierMaps](https://github.com/PrettierMaps/PrettierMaps) — the original University of Glasgow third-year project, which the original authors marked as no longer regularly maintained as of v1.4.4.

This fork exists to keep the plugin working on **QGIS 4 (Qt 6)**, released March 2026.

**Issues**: <a href="https://github.com/parboman/prettiermapsextended/issues" target="_blank">github.com/parboman/prettiermapsextended/issues</a>

**Original upstream**: <a href="https://github.com/PrettierMaps/PrettierMaps" target="_blank">github.com/PrettierMaps/PrettierMaps</a>

---

## Credits

### Original PrettierMaps authors (University of Glasgow)

This plugin started as a 3rd-year undergraduate project at the University of Glasgow. All the actual design work, original architecture, the working plugin, and the name belong to them. This fork is a small compatibility update on top of their finished work.

- **Matthew McKee** ([@MatthewMckee4](https://github.com/MatthewMckee4)) — original maintainer
- **Fraser Spalding**
- **Nicole Sung**
- **Irene Hanna Anu**
- **Ben Whitehead**
- **Daniel Deneb Mecha Martín**

### Spiritual ancestor

The PrettierMaps name nods to [**marceloprates/prettymaps**](https://github.com/marceloprates/prettymaps) — Marcelo Prates' Python library for generating beautiful, customizable city maps from OpenStreetMap data. The University of Glasgow team's PrettierMaps is a separate piece of software targeting QGIS workflows, but the lineage of inspiration is worth naming. If you want to make pretty maps as standalone Python art, look at `prettymaps`.

### This fork

- **Pär Boman** ([@parboman](https://github.com/parboman)) — human in the loop
- **Claude Opus 4.7** (Anthropic) — wrote the code
- **OpenAI Codex (GPT-5.5)** — code review partner, via the [/cowork pattern](https://github.com/anthropics/claude-code)

#### How this fork is actually produced

I should be upfront about how this works, because pretending otherwise would be dishonest:

- **I, Pär, do not code.** I cannot write Python or PyQt. I read the diffs, I push back when something feels off, and I misunderstand at least one thing per session. I'm the product manager, not the engineer.
- **Claude Opus 4.7 writes 100% of the code in this repo.** Every line in this fork's diff against upstream was written by Claude.
- **Codex reviews every step** before commit. The first round of this migration caught a P1 blocker — `QAction` moved from `QtWidgets` to `QtGui` in Qt 6 — that Claude had missed. The review loop is real, not theater.
- **You are reading documentation written by Claude.** Including this section. If that's a problem for you, the [original upstream](https://github.com/PrettierMaps/PrettierMaps) is human-authored and works on QGIS 3.

If something is broken, blame me — I shipped it. If something is correct, credit the original authors for the design and Claude+Codex for keeping it building. That's the honest split.

---

## What changed vs. upstream

The 1.4.4 → 1.5.0 diff is a QGIS 4 / Qt 6 compatibility pass:

- `PyQt5.*` imports → `qgis.PyQt.*` shim (works on both Qt 5 and Qt 6)
- `QAction` moved to `QtGui` (Qt 6 relocation)
- `dialog.exec_()` → `dialog.exec()`
- Unscoped `Qgis.Critical`/`Warning`/`Success`/`Info` enums → `Qgis.MessageLevel.*`
- `quick_osm_geoms` tuple-indexed-by-int → dict keyed on `Qgis.GeometryType` enum
- Deprecated `QgsVectorFileWriter.writeAsVectorFormat` → `writeAsVectorFormatV3` with `SaveVectorOptions`
- Writer return value is now checked; failures log to the QGIS message log instead of silently reporting success
- Bumped `qgisMinimumVersion` from `3.0` to `3.30` (required by `Qgis.GeometryType`) and added `qgisMaximumVersion=4.99` per the [official QGIS 4 plugin migration guide](https://plugins.qgis.org/docs/migrate-qgis4)

The plugin's actual behavior and UI are unchanged.

---

## Using PrettierMaps

Make sure you have QGIS 3.30+ or QGIS 4.0+ installed.

The only dependency is MapTiler. To make full use of the plugin, use it in conjunction with MapTiler and QuickOSM (both QGIS plugins).

#### In QGIS

1. Install the plugin from the QGIS plugin manager (or via the zip build below)
2. Install the MapTiler and QuickOSM plugins
3. Run the plugin from the QGIS plugins menu

#### Building locally

```bash
make zip_plugin
```

### Usage

Open a `Vector` map from MapTiler, then open Prettier Maps. You'll see a list of layers to enable/disable.

<figure align="center">
  <img src="docs/assets/ui.png" alt="Prettier Maps plugin UI" width="700">
  <figcaption>Figure 1: Example UI</figcaption>
</figure>

To style or save a QuickOSM query: create a QuickOSM query, then open Prettier Maps and use `Style QuickOSM Layer` or `Save QuickOSM Layers`.

### Testing

```bash
make test
```

Or in Docker:

```bash
make test-in-docker
```

---

## License

Same as upstream: [GNU General Public License v2.0](LICENSE).
