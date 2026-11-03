#!/usr/bin/env bash
# Restaura o backup mais recente em DB isolado (validação — não altera gabtech).
set -euo pipefail

TEST_DB="${GABTECH_RESTORE_TEST_DB:-gabtech_restore_test}"
BACKUP_DIR="${GABTECH_BACKUP_DIR:-/var/backups/gabtech}"
LATEST="$(ls -t "$BACKUP_DIR"/gabtech_*.sql.gz 2>/dev/null | head -1)"

if [[ -z "$LATEST" ]]; then
  echo "Nenhum backup em $BACKUP_DIR"
  exit 1
fi

echo "Backup: $LATEST"
sudo -u postgres psql -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$TEST_DB';" 2>/dev/null || true
sudo -u postgres dropdb --if-exists "$TEST_DB"
sudo -u postgres createdb -O gabtech "$TEST_DB"
gunzip -c "$LATEST" | sudo -u postgres psql -v ON_ERROR_STOP=1 -d "$TEST_DB" -q

echo "--- Validação ---"
sudo -u postgres psql -d "$TEST_DB" -c "SELECT COUNT(*) AS gabinetes FROM core_gabinete;"
sudo -u postgres psql -d "$TEST_DB" -c "SELECT schema_name FROM core_gabinete ORDER BY 1;"
sudo -u postgres psql -d "$TEST_DB" -c "SELECT COUNT(*) AS dominios FROM core_dominio;"
echo "OK: restore de teste concluído em database \"$TEST_DB\"."
