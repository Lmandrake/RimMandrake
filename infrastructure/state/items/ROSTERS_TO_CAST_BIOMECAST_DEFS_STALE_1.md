# ROSTERS_TO_CAST_BIOMECAST_DEFS_STALE_1 — rosters_to_cast.py excludes nearly every live roster row

## Found while resolving `ANIMAL_TOLERANCES_JOIN_BROKEN_1`, 2026-09-20 FOUNDRY

`design/Jawa/fauna/rosters_to_cast.py` regenerates `cast_assignment.csv` (the fauna
cast record 7+ downstream generators read: `gen_cast_patch.py`, `animal_tolerances.py`,
`allocate_cast.py`, `refill_cast.py`, `gen_name_patch.py`, `gen_creature_art_sheet.py`,
`gen_creature_size_sheet.py`) from `design/Jawa/worldbuilding/biomes/rosters/*.json` —
the owner-authored source of truth since `BIOME_FAUNA_ASSIGNMENT_SITTING_1` (2026-09-09).

Its `BIOMECAST_DEFS` set (line ~67), sourced from `_def_bindings_2026-09-09.md §1`,
still lists the **23 pre-migration biome defNames** (`Desert`, `AB_MycoticJungle`,
`ZBiome_Badlands`, …) that `BIOME_OWNERSHIP_WAVE_1` replaced with `RUT_`-prefixed
BiomeDefs. But the roster JSONs themselves were already re-authored with the live
names — `the_rot.json`'s `defNames` is `['RUT_TheRot']`, `the_miasma.json` is
`['RUT_Miasma']`, etc. (confirmed: every roster file's `defNames` field checked,
2026-09-20). Since `build_rows()` requires `b in BIOMECAST_DEFS` to accept a roster's
fauna rows, and `BIOMECAST_DEFS` names the OLD biomes while the rosters name the NEW
ones, **almost every roster row is routed to `offowner` and silently excluded.**

**MEASURED** (dry run, `python3 rosters_to_cast.py --out /tmp/cast_assignment_DRYRUN.csv`,
output never written to the real file): **62 rows across 5 biomes**, versus hundreds of
rows sitting in the rosters — `RUT_Desert` alone has 53 fauna rows in `desert.json` and
gets zero. The only rows that land are the ones still keyed to an old name somewhere
(`fall_line.json`'s injection layer uses `['ExtremeDesert', 'Desert', 'AridShrubland']`;
`the_pyrelands.json` uses `['ZBiome_Grasslands']`, never renamed; `the_lantern_deeps.json`
partially matches via `AB_PropaneLakes`).

## Why this wasn't caught yet

`cast_assignment.csv` on disk today (232 unique animal defNames, still keyed to the old
biome names) predates this defect being introduced — it was generated once, correctly,
back when `BIOMECAST_DEFS` and the rosters still agreed, and has only been hand-edited
incrementally since (`MLIE_FAUNA_ABSORPTION_1`'s many "repointed to RSW_ port" passes
touch individual rows, never a full `rosters_to_cast.py --write` regenerate). Nobody has
re-run the full regenerate since the rosters were renamed, so the drift has been
invisible.

## Owed

1. Rebuild `BIOMECAST_DEFS` from the live `RUT_`-prefixed names the same way
   `biome_flora.py`'s `FAMILIES` was rekeyed at `366c278d6` — cross-check against each
   roster's own `defNames`, not name-guessing.
2. Before writing the real `cast_assignment.csv`, diff the regenerated roster against
   today's file the same way `ANIMAL_TOLERANCES_JOIN_BROKEN_1`'s fix did: this file
   feeds `gen_cast_patch.py`, `animal_tolerances.py` and 5 other generators, at least
   one of which (`animal_tolerances.py`, now merge-safe per its own fix) already
   defends itself against a shrinking cast; the others may not.
3. Regenerating `cast_assignment.csv` for real is a bigger, more consequential act than
   this note — treat it as its own pass, not a one-line fix folded into another item.

## Not measured here

Whether `gen_cast_patch.py`'s own output (were `BiomeCast_Ashkarr.xml` not already
retired) would look meaningfully different once `cast_assignment.csv` reflects the real
roster content — out of scope; that file stays dead per `BIOME_CAST_PATCH_DEAD_NAMES_1`.
