# todo — prettiermapsextended

- [ ] [burn] **Per-layer sublayer selection.** `MainDialog.layer_checkboxes` is
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
