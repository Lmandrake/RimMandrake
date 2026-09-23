# LONGSHADE_RM_MOD_BUILD_1 — build RM_LongShade as its own RimMandrake mod

**the Long Shade (the livable desert)**

Phase A row 2 of `design/RimMandrake/biome_mod_architecture.md`. Parent:
`BIOME_MOD_SPLIT_EXECUTION_1`. Governed by `BIOME_PAINT_ONCE_AT_THE_END_1`.

## 🔑 STATE — MEASURED 2026-09-23, from scratch (no `RM_` twin, no folder exists)

| step | state |
|---|---|
| 1 scaffold | ⛔ OWED — `src/RimMandrake/` has no `LongShade`/`Desert` folder (MEASURED `ls`); confirmed by `Transient/biome_standalone_status_2026-09-23.md:40` (MISSING) |
| 2 copy content | ⛔ OWED — BiomeDef, terrain/weather/disease tables, 53 fauna + 9 flora rows all live only in `RUT_Desert.xml` (305 lines) |
| 3 freeze twin | ⛔ OWED — `RUT_Desert.xml` header (lines 1-102) is the authoring note, no freeze banner |
| 4 retarget | ⛔ OWED but SMALL — every live reference sampled is comment/doc-only (item 7) |
| 5 prove it loads | ⛔ Desktop-only, blocked on 1-4 |
| 6 commit/push | owed with step 5 |
| paint-list append | ✅ present — `infrastructure/state/facts/biome_paint_list.md:28`, row `RUT_Desert / the Desert / ... / PAINT` |

### 2. The def today

`src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Desert.xml`, 305 lines (`wc -l`).
`workerClass = RimWorld.BiomeWorker_Desert` — **vanilla Core, not a donor type** → no
`RM_BiomeWorker_LongShade` owed (this biome does NOT hit the generic step-2 donor-worker
case). `modExtensions`: **none present** (checked, no such block). Terrain
(`terrainsByFertility`): `Sand` ≤0.8, `Soil` >0.8, both vanilla. Weather
(`baseWeatherCommonalities`): `Clear` 90, `DryThunderstorm` 4, `Rain`/`RainyThunderstorm`/
`SnowGentle`/`SnowHard` 0, `GrayPall` 1 (MayRequire Anomaly), `Sandstorm` 4 (MayRequire
Odyssey) — all vanilla/DLC, no custom WeatherDef. Diseases: 9 vanilla `Disease_*` defs by
name (Flu, Plague, GutWorms, MuscleParasites, FibrousMechanites, SensoryMechanites,
AnimalFlu, AnimalPlague, OrganDecay). `foragedFood = RSW_RawHubbaGourd` (MayRequire
`mandrake.rsw.swbestiary`). `allowedPackAnimals`: 5 `RSW_` herd defs (Bantha/Ronto/Eopie/
Jamel/Falumpaset), all MayRequire `mandrake.rsw.swbestiary`.

### 3. wildAnimals split

53 rows (MEASURED via `xml.etree`, `len(list(wildAnimals))` == 53; the block is entirely
the **shorthand** `<DefName>commonality</DefName>` form, no `<li>`).

- **51 rows `RSW_*`**, MayRequire `mandrake.rsw.swbestiary` → **all** go to
  `WildAnimals_LongShade.xml` — does not exist yet (`ls .../UtinniPatches/Patches/` has
  only `WildAnimals_{CrackedLands,Greentide,Pyrelands}.xml`).
- **2 rows `JOE_Landopus`, `JOE_Cephalope`** — no MayRequire, NOT Star-Wars-named (donor
  "Cephaloids" mod, absorbed verbatim by `STAT_NORM_WAVE2_RETIRE_1`). Their defs live in
  `src/RimUtinni/UtinniPatches/Defs/Absorbed_Cephaloids/Absorbed_Cephaloids_Defs.xml`
  (817 lines) which is **also used by `RUT_ExtremeDesert.xml`** (Stillsand). Per Q9
  (non-SW donor fauna: leave inline) these belong in `RM_LongShade`'s own wildAnimals —
  but the def home is shared with Stillsand, so a wholesale move orphans that mod.
  **Flag for FOUNDRY/BENCH, not resolved here.**

