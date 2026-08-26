## spec
Owner, 2026-08-21: *"Please immediately equip the mutators, landforms, etc. into the world
generator script."*

Before this, `w9_run.py` ran stages 1, 2, 3, 5, 6 and the tile bundle had no mutator column
and no landmark column at all. The planet painted with correct terrain and no local-map
character and no named places. The census of 2026-08-20 inventoried what exists (336
mutators, 113 landmarks; 218 and 69 fit this planet) and deliberately stopped short of a
placement plan. This item is the placement plan and the plumbing.

**Built:**

`src/RimMandrake/Utils/ashkarr_populate.py` → two new authored files:

    world/ASHKARR_WORLDMAP_mutators.csv    tile,mutators      1,829 tiles
    world/ASHKARR_WORLDMAP_landmarks.csv   tile,landmark,why     16 tiles

⛔ **It is not a generator.** No seed, no knobs, no parameters, no way to roll a second
planet. The rules are hand-authored decisions about Ash'karr written as code so they are
reproducible rather than re-typed.

**Mutators are DERIVED** — each rule restates a column the map already carries:
`Coast` 369 (land tile with ≥1 water neighbour, over `world_graph.npz`) · `Mountain` 1,459
(hilliness ordinal ≥4) · `Oasis` 188 (`ZBiome_DesertOasis` inside the def's own 20–60 °C
gate; 39 of the 227 fall outside it).

⭐ `Coast` is the fix for the defect the owner named on 2026-08-17: the world carried 5,233,
of which 4,831 were on non-water tiles and 2,116 deep inland, placed for the original sea
layout and stranded when the repaint moved the water.

**Landmarks are HAND-PLACED**, 16, the cap from census §7 — `AbandonedColonyOutlander` at
The Setdown (2476) · `AncientQuarry` at The Ore Moot · `Valley` at The Scald Gate ·
`sw_Sarlacc` at Sarlacc Ground · `AncientLaunchSite` at the Rust Cathedral · `LavaCrater` +
`LavaLake` on the Scald rim · `AncientHeatVent` ×3 on the hottest ground · `Oasis` ×6.
The salt pans are deliberately empty: `DryLake`/`VEE_SaltPlains` may not be legal on
`Wasteland`, and a landmark that cannot fire logs nothing.

`w9_run.py` gained three stages, and their ORDER is engine fact, not taste:

    3b  clear the 49 vanilla landmark leftovers  (AddLandmark refuses an occupied tile)
    4   add landmarks   🔴 BEFORE settlements
    4b  add mutators    🔴 AFTER landmarks

## verify
Offline, done: `ashkarr_populate.py` runs clean and writes both files; both scripts parse;
the three settlement-anchored landmarks resolve 2.4–2.9° from their anchor, which is the
second ring — the first legal one, because `IsValidTile` refuses a settlement tile *and*
its neighbours, so the census's "one tile adjacent" was not placeable.

Live, on the rehearsal run — **§6, decision strings 6b, 7, 7b and 8.**
⚠️ **REPOINTED 2026-08-26 (WORLDGEN_CITATIONS_REPOINT_CHECK_1).** §6 is no longer in
`infrastructure/state/WORLDPAINT_REHEARSAL.md` — the live file now holds only §4 and §7. §5/§6/§6b were
split to `infrastructure/state/archive/WORLDPAINT_REHEARSAL_ARCHIVE.md` at `c4455458`, and that archive
was deleted whole at `892beac2`. Read §6 with
`git show 892beac2^:infrastructure/state/archive/WORLDPAINT_REHEARSAL_ARCHIVE.md`.
🔑 Cite by SECTION, never by line number.

## criteria
- stage 3b removes **49** leftover landmarks
- stage 4 reports **added 16 of 16** across 8 defs, and any `validity[]` entry the engine
  calls invalid is recorded rather than ignored
- stage 4b places **Coast 369 · Mountain 1459 · Oasis 188**
- the Oasis read-back reports **188 of 188**. 🔑 **0 is a FINDING, not a failure** — it would
  mean `AddMutator` honours `biomeWhitelist` after all, and the census's one-line
  `PatchOperationAdd` is needed. File it; do not patch around it in the runner.
- 🔴 and the owner looks at the planet and does not immediately name a defect

## notes
Owned by CHECK because this is live content injection over the bridge and `w9_run.py` is the
bridge driver. No new design ruling was needed: the landmark table is census §7, already
written. ⚠️ The one thing here that is genuinely unproven is whether `AddMutator` consults
`biomeWhitelist`; it is expected not to, by the same logic that makes `AddLandmark` ignore
`IsValidTile`, and the run measures it rather than assuming it.
