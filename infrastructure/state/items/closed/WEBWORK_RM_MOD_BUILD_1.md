# WEBWORK_RM_MOD_BUILD_1 — build RM_Webwork as its own RimMandrake mod

**the Webwork**

Phase A row 17 of `design/RimMandrake/biome_mod_architecture.md`. Parent:
`BIOME_MOD_SPLIT_EXECUTION_1`. Governed by `BIOME_PAINT_ONCE_AT_THE_END_1`.

## 🔑 STATE — MEASURED 2026-09-23

### 1. Step table

| step | state |
|---|---|
| 1 scaffold | ⛔ OWED — `ls src/RimMandrake/Webwork` = no such directory |
| 2 copy content | ⛔ OWED — content lives only in `RUT_Webwork.xml` (160 lines); no `RM_Webwork` def anywhere in `src/` |
| 3 freeze the twin | ⛔ OWED — no freeze header in `RUT_Webwork.xml` (read whole file) |
| 4 retarget | ⛔ OWED — see §7; small (2 doc tables, 3 tooling files); 2 patch files' hits are comments only, like Greentide |
| 5 prove it loads | ⛔ Desktop-only, blocked on 1–4 |
| 6 commit/push | owed with step 5 |
| paint-list append | ✅ DONE — row present, `infrastructure/state/facts/biome_paint_list.md:49` |

### 2. The def today

`src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Webwork.xml`, 160 lines, header dated
2026-09-09 (BIOME_OWNERSHIP_WAVE_1), donor `AB_FeraliskInfestedJungle` (Alpha Biomes).

- `workerClass`: `AlphaBiomes.BiomeWorker_FeraliskInfestedJungle` (donor) → owed
  `RimMandrake.Webwork.RM_BiomeWorker_Webwork` at step 2.
- `modExtensions`: one — `RimMandrake.CreatureBehaviors.RM_FrontCreepExtension`
  (already RM_-tier, ships in the already-active `mandrake.rm.creaturebehaviors`;
  confirmed in `RM_CreatureBehaviors.csproj:66` `<Compile Include>` list, not
  silently dropped). Names `RUT_Webwork_Anchor`/`_Web`/`_Gutter` as its front things.
- terrainsByFertility: `AB_DenseMud`, `AB_DenseGrass` (Alpha Biomes donor terrains),
  `SoilRich` (vanilla).
- baseWeatherCommonalities: 8 vanilla WeatherDefs (Clear/Fog/Rain/DryThunderstorm/
  RainyThunderstorm/FoggyRain/SnowGentle=0/SnowHard=0) — no donor/SW weather.
- diseases: 6 vanilla DiseaseIncidentDefs (Malaria, SleepingSickness, Flu, Plague,
  GutWorms, MuscleParasites) — no donor/SW disease.
- `allowFarmingCamps=true`, `animalDensity=1.0` (corrected from donor 5.4, per
  header comment), `plantDensity=0.9`.

### 3. wildAnimals split — 4 rows, ALL going to Utinni

| defName | commonality | MayRequire | verdict |
|---|---|---|---|
| `Wyyyschokk` | 0.4 | `mlie.starwarsanimalcollection` (donor SW) | → Utinni patch |
| `RSW_JewelBeetle` | 0.3 | `mandrake.rsw.swbestiary` (ours, RSW-tier) | → Utinni patch |
| `Kreetle` | 0.8 | `mlie.starwarsanimalcollection` (donor SW) | → Utinni patch |
| `Shyrack` | 0.2 | `mlie.starwarsanimalcollection` (donor SW) | → Utinni patch |

