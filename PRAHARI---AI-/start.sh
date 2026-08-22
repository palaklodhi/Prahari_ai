#!/usr/bin/env bash
# One-command local launch for the Prahari platform (no Docker required).
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"

echo "▶ Starting Prahari backend (FastAPI :8000)…"
cd "$ROOT/backend"
[ -d .venv ] || python3 -m venv .venv
./.venv/bin/pip install -q -r requirements.txt
./.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACK=$!

echo "▶ Starting Prahari frontend (Vite :5173)…"
cd "$ROOT/frontend"
[ -d node_modules ] || npm install
npm run dev &
FRONT=$!

trap "kill $BACK $FRONT 2>/dev/null" EXIT
echo ""
echo "  ✅ Prahari is live:"
echo "     Frontend  →  http://localhost:5173"
echo "     API docs  →  http://localhost:8000/docs"
echo ""
wait
