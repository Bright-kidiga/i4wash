##!/bin/bash
#set -e
#
#cd $FRAPPE_HOME/frappe-bench
#
## Ensure required environment variables are set
#: "${SITE_NAME:?Need to set SITE_NAME}"
#: "${DB_HOST:?Need to set DB_HOST}"
#: "${DB_ROOT_PASSWORD:?Need to set DB_ROOT_PASSWORD}"
#: "${ADMIN_PASSWORD:?Need to set ADMIN_PASSWORD}"
#
## Check if site already exists
#if [ ! -d "sites/$SITE_NAME" ]; then
#    echo "Site $SITE_NAME does not exist. Creating..."
#
#    # Create site non-interactively
#    bench new-site "$SITE_NAME" \
#        --db-host "$DB_HOST" \
#        --db-root-username root \
#        --db-root-password "$DB_ROOT_PASSWORD" \
#        --admin-password "$ADMIN_PASSWORD" \
#
#else
#    echo "Site $SITE_NAME already exists. Skipping creation."
#fi
#
## Start bench
#bench start
