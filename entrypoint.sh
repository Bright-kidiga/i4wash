#!/bin/bash
set -e

cd $FRAPPE_HOME/frappe-bench

# Check if site already exists
if [ ! -d "sites/$SITE_NAME" ]; then
    echo "Site $SITE_NAME does not exist. Creating..."
    bench new-site $SITE_NAME \
        --db-host $DB_HOST \
        --db-name $DB_NAME \
        --db-root-username $DB_USER \
        --db-password $DB_PASSWORD \
        --admin-password $ADMIN_PASSWORD
else
    echo "Site $SITE_NAME already exists. Skipping creation."
fi

# Start bench
bench start
