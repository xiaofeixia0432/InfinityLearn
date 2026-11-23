#!/bin/bash
# InfinityLearn 前端启动 wrapper

set -e

FRONTEND_DIR="/Users/apple/Desktop/学习/AcquireKnowledge/frontend"
NODE_BIN="/usr/local/bin/node"
VITE_JS="$FRONTEND_DIR/node_modules/vite/bin/vite.js"

cd "$FRONTEND_DIR"
export HOME="${HOME:-/Users/apple}"
export BACKEND_PORT="8010"
export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

echo "[wrapper] starting vite, cwd=$(pwd)"
echo "[wrapper] node=$NODE_BIN"

exec "$NODE_BIN" "$VITE_JS" --host
