#!/bin/bash
# macOS / Linux：从迁移包还原（在解压目录内执行，或传入 zip 路径）
set -e
cd "$(dirname "$0")/.."
if [ -f "deploy/migrate.py" ]; then
  exec python3 deploy/migrate.py restore "$@"
fi
exec python3 migrate.py restore "$@"
