#!/bin/bash
set -e

# Aller dans le dossier back/
cd "$(dirname "$0")/.."

EXCEL=$1
PDF=$2
OUTPUT=${3:-outputs/result.json}

if [ -z "$EXCEL" ] || [ -z "$PDF" ]; then
    echo "Usage: ./scripts/run_extraction.sh <excel> <pdf> [output]"
    exit 1
fi

echo "Excel: $EXCEL"
echo "PDF: $PDF"
echo "Output: $OUTPUT"
echo ""

uv run python -m src.extracting.main "$EXCEL" "$PDF" "$OUTPUT"