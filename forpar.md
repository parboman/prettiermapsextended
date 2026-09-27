# For Pär — prettiermapsextended

## Waiting on your ruling

- **GitHub repo "homepage" field still points at the upstream project's site**
  (`https://prettiermaps.github.io/PrettierMaps/`). This fork has its own
  `docs/` mkdocs source and its own registry page. Point it at
  `https://plugins.qgis.org/plugins/prettier_maps_extended/`, at the repo
  itself, at a published docs site, or leave it crediting upstream? One
  command either way:
  `gh api repos/parboman/prettiermapsextended -X PATCH -f homepage='<url>'`

## Burn run 2026-09-27 (deadline-ae)

- **Landed:** same-named styles under different source layers (`423dd17`, `Source: par/same-named-styles`).
  New dialog regression test fails on the old code, passes now; `make test-macos` 30 passed; Codex CLEAN.
  Not released — Unreleased CHANGELOG carries it, with the exact-duplicate residual as a Known limitation.
