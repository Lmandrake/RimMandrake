# BIOME_WORLD_SWITCH_WAVE_1 — repaint the planet onto the owned BiomeDefs

Owner, 2026-09-12, at the bench reading the world map at tile 17007: *"We have
tickets out to make ALL biomes on the Worldmap our own, right? This one still says
GRINDTerra Deep Desert."* Answer: no — `BIOME_OWNERSHIP_WAVE_1` closed at `cc11aee6e`
on **def authoring only** ("world-tile switch is a separate, later bridge" item, per its
own commit message) and that later item was never filed. Its verify line ("zero defs
from the donor list remain painted") was therefore never met.

## MEASURED 2026-09-12 (live `jawa/world_tile_export`, 21,872 tiles)
- **Ours: 3,983 tiles / 6 defs. Donor or vanilla: 17,889 tiles / 23 defs (82%).**
- ExtremeDesert 3969 · AB_PropaneLakes 2531 · Desert 2390 · AB_MycoticJungle 2204 ·
  Wasteland 1853 · AB_RockyCrags 1135 · ZBiome_Badlands 970 · AridShrubland 628 ·
  PoisonForest 546 · AB_MechanoidIntrusion 236 · BiomeCypreJungle 235 ·
  ZBiome_DesertOasis 223 · ZBiome_Grasslands 222 · AB_OcularForest 179 ·
  AB_FeraliskInfestedJungle 161 · AB_GelatinousSuperorganism 96 · AB_MiasmicMangrove 93 ·
  Scarlands 90 · COMIGO_GreaterSwamp_Tropical 43 · AB_TarPits 41 ·
  AB_PyroclasticConflagration 31 · LavaField 8 · Volcano 5.
- Why the owner sees "GRINDTerra": vanilla `ExtremeDesert`/`Desert`/`AridShrubland` are
  RE-DECLARED by `grimterra.terrainretexturemod` (live `get_defs` reports that mod as the
  def's source), so the tile card credits GRiNDTerra even though our campaign label
  ("the Deep Desert") is applied. Owning the tile with `RUT_ExtremeDesert` is the only
  fix; relabelling cannot change the source mod.

## spec
- Template: `PYRELANDS_WORLD_SWITCH_1` (batches, getter read-back, CSV re-export + LOSS
  diff, R36 backup bar). Map donor def → owned def from `BIOME_OWNERSHIP_WAVE_1`'s
  commit (`RUT_Desert`, `RUT_ExtremeDesert`, `RUT_AridShrubland`, `RUT_Wasteland`,
  `RUT_PoisonForest`, `RUT_Scarlands`, `RUT_Contagion`, `RUT_Webwork`, `RUT_Slime`,
  `RUT_TheRot`, `RUT_TheForge` (LavaField/Volcano/AB_PyroclasticConflagration),
  `RUT_RustCathedral`, `RUT_Umbra`, `RUT_CrackedLands`, `RUT_ForsakenCrags`,
  `RUT_FeverWood`, `RUT_Greentide`, `RUT_Miasma`, `RUT_Sump`, `RUT_WeepingStones`;
  `ZBiome_Grasslands` → `RM_FE_Pyrelands` rides `PYRELANDS_WORLD_SWITCH_1`;
  `BiomeGRimond` is already switched).
- Order: biome before links (a repaint over a river hides it — re-read
  `rimbridge/references/world-authoring.md`); one `world_commit` at the end; deliberate
  CANONICAL re-save with the Saves backup + stat-after discipline.
- Regenerate the de-dup union and the animal-side `wildBiomes` strip against the new
  defNames as each batch lands; `WORLDMAP_BIOME_ICONS_REGEN_1` afterwards.

## verify
- Fresh live tile export: **zero** of the 23 donor/vanilla defs above remain painted;
  every painted def is `RUT_`/`RM_`-tier. Say the count.
- Tile 17007's card reads an owned def (no donor mod credited) — the owner looks.
- Full-list load, zero new Config errors; one quicktest map per switched batch.

## traps
- The frozen world CSV (`world/ASHKARR_WORLDMAP_tiles.csv` + `.frozen.json` stamp) must
  be re-exported and re-stamped in the same change, or the next fingerprint check fails.
- `world_tile_set` on a river/road tile: check `allowRivers`/`allowRoads` on the OWNED
  def first — a def that forbids them silently drops the link.

## status — DONE (live), 2026-09-12 (FOUNDRY)

All 22 donor/vanilla defs in this item's scope switched. **17,667 tiles repainted**
(the item's 17,889 minus `ZBiome_Grasslands` 222, which rides
`PYRELANDS_WORLD_SWITCH_1`). Live `jawa/world_tile_export` after
`jawa/world_commit`: **zero** of those 22 defs remain painted anywhere; 21,872/21,872
tiles account for. Driver: `world/biome_world_switch_apply.py`.

### mapping used — every pair resolved from evidence, none guessed
Sixteen pairs come from `cc11aee6e`'s own commit message. The six the message left
unpaired were resolved from each `RUT_*.xml`'s header comment, which names its donor
outright ("Replaces the donor `X`"); the pairing is a clean 6↔6 bijection against the
six donors the message did not name. **Nothing was excluded as unresolved.**

| donor def | tiles before | → owned def | after | source of the pairing |
|---|---:|---|---:|---|
| ExtremeDesert | 3969 | RUT_ExtremeDesert | 3969 | commit msg |
| AB_PropaneLakes | 2531 | RUT_Umbra | 2531 | commit msg (land tiles; the 57 `RUT_PropaneLake` water tiles were already owned and untouched) |
| Desert | 2390 | RUT_Desert | 2390 | commit msg |
| AB_MycoticJungle | 2204 | RUT_TheRot | 2204 | commit msg |
| Wasteland | 1853 | RUT_Wasteland | 1853 | commit msg |
| AB_RockyCrags | 1135 | RUT_ForsakenCrags | 1135 | `RUT_ForsakenCrags.xml` header |
| ZBiome_Badlands | 970 | RUT_CrackedLands | 970 | commit msg |
| AridShrubland | 628 | RUT_AridShrubland | 628 | commit msg |
| PoisonForest | 546 | RUT_PoisonForest | 546 | commit msg |
| AB_MechanoidIntrusion | 236 | RUT_RustCathedral | 236 | commit msg |
| BiomeCypreJungle | 235 | RUT_Greentide | 235 | `RUT_Greentide.xml` header |
| ZBiome_DesertOasis | 223 | RUT_WeepingStones | 223 | `RUT_WeepingStones.xml` header |
| AB_OcularForest | 179 | RUT_Contagion | 179 | commit msg |
| AB_FeraliskInfestedJungle | 161 | RUT_Webwork | 161 | commit msg |
| AB_GelatinousSuperorganism | 96 | RUT_Slime | 96 | commit msg |
| AB_MiasmicMangrove | 93 | RUT_Miasma | 93 | `RUT_Miasma.xml` header |
| Scarlands | 90 | RUT_Scarlands | 90 | commit msg |
| COMIGO_GreaterSwamp_Tropical | 43 | RUT_FeverWood | 43 | `RUT_FeverWood.xml` header |
| AB_TarPits | 41 | RUT_Sump | 41 | `RUT_Sump.xml` header |
| AB_PyroclasticConflagration | 31 | RUT_TheForge | **44** | commit msg (3 donors merge) |
| LavaField | 8 | RUT_TheForge | ↑ | commit msg |
| Volcano | 5 | RUT_TheForge | ↑ | commit msg |

**Excluded, deliberately:** `ZBiome_Grasslands` (222) — `PYRELANDS_WORLD_SWITCH_1`.

### verification (fresh live export, not the setter's own word)
- After-census: 27 painted defs, **every one `RUT_`** except `ZBiome_Grasslands` 222.
  Donor counts moved exactly, none duplicated or dropped
  (`RUT_TheForge` = 5+8+31 = 44 ✓).
- Whole-planet field diff before→after: **`biome` on 17,667 tiles; every other engine
  field on 0 tiles.** Nothing else moved.
- All 20 `RUT_` defs confirmed live and loaded first (`jawa/get_defs`, 20/20 resolved,
  `modName: RimUtinni Patches (Jawa campaign)`).
- **Tile 17007 now reads `RUT_ExtremeDesert`, sourced to RimUtinni Patches** — the
  owner's "GRiNDTerra Deep Desert" complaint is answered.
- Canonical CSV rebased from the live export
  (`ashkarr_rebase_from_save.py --apply`): only `biome` changed, 17,667 tiles; the CSV
  was otherwise already in sync. `verify_frozen.py --restamp` → ✅ CURRENT,
  sha `d48b69a2d49d`, 21,872 rows.
- Save: `BIOME_WORLD_SWITCH_WAVE_1_2026-09-12.rws` (16,466,747 B). Backup taken first
  (`CANONICAL_ASHKARR_START_2026-09-12.rws.bak-pre-biome-world-switch-2026-09-12`);
  Saves folder stat before/after shows **exactly one new file and no existing file
  changed** — `saveName` was honoured this time.

### 🔴 consequence the owner should rule on — 239 road tiles went invisible
Measured, not feared. Four owned defs are more restrictive than the donor they replace:

| tile change | link effect |
|---|---|
| ExtremeDesert (roads T) → RUT_ExtremeDesert (roads **F**) | **205 tiles' roads hidden** |
| AB_PropaneLakes (roads T) → RUT_Umbra (roads **F**) | **34 tiles' roads hidden** |
| LavaField/Volcano (rivers T) → RUT_TheForge (rivers **F**) | 5 tiles' rivers hidden |

`hiddenByBiome` 15 → **259**; visible road edge-ends 2470 → 2032, visible rivers
636 → 630. ✅ **Nothing was deleted** — stored `potentialRoads` stayed at 2,470 and
`potentialRivers` at 652 across the switch, so flipping a def's `allowRoads` restores
every link with no re-authoring.
- `RUT_ExtremeDesert`'s ban is **owner-ruled and quoted in the def** (dune_sea.md SS6,
  "No roads through the deep dune"), so those 205 are arguably the intent landing.
- `RUT_Umbra`'s `allowRoads=false` carries **no sheet ban in its header comment** while
  the donor allowed roads and 34 tiles use them. Flagged as possibly unintended — a
  one-line def change would restore them.

### follow-up 2026-09-12 (offline bookkeeping, no bridge) — wildBiomes eviction + icons

**wildBiomes eviction/de-dup: ran successfully, output NOT shipped (stale input found).**
No code change was needed or made — `biome_wildbiomes_evictions.py`'s dedup logic is
untouched. Root cause of the ">300s timeout": the animal-side scan
(`gen_cast_patch._animal_side_biomes()`) walks every INSTALLED mod's raw XML across
`/mnt/c/...` (WSL→Windows drive, ~1,254 mods, pruned to skip Textures/Sounds/etc. per
its own comment) plus the newest def-dump capture; that cross-filesystem walk is
genuinely ~10 minutes end to end (measured: started 18:53, cache file written 19:03),
not a bug — the tool already documents exactly why it can't be capture-only (a
disk-only or capture-only source each miss real collisions; see its docstring's
2026-08-26/2026-08-22 incident history). The only "fix" applied was operational: run
in the background with `--cache <path>` instead of under a short synchronous timeout;
a second run now reuses the cache and returns instantly. **Not** changed: which mods
it walks, what counts as a collision, any filtering logic.

