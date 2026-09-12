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
