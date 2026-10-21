#!/bin/bash
# Starts n8n inside GitHub Codespaces.
# N8N_PROXY_HOPS: n8n runs behind the Codespaces proxy, so trust 1 proxy hop.
# WEBHOOK_URL: tells n8n its public address, so the chat and webhooks can reach it.
export N8N_PROXY_HOPS=1
export WEBHOOK_URL="https://${CODESPACE_NAME}-5678.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}/"
echo "n8n address: $WEBHOOK_URL"
n8n start
