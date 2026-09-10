<!-- World-changes and observations git can't see: deploys, server commands, live
     decisions, run/test observations. One dated line per entry.
     Contract: ~/ai/docs/claude/project-structure.md §log.md -->

# prettiermapsextended — log

- **2026-09-10** 1.5.0 confirmed approved on plugins.qgis.org (approval mail 2026-05-28, reviewer zimbogisgeek) — closes the open question the May memo left #registry
- **2026-09-10** GitHub issues ENABLED on parboman/prettiermapsextended (`has_issues: true`); metadata.txt's `tracker=` link had been advertising a disabled tracker since the fork #repo
- **2026-09-10** 1.5.1 uploaded to plugins.qgis.org, then withdrawn from the review queue by Pär before approval — a Bandit scan of that package found the asserts guarding a rendererless layer #registry
- **2026-09-10** 1.5.2 built and scanned clean by Pär (his scanner + local Bandit/flake8/ruff all zero); registry upload + review outcome not confirmed in-session #registry
- **2026-09-10** the test suite runs natively on this Mac for the first time (`make test-macos`, QGIS 4.0.2 bundled interpreter): 7 → 26 tests. First run pip-installs pytest into `~/.cache/prettiermaps-qgis-test/site` #testing
