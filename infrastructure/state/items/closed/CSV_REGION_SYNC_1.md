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

## Landed 2026-09-12 — five renames + freeze re-stamp (owner's yes on card)
Owner's word (card sitting 2026-09-12): "As long as it came from the most
recent save game" — provenance verified before landing: save last written
Sep 10 23:57, CSV↔save comparison ran after it (0/21872 differ), save
untouched since. Candidate copied over `world/ASHKARR_WORLDMAP_tiles.csv`,
`verify_frozen.py --restamp` run, stamped sha 274aecc5ff76… matches bytes
(MEASURED); all five dead names now 0, Sootreach 433 exact. REMAINING: the
34-tile Abandoned Mines split (needs its per-tile list from a live bridge
read — game currently down). NOTE: census artifacts cite the pre-rename CSV
sha 756d9ffc8a22; only the region column changed, so all census counts stand.

## COMPLETE 2026-09-12 — Abandoned Mines landed, item done
The per-tile authority arrived by live bridge read (game up, world loaded,
`jawa/world_features_get` + 3-tile cross-check via a second route): feature
"The Abandoned Mines" (uniqueID 92), 34 member tiles — exactly 22 ex-Ashfall
Range + 12 ex-Notch as the audit predicted. CSV patched (34 rows, region
column only), freeze re-stamped, stamp matches bytes. Independent check:
post-patch Ashfall Range = 324 = the live save's own tileCount for that
feature. All 809 region mismatches from the audit are now resolved.
(Note: the landing commit shows all lines changed — the rewrite normalized
CSV quoting; a field-by-field comparison against HEAD~1 confirmed exactly 34
rows / region-only semantic difference. MEASURED.)
