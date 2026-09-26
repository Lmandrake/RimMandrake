# GREENTIDE_RM_MOD_BUILD_1 — build RM_Greentide as its own RimMandrake mod

**the Greentide - twin pair, mod EXISTS (123 vs 287 lines)**

Phase A row 13 of `design/RimMandrake/biome_mod_architecture.md`. Parent:
`BIOME_MOD_SPLIT_EXECUTION_1`. Governed by `BIOME_PAINT_ONCE_AT_THE_END_1`.

## 🔑 STATE — MEASURED 2026-09-22 on the Mac, and narrower than the spec below implies

🔴 **`biome_mod_architecture.md` §4a supersedes the six-step restatement below for this biome:**
*"Greentide's Phase A is steps 3, 4 and 6 only."* Steps 1 and 2 are already done — the mod exists
and its content is authored — and **§4a rules that NOTHING IS MERGED IN**, because the merge the
old plan specified would break the split. Read §4a before this item's `## spec`.

| step | state |
|---|---|
| 1 scaffold | ✅ DONE — `mandrake.rm.greentide`, `loadAfter` on `mandrake.rm.creaturebehaviors`, `RM_GreentideSettings : ModSettings` with `SettingsCategory`/`DoSettingsWindowContents`, `Defs/BiomeDefs/` present |
| 2 copy content | ✅ DONE — 24 files: `RM_Greentide` BiomeDef, own `workerClass` `RimMandrake.Greentide.RM_BiomeWorker_Greentide`, terrains, hediffs, jobs, workgivers, designations, items, keyed language, compiled `RimMandrake.Greentide.dll`. `wildAnimals` is 7 vanilla entries with zero `RSW_`/`RUT_` rows — correct per step 2, the Star Wars cast arrives via `WildAnimals_Greentide.xml` |
| 3 freeze the twin | ✅ DONE 2026-09-22, header present and forbidding the merge |
| 4 retarget | ✅ **NOTHING OWED — RE-MEASURED 2026-09-23, file by file.** All five candidates were comments or deliberate non-patches; see below |
| 5 prove it loads | ⛔ Windows Desktop only |
| 6 commit/push | owed with step 5 — step 4 produced no edits to commit |
| paint-list append | ✅ both rows present in `infrastructure/state/facts/biome_paint_list.md` (and corrected at `f4998b494` — they were still ordering the forbidden merge) |

### 🔴 Step 4 is MUCH narrower than the reference counts suggest — do not sweep it

Raw counts show ~30 places naming `RUT_Greentide` and not `RM_Greentide`. **Most are correct as
they are.** The mod's own `About.xml` scopes eight `GREENTIDE_MECHANICS_1` mechanics *out* of the
generic mod by name — wet-bulb, dry-air blower, scald/steam devils, Roil/Breaklight weather,
tree-fall, Lunger, root causeways, the Greatbole. So these must stay `RUT_`-only and a mechanical
"second op" pass would wire eight deliberately-excluded campaign mechanics into a franchise-free
mod:

- `RUT_GreentideWetBulbLock_BiomeWiring.xml` (10 refs) — scoped out, leave
- `RUT_RoilLock_BiomeWiring.xml` (10 refs) — scoped out, leave
- `RUT_Greentide_LivingBolesGenStep*.xml`, `RUT_Greentide_RootCausewaysGenStep*.xml` — scoped out
- `RUT_Breaklight.xml`, `RUT_RoilWeather.xml`, `RUT_GreentideWetBulbLock.xml` — scoped out
- `FishTypesStrip_NoFishBiomes.xml` — `RM_Greentide` has no `fishTypes` to strip (MEASURED absent)

✅ **Also NOT a defect, checked and cleared:** the three `EnvironmentalHazards` C# files that name
`RUT_Greentide` (`RM_LivingBoleBiomeExtension.cs`, `RM_WetBulbExtension.cs`,
`RM_RootCausewayBiomeExtension.cs`) carry it **only inside explanatory comments** as example XML —
there are no hardcoded defName string literals. Step 4's *"kit C# string constants"* clause has
nothing to do here. ⛔ Do not "retarget" a comment.

