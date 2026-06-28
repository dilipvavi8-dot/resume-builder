#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"

if [[ ! -x "$BACKEND_DIR/.venv/bin/uvicorn" ]]; then
  echo "Backend dependencies are missing."
  echo "Run: cd backend && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt"
  exit 1
fi

if [[ ! -d "$FRONTEND_DIR/node_modules" ]]; then
  echo "Frontend dependencies are missing."
  echo "Run: cd frontend && npm install"
  exit 1
fi

if [[ ! -f "$BACKEND_DIR/.env" && -f "$BACKEND_DIR/.env.example" ]]; then
  cp "$BACKEND_DIR/.env.example" "$BACKEND_DIR/.env"
fi

if [[ ! -f "$FRONTEND_DIR/.env.local" && -f "$FRONTEND_DIR/.env.example" ]]; then
  cp "$FRONTEND_DIR/.env.example" "$FRONTEND_DIR/.env.local"
fi

cleanup() {
  trap - EXIT INT TERM
  [[ -n "${BACKEND_PID:-}" ]] && kill "$BACKEND_PID" 2>/dev/null || true
  [[ -n "${FRONTEND_PID:-}" ]] && kill "$FRONTEND_PID" 2>/dev/null || true
  wait 2>/dev/null || true
}

trap cleanup EXIT INT TERM

echo "Starting Rolecraft..."
echo "Backend: http://127.0.0.1:8000"
echo "Frontend: http://localhost:3001"
echo "Press Ctrl+C to stop both services."

(
  cd "$BACKEND_DIR"
  exec .venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000
) &
BACKEND_PID=$!

(
  cd "$FRONTEND_DIR"
  exec npm run dev -- --port 3001
) &
FRONTEND_PID=$!

while kill -0 "$BACKEND_PID" 2>/dev/null && kill -0 "$FRONTEND_PID" 2>/dev/null; do
  sleep 1
done

echo "One Rolecraft service stopped. Shutting down the other service."
