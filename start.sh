#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR=$(cd "$(dirname "$0")" && pwd)

# ------------------------------
# Python 仮想環境の準備
# ------------------------------
if [[ ! -d "$ROOT_DIR/.venv" ]]; then
  python3 -m venv "$ROOT_DIR/.venv"
fi

# shellcheck disable=SC1091
source "$ROOT_DIR/.venv/bin/activate"
pip install --upgrade pip
pip install -r "$ROOT_DIR/backend/requirements.txt"

# ------------------------------
# フロントエンドのビルド
# ------------------------------
pushd "$ROOT_DIR/frontend" >/dev/null
npm install
npm run build
popd >/dev/null

# ------------------------------
# バックエンド起動
# ------------------------------
uvicorn backend.main:app --host 0.0.0.0 --port 8000
