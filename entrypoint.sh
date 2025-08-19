#!/bin/bash
set -e

cd $FRAPPE_HOME/frappe-bench

# Ensure required environment variables are set
: "${SITE_NAME:?Need to set SITE_NAME}"
: "${DB_HOST:?Need to set DB_HOST}"
: "${DB_PORT:?Need to set DB_PORT}"
: "${DB_NAME:?Need to set DB_NAME}"
: "${DB_USER:?Need to set DB_USER}"
: "${DB_PASSWORD:?Need to set DB_PASSWORD}"
: "${ADMIN_PASSWORD:?Need to set ADMIN_PASSWORD}"

# Check if site already exists
TABLE_EXISTS=$(mysql -u"$DB_USER" -p"$DB_PASSWORD" -h"$DB_HOST" -P "$DB_PORT" --skip-ssl -D"$DB_NAME" -e "SHOW TABLES LIKE 'tabSingles';" -s --skip-column-names || true)

if [ -z "$TABLE_EXISTS" ]; then
    echo "Site $SITE_NAME does not exist. Creating..."
    bench new-site "$SITE_NAME" \
        --db-host "$DB_HOST" \
        --db-port "$DB_PORT" \
        --db-root-username "$DB_USER" \
        --db-password "$DB_PASSWORD" \
        --admin-password "$ADMIN_PASSWORD" \
        --no-mariadb-socket \
        --verbose
else
    echo "Site already exists. Skipping creation."
fi

# Start bench
exec bench start
