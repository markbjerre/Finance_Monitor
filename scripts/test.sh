#!/bin/bash
# Run Finance dashboard tests
# Usage: ./scripts/test.sh or from project root: bash scripts/test.sh

set -e
cd "$(dirname "$0")/.."
python -m pytest tests/ -v
