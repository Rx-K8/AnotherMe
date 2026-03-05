#!/usr/bin/env bash
set -euo pipefail

pytest tests/ -v --tb=short -m "not gpu" \
  --cov --cov-report=term-missing --cov-report=html
