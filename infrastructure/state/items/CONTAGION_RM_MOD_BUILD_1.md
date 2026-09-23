# CONTAGION_RM_MOD_BUILD_1 — build RM_Contagion as its own RimMandrake mod

**the Contagion**

Phase A row 16 of `design/RimMandrake/biome_mod_architecture.md`. Parent:
`BIOME_MOD_SPLIT_EXECUTION_1`. Governed by `BIOME_PAINT_ONCE_AT_THE_END_1`.

## 🔑 STATE — MEASURED 2026-09-23

### 1. Step table

| step | state |
|---|---|
| 1 scaffold | ⛔ OWED — no `src/RimMandrake/Contagion/` folder exists (checked, absent) |
| 2 copy content | ⛔ OWED — mod does not exist; content today lives only at `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Contagion.xml` |
| 3 freeze twin | ⛔ OWED — file carries only its authoring comment, no freeze header |
| 4 retarget | ⛔ OWED — see §7; most repo hits are prose, ~10 real retargets |
| 5 prove it loads | ⛔ Windows Desktop only |
| 6 commit/push | owed with step 5 |
| paint-list append | ✅ DONE — row present, `infrastructure/state/facts/biome_paint_list.md:26` |

### 2. The def today

Path `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Contagion.xml`, **156 lines** (MEASURED
`wc -l`). `workerClass` = `AlphaBiomes.BiomeWorker_OcularForest` — donor type → owes
`RM_BiomeWorker_Contagion`. `modExtensions`: **none** (MEASURED, `find('modExtensions')` →
`None`). Terrain: `lakeBeachTerrain`/`mudTerrain`/`riverbankTerrain` = `GU_AlienSandFine`;
`terrainsByFertility` = `GU_AlienSandFine`(≤0.2) → `GU_AlienSand`(0.2–0.87) →
`GU_RichAlienSand`(≥0.87) — ⚠️ none of the three `GU_` terrain defs resolve anywhere in this
repo's `src/` (MEASURED grep); unnamed-donor terrain, pre-existing, carried over as-is, not
this migration's problem. Weather (MEASURED, 6 entries): `AB_RedFog`(70, MayRequire
`sarg.alphabiomes`) `Clear`(8) `Rain`(1) `DryThunderstorm`(1) `RainyThunderstorm`(1)
`FoggyRain`(1). Diseases (MEASURED, 8): `AB_Disease_SporesAllergy`(50)
`AB_Disease_AnimalSporesAllergy`(50) both MayRequire `sarg.alphabiomes`,
`Disease_Malaria`(160) `Disease_SleepingSickness`(140) `Disease_Flu`(100)
`Disease_Plague`(100) `Disease_GutWorms`(80) `Disease_MuscleParasites`(80).

### 3. wildAnimals split

MEASURED via `xml.etree` (`len(list(node))` on `<wildAnimals>` — the shorthand
`<DefName>commonality</DefName>` form throughout, no `<li>`): **11 rows, ZERO Star Wars
entries** (no `RSW_`/`SW_`/`mlie.*`).

| defName | commonality | prefix/donor | verdict |
|---|---|---|---|
| AA_OcularJelly | 2.0 | sarg.alphaanimals | stays in `RM_Contagion` (non-SW donor, §3b) |
| AA_RedSpore | 0.85 | sarg.alphaanimals | stays |
| AA_RedGoo | 0.75 | sarg.alphaanimals | stays |
| AA_InfectedAerofleet | 0.5 | sarg.alphaanimals | stays |
| AA_BloodShrimp | 0.2 | sarg.alphaanimals | stays |
| AA_Drainer | 0.15 | sarg.alphaanimals | stays |
| RUT_Sytheclaw | 0.15 | ours, no MayRequire | 🔑 special case, below |
| AA_Helixien | 0.1 | sarg.alphaanimals | stays |
| AA_RoughPlatedMonitor | 0.1 | sarg.alphaanimals | stays |
| AA_Swarmling | 0.1 | sarg.alphaanimals | stays |
| AA_DrainerLarva | 0.05 | sarg.alphaanimals | stays |

