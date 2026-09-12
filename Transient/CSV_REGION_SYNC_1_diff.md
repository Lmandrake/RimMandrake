# CSV_REGION_SYNC_1 — prep diff (PARTIAL: five renames only, Abandoned Mines BLOCKED)

## What was applied to the candidate
Source: `/mnt/d/Luke/dev/Rimworld/world/ASHKARR_WORLDMAP_tiles.csv`
(21872 data rows, 1810387 bytes, sha256 `756d9ffc8a22c3d220ada5988df7d89527685766344d63cc667664cf28ee6bb7`)
Candidate: `/mnt/d/Luke/dev/Rimworld/Transient/CSV_REGION_SYNC_1_candidate.csv`
(1809793 bytes — smaller only because the new names are shorter on net)

Line-by-line diff (field-split on `,`, CRLF preserved) confirms: **775 rows changed,
0 changes in any column other than `region`.**

| old region | new region | rows changed (MEASURED) | item's stated count |
|---|---|---|---|
| South Crags | Sootreach | 433 | 433 |
| Level | Knuckles | 141 | 141 |
| Venom Wood | Fuelmere | 72 | 72 |
| Coldshelf | Sunshelf | 68 | 68 |
| Thornend | Frostvein | 61 | 61 |
| **total** | | **775** | 775 |

All five counts match the item file and `world/_audit/post_freeze_2026-09-11.json`
exactly (that audit's own region counter over the live CSV was re-run here
independently and agrees row for row).

## BLOCKED: "The Abandoned Mines" (34 tiles: Ashfall Range 22 + Notch 12)

Not applied. The five renames above are a straight global string substitution
(every row bearing the old name gets the new one) and need no per-tile lookup.
The Abandoned Mines split is different: it needs to know **which specific 22 of
Ashfall Range's 346 CSV rows and which specific 12 of Notch's 68 CSV rows** the
canonical save reassigns — a per-tile membership question, not a name swap.

What was searched, and why each route came up short:
- `world/_audit/post_freeze_2026-09-11.json` (POST_FREEZE_WORLDMAP_AUDIT_1's own
  output) states the counts (22 from Ashfall Range, 12 from Notch) and confirms
  the region column mismatch, but carries no tile-ID list — it names the
  *what*, not the *which*.
- `world/ASHKARR_WORLDMAP_tiles.csv.frozen.json` corroborates the same two
  counts (346 CSV vs 324 "live" for Ashfall Range, 68 vs 56 for Notch — deltas
  of 22 and 12) but likewise carries no tile IDs.
- No other file in the repo names "Abandoned Mines" together with a tile list
  (`grep -rl` across `*.py/*.json/*.md/*.csv` for the five new/old region names
  found only the item file, the audit JSON/HTML, frozen.json, and unrelated
  worldmap tooling — no per-tile artifact).
- The save's own XML (`.../Saves/CANONICAL_ASHKARR_2026-09-09.rws`) carries 71
  `WB_MapLabelFeature` entries — a mod's point labels (name + single
  `drawCenter` per feature) — not vanilla `WorldFeature` tile membership.
  Vanilla `Find.World.features` (real flood-filled per-tile region membership)
  is a runtime-computed structure, not one this save serializes.
- Tried deriving per-tile assignment offline by nearest-`drawCenter` (Voronoi)
  from the CSV's lat/lon: calibrated the lat/lon→xyz convention against 66
  stable (unrenamed) region centroids (best fit: `(cosLat·sinLon, sinLat,
  −cosLat·cosLon)`, avg alignment 0.978) — but a full nearest-point
  reassignment over all 21872 tiles disagreed with the live CSV `region`
  column on ~15,000 tiles, nowhere near the "69 of 71 match exactly" the
  freeze record reports. So point-Voronoi is not the actual mechanism behind
  this column, and using it to pick the 34 tiles would be re-deriving region
  assignment, which the item explicitly rules out ("do not re-derive region
  assignment yourself beyond the six mappings above").
- The live bridge (`jawa/world_features_get`, which reads `Find.World.features`
  directly and is the tool the world-editing skill names as the real per-tile
  authority) was not used: the bridge is currently held by FOUNDRY
  (`infrastructure/state/BRIDGE`: "batched live verification... worldmap
  river/shorthash/mutator checks", idle 21 min, not yet stale at the 45-minute
  mark) doing an overlapping worldmap live-verification pass. Taking it now
  risks colliding with that in-flight work and this task is scoped PREP ONLY
  (offline), so it was left alone rather than pre-empted.

**To close this**: either pull the tile-ID list from whoever/whatever produced
`post_freeze_2026-09-11.json` (if it still has the per-tile working data), or —
once the bridge is free — run `jawa/world_features_get` for "The Abandoned
Mines" against `CANONICAL_ASHKARR_2026-09-09.rws` and intersect its tile IDs
with the CSV rows currently reading `Ashfall Range`/`Notch`.

## Frozen record (untouched)
- Path: `/mnt/d/Luke/dev/Rimworld/world/ASHKARR_WORLDMAP_tiles.csv.frozen.json`
- Current fingerprint fields (unedited by this prep): `sha256`
  `756d9ffc8a22c3d220ada5988df7d89527685766344d63cc667664cf28ee6bb7`,
  `rows` 21872, `bytes` 1810387 — this matches the CSV on disk right now
  (confirmed current by `world/_audit/post_freeze_2026-09-11.json`'s own
  `freeze_fingerprint: MEASURED-ok` verdict).
- Not re-stamped. Not edited. No frozen-file, repo-file edit, or commit was
  made by this prep task.

## Landing procedure (needs the owner's explicit word — not run)

Five-renames-only version:
```
cp /mnt/d/Luke/dev/Rimworld/Transient/CSV_REGION_SYNC_1_candidate.csv \
   /mnt/d/Luke/dev/Rimworld/world/ASHKARR_WORLDMAP_tiles.csv
python3 src/RimMandrake/Utils/verify_frozen.py --restamp world/ASHKARR_WORLDMAP_tiles.csv
```
(then verify `frozen.json`'s new sha/rows/bytes, `git add` the two changed
paths by name, commit citing CSV_REGION_SYNC_1 as authority — per the item
spec the restamp must cite this item and happen in the same change as the
edit.)

If the Abandoned Mines split is resolved before landing, patch the candidate
CSV first (34 more rows, Ashfall Range→The Abandoned Mines ×22 and
Notch→The Abandoned Mines ×12) and re-verify the diff (should then show 809
total changed rows, 0 non-region column diffs) before running the two
commands above.
