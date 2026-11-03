#!/usr/bin/env bash
# Emite/renova certificado Let's Encrypt (HTTP-01 via nginx).
# Pré-requisito: registros DNS tipo A apontando para esta VPS (168.231.91.74).
set -euo pipefail

DOMAINS=(
  gabtech.app.br
  app.gabtech.app.br
  api.gabtech.app.br
  mandato-demo.gabtech.app.br
)

echo "Verificando DNS..."
for d in "${DOMAINS[@]}"; do
  ip="$(getent ahosts "$d" 2>/dev/null | awk '/STREAM/ {print $1; exit}')"
  if [[ -z "$ip" ]]; then
    echo "ERRO: sem registro A para $d — configure no Registro.br antes de continuar."
    exit 1
  fi
  echo "  $d -> $ip"
done

args=()
for d in "${DOMAINS[@]}"; do
  args+=(-d "$d")
done

certbot --nginx "${args[@]}" \
  --non-interactive \
  --agree-tos \
  --register-unsafely-without-email \
  --redirect

echo "OK. Teste: curl -sI https://app.gabtech.app.br/ | head -3"