### 4. wildPlants split

9 rows (same method): `RM_Leachmoss` 1.5, `RSW_Ultracactus` 0.8, `RUT_Vorrel` 0.1,
`RM_Venomvine` 0.25, `RSW_Dunegrass` 0.6, `RSW_Plant_Chakroot_Wild` 0.3,
`RSW_Plant_HubbaGourd_Wild` 0.2, `RSW_VellaraBloom` 0.12, `RSW_SweetbarkTree` 0.06.

- `RM_Leachmoss` / `RM_Venomvine` — already RimMandrake-tier
  (`mandrake.rm.environmentalhazards`), stay wired by MayRequire, **no move**.
- `RUT_Vorrel` — Utinni-tier (`mandrake.rut.ashkarrflora`, `RUT_Staggerseed.xml` family)
  → per §7 Q8 (dissolve ashkarrflora, plants move into the biome's own RM mod, renamed
  `RM_`) this **moves** into `RM_LongShade` as `RM_Vorrel*` (name still WORKING per
  `STAGGERSEED_SHIPPING_NAME_1`).
- **6 rows `RSW_*`** (Ultracactus/Dunegrass/Chakroot/HubbaGourd/VellaraBloom/SweetbarkTree)
  — genuine RimStarWars-tier flora (chak-root, hubba gourd are canon Tatooine plants).
  🔴 **No `WildPlants_<Biome>.xml` route exists anywhere yet** — `WildAnimals_Greentide.xml`
  itself documents this identical 8-row gap as still OWED (comment at its line 73), with no
  actual `wildPlants` `<Operation>` present. This is a shared, still-unsolved shape across
  biome mods, not a Long Shade-specific defect.
- No owner-rejected rows to flag: none of these 9 appear in `desert.md`'s `flora_purged`
  list (26 rejected Earth-nameable rows — `Plant_SaguaroCactus`, `Plant_Agave`, etc. —
  correctly never wired).

### 5. Roster vs def diff

