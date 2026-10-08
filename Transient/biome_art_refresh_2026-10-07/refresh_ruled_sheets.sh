#!/bin/sh
# Idempotent: join finished artpipe renders, rebuild the six ruled biome sheets (decisions kept, same URLs/ports,
# dead servers restarted persistently), verify decisions still name the same art, check every URL, rewrite MORNING_SHEETS.md.
R=/home/mandrake/rm/bench
cd "$R" || exit 1
python3 src/RimMandrake/Utils/art/art.py backfill artpipe | tail -1
python3 src/RimMandrake/Utils/art/refresh_sheets.py --no-backfill --force \
  --only miasma_sheet --only feverwood_sheet --only greentide_sheet --only desert_sheet_2026-10-04 \
  --only leaningscrub_sheet --only webwork_sheet 2>&1 | tail -12
python3 src/RimMandrake/Utils/art/remap_decisions.py | grep -E "miasma|feverwood|greentide|^desert|leaningscrub|webwork"
python3 Transient/biome_art_refresh_2026-10-07/morning_sheets.py
