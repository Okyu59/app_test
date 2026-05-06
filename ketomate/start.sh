#!/bin/bash
set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"
BACKEND="$ROOT/backend"
FRONTEND="$ROOT/frontend"

# 백엔드 venv 설정
if [ ! -d "$BACKEND/.venv" ]; then
  python3 -m venv "$BACKEND/.venv"
  "$BACKEND/.venv/bin/pip" install -q -r "$BACKEND/requirements.txt"
fi

# .env 확인
if [ ! -f "$BACKEND/.env" ]; then
  cp "$BACKEND/.env.example" "$BACKEND/.env"
  echo "⚠️  $BACKEND/.env 에 ANTHROPIC_API_KEY를 입력해주세요."
  exit 1
fi

# 백엔드 실행 (백그라운드)
echo "🚀 Backend: http://localhost:8000"
"$BACKEND/.venv/bin/uvicorn" main:app --reload --app-dir "$BACKEND" --port 8000 &
BACKEND_PID=$!

# 프론트엔드 실행
echo "🌐 Frontend: http://localhost:5173"
cd "$FRONTEND" && npm run dev

kill $BACKEND_PID 2>/dev/null || true
