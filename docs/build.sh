#!/usr/bin/env bash
set -euo pipefail

DOCS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$DOCS_DIR/.." && pwd)"
SRC_DIR="$ROOT_DIR/src/aandd_reader"
STAGE_DIR="$DOCS_DIR/_generated"
OUTPUT_DIR="$DOCS_DIR/_build/html"

if [[ ! -d "$SRC_DIR" ]]; then
    echo "ERROR: package directory not found: $SRC_DIR" >&2
    exit 1
fi

export AANDD_READER_REPO_ROOT="$ROOT_DIR"
export PYTHONPATH="$ROOT_DIR/src:${PYTHONPATH:-}"

rm -rf "$STAGE_DIR" "$DOCS_DIR/_build"
mkdir -p "$OUTPUT_DIR"

for lang in en ja; do
    mkdir -p "$STAGE_DIR/$lang"
    cp -R "$DOCS_DIR/$lang/." "$STAGE_DIR/$lang/"
    mkdir -p "$STAGE_DIR/$lang/api"
    sphinx-apidoc --force --module-first -o "$STAGE_DIR/$lang/api" "$SRC_DIR"
    if [[ ! -f "$STAGE_DIR/$lang/api/modules.rst" ]]; then
        echo "ERROR: API toctree missing ($lang)" >&2
        exit 1
    fi
done

# The English source index is built directly at the site root; no redirects.
sphinx-build -b html -c "$DOCS_DIR" -D language=en "$STAGE_DIR/en" "$OUTPUT_DIR"
sphinx-build -b html -c "$DOCS_DIR" -D language=en "$STAGE_DIR/en" "$OUTPUT_DIR/en"
sphinx-build -b html -c "$DOCS_DIR" -D language=ja "$STAGE_DIR/ja" "$OUTPUT_DIR/ja"

for page in \
    "$OUTPUT_DIR/index.html" \
    "$OUTPUT_DIR/api/modules.html" \
    "$OUTPUT_DIR/tutorials/intro.html" \
    "$OUTPUT_DIR/en/index.html" \
    "$OUTPUT_DIR/en/api/modules.html" \
    "$OUTPUT_DIR/en/tutorials/intro.html" \
    "$OUTPUT_DIR/ja/index.html" \
    "$OUTPUT_DIR/ja/api/modules.html" \
    "$OUTPUT_DIR/ja/tutorials/intro.html"; do
    if [[ ! -f "$page" ]]; then
        echo "ERROR: expected HTML missing: $page" >&2
        exit 1
    fi
done

touch "$OUTPUT_DIR/.nojekyll"
printf 'Built documentation at %s\n' "$OUTPUT_DIR"
