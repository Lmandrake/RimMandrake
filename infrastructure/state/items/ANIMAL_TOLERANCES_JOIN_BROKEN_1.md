# ANIMAL_TOLERANCES_JOIN_BROKEN_1 — RESOLVED: join fixed, regenerate made merge-safe, deployed

## Found while closing `BIOME_CAST_PATCH_DEAD_NAMES_1`, 2026-09-20 FOUNDRY

That item confirmed `src/RimUtinni/UtinniPatches/Patches/BiomeCast_Ashkarr.xml` (the
fauna cast patch) targeted 22 pre-migration biome defNames that `BIOME_OWNERSHIP_WAVE_1`
(2026-09-09) replaced with `RUT_`-prefixed BiomeDefs — zero of those 22 names are
painted on any of the frozen world's 21,872 tiles, so the file was pure no-op dead
weight and was deleted (design + src + deployed copies).

`design/Jawa/fauna/animal_tolerances.py`'s `homes()` had the identical root-cause
defect — it reads `cast_assignment.csv`'s `biome` column (pre-migration names:
`Desert`, `AB_MycoticJungle`, …) and looked each one up in `world/ASHKARR_WORLDMAP_
tiles.csv`'s `biome` column, now exclusively `RUT_`-prefixed. Every lookup missed.
Unlike the dead cast file, the deployed `AnimalTolerances_Ashkarr.xml` (16,103 lines,
401 `PatchOperationConditional`s, `ComfyTemperatureMin`/`Max` — a **hard spawn gate**,
`WildAnimalSpawner.cs:47/111`, strict inequality, buffer 0) targets the ANIMAL's own
`ThingDef/statBases` directly, so it kept applying live and unaffected by the name
migration — meaning the danger was never "currently broken," only "would delete a
live safety net for ~200 animals the instant anyone ran the generator expecting a
routine refresh."

## Root cause, and why it went further than expected

`_OLD_TO_NEW_BIOME` in `animal_tolerances.py` now resolves the join, cross-derived
from `biome_flora.py`'s FAMILIES rekey (`366c278d6`, `BIOME_FLORA_GENERATOR_REPAIR_1`
— a commonality-multiset match, not name-guessing) plus `9350e29a3`
(`PROPANE_LAKES_ROSTER_STALE_1`) for `AB_PropaneLakes` → `RUT_Umbra`, the one pair
that moved to a differently-named biome outright. A dry run with only that fix
resolved every biome name (zero "matched nothing" misses) — but it also surfaced a
**second, independent drift that the original filing didn't anticipate**:

- Of the 401 animal defNames the deployed patch already covers, only **44** are still
  named anywhere in today's `cast_assignment.csv` at all — `MLIE_FAUNA_ABSORPTION_1`'s
  many passes since the last regenerate (2026-09-12, `935b29048`) ported most of the
  original Alpha Animals (`AA_*`)/`BMT_*` cast onto `RSW_`/ported replacements,
  leaving the old names in the CSV nowhere.
- Of those 401, **310 are still live race ThingDefs** in today's 617-mod def dump
  (MEASURED against `defs.sqlite`, 2026-09-20 01:40 capture) — i.e. mostly "no longer
  curated," not "no longer real." A regenerate that simply emitted `compute()`'s rows
  (only animals `homes()` can join today) would have written **129 operations**,
  silently dropping the widened band for those ~280+ still-loaded animals — a
  narrowing-by-omission, exactly the class of bug the file's own "WIDEN ONLY, NEVER
  NARROW" rule (2026-08-23 ruling) exists to prevent. Only 91 of the 401 are
  genuinely gone from the current dump (BMT_/other retired mod defs) and safe to drop
  outright, since a `PatchOperationConditional` on a nonexistent def already no-ops
  harmlessly.

## Fix shipped, `design/Jawa/fauna/animal_tolerances.py`

1. **`_OLD_TO_NEW_BIOME`** (module-level dict) + `homes()` resolves through it before
   the tile-temp lookup, warning loudly (not silently) if any biome name still
   matches nothing.
2. **`pin_orphans()`** (new): before writing, reads the *currently deployed* file's
   defNames (`_deployed_defnames()`, called before `emit()` overwrites it). Any
   defName the deployment already covers but that `compute()`'s fresh join didn't
   reach gets **pinned** to its own current (already-patched) value verbatim — same
   XML shape, `new == cur`, clearly commented `"not in current cast_assignment.csv;
   pinned to today's live value so a regenerate cannot narrow it"`. Only a defName
   absent from the current def dump entirely is dropped.
3. Corrected the generated file's own stale header (*"Assumes BiomeCast_Ashkarr.xml
   SHIPS ... Deploy both or neither"*) and the module docstring's matching claim —
   both false since that file's retirement.

**Verified, not assumed:**
- Dry run (no `--write`): 129 refitted, 94 "already survived their whole home" (no
  op needed — base value already wide enough), 297 pinned, 91 genuinely-gone dropped.
  Final file: **426 operations** (was 401).
- XML well-formed (`xml.etree.ElementTree.parse`) — caught and fixed one self-inflicted
  bug in this pass: a `--` inside a generated `<!-- ... -->` comment, illegal XML.
- **Empirical zero-narrowing diff**: parsed old (401 ops) vs new (426 ops) per-defName
  min/max. 91 dropped (exactly the confirmed-gone set), **0 narrowed**. Every animal
  the deployed file protected today keeps a MIN ≤ old MIN and MAX ≥ old MAX.
- `validate_patch.py --live <DefDump>`: 0 errors (defName-existence checked for all
  426; the WARNs are the generator's own pre-existing, intentional add-if-missing
  xpath shape, present at the same per-animal rate as before).
- Confirmed the def dump reflects **post-patch** state before trusting any "already
  wide enough" comparison (`AA_AcanthamoebaGiganteaHuge`'s dump MAX reads `81.2`,
  matching the deployed patch's widened value exactly, not the pre-patch `65`) — so
  `compute()`'s `cur` was always comparing against live reality, making its
  widen-only clamp a real guarantee, not a hope.
- Deployed via `deploy_custom_mods.py --mod UtinniPatches --apply` (also picked up an
  unrelated already-committed `WildAnimals_Pyrelands.xml` fix that was sitting
  undeployed). Game is up on the full 617-mod list; per the standing rule, this only
  prepares the next load — no restart triggered.

## Not this item's job (unchanged)

Whether the widened bands are numerically RIGHT for the `RUT_` biome each animal
actually spawns in (versus merely non-empty) remains a follow-on question.

## Spun off, not fixed here

`design/Jawa/fauna/rosters_to_cast.py`'s `BIOMECAST_DEFS` set (the list of biome
defNames it will accept a roster row for) **still lists the same 23 pre-migration
biome names**, while the actual `design/Jawa/worldbuilding/biomes/rosters/*.json`
files were already re-authored with the live `RUT_` names. A dry run
(`--out /tmp/...`, not written to the real file) produces only **62 rows across 5
biomes** today — nearly every roster's fauna (hundreds of rows across `RUT_Desert`,
`RUT_TheRot`, `RUT_Miasma`, …) is silently excluded as "off-owner." Filed as
`ROSTERS_TO_CAST_BIOMECAST_DEFS_STALE_1` — this is the actual generator of
`cast_assignment.csv` and a much larger-blast-radius fix (7+ downstream consumers),
out of scope for this pass.
