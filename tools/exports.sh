#!/usr/bin/env bash
# Renders assets/brand/export/*.svg to PNG with the gstack browser (run tools/exports.py first).
#   icon.png              1024 x 1024
#   wordmark-on-*.png     2400 wide, height from the export's aspect
set -euo pipefail
cd "$(dirname "$0")/.."
B=~/.claude/skills/gstack/browse/dist/browse
E=assets/brand/export
T=$(mktemp -d)
trap 'rm -rf "$T"' EXIT

render() { # svg, width, height, background
  local name; name=$(basename "$1" .svg)
  printf '<!doctype html><style>html,body{margin:0;width:%spx;height:%spx;background:%s;overflow:hidden}img{display:block;width:100%%;height:100%%}</style><img src="file://%s">' \
    "$2" "$3" "$4" "$PWD/$1" > "$T/$name.html"
  $B viewport "${2}x${3}" >/dev/null
  $B goto "file://$T/$name.html" >/dev/null
  $B screenshot --viewport "$PWD/$E/$name.png" >/dev/null
  echo "$E/$name.png $(sips -g pixelWidth -g pixelHeight "$E/$name.png" | awk '/pixel/{printf "%s ", $2}')"
}

vb() { sed -E 's/.*viewBox="([^"]+)".*/\1/' "$1" | head -1 | awk '{printf "%d", 2400 * $4 / $3 + 0.5}'; }

render $E/icon.svg 1024 1024 '#0c0a0a'
render $E/wordmark-on-ink.svg 2400 "$(vb $E/wordmark-on-ink.svg)" '#0c0a0a'
render $E/wordmark-on-bone.svg 2400 "$(vb $E/wordmark-on-bone.svg)" '#eee9da'
