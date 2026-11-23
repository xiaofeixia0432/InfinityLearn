#!/bin/bash
# macOS / Linux：打包迁移包
set -e
cd "$(dirname "$0")/.."
exec python3 deploy/migrate.py export "$@"