### ✅ The "genuinely owed set" was NOT owed — all five confirmed file by file, 2026-09-23

The item said this set *"needs confirming file by file"*. It was confirmed, and **0 of 5 need a second
op.** Each was read, not counted:

- **`BiomeDescriptions_Ashkarr.xml`** — its one reference is a **trailing comment**
  (`<!-- "the Greentide" - RUT_Greentide ... -->`); the operation itself targets the **donor** def
  `BiomeCypreJungle`. ⇒ And a second op would be wrong anyway: `RM_Greentide_Biome.xml` **already
  carries its own `<label>` and a 396-character `<description>`** natively, deliberately worded
  franchise-free (no Scald, no donor geography). Nothing to patch.
- **`BiomeFlora_Ashkarr.xml`** — its one reference is a comment **inside that file's own
  "biomes this file deliberately does NOT patch" block**, reading *"`RUT_Greentide` (11 plants,
  authored in its own def)"*. ⇒ The file already excludes the Greentide on purpose, for the reason
  `BIOMEFLORA_PATCH_WIPES_WILDPLANTS_1` records. ⛔ Do not add it back in.
- **`RSW_ScrapNestBird.xml`** (1 ref) and **`RSW_TunnelSnake.xml`** (2 refs) — **every one is inside an
  XML comment.** Both files' `<wildBiomes>` lists `AridShrubland` only, and both say in their own prose
  that `wildBiomes` is donor metadata a BiomeDef never reads because `wildAnimals` fully replaces it
  per-biome. ⇒ Exactly the case this item already cleared for the three `EnvironmentalHazards` C# files:
  ⛔ **do not retarget a comment.** The item listed these as owed while stating that rule two paragraphs
  above — that contradiction is what this correction removes.
- **`gen_cast_patch.py`** — was marked UNMEASURED. MEASURED now: **zero occurrences of "Greentide"** in
  the file, and it writes the `RUT_`-prefixed campaign layer by design. Nothing owed.
- ⚠️ `BiomeNames_Ashkarr.xml` not referencing `RUT_Greentide` is **not** a mystery to solve: our biomes
  carry their own labels natively, as `RM_Greentide_Biome.xml` demonstrates.

🔑 **What the audit actually found, and it is a different piece of work in a different item:**
`RM_Greentide`'s own `wildPlants` still holds **six vanilla temperate rows** — `Plant_TreeOak` 2.0,
`Plant_TreePoplar` 1.2, `Plant_Bush` 1.5, `Plant_Grass` 2.0, `Plant_TallGrass` 1.0, `Plant_Berry` 0.6 —
**which is precisely the list the owner rejected** when he asked for a jungle of our own. ⇒ That is
`GREENTIDE_JUNGLE_TREE_ROSTER_1`'s 22 rows landing in this def, not a retarget, and it is ⛔ **blocked
on a Desktop measurement**: whether his fire ruling (*harmed by fire, never an ignition source*) is
expressible at all, which every one of the 22 rows depends on.

⇒ **This item's remaining work is step 5 (prove it loads, Desktop-only) and step 6 (commit/push).**
Step 4 closed with nothing to write.

Retarget-outright (target need not be on the world): `_def_bindings_2026-09-09.md`,
`biome_name_migration.py`, `biome_flora.py`, `gen_fish_types.py`, `biome_flora_rosters.md`,
`the_greentide.json`, `validation.py` `QUALIFYING_BIOMES`, and the queue items that still name only
the twin.

## ✅ Two of §4a's three optional additions are RULED IN — owner, 2026-09-22

He was offered §4a's three unapplied cherry-picks as a checkbox card and took these two:

1. **`Disease_OrganDecay` as a 7th disease** on `RM_Greentide` (it currently carries six:
   `Disease_Flu`, `Disease_Plague`, `Disease_Malaria`, `Disease_GutWorms`, `Disease_AnimalFlu`,
   `Disease_AnimalPlague`).
