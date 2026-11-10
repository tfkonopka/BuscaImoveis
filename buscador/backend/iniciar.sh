#!/usr/bin/env bash
# Sobe o buscador de imóveis em http://127.0.0.1:8777
set -e
cd "$(dirname "$0")"

if [ ! -d .deps ]; then
  echo "📦 Instalando dependências (1ª vez)..."
  pip3 install --target=.deps -r requirements.txt
fi

echo "🚀 Buscador em http://127.0.0.1:8777  (Ctrl+C para parar)"
PYTHONPATH=.deps .deps/bin/uvicorn main:app --host 127.0.0.1 --port 8777
