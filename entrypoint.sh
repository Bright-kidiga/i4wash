#!/bin/bash
set -e

cd $FRAPPE_HOME/frappe-bench

# Ensure required environment variables are set

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
