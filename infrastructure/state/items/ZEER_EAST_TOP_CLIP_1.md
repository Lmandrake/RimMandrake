## spec

The same 2026-09-17 render wave (`9e7e773a0`) that **fixed** Zeer's
facing-height break introduced a boundary break in `Zeer_east.png`.

**MEASURED 2026-09-18** with `art_checks.py`, comparing the pre-wave blob
(`9e7e773a0^`) against the file on disk:

| check | pre-wave | now |
|---|---|---|
| `facing_height_consistency` | **1.480, high** (south 1.48x taller than east) | **1.024, clean** ✅ |
| `boundaries_respected` on `Zeer_east.png` | no finding | **top margin 0 px, high** — "drawing touches the canvas edge on top and is clipped" |

The mechanism is visible in the numbers and is a trade, not an accident: the
regen scales every Zeer facing to near-full canvas — east 0.990, north 0.967,
south 0.980 of canvas height — which is exactly what bought the 1.024 ratio
(the cleanest row in the corpus, down from the worst-but-three). At 0.990 of
canvas there is no margin left, so the east facing's top is clipped.

⭐ **The height fix is good and must not be reverted.** What is owed is the same
silhouette with a margin: scale the set down a few percent so all three facings
still agree AND none touches an edge.

## verify

`python3 src/RimMandrake/Utils/art_checks.py src/RimStarWars/ZeerArtOverride` —
no `boundaries_respected` finding at `high` on any Zeer facing, and
`facing_height_consistency` still clean (ratio at or below 1.35).

Then in `src/RimMandrake/Utils/art_checks.py`, drop the `Zeer_east.png` row
from `BOUNDARY_MUST_FLAG_HIGH`. ⚠️ `GizkaW_south.png` must STAY in that list —
it is the corpus-independent anchor that keeps the check covered, and removing
both leaves `boundaries_respected` with no positive fixture at all.

## open

- Offline-fixable; no bridge or game load needed to measure it.
- Three other facings currently raise the same `high` boundary finding and are
  NOT part of this item, because they were not checked against their pre-wave
  blobs: `Iriaz_south.png`, `GR_Mantistanis_south.png` (both touched by
  2026-09-17 commits), and `GizkaW_south.png` (**pre-existing** — confirmed
  clipped in the pre-`bd9a1b8ee` blob too, unchanged since 2026-09-14). Worth a
  sweep, not worth assuming.