Ran it for real against the post-switch painted set (fresh capture
`2026-09-12T22-49-15Z`): **688 eviction pairs found, but 686 of them are noise**, not
signal. `painted_defs()` unions the live tile CSV (correctly all-`RUT_` now) with
`design/Jawa/worldbuilding/biomes/rosters/*.json`'s `defNames` field — and **at least
20 of those 22 roster files still name the OLD DONOR bare defName**
(`arid_shrubland.json`→`AridShrubland`, `desert.json`→`Desert`,
`dune_sea_deep_desert.json`→`ExtremeDesert`, `fall_line.json`→ all three,
`forsaken_crags.json`→`AB_RockyCrags`, `poison_forest.json`→`PoisonForest`, etc. —
only `the_lantern_deeps.json` and `the_propane_lakes.json` already carry a `RUT_`
name). That's why the run's 4 non-empty biome buckets were `AridShrubland` 256,
`Desert` 232, `ExtremeDesert` 198 (all bare donor names, now painted on **zero**
tiles per this item's own verification — so these 686 ops would be dead weight
against the tool's own stated rule, "an unpainted biome ... is none of our
business") and `RUT_Scarlands` 2 (the one **genuine** new pair, reached via the live
CSV directly, not the roster). Also seen: 103 rostered pairs left to the de-dup
union, 17 already shipped there, 194 skipped as installed-but-not-in-the-live-mod-set.

