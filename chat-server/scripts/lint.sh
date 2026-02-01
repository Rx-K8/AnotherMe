#!/usr/bin/env bash

set -e
set -x

mypy --strict app
ruff check app
ruff format app --check