- **flora**: roster (9) == def (9) exactly, 1:1 by defName. No diff.
- **fauna**: roster (53) == def (53) by count, not by literal string — the roster stores
  **pre-port donor/bare names** (`Bantha`, `AA_DesertAve`, …), the def stores the
  **ported** `RSW_`/`JOE_` names (e.g. `AA_DesertAve`→`RSW_Sandstrider`,
  `AA_Terramorph`→`RSW_Ferroclaw`, `AA_MammothWorm`→`RSW_Tuskcoil` — all confirmed 1:1 by
  commonality + the def's own inline comments). **Two real diffs, not naming noise:**
  - roster row `AA_SandLion` (0.5, "sand burrower swimmer") has **no** wired def row —
    UNCERTAIN whether superseded by `JOE_Cephalope`'s near-identical description or
    genuinely dropped.
  - def rows `RSW_Stoneback` (0.5) and `RSW_TruffleMole` (0.5) are wired (comment:
    `DESERT_ROUND2_IMPORTS_UNLANDED_1`, 2026-09-20) but **absent from `rosters/desert.json`**
    — the roster file is stale by these 2 additions.
- **Art presence**: not re-measured row-by-row here (62 rows is out of this item's budget)
  — CITING `DESERT_FAMILY_PORT_EXECUTION_1`'s own MEASURED figure for the whole desert
  family (109 rows spanning Long Shade + Stillsand + Leaning Scrub): only 3 of 84 ported
  rows carry our own art, 81 still point at donor texture paths, and 77 of those 81 already
  have art jobs **in flight** in the artpipe (source `DESERT_FAMILY_PORT_EXECUTION_1`) —
  do not re-queue them.

### 6. Content to move into the mod

- `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Desert.xml` → becomes `RM_LongShade`
  (step 2, the whole def).
- `src/RimUtinni/AshkarrFlora/Defs/ThingDefs_Plants/RUT_Staggerseed.xml` +
  `HediffDefs/RUT_Staggerseed_Hediffs.xml` + `ThingDefs_Items/RUT_Staggerseed_Items.xml` +
  `RecipeDefs/RUT_Staggerseed_Recipes.xml` + `ThoughtDefs/RUT_Staggerseed_Thoughts.xml` →
  move + rename `RM_Vorrel*` (Q8).
- **OPEN, do not move yet**: `Absorbed_Cephaloids_Defs.xml` (817 lines) — shared with
  Stillsand (`RUT_ExtremeDesert`), see item 3.

Stays in Utinni/RimStarWars (correct as-is): `RSW_Ultracactus.xml` and the other RSW_
flora/fauna (own tier, `mandrake.rsw.swbestiary`) — referenced, not owned, by this biome.
**No C# is owed to move**: shade-grid mechanics (`RM_MapComponent_ShadeGrid`,
`RM_HediffComp_ShadeStagger`, `RM_JobGiver_WanderInShadeGrid`,
`RM_ShadeSeekingWanderExtension`) already ship in `mandrake.rm.creaturebehaviors`; contact-
venom (`RM_Patch_LeachmossWildSpawnGate.cs` etc.) already ships in
`mandrake.rm.environmentalhazards` — both §2d shared libraries, `loadAfter` only.

### 7. `RUT_Desert` references across the repo

`grep -rl "RUT_Desert\b"` (excluding `.git`, the def itself, `items/closed/`) returns
~40 hits. Sampled the load-bearing ones:

- `BiomeDescriptions_Ashkarr.xml:222` — **comment only**; the actual `<Operation>` xpath
  targets the **donor** vanilla `Desert` def, and its `<value>` is byte-identical to
  `RUT_Desert.xml`'s own native `<description>` — no second op needed (same pattern as
  Greentide's clearance of this file).
- `BiomeNames_Ashkarr.xml`, `AnimalTolerances_Ashkarr.xml`, the doctrine patches
  (`AncientDangerGenSteps_AmbientDoctrine.xml` etc.) — **zero** references to `RUT_Desert`
  (checked); Long Shade has no doctrine wiring to retarget.
- `RSW_Groundrunner.xml`, `RSW_GreatDevourer.xml`, `RSW_MatureFleshbeast.xml`,
  `RSW_ShadeWhale.xml`, `RSW_WraidAlpha.xml`, `RM_Leachmoss.xml` — **comment/prose only**
  (`<race><wildBiomes>` is explicitly dropped on all of these) — leave.
- `design/Jawa/mods/biome_flora.py:108` — the generator already special-cases `RUT_Desert`
  as "OWNED def, no operation emitted"; needs a matching no-op entry for `RM_LongShade`,
  not urgent.
- `modset_builder.py:243-247`, `canon.yml:679`, dashboards, `CODE_REVIEW_STATUS.json` —
  comment/generated, not owed.
- Design docs (`_def_bindings_2026-09-09.md`, `biome_flora_rosters.md`,
  `desert_shade_plants_design.md`, `explosive_plant_growth_design.md`,
  `biome_name_migration.py`) — retarget-outright per step 4's own list.
- `validation.py` `QUALIFYING_BIOMES`: **0 hits for `RUT_Desert`** anywhere in the repo
  (MEASURED grep) — nothing to retarget there.

⇒ **Nothing found needs a "second op" — step 4's scope here is comment/doc-only.**

### 8. Mechanics/kit state

SHIPPED (§2d shared libraries, cite not rebuild): shade grid
(`RM_MapComponent_ShadeGrid` + `RM_JobGiver_WanderInShadeGrid` +
`RM_HediffComp_ShadeStagger`/`RM_HediffCompProperties_ShadeStagger` +
`RM_ShadeSeekingWanderExtension`, in `mandrake.rm.creaturebehaviors`); contact venom
(`CompContactVenom`/`MapComponent_ContactVenom` + Leachmoss spawn gate, in
`mandrake.rm.environmentalhazards`). Unbuilt (`desert.md:372-383` `## Owed`): glitter-birds
(shadow commensals), sand filter-feeding C# for the shade-whale, burst-predator statFactor
polish, world-feature authoring for the wide gaps, `WORLDMAP_DESERT_BAND_REPAIR_1` (only
~51% of the def sits in its own arc 60-88 band). **None block Phase A steps 1-6** — the
sheet's own §10 says the def/roster can land first.

### 9. Dependencies & items building INTO this mod

| item | state (from its own text) | blocks step 2? |
|---|---|---|
| `BIOME_MOD_SPLIT_EXECUTION_1` | parent item | no |
| `BIOME_SPECIFIC_FAUNA_LAW_1` | names Long Shade as an example | no — governs future review, not this build |
| `DESERT_FAMILY_PORT_EXECUTION_1` | def port ~96/109 done; 12 rows blocked on owner (7 droids + vanilla replacements, none in `RUT_Desert`'s own tables); art review owed | no — step 2 copies the already-ported `RSW_`/`JOE_` names as-is |
| `DESERT_PORT_PLACEHOLDER_ART_1` | art follow-on | no |
| `EXTREME_DESERT_SIGNATURE_FLORA_1`, `ECOSYSTEM_PYRAMID_LAW_1`, `COMMISSION_LEDGER_CLEANUP_1`, `FALL_LINE_ARRIVAL_MECHANISM_1`, `DUPLICATE_CANON_DEFNAME_PAIRS_1`, `ROSTER_DEAD_BMT_NAMES_SWEEP_1`, `BIOME_WORLD_SWITCH_WAVE_1` | cite `RUT_Desert` in passing/history | no |

(States above are read from each item's own prose, not re-verified with `rimflow show`
this pass — budget.)

### 10. Blockers

**None for steps 1-4.** Step 5 (prove it loads) is Desktop-only. The two flagged open
questions (shared `Absorbed_Cephaloids` ownership with Stillsand; no `WildPlants_<Biome>`/
foragedFood/pack-animal Utinni-patch shape exists anywhere yet) are design questions, not
blockers — Greentide shipped steps 1-3 with its own identical wildPlants gap still open.

### 11. Concrete step plan

1. Scaffold `src/RimMandrake/LongShade/About/About.xml`, packageId `mandrake.rm.longshade`,
   `loadAfter`: `mandrake.rm.creaturebehaviors`, `mandrake.rm.environmentalhazards`.
   `RM_LongShadeSettings : ModSettings` (master toggle + shade-grid/contact-venom
   cross-biome toggles, §6a). Empty `Defs/BiomeDefs/`.
   `deploy_custom_mods.py --mod LongShade` dry run → `--apply`.
2. Copy `RUT_Desert.xml` → `src/RimMandrake/LongShade/Defs/BiomeDefs/RM_LongShade.xml`,
   defName `RM_LongShade`, `workerClass` unchanged (vanilla). Strip the 51 `RSW_`
   wildAnimals rows; keep `JOE_Landopus`/`JOE_Cephalope` inline pending the shared-
   Cephaloids decision (item 3/6). Move+rename `RUT_Vorrel*` → `RM_Vorrel*` into this
   mod's own Defs. Leave `RM_Leachmoss`/`RM_Venomvine` as external MayRequire refs.
3. Write `src/RimUtinni/UtinniPatches/Patches/WildAnimals_LongShade.xml`: 51
   `PatchOperationAdd` rows onto `/Defs/BiomeDef[defName="RM_LongShade"]/wildAnimals`,
   `MayRequire="mandrake.rsw.swbestiary"`, `loadAfter mandrake.rm.longshade`. Raise the 6
   RSW_ wildPlants rows / `RSW_RawHubbaGourd` foragedFood / 5 RSW_ pack-animal rows to
   BENCH as the same unsolved shape Greentide already carries open — do not invent a new
   patch shape unilaterally.
4. Freeze `RUT_Desert.xml` with the standard header comment, body byte-for-byte otherwise.
5. Retarget (comment/doc only, item 7): `_def_bindings_2026-09-09.md`,
   `biome_flora_rosters.md`, `desert_shade_plants_design.md`, `biome_flora.py`'s OWNED-def
   table (add `RM_LongShade` beside `RUT_Desert`).
6. Prove: minimal list + `LongShade` + `mandrake.rut.patches` +
   `mandrake.rm.creaturebehaviors` + `mandrake.rm.environmentalhazards` +
   `mandrake.rsw.swbestiary` + all 5 expansions; quicktest on a scratch world tile set to
   `RM_LongShade`.
7. Commit (name what `RUT_Desert` got wrong: nothing yet — it's the source of truth being
   copied, not corrected) + append `RM_LongShade`/`mandrake.rm.longshade` to
   `WORLD_REMAKE_FINAL_STEP_1`'s paint list.

## spec

🔑 **`biome_mod_architecture.md` §5 Phase A is the authority — read it, do not re-derive
it from here.** Steps 1–6, restated only far enough to start:

1. **Scaffold** `About/About.xml` with `mandrake.rm.longshade`, `loadAfter` on the §2d shared libraries,
   a `ModSettings` class with the master toggle (§6), an empty `Defs/BiomeDefs/`.
   `deploy_custom_mods.py --mod <name>` dry run, then `--apply`.
2. **Copy the content in** as `RM_LongShade` — the BiomeDef plus its terrain, plant, weather,
   condition and hediff defs, textures, and the kit C# under namespace
   `RimMandrake.<Mod>`. ⛔ Every `RSW_`/`SW_`/`RUT_` entry in `<wildAnimals>` stays OUT and
   goes to `src/RimUtinni/UtinniPatches/Patches/WildAnimals_<Biome>.xml` as a
   `PatchOperationAdd` onto `RM_LongShade`, with `MayRequire="mandrake.rsw.swbestiary"`.
   `WildAnimals_Pyrelands.xml` is the existing shape. Any donor `workerClass`
   (`AlphaBiomes.*`, `VanillaBiomes.*`, `BiomesPlus.*`, `ReGrowthCore.*`) becomes this
   mod's own `RM_BiomeWorker_<X>` — a donor type in `workerClass` is a hard dependency the
   RimMandrake tier may not assume.
3. **FREEZE the `RUT_` def, do not delete it.** It carries the player's world until the
   terminal paint. Byte-for-byte as it is, one header comment only: *"carrying the world
   until the terminal paint; content lives in `mandrake.rm.longshade`; do not edit here."* From that moment
   every content fix lands in `RM_LongShade` only.
4. **Retarget what does not need to be on the world** (kit specs, `_def_bindings_*.md`,
   queue items, `validation.py` `QUALIFYING_BIOMES`, kit C# string constants). Anything
   that must keep working on the live world (`BiomeNames_Ashkarr.xml`,
   `BiomeDescriptions_Ashkarr.xml`, doctrine patches, `race/wildBiomes`,
   `gen_cast_patch.py` output) gets a **second** op for `RM_LongShade` beside the `RUT_` one, so
   both behave identically until Phase B.
5. **Prove it loads and plays** — minimal list + this mod + `mandrake.rut.patches` +
   **all five expansions** (owner, 2026-09-19: every test list carries every expansion).

## verify

- Zero new Config errors in `Player.log` — and 🔴 grep the log, `validate_patch.py` cannot
  see config errors.
- `validate_patch.py <path> --live --defs` on the new Utinni fauna patch. An unmatched
  `PatchOperationAdd` is **silent**, so a clean run is not proof a row landed — confirm
  from a post-load def dump.
- A quicktest map on a **scratch** world whose landing tile is set to `RM_LongShade` through
  `jawa/world_*` at `Page_SelectStartingSite`. ⛔ Never the canonical save.
- `deploy_custom_mods.py` plan read before `--apply`; a `-` line is a deletion, look at it.

## criteria

`mandrake.rm.longshade` exists, deploys, and loads clean carrying `RM_LongShade` with its own content and its own
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