Checked whether this also threatens the actual fauna CAST (not just the eviction
step): it doesn't. `cast_assignment.csv` (the source `gen_cast_patch.py` reads for
`BiomeCast_Ashkarr.xml`) is *also* 22/23 donor-named, and the shipped
`BiomeCast_Ashkarr.xml` itself patches 0 `RUT_` defs / 23 donor defs — but every
`RUT_*.xml` (e.g. `RUT_Desert.xml` line 34) says its `wildAnimals`/`wildPlants` were
**transplanted in at authoring time** (`BIOME_OWNERSHIP_WAVE_1`, 2026-09-09) from
that same patch/roster snapshot. So the live cast is intact and baked into the def
itself; `BiomeCast_Ashkarr.xml` is now a harmless no-op for these 22 biomes (correct
by the design comment, not a bug) — flagged and verified, not left as a scare.

**Decision: did not write/ship the eviction XML this pass.** Regenerating
`BiomeCastEvictions_WildBiomes.xml` today would bake the 686 dead-donor-name ops into
a file whose own header says "GENERATED — do not hand-edit," permanently encoding the
roster staleness as if it were real Ash'karr content. Real next step, NOT done here
(roster content edits are a design call, not this task's "input-fetch only" mandate):
rename the `defNames` entries in the ~20 stale roster JSON files above to their
`RUT_` counterparts (the same 1:1 mapping already established in this item's own
mapping table), then re-run `biome_wildbiomes_evictions.py --cache <fresh path> --xml
src/RimUtinni/UtinniPatches/Patches/BiomeCastEvictions_WildBiomes.xml` — at that point
it should cleanly find only the real cross-biome pairs (starting from `RUT_Scarlands`'s
2, likely joined by a few more once the other 19 defs are correctly named).

**Icon regen: there is no script to re-run.** Rechecked `WORLDMAP_BIOME_ICONS_REGEN_1`
(closed `a0728d4be8`, 2026-09-07 MEASURED): worldmap decoration icons are picked by
Biomes Kit's (`zal.biomeskit`) `BiomesKitControls` modExtension — hand-authored
forest/hill/mountain threshold flags on each `BiomeDef` selecting one of several baked
PNG sheets — with **zero code path from `wildPlants`/`wildAnimals`**, so "regenerate
after reassignment" was never a real mechanism to begin with; that finding stands
unchanged by today's tile-paint switch. Checked whether it's moot now anyway: **none**
of the 20 new `RUT_*.xml` biome defs carry a `BiomesKitControls` modExtension at all
(grepped all 20), so tiles painted with them get Biomes Kit's default icon behaviour
for an unflagged biome, not the donor's icon set and not a matched one either. Fixing
this is a manual per-def authoring pass (pick forest/hill/mountain thresholds per
`RUT_*` biome) needing the owner's call on target icon sets — exactly the kind of
"needs a fresh item, not a re-run" case `WORLDMAP_BIOME_ICONS_REGEN_1` already
recommended in 2026-09-07; not attempted here (design authoring, not bookkeeping).

### follow-up 2026-09-12 part 2 (offline bookkeeping, no bridge) — roster rename, eviction rerun, STILL not shipped

**Renamed 19 stale roster `defNames` entries to their `RUT_` successors** (pure key
rename, nothing else touched — checked with a post-edit grep sweep, clean):
`arid_shrubland.json`→`RUT_AridShrubland`, `desert.json`→`RUT_Desert`,
`dune_sea_deep_desert.json`→`RUT_ExtremeDesert`, `forsaken_crags.json`→`RUT_ForsakenCrags`,
`poison_forest.json`→`RUT_PoisonForest`, `the_contagion.json`→`RUT_Contagion`,
`the_cracked_lands.json`→`RUT_CrackedLands`, `the_fever_wood.json`→`RUT_FeverWood`,
`the_forge.json`→`RUT_TheForge` (its 3-donor list `AB_PyroclasticConflagration`/
`LavaField`/`Volcano` collapsed to the one owned def), `the_greentide.json`→`RUT_Greentide`,
`the_miasma.json`→`RUT_Miasma`, `the_rot.json`→`RUT_TheRot`,
`the_rust_cathedral.json`→`RUT_RustCathedral`, `the_scarlands.json`→`RUT_Scarlands`,
`the_slime.json`→`RUT_Slime`, `the_sump.json`→`RUT_Sump`, `the_webwork.json`→`RUT_Webwork`,
`wasteland.json`→`RUT_Wasteland`, `weeping_stones.json`→`RUT_WeepingStones`.

**Deliberately NOT touched** (per this pass's explicit scope): `fall_line.json`
(`ExtremeDesert`/`Desert`/`AridShrubland` — rides a separate item), `the_pyrelands.json`
(`ZBiome_Grasslands` — `PYRELANDS_WORLD_SWITCH_1`), `the_lantern_deeps.json` and
`the_propane_lakes.json` (both still carry bare `AB_PropaneLakes`, left as-is on
explicit instruction), `the_blue_desert.json` (`BiomeGRimond` — already-switched per
this item's own spec line), and the already-`RUT_`-only files (`nightside_ice.json`,
`the_grey_sea.json`, `the_scald.json`, `the_twilight_sea.json`, `wreck_fields.json`
which is empty).

**Reran `biome_wildbiomes_evictions.py --cache <scratch> --xml
.../BiomeCastEvictions_WildBiomes.xml` with a fresh cache (no prior cache existed;
full ~1,254-mod walk, ran to completion, no timeout).** Result: **still 690 pairs
across 4 biomes** — `AridShrubland` 256, `Desert` 234, `ExtremeDesert` 199,
`RUT_Scarlands` 1 (down from 2 pre-rename; the scarlands roster's own fauna-admission
key changed from `Scarlands` to `RUT_Scarlands`, shifting which pairs count as
already-rostered — not investigated further, flagged only).

**Root cause of why the noise didn't clear: `fall_line.json`.** `painted_defs()`
(`src/RimMandrake/Utils/biome_wildbiomes_evictions.py` line 79-83) unions the live
tile CSV with **every** roster file's `defNames` unconditionally — it has no concept
of `"injection_layer": true` and cannot distinguish "this name is a currently-painted
BiomeDef" from "this name identifies a host biome an injection layer overlays."
`fall_line.json` is exactly the second kind (its own `note` field: *"NOT a BiomeDef...
entries are ADDITIONS injected over the underlying defs"*) and its `defNames` are
still the three bare donor names by this pass's explicit instruction not to touch it.
Because those three names are still real strings in the union, `painted_defs()`
reports `AridShrubland`/`Desert`/`ExtremeDesert` as "painted" even though the live
tile export shows **zero** tiles for all three — reproducing the exact 3-bucket noise
pattern from the pre-rename run (686 pairs then, 690 now), just with slightly
different counts because the OTHER 19 files no longer double-contribute fauna
admissions under those bare keys.

**Decision: did NOT ship the regenerated XML.** Per this pass's own stop condition
("suspiciously large counts against biomes that should be zero-tile now"), the run
was reverted (`git checkout -- .../BiomeCastEvictions_WildBiomes.xml`) rather than
committed — the working tree is back to the pre-run committed content, unchanged from
before this session.

**Real next step, NOT done here** (a scope/design call, not this pass's bookkeeping
mandate): either (a) rename `fall_line.json`'s three host names to their `RUT_`
successors too — but that was explicitly out of scope this pass and its "rides a
separate item" framing needs resolving first — or (b) teach `painted_defs()` (and
`rostered()`) to skip `"injection_layer": true` rosters when computing the painted
set, since an injection layer's `defNames` are host references, not paint. Either
fix, alone, should collapse the run to `RUT_Scarlands`' handful of genuine pairs.
Not attempted here: a tool-logic change is outside "input-fetch only" bookkeeping,
and renaming `fall_line.json` contradicts this pass's own explicit instruction.

### owed, not done here
- **wildBiomes eviction patch still not regenerated/shipped**, even after the 19-file
  roster rename above — now blocked on `fall_line.json` (out of this pass's scope) and/or
  a `painted_defs()`/`rostered()` fix to exclude `injection_layer` rosters; see
  "part 2" follow-up above for the exact root cause and the two candidate fixes.
- **Worldmap biome icons for all 20 new `RUT_` defs** — none carry `BiomesKitControls`;
  needs a manual authoring pass with the owner's icon-set call, not a script.
- Full-list cold load + per-batch quicktest (this item's third verify line) — not run.
- The links CSV was **not** rebased. `ashkarr_rebase_from_save.py` would have written
  1,235 road edges over the canonical 1,387: that 152-edge delta is **pre-existing
  drift**, not this pass's doing (potential links were 2,470 before and after), and
  absorbing it silently into this change would have hidden it. Needs its own look.
