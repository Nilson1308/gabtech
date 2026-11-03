#!/usr/bin/env bash
# Adiciona subdomínio de tenant ao certificado nginx existente.
# Uso: certbot-expand-domain.sh novo-slug.gabtech.app.br
set -euo pipefail

NEW_DOMAIN="${1:?Informe o FQDN (ex.: cliente.gabtech.app.br)}"
CERT_NAME="${GABTECH_CERT_NAME:-gabtech.app.br}"

mapfile -t EXISTING < <(
  certbot certificates -n 2>/dev/null | sed -n "s/^    Domains: //p" | tr ' ' '\n' | sed '/^$/d'
)

if [[ " ${EXISTING[*]} " == *" $NEW_DOMAIN "* ]]; then
  echo "Domínio já no certificado: $NEW_DOMAIN"
  exit 0
fi

args=()
for d in "${EXISTING[@]}"; do
  args+=(-d "$d")
done
args+=(-d "$NEW_DOMAIN")

certbot --nginx --cert-name "$CERT_NAME" --expand "${args[@]}" --non-interactive
nginx -t && systemctl reload nginx
echo "Certificado expandido com: $NEW_DOMAIN"
