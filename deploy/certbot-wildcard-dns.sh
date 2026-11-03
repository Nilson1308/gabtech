#!/usr/bin/env bash
# Certificado wildcard (*.gabtech.app.br) — desafio DNS manual no Registro.br.
# Após certbot pedir TXT _acme-challenge.gabtech.app.br, publique no DNS e Enter.
set -euo pipefail

certbot certonly --manual --preferred-challenges dns \
  -d 'gabtech.app.br' -d '*.gabtech.app.br' \
  --agree-tos --register-unsafely-without-email

echo "Depois: aponte nginx tenant regex para /etc/letsencrypt/live/gabtech.app.br/ (ou nome do cert)."
