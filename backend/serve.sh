#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

PORT="${DJANGO_DEV_PORT:-8800}"
ADDR="${DJANGO_DEV_ADDR:-0.0.0.0}"

echo "GabTech API (tenant gabinete_demo):"
echo "  http://localhost:${PORT}/admin/"
echo "  http://demo.localhost:${PORT}/api/auth/login/"
exec "$ROOT/.venv/bin/python" manage.py runserver "${ADDR}:${PORT}"
