.PHONY: venv
venv:
	uv sync --all-groups
	uv run pre-commit install

.PHONY: clean
clean:
	rm -rf .venv
	rm -rf .pytest_cache
	rm -rf .hypothesis
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	rm -rf build/
	rm -rf prettier_maps_extended.egg-info/
	find . -type d -name "__pycache__" -exec rm -rf {} +


.PHONY: ruff
ruff:
	uv run ruff check . --fix
	uv run ruff format .

.PHONY: mypy
mypy:
	uv run mypy .

.PHONY: test
test:
	uv run pytest

.PHONY: test-macos
test-macos:
	./scripts/run-tests-macos.sh

.PHONY: cov
cov:
	pytest -s -v --cov=prettier_maps_extended --cov=tests --cov-report=term-missing:skip-covered

.PHONY: test-in-docker
test-in-docker:
	docker build -t my-qgis-app -f .devcontainer/Dockerfile.test .
	docker run --rm -it my-qgis-app

.PHONY: zip_plugin
zip_plugin:
	rm -f prettier_maps_extended.zip
	# Keep the in-package LICENSE in sync with the canonical repo-root one,
	# since plugins.qgis.org requires LICENSE inside the plugin directory.
	cp LICENSE prettier_maps_extended/LICENSE
	# Never ship bytecode or macOS cruft to the registry — running the test
	# suite leaves __pycache__ inside the package directory.
	zip -r prettier_maps_extended.zip prettier_maps_extended \
		-x '*/__pycache__/*' '*.pyc' '*.DS_Store'

.PHONY: docs
docs:
	uv run mkdocs build