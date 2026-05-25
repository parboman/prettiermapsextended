<h1 align="center">Prettier Maps (Extended) 1.5.0</h1>

<p align="center">
  <img src="assets/logo.png" alt="Prettier Maps logo" width="350">
</p>
<p align="center">
    <em>Style and work with maps easily in QGIS — QGIS 4 / Qt 6 compatible fork</em>
</p>

---

This is a public, AI-maintained fork of the original University of Glasgow PrettierMaps project. See the [repository README](https://github.com/parboman/prettiermapsextended#credits) for full credits and an honest account of how this fork is produced (Claude Opus writes the code, Codex reviews it, Pär is the human in the loop).

**Repository**: <a href="https://github.com/parboman/prettiermapsextended" target="_blank">github.com/parboman/prettiermapsextended</a>

**Issues**: <a href="https://github.com/parboman/prettiermapsextended/issues" target="_blank">github.com/parboman/prettiermapsextended/issues</a>

**Original upstream**: <a href="https://github.com/PrettierMaps/PrettierMaps" target="_blank">github.com/PrettierMaps/PrettierMaps</a>

---

PrettierMaps is a QGIS plugin that allows users further ease in creating and working with stylised maps. It works in tandem with MapTiler and QuickOSM (also QGIS plugins) and allows for easier management of MapTiler layers, and styling and saving of QuickOSM queries.

---

## Using PrettierMaps

Make sure you have the QGIS application installed

The only dependency is MapTiler. However to make full use of the plugin, it is recommended to use the plugin in conjunction with MapTiler and QuickOSM.

#### Locally

1. Install the plugin dependencies to your QGIS Python environment:

```bash
pip install -e .[dev,test,docs]
```

2. Create the QGIS zip file:

```bash
make zip_plugin
```

#### In QGIS

1. Install the plugin from the QGIS plugin manager
2. Install the MapTiler and QuickOSM plugins from the QGIS plugin manager
3. Run the plugin from the QGIS plugin manager

### Usage

To use the plugin, open a `Vector` map from MapTiler and then open the PrettierMaps plugin. There you will see a list of layers that you can enable/disable.

<figure align="center">
  <img src="assets/ui.png" alt="Image of PrettierMaps plugin UI" width="700">
  <figcaption>Figure 1: Example UI of PrettierMaps plugin v1.5.0</figcaption>
</figure>

To style or save a QuickOSM query, create a QuickOSM query using the QuickOSM plugin, then open the PrettierMaps plugin. You can now style this query by clicking the `Style QuickOSM Layer` button, and save by clicking `Save QuickOSM Layers`

## Maintaining

The original PrettierMaps was a 3rd year University project at the University of Glasgow and is no longer regularly maintained upstream. This extended fork picks up QGIS 4 compatibility — see the [README](https://github.com/parboman/prettiermapsextended#readme) for the working model.

## License
GPL v2 — same as upstream. See the [LICENSE file](https://github.com/parboman/prettiermapsextended/blob/main/LICENSE).