🔴 **Unlike Greentide (7 vanilla wildAnimals, 0 SW), Webwork's wildAnimals block is
4-for-4 Star Wars fauna** (measured from the MayRequire on each `<li>`). Per
`SW_FAUNA_NEVER_IN_RM_TIER_1` (owner ruling, taken by question card 2026-09-22,
item state `proposed`/`needs offline` but the ruling itself is recorded and cited
as binding by `BIOME_MOD_SPLIT_EXECUTION_1`'s own text), `RM_Webwork`'s
`wildAnimals` block ships **empty** at step 2 — every row moves to a new
`WildAnimals_Webwork.xml`, which **does not exist yet** (confirmed:
`find src/RimUtinni -iname '*Webwork*'` finds only `RUT_Webwork.xml` and
`RUT_WebworkStructures.xml`). `WildAnimals_Pyrelands.xml` is the shape to copy.

### 4. wildPlants split — 7 rows

| defName | commonality | source | verdict |
|---|---|---|---|
| `AB_JungleTree` | 1.1 | Alpha Biomes donor (non-SW) | stays in `RM_Webwork` |
| `RG_Plant_TropicalChokevine` | 1.0 | ReGrowth donor (non-SW) | stays |
| `AB_TangleTea` | 0.4 | Alpha Biomes | stays |
| `Plant_TookeTrap_Wild` | 0.3 | ⚠️ UNCERTAIN | see below |
| `AB_Gomphoeria` | 0.15 | Alpha Biomes | stays |
| `AB_RedBugloss` | 0.07 | Alpha Biomes | stays |
| `AB_Aaklac` | 0.05 | Alpha Biomes | stays |

No owner-rejected vanilla-Earth flora present — the roster's own `flora_purged`
list (`Plant_Grass`/`TallGrass`/`ShrubLow`/`Alocasia`/`Berry`) is already absent
from the live def.

⚠️ **`Plant_TookeTrap_Wild` flag for BENCH/owner, not resolved here**: "tooke-trap"
is CLAUDE.md's own listed example of genuine Star Wars canon IP (Q11a). This
defName appears nowhere else in the repo (`grep -rl` outside `RUT_Webwork.xml`:
zero hits) — it is a bare donor reference with no `MayRequire`, because
`<wildPlants>` uses the shorthand `<DefName>commonality</DefName>` form, which
**cannot carry a MayRequire attribute at all**. So even if it is SW canon, today's
file structurally cannot express the dependency gate the other three animals use.
UNMEASURED: which mod actually ships this defName (not found in
`design/RimStarWars/canon_references/`, which proves nothing per CLAUDE.md's own
137-entries caveat). SW_FAUNA_NEVER_IN_RM_TIER_1's ruling text is titled "fauna"
only — whether it extends to flora is an owner call, not mine to assume.

### 5. Roster vs def diff

Roster (`rosters/the_webwork.json`) fauna: `Wyyyschokk` 0.4, `RSW_JewelBeetle` 0.3,
`Kreetle` 0.2→**0.8 live** (ECOSYSTEM_PYRAMID_LAW_1 boost, already applied to the
def), `Shyrack` 0.2, plus two UNWIRED: `AA_Feralisk` 0.5, `GR_Chickenspider` 0.5.

- **`AA_Feralisk` is stale, not just unwired**: `WYYYSCHOKK_FERALISK_MERGE_1`
  (closed) cut `ThingDef/AA_Feralisk` via Cherry Picker as part of the whole
  `-lisk` clade retirement — the roster row names a **dead def**. Wiring it would
  be wrong, not merely owed.
- `GR_Chickenspider`: UNMEASURED whether it is a live def in the current mod set —
  not checked this pass.
- Roster flora (7 rows) matches the def's 7 `wildPlants` rows exactly — nothing
  unwired, nothing extra.
- Roster `new_defs` (design wishlist, not fauna/flora arrays): egg-mite, pale
  flowers, Wyyyschokk guild pawnkinds (nettik/chirrik/rothrik), parasitic root-mat
  flora — **none built**, none in the def; not step-2 blockers, just not authored.
- Art: UNMEASURED for every roster def this pass (not checked against
  `_south.png`).

### 6. Content to move into the mod

- `src/RimMandrake/CreatureBehaviors/Source/{RM_MapComponent_SenseWeb,
  RM_CompSenseWebNode,RM_JobGiver_ChewAnchors,RM_ChewableExtension,
  RM_FrontCreepExtension}.cs` — **already correctly RM_-tier**, in the shared
  `mandrake.rm.creaturebehaviors` assembly per the 2026-09-11 card ruling ("the
  separate RM_ creature-behaviors assembly... NOT
  `mandrake.rm.environmentalhazards`"). ⛔ Do NOT move into `mandrake.rm.webwork`
  — this mod merely `loadAfter`s it.
- `src/RimUtinni/UtinniPatches/Defs/ThingDefs_Buildings/RUT_WebworkStructures.xml`
  (136 lines, Anchor/Web/Gutter Things) — ⚠️ UNCERTAIN per §3a's test: nothing in
  the three defs' fields is Star Wars- or campaign-specific (placeholder Hive
  texture, generic flammable structures); could plausibly be RM_-tier content
  that only "looks like Utinni." Not resolved — a judgment call, not measured.
- `src/RimUtinni/ShokkweaveEconomy/**` (8 files + DLL) — stays Utinni: the
  Shokkweave sole-source rename/economy is explicitly campaign-specific
  (`the_webwork.md` §6 ban 4, `SHOKKWEAVE_SOLE_SOURCE_1`), not this item's scope.
- `src/RimStarWars/Shokk/**` — correctly its own RSW-tier mod already
  (`SHOKK_RSW_MOD_1`, closed); not part of this mod.

### 7. `RUT_Webwork` references across the repo

`grep -rl` found ~50 hits; most are generated/historical (dashboards, handoffs,
Transient, CODE_REVIEW_STATUS.json) — left alone. Of the rest:

**(a) retarget outright** (tooling/docs, no live-world dependency):
`design/Jawa/fauna/biome_name_migration.py:23`, `design/Jawa/mods/biome_flora.py:162`,
`design/Jawa/worldbuilding/biome_flora_rosters.md:142`,
`design/Jawa/worldbuilding/biomes/_def_bindings_2026-09-09.md:40`,
`src/RimMandrake/Utils/build_landmark_density_sheet.py:65,80`,
`infrastructure/state/facts/biome_rosters.md:72`.

**(b) comment only — NOT owed** (same pattern Greentide's exemplar found):
`src/RimUtinni/UtinniPatches/Patches/BiomeDescriptions_Ashkarr.xml:174` — the
xpath targets donor `AB_FeraliskInfestedJungle`, not `RUT_Webwork`; `RUT_Webwork`
appears only in a trailing comment, and the def already carries its own native
`<label>`/`<description>`. `BiomeFlora_Ashkarr.xml:51` — inside that file's own
"biomes this file deliberately does NOT patch" comment block.
`src/RimMandrake/Utils/ashkarr_place_complex_structures.py:87` — comment on the
donor name, not `RUT_Webwork`.

**(c) leave until Phase B** (must keep working on the live world):
`world/biome_world_switch_apply.py:27` — the `MAP` donor→our tuple list; becomes
`RUT_Webwork`→`RM_Webwork` only at the terminal paint, per
`BIOME_PAINT_ONCE_AT_THE_END_1`.

**(d) flag, not owed by this item**:
`src/RimUtinni/ShokkweaveEconomy/Source/GenStep_ScatterWebworkSilk.cs` gates on
the literal string `map.Biome.defName == "RUT_Webwork"` in C#. This is correct
today and stays correct through Phase A (the painted def doesn't change until
Phase B) — flagging only so whoever executes Phase B knows this file also needs
a look, since it's C# not a patchable xpath.

`gen_cast_patch.py` (`design/Jawa/fauna/gen_cast_patch.py`): **0** occurrences of
"Webwork" — nothing owed there, unlike the item template's generic assumption.
No `validation.py` `QUALIFYING_BIOMES` reference to Webwork exists (the only
`QUALIFYING_BIOMES` hit repo-wide is `src/RimUtinni/LanternDeeps/validation.py`,
unrelated to this biome).

### 8. Mechanics/kit state

Per `webwork_kit_spec.md`'s own 7-mechanic summary + `WEBWORK_KIT_BUILD_1`
(closed, `rimflow show`: `done`) and `SHOKK_RSW_MOD_1` (closed, `done`):

| # | mechanic | state |
|---|---|---|
| 1 web-sense + convergence | ⚠️ PARTIAL — `RM_MapComponent_SenseWeb`+`RM_CompSenseWebNode` SHIPPED (`mandrake.rm.creaturebehaviors`); `RM_JobGiver_SenseWebConverge` (targeting) UNBUILT, needs the Wyyyschokk race's own ThinkTree |
| 2 concealed-burst ambush | ⛔ UNBUILT — no ambusher PawnKind dormancy XML yet |
| 3 Shokk-bound hediff | ✅ SHIPPED — `src/RimStarWars/Shokk/Defs/HediffDefs/RSW_Shokk_HediffDefs.xml` + spit DamageDef |
| 4 light-moat (sun-scald) | ✅ SHIPPED — in the Shokk RSW assembly per `WEBWORK_KIT_BUILD_1`'s own scope note |
| 5 beetle anchor-chewing | ✅ SHIPPED (`RM_JobGiver_ChewAnchors`+`RM_ChewableExtension`) but **unexercised** — no consumer race ThinkTree calls it |
| 6 margin creep | ✅ SHIPPED, LIVE-VERIFIED 2026-09-12 (`WEBWORK_KIT_BUILD_1`'s own closing note) |
| 7 droid-priority targeting | ⛔ UNBUILT — folds into #1's unbuilt JobGiver |

Economy (`SHOKKWEAVE_SOLE_SOURCE_1`, `rimflow show`: `ready`/`needs game-up`,
still open): rename+trader-strip+butchery live-verified; web-cutting/nest-raid
built and offline-validated; border creep-web yield-half committed,
emergent-Shokk-spawn half unbuilt (needs new C#, not a patch).

⇒ **None of this blocks steps 1–4 of THIS item.** Every shipped mechanic already
lives in an already-active sibling mod (`mandrake.rm.creaturebehaviors`,
the Shokk RSW mod, `mandrake.rut.shokkweaveeconomy`); `mandrake.rm.webwork` only
needs to `loadAfter` the first.

### 9. Dependencies & items building into this mod

| item | `rimflow show` state | blocks step 2? |
|---|---|---|
| `BIOME_MOD_SPLIT_EXECUTION_1` (parent) | `proposed`/`needs offline` — its own 10 owner questions are UNBLOCKED per its body, but the item's stored state line hasn't moved | no, it's the parent ticket |
| `WEBWORK_KIT_BUILD_1` | `done`/`needs deploy` | no — lands in `mandrake.rm.creaturebehaviors`, not here |
| `SHOKK_RSW_MOD_1` | `done`/`needs offline` | no — own RSW mod; `WildAnimals_Webwork.xml` will `MayRequire` it |
| `SHOKKWEAVE_SOLE_SOURCE_1` | `ready`/`needs game-up` | no — Utinni-tier economy |
| `SW_FAUNA_NEVER_IN_RM_TIER_1` | `proposed`/`needs offline` | **shapes** step 2 (wildAnimals ships empty) but doesn't block it |
| `DUPLICATE_CANON_DEFNAME_PAIRS_1` | `proposed`/`needs offline` | no — flags `Kreetle` vs `RSW_Kreetle` as a planet-wide naming problem across 5 biomes incl. this one; not this item's fix |
| `ECOSYSTEM_PYRAMID_LAW_1` | `proposed`/`needs deploy` | no — its Webwork fix (Kreetle 0.2→0.8) is **already applied** to the live def, nothing further owed here |

### 10. Blockers

**None for steps 1–4.** ⚠️ One open judgment call before step 2 finalizes
`wildPlants`: `Plant_TookeTrap_Wild`'s canon status (§4) — small, non-blocking for
scaffolding. Step 5 is Desktop-only (bridge/live-load proof).

### 11. Concrete step plan

1. **Scaffold** `src/RimMandrake/Webwork/About/About.xml`,
   packageId `mandrake.rm.webwork`, `loadAfter`: `mandrake.rm.creaturebehaviors`
   (owns the `RM_FrontCreepExtension`/`RM_ChewableExtension`/SenseWeb comps this
   def's `modExtensions` and structures reference). `RM_WebworkSettings :
   ModSettings` with a master toggle (§6a); no per-mechanic dial belongs here yet
   since the shipped kit mechanics' own toggles already live in
   `mandrake.rm.creaturebehaviors`'s settings screen.
2. **Copy**: `RM_Webwork` BiomeDef with its native label/description (copy
   verbatim — already franchise-free), new `workerClass`
   `RimMandrake.Webwork.RM_BiomeWorker_Webwork` (read the donor
   `AlphaBiomes.BiomeWorker_FeraliskInfestedJungle` via RimSage before
   reimplementing — Desktop-only), terrains/weather/diseases copied unchanged
   (⚠️ `AB_DenseMud`/`AB_DenseGrass` are Alpha Biomes TerrainDefs — flag Alpha
   Biomes as a soft dependency, same as the donor `workerClass` note already
   implies). `wildPlants` copied as-is pending the `Plant_TookeTrap_Wild` call.
   `wildAnimals` ships **empty**.
3. **Freeze** `RUT_Webwork.xml` with the standard header, unchanged otherwise.
4. **Retarget** the 6 tooling/doc hits in §7(a); leave §7(b)/(c)/(d) as reasoned
   above.
5. **New file** `src/RimUtinni/UtinniPatches/Patches/WildAnimals_Webwork.xml`
   (does not exist), shaped like `WildAnimals_Pyrelands.xml`: 4
   `PatchOperationAdd` rows onto `/Defs/BiomeDef[defName="RM_Webwork"]/wildAnimals`
   — `Wyyyschokk`/`Kreetle`/`Shyrack` each `MayRequire="mlie.starwarsanimalcollection"`,
   `RSW_JewelBeetle` `MayRequire="mandrake.rsw.swbestiary"`.
6. **Prove it loads** (Desktop, minimal list + this mod + `mandrake.rut.patches`
   + `mandrake.rm.creaturebehaviors` + all five expansions), then commit/push.
   Paint-list row already present — nothing to append.

## spec

🔑 **`biome_mod_architecture.md` §5 Phase A is the authority — read it, do not re-derive
it from here.** Steps 1–6, restated only far enough to start:

1. **Scaffold** `About/About.xml` with `mandrake.rm.webwork`, `loadAfter` on the §2d shared libraries,
   a `ModSettings` class with the master toggle (§6), an empty `Defs/BiomeDefs/`.
   `deploy_custom_mods.py --mod <name>` dry run, then `--apply`.
2. **Copy the content in** as `RM_Webwork` — the BiomeDef plus its terrain, plant, weather,
   condition and hediff defs, textures, and the kit C# under namespace
   `RimMandrake.<Mod>`. ⛔ Every `RSW_`/`SW_`/`RUT_` entry in `<wildAnimals>` stays OUT and
   goes to `src/RimUtinni/UtinniPatches/Patches/WildAnimals_<Biome>.xml` as a
   `PatchOperationAdd` onto `RM_Webwork`, with `MayRequire="mandrake.rsw.swbestiary"`.
   `WildAnimals_Pyrelands.xml` is the existing shape. Any donor `workerClass`
   (`AlphaBiomes.*`, `VanillaBiomes.*`, `BiomesPlus.*`, `ReGrowthCore.*`) becomes this
   mod's own `RM_BiomeWorker_<X>` — a donor type in `workerClass` is a hard dependency the
   RimMandrake tier may not assume.
3. **FREEZE the `RUT_` def, do not delete it.** It carries the player's world until the
   terminal paint. Byte-for-byte as it is, one header comment only: *"carrying the world
   until the terminal paint; content lives in `mandrake.rm.webwork`; do not edit here."* From that moment
   every content fix lands in `RM_Webwork` only.
4. **Retarget what does not need to be on the world** (kit specs, `_def_bindings_*.md`,
   queue items, `validation.py` `QUALIFYING_BIOMES`, kit C# string constants). Anything
   that must keep working on the live world (`BiomeNames_Ashkarr.xml`,
   `BiomeDescriptions_Ashkarr.xml`, doctrine patches, `race/wildBiomes`,
   `gen_cast_patch.py` output) gets a **second** op for `RM_Webwork` beside the `RUT_` one, so
   both behave identically until Phase B.
5. **Prove it loads and plays** — minimal list + this mod + `mandrake.rut.patches` +
   **all five expansions** (owner, 2026-09-19: every test list carries every expansion).

## verify

- Zero new Config errors in `Player.log` — and 🔴 grep the log, `validate_patch.py` cannot
  see config errors.
- `validate_patch.py <path> --live --defs` on the new Utinni fauna patch. An unmatched
  `PatchOperationAdd` is **silent**, so a clean run is not proof a row landed — confirm
  from a post-load def dump.
- A quicktest map on a **scratch** world whose landing tile is set to `RM_Webwork` through
  `jawa/world_*` at `Page_SelectStartingSite`. ⛔ Never the canonical save.
- `deploy_custom_mods.py` plan read before `--apply`; a `-` line is a deletion, look at it.

## criteria

`mandrake.rm.webwork` exists, deploys, and loads clean carrying `RM_Webwork` with its own content and its own
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
