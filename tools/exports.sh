#!/usr/bin/env bash
# Renders assets/brand/export/*.svg to PNG with the gstack browser (run tools/exports.py first).
# Each SVG is drawn into a canvas at the target size and saved from canvas.toDataURL, so transparent areas stay transparent
# (a page screenshot would paint them white).
#   icon.png                    1024 x 1024 (opaque ink tile)
#   wordmark-for-*-bg.png       2400 wide, transparent background
set -euo pipefail
cd "$(dirname "$0")/.."
B=~/.claude/skills/gstack/browse/dist/browse
E=assets/brand/export
T=$(mktemp -d)
trap 'rm -rf "$T"' EXIT

render() { # svg, width
  local name; name=$(basename "$1" .svg)
  python3 - "$1" "$2" "$T/$name.html" <<'PY'
import sys, re, json, base64
src, W, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
svg = open(src).read()
_, _, vw, vh = map(float, re.search(r'viewBox="([^"]+)"', svg).group(1).split())
H = round(W * vh / vw)
svg = svg.replace('<svg ', f'<svg width="{W}" height="{H}" ', 1)
url = 'data:image/svg+xml;base64,' + base64.b64encode(svg.encode()).decode()
open(out, 'w').write(f'''<!doctype html><script>
const i = new Image(); i.onload = () => {{ const c = document.createElement('canvas'); c.width = {W}; c.height = {H};
  c.getContext('2d').drawImage(i, 0, 0, {W}, {H}); window.out = c.toDataURL('image/png'); }};
i.src = {json.dumps(url)};
</script>''')
PY
  $B goto "file://$T/$name.html" >/dev/null
  $B js "window.out" | sed 's/^data:image\/png;base64,//' | base64 -d > "$E/$name.png"
  echo "$E/$name.png $(sips -g pixelWidth -g pixelHeight -g hasAlpha "$E/$name.png" | awk '/pixel|Alpha/{printf "%s ", $2}')"
}

render $E/icon.svg 1024
render $E/wordmark-for-light-bg.svg 2400
render $E/wordmark-for-dark-bg.svg 2400
