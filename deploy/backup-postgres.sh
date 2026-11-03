#!/usr/bin/env bash
# Backup diário sugerido: cron → 0 3 * * * root /var/www/gabtech/deploy/backup-postgres.sh
set -euo pipefail

BACKUP_DIR="${GABTECH_BACKUP_DIR:-/var/backups/gabtech}"
RETENTION_DAYS="${GABTECH_BACKUP_RETENTION_DAYS:-14}"
STAMP="$(date +%Y%m%d_%H%M%S)"
FILE="$BACKUP_DIR/gabtech_${STAMP}.sql.gz"

mkdir -p "$BACKUP_DIR"
sudo -u postgres pg_dump -d gabtech | gzip > "$FILE"
find "$BACKUP_DIR" -name 'gabtech_*.sql.gz' -mtime +"$RETENTION_DAYS" -delete
echo "Backup: $FILE"
