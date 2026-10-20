#!/bin/bash
# The weir's foam toe (look-free): painted white water through codex $imagegen, so the water overlay is drawn art, not
# script blobs (placeholder_detect FLAT, 2026-10-17). Writes raw/foam_toe.png.
HERE="$(cd "$(dirname "$0")" && pwd)"; REPO="$(cd "$HERE/../../../../.." && pwd)"
RMS="$(python3 "$REPO/src/RimMandrake/Utils/rmpaths.py" scratch)" || exit 2   # data root (rmpaths.py)
python3 "$REPO/skills/generating-images/scripts/codex_image.py" generate --model gpt-6.1-sol --out "$HERE/raw/foam_toe.png" \
  --codex-home "$RMS/codex/home_weir_foam" --timeout 900 --prompt "Game texture for RimWorld, seen from straight above: a long horizontal band of churning white river foam where water has just poured over a low weir. Wide landscape image, 1536x1024. The band runs the full width of the image and continues off both side edges (a repeating strip). Along the top edge of the band the foam is dense, bright white and frothy with small bubbles; going down it breaks up into scattered white patches, streaks and bubbles that thin out and stop about two thirds of the way down. Soft painted game-art style with crisp bubble edges, white to pale blue-grey only. Fully transparent background with real alpha everywhere there is no foam: draw no water, no river, no ground, no rocks, no shadow." > "$HERE/raw/foam_toe.log" 2>&1
echo "foam exit=$?"