⇒ **No `WildAnimals_Contagion.xml` Utinni patch is needed for fauna at all** — same finding
shape as Greentide's exemplar ("zero RSW/RUT rows"): step 2's generic text ("every
RSW_/SW_/RUT_ entry stays OUT") does not literally apply here because there are zero SW rows.

🔑 **`RUT_Sytheclaw` is the one real case, and it is NOT Star Wars** (§7 Q10, ruled
2026-09-22: all seven misfiled campaign creatures, Sytheclaw included, "move into their
biome's RimMandrake mod, renamed `RM_`"). Its ThingDef/PawnKindDef live at
`src/RimUtinni/UtinniPatches/Defs/ThingDefs_Races/RUT_PyrelandsPortedFauna.xml:251,384`
(Utinni tier today), and it is **shared inline across three biomes** — Pyrelands (0.2),
Greentide (0.2, `WildAnimals_Greentide.xml:132`), and here (0.15). `BIOME_SPECIFIC_FAUNA_LAW_1`
lists it among the 52 multi-homed species, unadjudicated, and multi-home evictions are
STOPPED (owner ruling) — do not evict it here. No item executes the Q10 rename sweep yet.
Until it lands, wiring `RUT_Sytheclaw` inline into `RM_Contagion` creates a live cross-tier
dependency (a RimMandrake def needing a RimUtinni-tier def to resolve) — recommend gating it
`MayRequire="mandrake.rut.patches"` in the copy, matching the caution
`WildAnimals_Greentide.xml:92-97` already records for this same creature.

### 4. wildPlants split

MEASURED (10 rows, shorthand form): `AB_AlienGrass`(1.0) `AB_AlienTree`(1.0)
`AB_RedLeaves`(0.6) `AB_HalfAlienTree`(0.5) `AB_RedPlantsTall`(0.5) `AB_GlobularPlant`(0.4)
`AB_TentacularPlant`(0.4) `AB_BloodBouquet`(0.3) `RUT_RustPuff`(0.3, MayRequire
`mandrake.rut.rotsporekit`) `AB_AlienTree_Polluted`(0.15). All `AB_` rows are non-SW donor
(Alpha Biomes) → stay in `RM_Contagion` (⚠️ these carry no MayRequire at all today, unlike
the weather/disease blocks — pre-existing gap, not introduced by this migration).
`RUT_RustPuff` is a real cross-mod dependency: its ThingDef lives in
`src/RimUtinni/RotSporeKit/Defs/ThingDefs_Plants/RUT_RotSporeKit_Flora.xml` (MEASURED grep)
— `mandrake.rut.rotsporekit`, which §2a row 3 says **absorbs into `mandrake.rm.therot`**
(owed, not done); until then keep its current MayRequire. No plant row here is
owner-rejected filler (unlike Greentide's 6 vanilla rows) — nothing to flag.

### 5. Roster vs def diff

Roster fauna: 16 rows (`the_contagion.json` `fauna`). 11 match the def 1:1 (10 `AA_`
keep/adjust-keep + `RUT_Sytheclaw`). **5 roster rows are NOT wired into the def today**
(all `"action": "import"`; all donor-mod defNames, not ours — art means that donor's own
texture, UNMEASURED whether those donor mods are even in the current load):
`AA_Eyeling`(0.6), `AA_FungalHusk`(0.5, size-ruled 2 cells), `AA_OcularNightling`(0.5),
`AG_OcularSlinger`(0.5, donor prefix UNMEASURED), `GR_Fleshling`(0.5). No def row is absent
from the roster. Roster flora: 10 rows, 1:1 match with the def's 10 `wildPlants` — no diff.
`flora_purged` (`AB_EyeGrass` + wholesale donor vanilla) are correctly absent from both.

### 6. Content to move into the mod

Nothing under `src/RimUtinni/**` is Contagion-biome *mechanics* content — MEASURED: no
`kits/contagion_kit_spec.md` exists (only Phase-A row with no kit). What moves is the
`RUT_Contagion.xml` BiomeDef itself (156 lines, self-contained, no separate terrain/plant
files) — copy whole, retarget defName, ship as `RM_Contagion`.

**Looks like it belongs, stays in Utinni**: `RUT_ContagionRingScatter.xml`,
`RUT_ContagionRingScatter_Register.xml`, `RUT_ContagionProbe.xml` (IncidentDef),
`RUT_DeadCreep.xml`, `RUT_DyingCreep.xml`, `RUT_IncidentWorker_ContagionProbe.cs` — all named
"Contagion" but are **The Forge's F5 die-off ring** (§8), hardcoded to `RUT_TheForge`, not
this biome. Leave for `THEFORGE_RM_MOD_BUILD_1`.

### 7. References to `RUT_Contagion` across the repo

MEASURED `grep -rl "RUT_Contagion"` (33 hits total), each read:

- **Retarget outright**: `design/Jawa/fauna/biome_name_migration.py`,
  `design/Jawa/mods/biome_flora.py`, `biome_flora_rosters.md`, `_def_bindings_2026-09-09.md`,
  `rosters/the_contagion.json`'s own `defNames` list, `creature_register_rows.json`,
  `facts/biome_rosters.md` + `facts/biome_paint_list.md`.
- **Needs a SECOND op for `RM_Contagion`**: `world/biome_world_switch_apply.py` (the MAP
  list), `Patches/BiomeDescriptions_Ashkarr.xml`, `Patches/BiomeFlora_Ashkarr.xml` — ⚠️
  UNMEASURED whether the Contagion block there wipes `wildPlants` the way Greentide's did
  (`BIOMEFLORA_PATCH_WIPES_WILDPLANTS_1`) — read before touching.
- **Comment/prose — leave**: `fall_line.md`, `forge_kit_spec.md`, `biome_mod_architecture.md`,
  5 closed items, 6 live items (`BIOME_WORLD_SWITCH_WAVE_1`, `BIOME_SPECIFIC_FAUNA_LAW_1`,
  `ECOSYSTEM_PYRAMID_LAW_1`, `FORGE_MECHANICS_1`, `OCULAR_OVERDRIVE_SITE_1`,
  `MIASMA_MECHANICS_1`), a handoff doc, a research doc, `build_landmark_density_sheet.py`,
  dashboard/health JSON, 4 `Transient/*` files — none is an executable retarget.
- C#: `RUT_IncidentWorker_ContagionProbe.cs` names `RUT_TheForge`, not `RUT_Contagion` —
  Forge's, no move here.

### 8. Mechanics/kit state

**No Contagion-specific kit exists** — the one Phase-A row with no `kits/*_kit_spec.md`.
Step 2's "kit C#" clause is empty for this biome.

🔑 **F5 "the Contagion die-off ring" belongs to THE FORGE, not this mod.**
`forge_kit_spec.md:314` names it as a Forge mechanic (dead creep ring at the ash skirts
where the Forge borders the Contagion). Confirmed from the shipped C#:
`src/RimMandrake/EnvironmentalHazards/Source/RUT_IncidentWorker_ContagionProbe.cs` — its own
header says *"FORGE_MECHANICS_1 F5"* and it hardcodes the `RUT_TheForge` biome defName, not
`RUT_Contagion`. Ships in `RimMandrake.EnvironmentalHazards` (already RimMandrake-tier,
`RM_EnvironmentalHazards.csproj`) — **SHIPPED**, per `FORGE_MECHANICS_1` (state `doing`). Its
defs (`RUT_ContagionProbe`, `RUT_DeadCreep`, `RUT_DyingCreep`, `RUT_ContagionRingScatter*`)
still live under `src/RimUtinni/UtinniPatches/` and move with `THEFORGE_RM_MOD_BUILD_1`, not
this item — nothing here waits on it and nothing here should absorb it.
(`Transient/contagion_placement_preview_2026-09-07.svg` is the Contagion's world-placement
preview, unrelated to F5 — not relevant to this mod build, not cited further.)

`CONTAGION_GENOME_ORGAN_GROWING_1` (design, `proposed`) targets "a relevant Contagion
creature" — UNMEASURED which one, its own design pass, not this build.

### 9. Dependencies & items building INTO this mod

- `CONTAGION_GENOME_ORGAN_GROWING_1` — proposed, needs offline; picks a host creature from
  this roster later; does not block this mod.
- `FORGE_MECHANICS_1` — doing, needs offline; F5 references "the Contagion" by name but
  ships into Forge (§8) — no dependency either direction.
- `BIOME_SPECIFIC_FAUNA_LAW_1` — proposed, needs offline; holds `RUT_Sytheclaw`'s
  un-adjudicated multi-home status — informs §3's recommendation, does not block it.
- `OCULAR_OVERDRIVE_SITE_1` — doing, needs owner; custom-dungeon plot site on 3 Ashfall
  Range tiles of this biome — world/plot content, no def dependency here.
- `TREE_GRAPHICS_OWNERSHIP_1` — doing, BLOCKED (unrelated art blocker); owes the
  `AB_HalfAlienTree` art redo — art-only, does not block steps 1–4.
- `CONTAGION_BIOME_PLACEMENT_1` — **CLOSED** (`items/closed/`) — world placement done, not a
  build dependency (world contact is Phase B regardless).

### 10. Blockers

**None for steps 1–4.** The def, roster and sheet are all present. `RUT_Sytheclaw`'s
temporary `MayRequire` gate and whether to wait for the Q10 rename sweep are FOUNDRY's
call at build time, not blockers — either choice ships a working mod. Step 5 is
Windows-Desktop-only, which is not a blocker of 1–4 per standing rule.

### 11. Concrete step plan

1. `deploy_custom_mods.py --mod Contagion` dry run against new
   `src/RimMandrake/Contagion/About/About.xml`: packageId `mandrake.rm.contagion`. No §2d
   shared library is referenced (no modExtensions, no kit C#), so `loadAfter` is base +
   Odyssey only, plus soft `MayRequire` deps on `sarg.alphabiomes`/`sarg.alphaanimals`
   already in the def. `ModSettings` class `RM_ContagionSettings` with the master toggle
   (§6). Empty `Defs/BiomeDefs/`. Then `--apply`.
2. Copy `RUT_Contagion.xml`'s `<BiomeDef>` verbatim into `Defs/BiomeDefs/RM_Contagion.xml`,
   defName → `RM_Contagion`, `workerClass` → new `RimMandrake.Contagion.RM_BiomeWorker_Contagion`
   (port `AlphaBiomes.BiomeWorker_OcularForest` — read that class first, UNMEASURED here).
   Keep all 11 `wildAnimals` + 10 `wildPlants` inline (§3/§4 — zero go to a Utinni patch).
   Gate `RUT_Sytheclaw` `MayRequire="mandrake.rut.patches"` until the Q10 sweep lands
   `RM_Sytheclaw`. No `WildAnimals_Contagion.xml` file is needed.
3. Freeze `RUT_Contagion.xml` with the standard header, unchanged otherwise.
4. Retarget the 7 files in §7's first bullet outright; add a second op for the 3 files in
   §7's second bullet, onto `RM_Contagion`.
5/6. Desktop-only; commit with explicit paths naming what the twin's `workerClass`/donor
   terrain got wrong.

### False statements found elsewhere

`BIOME_MOD_SPLIT_EXECUTION_1.md`'s own `rimflow show` summary line still reads *"BLOCKED on
10 owner questions"* while its own body says *"✅ UNBLOCKED — all 10 questions ruled
2026-09-21"* and the architecture doc's §7 says *"Nothing is open... every row can start."*
The one-line summary is stale against the item's own body — flagging for BENCH, not editing
it myself.

## spec

🔑 **`biome_mod_architecture.md` §5 Phase A is the authority — read it, do not re-derive
it from here.** Steps 1–6, restated only far enough to start:

1. **Scaffold** `About/About.xml` with `mandrake.rm.contagion`, `loadAfter` on the §2d shared libraries,
   a `ModSettings` class with the master toggle (§6), an empty `Defs/BiomeDefs/`.
   `deploy_custom_mods.py --mod <name>` dry run, then `--apply`.
2. **Copy the content in** as `RM_Contagion` — the BiomeDef plus its terrain, plant, weather,
   condition and hediff defs, textures, and the kit C# under namespace
   `RimMandrake.<Mod>`. ⛔ Every `RSW_`/`SW_`/`RUT_` entry in `<wildAnimals>` stays OUT and
   goes to `src/RimUtinni/UtinniPatches/Patches/WildAnimals_<Biome>.xml` as a
   `PatchOperationAdd` onto `RM_Contagion`, with `MayRequire="mandrake.rsw.swbestiary"`.
   `WildAnimals_Pyrelands.xml` is the existing shape. Any donor `workerClass`
   (`AlphaBiomes.*`, `VanillaBiomes.*`, `BiomesPlus.*`, `ReGrowthCore.*`) becomes this
   mod's own `RM_BiomeWorker_<X>` — a donor type in `workerClass` is a hard dependency the
   RimMandrake tier may not assume.
3. **FREEZE the `RUT_` def, do not delete it.** It carries the player's world until the
   terminal paint. Byte-for-byte as it is, one header comment only: *"carrying the world
   until the terminal paint; content lives in `mandrake.rm.contagion`; do not edit here."* From that moment
   every content fix lands in `RM_Contagion` only.
4. **Retarget what does not need to be on the world** (kit specs, `_def_bindings_*.md`,
   queue items, `validation.py` `QUALIFYING_BIOMES`, kit C# string constants). Anything
   that must keep working on the live world (`BiomeNames_Ashkarr.xml`,
   `BiomeDescriptions_Ashkarr.xml`, doctrine patches, `race/wildBiomes`,
   `gen_cast_patch.py` output) gets a **second** op for `RM_Contagion` beside the `RUT_` one, so
   both behave identically until Phase B.
5. **Prove it loads and plays** — minimal list + this mod + `mandrake.rut.patches` +
   **all five expansions** (owner, 2026-09-19: every test list carries every expansion).

## verify

- Zero new Config errors in `Player.log` — and 🔴 grep the log, `validate_patch.py` cannot
  see config errors.
- `validate_patch.py <path> --live --defs` on the new Utinni fauna patch. An unmatched
  `PatchOperationAdd` is **silent**, so a clean run is not proof a row landed — confirm
  from a post-load def dump.
- A quicktest map on a **scratch** world whose landing tile is set to `RM_Contagion` through
  `jawa/world_*` at `Page_SelectStartingSite`. ⛔ Never the canonical save.
- `deploy_custom_mods.py` plan read before `--apply`; a `-` line is a deletion, look at it.

## criteria

`mandrake.rm.contagion` exists, deploys, and loads clean carrying `RM_Contagion` with its own content and its own
Mod Settings screen; the `RUT_` twin is frozen with its header and unchanged; the Star Wars
fauna ride a Utinni patch rather than the RimMandrake def; one commit, explicit paths, the
message naming what the twin got wrong; and the mod is appended to
`WORLD_REMAKE_FINAL_STEP_1`'s paint list.

## Watch out

- ⛔ **Do not paint, and do not cite a tile count as evidence about this biome.** The planet
  is painted ONCE, at the end. A def of ours carrying 0 tiles is the expected mid-migration
  state, not a defect.
- ⛔ **Do not delete the `RUT_` def.** Deleting a painted def before Phase B destroys the
  save.
- ⚠️ A `<li>` in the wrong place discards the WHOLE def, silently.
