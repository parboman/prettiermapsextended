#!/bin/bash
set -euo pipefail

REPO_ROOT=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)
shopt -s nullglob

if [ -z "${QGIS_APP:-}" ]; then
    apps=(/Applications/QGIS*.app)
    QGIS_APP=${apps[0]:-}
fi
if [ -z "$QGIS_APP" ] || [ ! -d "$QGIS_APP" ]; then
    printf 'Error: QGIS app bundle not found. Install QGIS or set QGIS_APP to its app bundle.\n' >&2
    exit 1
fi

interpreters=("$QGIS_APP"/Contents/MacOS/python3.*)
PY=${interpreters[0]:-}
if [ -z "$PY" ] || [ ! -f "$PY" ] || [ ! -x "$PY" ]; then
    printf 'Error: QGIS Python interpreter not found in %s/Contents/MacOS/python3.*. Check QGIS_APP or reinstall QGIS.\n' "$QGIS_APP" >&2
    exit 1
fi

stdlibs=("$QGIS_APP"/Contents/Resources/python3.*)
STDLIB=${stdlibs[0]:-}
if [ -z "$STDLIB" ] || [ ! -d "$STDLIB" ]; then
    printf 'Error: QGIS Python standard library not found in %s/Contents/Resources/python3.*. Check QGIS_APP or reinstall QGIS.\n' "$QGIS_APP" >&2
    exit 1
fi

# Resolve bundle paths before changing to the repository root.
QGIS_APP=$(cd "$QGIS_APP" && pwd -P)
PY="$QGIS_APP/Contents/MacOS/$(basename "$PY")"
STDLIB="$QGIS_APP/Contents/Resources/$(basename "$STDLIB")"
CACHE="${XDG_CACHE_HOME:-$HOME/.cache}/prettiermaps-qgis-test"
mkdir -p "$CACHE/home/lib"
CACHE=$(cd "$CACHE" && pwd -P)
ln -sfn "$STDLIB" "$CACHE/home/lib/$(basename "$PY")"

export PYTHONHOME="$CACHE/home"
export PYTHONPATH="$CACHE/site:$REPO_ROOT"
if ! "$PY" -c 'import pytest' >/dev/null 2>&1; then
    printf 'Installing pytest into %s/site (network required on first run).\n' "$CACHE"
    "$PY" -m pip install --quiet --target "$CACHE/site" pytest
fi

cd "$REPO_ROOT"
if [ "$#" -eq 0 ]; then
    set -- tests
fi
# PYTHONDONTWRITEBYTECODE keeps __pycache__ out of the plugin package,
# which the zip build would otherwise ship to plugins.qgis.org.
PYTHONHOME="$CACHE/home" PYTHONPATH="$CACHE/site:$REPO_ROOT" \
    PYTHONDONTWRITEBYTECODE=1 QT_QPA_PLATFORM=offscreen \
    "$PY" -m pytest -q -p no:cacheprovider "$@"
