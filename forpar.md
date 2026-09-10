# For Pär — prettiermapsextended

## Waiting on your ruling

- **GitHub repo "homepage" field still points at the upstream project's site**
  (`https://prettiermaps.github.io/PrettierMaps/`). This fork has its own
  `docs/` mkdocs source and its own registry page. Point it at
  `https://plugins.qgis.org/plugins/prettier_maps_extended/`, at the repo
  itself, at a published docs site, or leave it crediting upstream? One
  command either way:
  `gh api repos/parboman/prettiermapsextended -X PATCH -f homepage='<url>'`
