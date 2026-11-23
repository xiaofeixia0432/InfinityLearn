#!/bin/bash
# InfinityLearn 后端启动 wrapper
# 把 launchd 环境里可能缺失的变量显式补齐，确保 uvicorn 能正常启动

set -e

BACKEND_DIR="/Users/apple/Desktop/学习/AcquireKnowledge/backend"
# venv 放在 ~/.venvs 下（不在 Desktop 里，避开 macOS TCC 隐私保护）
VENV_PY="$HOME/.venvs/il-backend/bin/python3.13"

# 工作目录
cd "$BACKEND_DIR"

# 确保 HOME 存在（launchd Aqua session 应该有，但以防万一）
export HOME="${HOME:-/Users/apple}"

# 数据库配置（plist 也传了，但这里保险再显式 export 一次）
export DB_USER="root"
export DB_PASSWORD="Mysql@123"
export DB_NAME="knowledge_system"

# Python 与 PATH
export PYTHONUNBUFFERED=1
export PATH="$HOME/.venvs/il-backend/bin:/usr/local/opt/python@3.13/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

# 日志目录确保存在
mkdir -p "$BACKEND_DIR/logs"

# 打出启动环境快照（有助于排查）
echo "[wrapper] starting uvicorn, cwd=$(pwd)"
echo "[wrapper] python=$VENV_PY"
echo "[wrapper] db_host=127.0.0.1 db=$DB_NAME"

# exec 让它直接替换当前 shell 进程，这样 launchd 能正确追踪 PID 和 KeepAlive
exec "$VENV_PY" -m uvicorn app.main:app --host 127.0.0.1 --port 8010
