#!/bin/bash
set -e

cd $FRAPPE_HOME/frappe-bench

# Ensure required environment variables are set
: "${SITE_NAME:?Need to set SITE_NAME}"
: "${DB_HOST:?Need to set DB_HOST}"
: "${DB_ROOT_PASSWORD:?Need to set DB_ROOT_PASSWORD}"
: "${ADMIN_PASSWORD:?Need to set ADMIN_PASSWORD}"

# Start MariaDB in background if not already running
if ! mysqladmin ping -uroot -p"$DB_ROOT_PASSWORD" --silent; then
    echo "Starting MariaDB..."
    mysqld_safe --skip-networking=0 --skip-bind-address &

    # Wait for MariaDB to be ready
    until mysqladmin ping -uroot -p"$DB_ROOT_PASSWORD" --silent; do
        echo "Waiting for MariaDB to start..."
        sleep 2
    done
fi

# Check if site already exists
if [ ! -d "sites/$SITE_NAME" ]; then
    echo "Site $SITE_NAME does not exist. Creating..."

    # Create site non-interactively
    bench new-site "$SITE_NAME" \
        --db-root-username root \
        --db-root-password "$DB_ROOT_PASSWORD" \
        --admin-password "$ADMIN_PASSWORD" \

else
    echo "Site $SITE_NAME already exists. Skipping creation."
fi

# Start bench
bench start
