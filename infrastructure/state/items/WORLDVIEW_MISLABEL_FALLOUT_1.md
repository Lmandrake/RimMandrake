# WORLDVIEW_MISLABEL_FALLOUT_1 — every Ash'karr render carried the wrong region names

## what was wrong

MEASURED 2026-09-21: the savegame's `tileFeature` grid stores each tile's feature
**`uniqueID`** (21..92 on this planet), **not** its index into the features list.
`worldview.py` / `worldmap.py` read it as an index. ⇒ **Every region label on every
Ash'karr render pointed at the wrong region**, and the accompanying per-region tile counts
were wrong with it.

**Fixed** at `1a96f1e2a` (`worldmap.features()` now returns `uid`; `PlanetView` remaps
once). The fixed renderer independently reproduces the tile counts derived straight from
`tileFeatureDeflate`, and those agree with the record CSV's `region` column at Jaccard
**1.000 on all 71** — so the corrected mapping is confirmed from two directions.

## why this needs its own item — the renderer is fixed, the conclusions are not

🔴 **The project's rule for the world is "iterate by LOOKING"** (`worldview.py` is the
instrument, `the_one_map.md` the target). So this defect did not produce a wrong number in
a file nobody reads — **it fed wrong region names to the owner's eye**, repeatedly, and
judgments were made on them.

⚠️ **The blast radius is UNMEASURED and that is the whole job here.** Nothing is known yet
about which past conclusions are affected.

## spec

1. Find every artifact produced by `worldview.py`/`worldmap.py` that carries region LABELS
   — review sheets, audit reports, the Ash'karr audit artifact, biome sheets, any committed
   render or contact sheet. List them with dates.
2. For each, decide whether its conclusion **depended on which region a label named**. Most
   probably did not — a density or colour judgment survives a wrong caption. A judgment of
   the form *"region X is wrong / X should be Y"* does not.
3. Re-render the affected ones and re-check only those conclusions.
4. ⛔ Do NOT re-open a settled ruling merely because a render was mislabelled. Bring the
   owner the specific ones where the label carried the judgment; his time is the scarce
   thing, not renders.

## Watch out

- ⚠️ **Do not assume the fix is old.** It landed 2026-09-21; anything rendered before that
  commit is suspect, anything after is not.
- ⚠️ A render whose labels were never read (a pure terrain or elevation view) is unaffected.
  Check what the artifact was actually FOR before re-running it.
- 🔑 This is the second instrument this week that returned a confident, well-formed, wrong
  answer. Treat "the picture looked fine" as no evidence at all.

## criteria

Every label-bearing worldview artifact is listed and classified as unaffected or
re-checked, and any conclusion that actually rested on a mislabelled region is corrected or
put back to the owner.
