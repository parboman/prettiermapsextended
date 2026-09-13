# todo — prettiermapsextended

- [x] [burn] **Per-layer sublayer selection.** *Done 2026-09-13 in `bc88721` (branch
  `par/per-layer-sublayers`, unmerged): checkboxes keyed by `(layer id, style name)`,
  `filter_layers` takes layer id → style names, two-basemap dialog regression test added;
  `make test-macos` 26 → 29 passing.* `MainDialog.layer_checkboxes` is
  keyed by style name only, and `filter_layers` matches styles by name across
  every discovered layer. With two MapTiler basemaps loaded, unchecking a
  sublayer in one toggles the identically-named style in the other, and the
  first basemap's checkbox keeps showing the old state — the UI lies. Fix:
  key the checkbox map by `(layer id, style name)`, have `get_selected_layers`
  return a per-layer mapping, and change `filter_layers` to take
  `Dict[str, Set[str]]` (layer id → enabled style names). Update
  `test_filter_layers`, `test_filter_layers_at_project_root` and the three
  `mixed_source_styles` tests, which all call the current signature. Verify
  with `make test-macos` plus a headless two-basemap repro. Found by the
  cross-item sweep on 2026-09-10; documented as a known limitation in the
  1.5.1 changelog, and unreachable before 1.5.1 because the second basemap was
  never listed.
- [ ] [burn] **Same-named styles under different source layers collide.** Inside one
  `QgsVectorTileLayer`, two styles with the same `styleName()` under different source
  layers (e.g. `fill` under `water` and `fill` under `landcover`) share the
  `layer_checkboxes` key `(layer id, style name)` in `ui/dialog.py` `populate_layers`: the
  later checkbox overwrites the earlier, so toggling the earlier one does nothing while it
  still shows a state, and `filter_layers` enables or disables both by name. Predates
  `par/per-layer-sublayers` (main keyed by name alone). Fix: key checkboxes by
  `(layer id, source layer, style name)`, have `get_selected_layers` return layer id →
  set of `(style.layerName(), style.styleName())`, and match that pair in
  `filter_layers`; update every test that calls `filter_layers` plus
  `test_dialog_two_basemaps_toggle_independently`. Better landed before the next release
  so the `filter_layers` signature changes once, not twice. Add a dialog regression test
  (one layer, `water`/`fill` + `building`/`fill`, uncheck the first → only the water style
  disabled, both checkboxes independent) and drop the Known limitation in the Unreleased
  CHANGELOG section. Verify with `make test-macos`. Found by the dual review of
  `par/per-layer-sublayers` on 2026-09-13. Residual after the fix: two styles with the
  same source layer *and* style name would still collide — key by style index if that
  ever turns up in a real MapTiler style.