2. **`allowFarmingCamps`** — currently unset on `RM_Greentide` (MEASURED absent).

🔴 **The third is SUPERSEDED, not deferred.** §4a's *"a vanilla-only `fishTypes`/`maxFishPopulation`
pair"* was rejected in the same answer — verbatim: *"Create exotic new jungle fish to catch, not
base game fish."* ⛔ Do not author the vanilla-only pair; that work is now
`GREENTIDE_EXOTIC_JUNGLE_FISH_1`.

⇒ Also owed, same sitting: `GREENTIDE_JUNGLE_TREE_ROSTER_1` (he rejected the generic def's
oak-and-poplar tree list and ruled ≥10 jungle trees of our own, plus the signature giant).

## spec

🔑 **`biome_mod_architecture.md` §5 Phase A is the authority — read it, do not re-derive
it from here.** Steps 1–6, restated only far enough to start:

1. **Scaffold** `About/About.xml` with `mandrake.rm.greentide`, `loadAfter` on the §2d shared libraries,
   a `ModSettings` class with the master toggle (§6), an empty `Defs/BiomeDefs/`.
   `deploy_custom_mods.py --mod <name>` dry run, then `--apply`.
2. **Copy the content in** as `RM_Greentide` — the BiomeDef plus its terrain, plant, weather,
   condition and hediff defs, textures, and the kit C# under namespace
   `RimMandrake.<Mod>`. ⛔ Every `RSW_`/`SW_`/`RUT_` entry in `<wildAnimals>` stays OUT and
   goes to `src/RimUtinni/UtinniPatches/Patches/WildAnimals_<Biome>.xml` as a
   `PatchOperationAdd` onto `RM_Greentide`, with `MayRequire="mandrake.rsw.swbestiary"`.
   `WildAnimals_Pyrelands.xml` is the existing shape. Any donor `workerClass`
   (`AlphaBiomes.*`, `VanillaBiomes.*`, `BiomesPlus.*`, `ReGrowthCore.*`) becomes this
   mod's own `RM_BiomeWorker_<X>` — a donor type in `workerClass` is a hard dependency the
   RimMandrake tier may not assume.
3. **FREEZE the `RUT_` def, do not delete it.** It carries the player's world until the
   terminal paint. Byte-for-byte as it is, one header comment only: *"carrying the world
   until the terminal paint; content lives in `mandrake.rm.greentide`; do not edit here."* From that moment
   every content fix lands in `RM_Greentide` only.
4. **Retarget what does not need to be on the world** (kit specs, `_def_bindings_*.md`,
   queue items, `validation.py` `QUALIFYING_BIOMES`, kit C# string constants). Anything
   that must keep working on the live world (`BiomeNames_Ashkarr.xml`,
   `BiomeDescriptions_Ashkarr.xml`, doctrine patches, `race/wildBiomes`,
   `gen_cast_patch.py` output) gets a **second** op for `RM_Greentide` beside the `RUT_` one, so
   both behave identically until Phase B.
5. **Prove it loads and plays** — minimal list + this mod + `mandrake.rut.patches` +
   **all five expansions** (owner, 2026-09-19: every test list carries every expansion).

## verify

- Zero new Config errors in `Player.log` — and 🔴 grep the log, `validate_patch.py` cannot
  see config errors.
- `validate_patch.py <path> --live --defs` on the new Utinni fauna patch. An unmatched
  `PatchOperationAdd` is **silent**, so a clean run is not proof a row landed — confirm
  from a post-load def dump.
- A quicktest map on a **scratch** world whose landing tile is set to `RM_Greentide` through
  `jawa/world_*` at `Page_SelectStartingSite`. ⛔ Never the canonical save.
- `deploy_custom_mods.py` plan read before `--apply`; a `-` line is a deletion, look at it.

## criteria

`mandrake.rm.greentide` exists, deploys, and loads clean carrying `RM_Greentide` with its own content and its own
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
