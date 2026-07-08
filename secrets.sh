#!/bin/bash

# Run this LOCALLY before deploying.
# Pulls the secrets set in the local .envrc (the source of truth) and pushes
# them to the Digital Ocean droplet, where redeploy-site.sh sources them.
# Usage: ./secrets.sh

DROPLET="root@67.205.130.134"
REMOTE_SECRETS_FILE="mlh-portfolio/.envrc"
ENVRC_FILE="$(dirname "$0")/.envrc"

if [ ! -f "$ENVRC_FILE" ]; then
    echo "Error: $ENVRC_FILE not found."
    exit 1
fi

EXPORTS=""
for var in URL MYSQL_HOST MYSQL_USER MYSQL_PASSWORD MYSQL_DATABASE; do
    line=$(grep "^export ${var}=" "$ENVRC_FILE")
    if [ -z "$line" ]; then
        echo "Error: $var is not set in $ENVRC_FILE"
        exit 1
    fi
    EXPORTS+="$line"$'\n'
done

echo "Pushing secrets from .envrc to $DROPLET:$REMOTE_SECRETS_FILE ..."
printf '%s' "$EXPORTS" | ssh "$DROPLET" "cat > $REMOTE_SECRETS_FILE && chmod 600 $REMOTE_SECRETS_FILE" \
    || { echo "Error: Failed to set secrets on the droplet"; exit 1; }

echo "✅ Secrets set on Digital Ocean: URL, MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE"
