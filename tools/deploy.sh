#!/usr/bin/env bash
# Deploy to production (Cloudflare Pages), purge the edge cache twice, verify the CSS version is serving.
# Usage: tools/deploy.sh [branch]   (default: main = production; any other name = preview URL)
set -euo pipefail
cd "$(dirname "$0")/.."
BRANCH="${1:-main}"
ZONE=4de542e1c453af2c18b5f6448bc3c299
# shellcheck disable=SC1090
[ -n "${CLOUDFLARE_API_TOKEN:-}" ] || source ~/.zshrc 2>/dev/null || true
wrangler pages deploy . --project-name=bangarangapps-com --branch="$BRANCH" --commit-dirty=true 2>&1 | grep -E 'Deployment complete|rror'
[ "$BRANCH" = main ] || exit 0
purge() { curl -s -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE/purge_cache" -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" -H 'Content-Type: application/json' --data '{"purge_everything":true}' | grep -o '"success":[a-z]*'; }
purge; sleep 25; purge; sleep 5   # the edge can serve old assets under a new ?v= while propagating, so purge twice
V=$(grep -o 'site.css?v=[0-9]*' index.html | head -1 | cut -d= -f2)
for i in 1 2 3 4 5 6; do
  live=$(curl -s "https://bangarangapps.com/?t=$RANDOM" | grep -o 'site.css?v=[0-9]*' | head -1 | cut -d= -f2)
  [ "$live" = "$V" ] && { echo "live: v=$V"; exit 0; }; sleep 8
done
echo "NOT serving v=$V yet (saw v=$live)" >&2; exit 1
