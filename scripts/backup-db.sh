#!/bin/sh
# Script de backup de SQLite — ejecutado por el CronJob de Kubernetes
set -e

DB_SOURCE="/app/data/db.sqlite3"
BACKUP_DIR="/app/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/db_$TIMESTAMP.sqlite3"

if [ ! -f "$DB_SOURCE" ]; then
  echo "ERROR: No se encuentra la base de datos en $DB_SOURCE"
  exit 1
fi

mkdir -p "$BACKUP_DIR"
cp "$DB_SOURCE" "$BACKUP_FILE"
echo "Backup creado: $BACKUP_FILE"

# Conservar solo los últimos 30 backups
ls -t "$BACKUP_DIR"/db_*.sqlite3 | tail -n +31 | xargs -r rm -f
echo "Backups actuales: $(ls "$BACKUP_DIR"/db_*.sqlite3 | wc -l)"
