#!/usr/bin/env bash
# Run before every submission. All three must pass.
set -euo pipefail
cd "$(dirname "$0")/.."
ruff check src tests
mypy
pytest --cov=telemetry --cov-report=term-missing --cov-fail-under=90
