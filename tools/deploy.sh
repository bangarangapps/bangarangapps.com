#!/usr/bin/env bash
# Deploy to production (Cloudflare Pages), purge the edge cache twice, verify the CSS version is serving.
# Usage: tools/deploy.sh [branch]   (default: main = production; any other name = preview URL)
set -euo pipefail
cd "$(dirname "$0")/.."
BRANCH="${1:-main}"
ZONE=4de542e1c453af2c18b5f6448bc3c299
# the token lives in ~/.zshrc (zsh syntax), so read it through zsh rather than sourcing it here
CLOUDFLARE_API_TOKEN="${CLOUDFLARE_API_TOKEN:-$(zsh -c 'source ~/.zshrc >/dev/null 2>&1; print -r -- $CLOUDFLARE_API_TOKEN')}"
[ -n "$CLOUDFLARE_API_TOKEN" ] || { echo "CLOUDFLARE_API_TOKEN not found (see ~/.claude/ACCESS.local.md)" >&2; exit 1; }
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
