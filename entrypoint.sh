#!/bin/bash
set -e

cd $FRAPPE_HOME/frappe-bench

# Ensure required environment variables are set
: "${SITE_NAME:?Need to set SITE_NAME}"
: "${DB_ROOT_PASSWORD:?Need to set DB_ROOT_PASSWORD}"
: "${ADMIN_PASSWORD:?Need to set ADMIN_PASSWORD}"

# Wait for MariaDB to start using Python + PyMySQL
echo "Waiting for MariaDB to start..."
until python3 -c "import pymysql; pymysql.connect(host='127.0.0.1', user='root', password='$DB_ROOT_PASSWORD')" >/dev/null 2>&1; do
    echo "MariaDB not ready yet... sleeping 2 seconds"
    sleep 2
done

# Check if site already exists
if [ ! -d "sites/$SITE_NAME" ]; then
    echo "Site $SITE_NAME does not exist. Creating..."
    bench new-site "$SITE_NAME" \
        --db-root-username root \
        --db-root-password "$DB_ROOT_PASSWORD" \
        --admin-password "$ADMIN_PASSWORD"
else
    echo "Site $SITE_NAME already exists. Skipping creation."
fi

# Start bench
bench start
