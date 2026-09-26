# WORLD_LABEL_SIZE_HIERARCHY_1 — the planet has no visual label hierarchy

## the ask

🔴 **Owner ruling, 2026-09-21 (BENCH question card): size the whole planet.**

MEASURED: **all 71 world features on the canonical save sit at `maxDrawSizeInTiles = 10`**,
the bottom of the engine's size curve, so every label draws at the minimum. The 1,692-tile
Dune Sea letters exactly as large as Notch.

The Fall Line was raised to **26** (effective 15 → 42) as the single test case under
`FALL_LINE_MAJOR_REGION_LABEL_1`, verified by parsing the `.rws`, saved as
`ASHKARR_FALLLINE_LABEL26_2026-09-21` with the canonical save byte-unchanged. The other 70
are untouched. This item is the pass that scales them all.

## spec

1. Derive each feature's `maxDrawSizeInTiles` from its tile count — a curve, not a table,
   so a feature added later gets a sensible size without a hand edit.
2. Apply offline against the save. **No cold load is needed.**
3. Keep the Fall Line's 26 consistent with whatever curve is chosen, or say why it differs.
4. Produce one picture of the whole map for the owner before anything is written to the
   canonical save.

## Watch out

- 🔴 **Back up the canonical save and confirm its byte size afterwards.** Write to a NEW
  slot; `rimworld/save_game` has silently written the current slot instead of `saveName`.
- 🔴 **A `.rws` edit must use binary mode** — text mode rewrites line endings and silently
  changes the file. Check the size delta.
- ⚠️ 71 is the MEASURED feature count on the canonical save as of 2026-09-21. Re-measure
  before applying; the number moves as features are authored.

## criteria

Every world feature's label size reflects its extent, the owner has seen one picture of the
result, and the canonical save is only written on his word.

## DONE OFFLINE 2026-09-26 (FOUNDRY) — curve applied to a new slot, canonical untouched, waiting on his look

**Re-measured fresh, live from the canonical `.rws`** (not trusted from this item's own
71): still **71 `WorldFeature`s**, decoded directly from
`<world><grid><layers><values><li Class="SurfaceLayer"><tileFeatureDeflate>` — a base64 +
raw-DEFLATE array of 21,872 ushorts, one per tile, storing each tile's
`WorldFeature.uniqueID` **directly** (not a shortHash — confirmed: all 71 distinct grid
values match all 71 `<uniqueID>`s under `<world><features>` 1:1, counts sum to exactly
21,872). Min 16 tiles (Salt Gate), max 2,051 (Deadstone), Dune Sea 1,692, Fall Line 155 —
all matching prior measurements exactly. All 71 confirmed still at `maxDrawSizeInTiles=10`
in the canonical file (the live-game 26 from `FALL_LINE_MAJOR_REGION_LABEL_1` was only ever
persisted to `ASHKARR_FALLLINE_LABEL26_2026-09-21.rws`, never written back to canonical).

**The curve**, `src/RimMandrake/Utils/world_label_curve.py`:

```
maxDrawSizeInTiles = round(max(10, sqrt(tileCount) * 1.35))
```

Not invented for this pass — `K=1.35` is this codebase's own already-vetted
vanilla-equivalent multiplier from `WORLD_FEATURE_LABELS_OVERSIZED_1` (closed 2026-09-10):
vanilla's `FeatureWorker.AssignBestDrawPos` sets `maxDrawSizeInTiles = bestTileDist * 2.4`
from a region's inradius, and treating an A-tile region as a disk gives
`bestTileDist ≈ sqrt(A/π)`, so `2.4·sqrt(A/π) == 1.354·sqrt(A)`. Floor 10 is the engine
curve's own first knot and today's uniform value — nothing shrinks, only genuinely large
regions grow past it. Result: 9 of the smallest features stay at 10 (correctly — they were
already at the curve's floor), the rest climb smoothly to Deadstone at 61 and Dune Sea at
56. Full before/after table: `python3 src/RimMandrake/Utils/world_label_curve.py <save> --report-only`.

🔑 **Fall Line kept as a documented exception, not reset to the curve.** The curve alone
gives it ~17 (155 tiles, 38th of 71 by area — unremarkable), but
`fall_line_major_region_label.md` calls its 26 *"a deliberate PROMOTION, not a computed
size"* on the owner's explicit "major world region" instruction. That promotion is
hardcoded in the script (`FALL_LINE_OVERRIDE = 26`) and left untouched here rather than
reset downward — consistent with the item's own instruction to keep it consistent with
the curve or say why it differs.

**Applied OFFLINE, new slot only, verified by reading the written file back** (not trusted
from the writer's own "success"): `ASHKARR_LABELSIZES_2026-09-26.rws` in the live Saves
folder (`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon
Studios\Saves\ASHKARR_LABELSIZES_2026-09-26.rws`), 17,500,721 bytes — byte-identical size
to the source because every old ("10") and new value happens to be two digits. 62 of 71
`<maxDrawSizeInTiles>` tags changed, located by exact byte offset in document order
matched against `<world><features>`'s own `<li>` order (not a blind text replace — the
source text is identical across all 71 tags, so a blind replace could not tell them
apart).

🔴 **Canonical save confirmed untouched, before and after, by hash, not just size**:
`sha256 98b8ef82…` both times,
`CANONICAL_ASHKARR_START_2026-09-12.rws`, 17,500,721 bytes, unchanged mtime (Sep 20
07:28). Backed up first regardless, per the item's own belt-and-suspenders instruction:
`CANONICAL_ASHKARR_START_2026-09-12.rws.bak-pre-labelsizehierarchy-20260926T032006Z` in
the same Saves folder.

**The review picture** — rendered OFFLINE from the untouched canonical save using
`worldview.py`'s existing `--feature-sizes` override (built for exactly this kind of
label-size preview, no save write involved at all):

```
python3 src/RimMandrake/Utils/worldview.py <canonical.rws> --feature-sizes <curve.json> --out Transient/world_label_sizes --png
```

→ `Transient/world_label_sizes/CANONICAL_ASHKARR_START_2026-09-12.biome.equirect.png`
(`D:\Luke\dev\Rimworld\Transient\world_label_sizes\CANONICAL_ASHKARR_START_2026-09-12.biome.equirect.png`).
Large regions (Deadstone, Glare, Kiln, Long Sand, Nightspill, Twilight Sea, Sunreach, Gray
Crags) now read visibly larger than mid-size ones (Combs, Dew Belt, Twilight Crags), which
in turn read larger than the smallest (still at the floor). The flat, no-hierarchy look the
owner reacted to is gone.

**What is still owed, and is his**: whether this curve's sizes are right (LOOK at the
picture — the closed `WORLD_FEATURE_LABELS_OVERSIZED_1` flagged that even this same
vetted multiplier might still read big on the largest regions, judged only by looking,
never by the number), and whether to commit it to the canonical save at all. Per this
item's own criteria, that decision is not taken here.
`rimflow needs WORLD_LABEL_SIZE_HIERARCHY_1 --to owner` set accordingly; item left in
`doing`, not closed.
