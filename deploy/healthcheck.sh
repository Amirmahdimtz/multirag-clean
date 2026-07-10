#!/usr/bin/env bash
set -Eeuo pipefail

project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${project_dir}"

if [[ ! -f .env ]]; then
    echo "ERROR: .env does not exist. Copy .env.example and configure it first." >&2
    exit 1
fi

configured_public_port="$(
    sed -n 's/^MULTIRAG_PUBLIC_PORT=//p' .env | tail -n 1 | tr -d '[:space:]'
)"
public_port="${MULTIRAG_PUBLIC_PORT:-${configured_public_port:-2011}}"

echo "[1/4] Compose containers"
docker compose --env-file .env ps

echo "[2/4] PostgreSQL"
docker compose --env-file .env exec -T postgres \
    sh -ec 'pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"'

echo "[3/4] vLLM"
docker compose --env-file .env exec -T vllm \
    python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=5); print('vLLM: healthy')"

docker compose --env-file .env exec -T app python -c \
    "import os, urllib.request; request = urllib.request.Request(os.environ['MULTIRAG_LLM_BASE_URL'].rstrip('/') + '/models', headers={'Authorization': 'Bearer ' + os.environ['MULTIRAG_LLM_API_KEY']}); response = urllib.request.urlopen(request, timeout=10); print('vLLM models endpoint:', response.status)"

echo "[4/4] MultiRAG API"
python -c \
    "import urllib.request; response = urllib.request.urlopen('http://127.0.0.1:${public_port}/api/v1/health/', timeout=10); print('MultiRAG API:', response.status)"

echo "All production health checks passed."