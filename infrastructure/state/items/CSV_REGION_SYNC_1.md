# CSV_REGION_SYNC_1 — the frozen CSV's region column missed the name consolidation

Found by POST_FREEZE_WORLDMAP_AUDIT_1 (2026-09-11): 809 tiles' `region` values
are stale vs the canonical save — five ruled 1:1 renames (South Crags→Sootreach
433, Level→Knuckles 141, Venom Wood→Fuelmere 72, Coldshelf→Sunshelf 68,
Thornend→Frostvein 61) plus a real new region **The Abandoned Mines** (34 tiles
from Ashfall Range 22 + Notch 12). `region` is not an engine field — the world
is right, the record isn't. Anything that reasoned off those five names since
consolidation is citing dead ones.

## spec
- Patch the CSV's region column in place (patch-a-curated-artifact rule: diff
  to a temp path first, never re-allocate).
- 🔴 The CSV is FROZEN: editing it breaks `frozen.json`'s fingerprint. Re-stamp
  the freeze record in the SAME change, with this item cited as the authority —
  needs the owner's word before executing (a freeze re-stamp is deliberate,
  never routine).

## verify
Zero region mismatches on a re-run of the post-freeze comparison; frozen.json
matches the new CSV bytes.

## Prep done 2026-09-12 (BENCH belt wave) — candidate ready, Mines BLOCKED
`Transient/CSV_REGION_SYNC_1_candidate.csv` + `Transient/CSV_REGION_SYNC_1_diff.md`:
five renames applied, MEASURED 775 rows changed (433/141/72/68/61), diff confirms
region column only. The Abandoned Mines (34 tiles: Ashfall 22 + Notch 12) is NOT
in the candidate — no per-tile artifact names which tiles move; offline
re-derivation was tried, disagreed wildly, and was correctly NOT used. Needs the
audit's per-tile working data or one `jawa/world_features_get` when the bridge
frees. Landing (frozen CSV edit + freeze re-stamp) still waits on the owner's
word either way.
