# For Pär — prettiermapsextended

## Waiting on your hands

- **Drive the unreleased layer fixes in QGIS 4, then say "release 1.5.3".** Both are on main,
  and CHANGELOG has them under Unreleased. Tests only cover them headlessly. Run `make zip_plugin`
  in this repo, install the zip in QGIS 4 (Plugins → Install from ZIP), load two MapTiler
  vector basemaps and open Prettier Maps. Toggling a sublayer in one basemap must not change
  the other, and two same-named styles (e.g. `fill` under water and under landcover) each get
  their own working checkbox. Use version 1.5.3: the registry may count withdrawn 1.5.1 as
  used, and 1.5.2 is live.

## Burn run 2026-09-27 (deadline-ae)

- **Landed:** same-named styles under different source layers (`423dd17`, `Source: par/same-named-styles`).
  New dialog regression test fails on the old code, passes now; `make test-macos` 30 passed; Codex CLEAN.
  Not released — Unreleased CHANGELOG carries it, with the exact-duplicate residual as a Known limitation.
