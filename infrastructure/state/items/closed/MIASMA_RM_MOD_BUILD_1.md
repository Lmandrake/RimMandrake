# MIASMA_RM_MOD_BUILD_1 — build RM_Miasma as its own RimMandrake mod

**the Miasma**

Phase A row 19 of `design/RimMandrake/biome_mod_architecture.md`. Parent:
`BIOME_MOD_SPLIT_EXECUTION_1`. Governed by `BIOME_PAINT_ONCE_AT_THE_END_1`.

## 🔑 STATE — MEASURED 2026-09-23

### 1. Step table

| step | state |
|---|---|
| 1 scaffold | ⛔ OWED — `src/RimMandrake/Miasma/` does not exist (`ls` empty); no `mandrake.rm.miasma` in any `About.xml` (checked EnvironmentalHazards/Greentide as reference, absent everywhere) |
| 2 copy content | ⛔ OWED — the BiomeDef + 16 mechanic def files (§6) sit under `src/RimUtinni/UtinniPatches/Defs/**`; wildAnimals still carries 17 Star Wars rows inline (§3) |
| 3 freeze the RUT_ def | ⛔ OWED — `RUT_Miasma.xml` lines 4–56 are a build-provenance comment, not the Phase-A freeze header ("carrying the world until the terminal paint…") |
| 4 retarget | ⛔ OWED — narrow; see §7, most repo hits are prose/comments, genuine set is small |
| 5 prove it loads | ⛔ OWED, Desktop-only |
| 6 commit/push | ⛔ OWED, with step 5 |
| paint-list append | ✅ present, row `PAINT` — `infrastructure/state/facts/biome_paint_list.md:34` |

### 2. The def today

`src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Miasma.xml`, **260 lines** (`wc -l`).
`workerClass=AlphaBiomes.BiomeWorker_MiasmicMangrove` (donor) → owed `RM_BiomeWorker_Miasma`.
4 `modExtensions`, **all already RimMandrake-tier** (`mandrake.rm.environmentalhazards`, no move needed, just `loadAfter`): `BiomeGlowMultiplierExtension` (M4, glow 0.85), `RM_GradientAxisExtension` (M1, fresh→brine bands; brackish/brine terrain `MayRequire="mandrake.rm.flowworks"`), `RM_GradientSurgeExtension` (M2), `RM_StrandingPoolsExtension` (M3, placeholder-only spawn list). `biomeMapConditions`: `RUT_MiasmaWeatherLock`. Diseases: 9 (3 `sarg.alphabiomes`-gated, 6 vanilla). `terrainsByFertility`: `Mud` (vanilla) / `AB_FertileMud` (donor, **no `MayRequire` gate** — hard-dependency risk to fix at the copy). `baseWeatherCommonalities`: 8 entries, **INERT by the def's own header** (`ForcedWeather()` always wins), snow zeroed. `wildPlants`: 4 rows, `wildAnimals`: **31 rows** (MEASURED `len(list(wa))`, not `findall('li')` — addendum applied, all 31 are `<li>` form here, no shorthand `<DefName>` rows in `wildAnimals` for this def).

### 3. wildAnimals split (31 rows, parsed)

| verdict | count | rows |
|---|---:|---|
| stays inline (non-SW donor, Q9) | 9 | `VFEI2_Swarmling`, `VFEI2_BlackSwarmling`, `AA_Lockjaw`, `AA_Mantrap`, `AA_RaptorShrimp`, `AA_DecayDrake`, `AA_Helixien`, `AA_Slurrypede`, `AA_Thermadon` |
| → Utinni patch (Star Wars, Q11) | 17 | mlie: `Runyip`,`Shiro`,`Anooba`,`Grank`,`Whisperbird`,`Vornskyr`,`Zakkeg` (7); ours `RSW_`: `PodWorm`,`CrestedDragon`,`MeeJuv`,`AaroxisDendoria`,`FaaJuv`,`LaaJuv`,`YobshrimpJuv`,`RustNipperJuv`,`SiltLampreyJuv`,`OpeeSeaKillerJuv` (10) |
| ⚠️ stale — roster **evicted these**, still wired | 5 | `Kreetle`→AridShrubland, `Yobshrimp`→RUT_TwilightSea, `RSW_Gembug`→the_lantern_deeps, `AA_BloodShrimp`→AB_OcularForest, `AA_Plasmorph`→PoisonForest (all per `rosters/the_miasma.json` `evictions[]`) — these should be **deleted at step 2**, not patched anywhere |

`WildAnimals_Miasma.xml` does not exist yet (checked `UtinniPatches/Patches/`).

### 4. wildPlants split (4 rows, parsed) — clean, 0 diff vs roster

| verdict | rows |
|---|---|
| stays inline (non-SW donor, Q9) | `AB_MangroveTree` 25, `AB_ParasiticMangrove` 8, `AB_MangrovePalm` 6 — ⚠️ **none carries `MayRequire`**, add `sarg.alphabiomes` at the copy (96.5% of flora weight is this donor family — a real, not soft, dependency) |
| cross-mod, needs a live retarget later | `RUT_Nogtyl` 0.4, `MayRequire="mandrake.rut.rotsporekit"` — owned by row 3 (`RUT_TheRot`/`THEROT_RM_MOD_BUILD_1`), which absorbs `rotsporekit` into `RM_TheRot`. When that lands, this row's `MayRequire` must follow to whatever Nogtyl is renamed under `mandrake.rm.therot` |

No owner rejection found to cite (nothing here is vanilla temperate filler).

### 5. Roster vs def diff

Roster `fauna`: **32 rows** (MEASURED `json.load`, brief's 33 is close but not exact). Roster `flora`: 4 (matches def exactly, §4).
**6 roster fauna rows NOT wired**: `RSW_SandoAquaMonster` (def+art **both exist** — `src/RimStarWars/SWBestiary/Defs/SeaBeasts/ThingDefs_Races/SeaBeasts_Sando.xml`, `Textures/.../SandoAquaMonster_south.png` confirmed real file — cheap wire-in, Star Wars → Utinni patch); `Blarth`, `Blixus`, `Bogwing`, `JRWBeelzebufo`, `MarshHaunt` — **no def anywhere in `src/`** (searched whole tree by defName), not in the roster's own `new_defs` list either — these are unauthored content, distinct from the 5 `new_defs` the roster does name (warden mother, the stranded, fever-swarm, delta-loam composter, rainbow flora).
**5 def wildAnimals rows NOT in roster fauna** = exactly the 5 stale-eviction rows in §3. No other orphans.

### 6. Content to move into the mod

All franchise-free, all pass §3a: `RUT_Miasma.xml` (biome) plus 16 mechanic def files under `UtinniPatches/`: `GameConditionDefs/{RUT_GradientSurge,RUT_MiasmaWeatherLock}.xml`, `HediffDefs/{RUT_MiasmaExposure,RUT_Miasma_FeverForgedMinor,RUT_Miasma_HardenedImmunity,RUT_Miasma_StrangeTier}.xml`, `IncidentDefs/RUT_Surge.xml`, `MapGeneration/{RUT_Miasma_CrecheScatterer,RUT_Miasma_GradientAxisGenStep}.xml`, `ThingDefs_Buildings/RUT_CrecheMarker.xml`, `WeatherDefs/{RUT_MiasmaWeather,RUT_SurgeWeather}.xml`, `Languages/English/Keyed/RUT_Miasma_Mechanics.xml`, `Patches/{RUT_Miasma_CrecheScatterer_Register,RUT_Miasma_ForgeOnSurvival,RUT_Miasma_GradientAxis_Register}.xml`.
**No C# to move** — every mechanic class (`RM_MapComponent_GradientAxis`, `RM_GameCondition_GradientSurge`, `RM_StrandingPoolsExtension`+comps, `RM_CompTerritorialAnchor`, `RM_HediffComp_ForgeOnSurvival`, etc.) already lives in the shared `mandrake.rm.environmentalhazards` assembly (§2d) — `RM_Miasma` only needs `loadAfter` on it. ⚠️ Its per-mechanic settings toggles (`strandingPoolsEnabled`, `wardenCrecheScattererEnabled`, `crecheDespoilMemoryEnabled`, `biomeGlowMultiplierEnabled`, …) currently live in the **shared** `RM_EnvironmentalHazardsSettings` class (`RM_EnvironmentalHazardsMod.cs`), not a per-biome screen — §6a wants a master toggle on `RM_Miasma`'s own screen; step 1 needs to decide whether `RM_MiasmaMod.cs` is a thin wrapper over those shared statics or ships its own.

### 7. References to `RUT_Miasma` across the repo

~90 files grep-hit; sampled by category, same shape Greentide found ("most are comments"):
- **Comment/prose only, leave**: `RSW_ScrapNestBird.xml:25` (wildBiomes donor-metadata comment, same cleared pattern as Greentide); `BiomeFlora_Ashkarr.xml:40` (inside its own "deliberately does NOT patch" comment block); `RUT_Greentide.xml`/`RUT_Scarlands.xml`/`RotSporeKit` hits (cross-biome comparison prose).
- **Targets the donor, not `RUT_Miasma`** (comment only names it): `BiomeDescriptions_Ashkarr.xml:184-190` — `PatchOperationConditional` xpath is `BiomeDef[defName="AB_MiasmicMangrove"]`; `RUT_Miasma.xml` already carries the identical description natively (line 61). Nothing to retarget.
- **Retarget-outright at step 4** (target need not be live): `rosters/the_miasma.json`'s `"defNames": ["RUT_Miasma"]`, `design/Jawa/worldbuilding/biomes/kits/miasma_kit_spec.md`'s defName mentions, `_def_bindings_2026-09-09.md`, `biome_flora_rosters.md`.
- **Fact files, regenerate rather than hand-edit**: `infrastructure/state/facts/{biome_rosters,biome_paint_list}.md`.
- Everything else (item files, `Transient/*`, handoffs) is historical prose — leave.

### 8. Mechanics/kit state — MIASMA_MECHANICS_1

🔴 **All six mechanics have landed a build pass** (`MIASMA_MECHANICS_1.md`'s own line, its "M3 build pass" section, 2026-09-14: *"All six of MIASMA_MECHANICS_1's mechanics have now landed a build pass."*). rimflow still shows `doing` — correctly, by the item's own explicit words, because none has a live/quicktest pass.

| mechanic | code state | content owed |
|---|---|---|
| M1 gradient axis | ✅ SHIPPED — `RM_MapComponent_GradientAxis.cs`, `RM_GenStep_GradientAxis.cs`, `RM_GradientAxisExtension.cs` | none blocking |
| M2 surge | ✅ SHIPPED — `RM_GradientSurgeExtension.cs`, `RM_GameCondition_GradientSurge.cs`, `RUT_Surge.xml`, `RUT_GradientSurge.xml` | none blocking |
| M3 stranding pools | ✅ SHIPPED (mechanism) — `RM_MapComponent_StrandingPools.cs`, `RM_JobGiver_ReturnToWater.cs` | ⚠️ real roster `RUT_StrandedSpawnList` **not authored** — only a placeholder `Yobshrimp` (SW, itself an evicted row per §3) wired so the spawner compiles |
| M4 weather/exposure | ✅ SHIPPED — `RUT_MiasmaWeather.xml`, `RUT_MiasmaWeatherLock.xml`, `RM_HediffComp_EnvironmentalExposure.cs` | ⚠️ the carrier hediff isn't yet granted to every pawn on the map (needs a per-pawn scan comp, non-blocking) |
| M5 fever-forged boons | ✅ SHIPPED — `RM_HediffComp_ForgeOnSurvival.cs`, `RUT_Miasma_StrangeTier.xml` (5 hediffs), `RUT_Miasma_FeverForgedMinor.xml` | letter-text keys missing (falls back to key, non-blocking) |
| M6 warden mothers | ✅ SHIPPED (mechanism) — `RM_CompTerritorialAnchor.cs`, `RM_SetPieceElement_AnchoredPawn.cs`, `RUT_CrecheMarker.xml`, `RUT_Miasma_CrecheScatterer.xml` | 🔴 **`RUT_WardenMother` PawnKindDef does not exist anywhere** (grepped whole repo) — the roster's own `new_defs` "warden mother" row is unauthored content, not a code gap |

None of this blocks Phase A steps 1–4 — it is content to carry across at step 2 as-is.

### 9. Dependencies & items building INTO this mod

| item | rimflow state | relation |
|---|---|---|
| `MIASMA_MECHANICS_1` | `doing` | IS most of step-2 content (§8); not a blocker, lands with the copy |
| `MIASMA_FEVERWOOD_GREENTIDE_BMT_1` | `proposed` (body says the Miasma half is DONE — 2026-09-21, `RSW_CrestedDragon`/`RSW_PodWorm`/`RSW_AaroxisDendoria` renames already live in the def, confirmed §2/§3) | lands later; item's own `proposed` state field is stale vs. its body |
| `SW_FAUNA_NEVER_IN_RM_TIER_1` | `proposed` | Miasma is one of its 12 named `RUT_` defs; this item and step 2's "17 rows → Utinni patch" (§3) are the same work |
| `ECOSYSTEM_PYRAMID_LAW_1` | `proposed` | already checked against Miasma once (RSW_PodWorm bodySize-4 tuning); informational, not blocking |
| `DUPLICATE_CANON_DEFNAME_PAIRS_1` | `proposed` | names Kreetle as a dual-defName case; moot here since Kreetle is a stale eviction (§3), not a wire |

### 10. Blockers

**None for steps 1–4.** Step 5 (prove it loads) is Desktop-only, not a blocker of starting.

### 11. Concrete step plan

1. **Scaffold** `src/RimMandrake/Miasma/About/About.xml`, `packageId mandrake.rm.miasma`, `loadAfter`: `mandrake.rm.environmentalhazards` (all 4 modExtension classes + M2/M3/M6 comps), `mandrake.rm.flowworks` (brackish/brine terrain), `modDependencies` incl. `sarg.alphabiomes` (hard — 96.5% of flora weight, §4). `RM_MiasmaMod : Mod` + `RM_MiasmaSettings : ModSettings` (master toggle; decide whether it wraps the shared `RM_EnvironmentalHazardsSettings` statics, §6). Empty `Defs/BiomeDefs/`. `deploy_custom_mods.py --mod Miasma` dry run, then `--apply`.
2. **Copy in**: `RUT_Miasma.xml` → `Defs/BiomeDefs/RM_Miasma.xml` (defName `RM_Miasma`, `workerClass` → new `RM_BiomeWorker_Miasma` replacing `AlphaBiomes.BiomeWorker_MiasmicMangrove`); the 16 files of §6 into matching `Defs/` subfolders under the new mod, defName-retargeted to `RM_Miasma`; drop the 5 stale rows (§3); write `WildAnimals_Miasma.xml` (17 SW rows, §3) as a new `UtinniPatches/Patches/PatchOperationAdd` onto `RM_Miasma`, `MayRequire="mandrake.rsw.swbestiary"`/`"mlie.starwarsanimalcollection"` per row, shape from `WildAnimals_Pyrelands.xml`; add `MayRequire="sarg.alphabiomes"` to the 3 `AB_` flora rows and to `AB_FertileMud` in `terrainsByFertility` (§2/§4).
3. **Freeze** `RUT_Miasma.xml` — replace its provenance header with the standard freeze comment; leave body byte-for-byte otherwise.
4. **Retarget**: `rosters/the_miasma.json` `defNames`, `miasma_kit_spec.md`, `_def_bindings_2026-09-09.md`, `biome_flora_rosters.md` (§7). No "second op" needed — `BiomeDescriptions_Ashkarr.xml` already targets the donor, not `RUT_Miasma` (§7).
5. **Prove it loads** — minimal list + `mandrake.rm.miasma` + `mandrake.rm.environmentalhazards` + `mandrake.rm.flowworks` + `mandrake.rut.patches` + all five expansions; scratch-world quicktest at `RM_Miasma`.
6. **Commit/push**, one commit, message naming that `RUT_Miasma` carried an inert weather table and 5 stale-evicted wildAnimals rows the split does not carry forward. Append to `WORLD_REMAKE_FINAL_STEP_1` paint list (row already present, §1).

### False statements found elsewhere

- `infrastructure/state/items/MIASMA_MECHANICS_1.md:44-46` (the top `## verify` checklist) still reads *"Steps 4-7 (M2 surge, M3 stranding pools, M6 warden placement, M5 fever-forged) remain undone"* — contradicted by the same file's own later line (line ~1207, "M3 build pass" section): *"All six of MIASMA_MECHANICS_1's mechanics have now landed a build pass."* The top checklist was never updated after the M2/M3/M5/M6 build-pass sections were appended 2026-09-13/14.
- `design/Jawa/worldbuilding/biomes/the_miasma.md:224` ("## Owed") says *"`MIASMA_MECHANICS_1` (to file)"* — it has been filed since 2026-09-07 and carries six build passes; the sheet's Owed line predates the item's own history.

## spec

🔑 **`biome_mod_architecture.md` §5 Phase A is the authority — read it, do not re-derive
it from here.** Steps 1–6, restated only far enough to start:

1. **Scaffold** `About/About.xml` with `mandrake.rm.miasma`, `loadAfter` on the §2d shared libraries,
   a `ModSettings` class with the master toggle (§6), an empty `Defs/BiomeDefs/`.
   `deploy_custom_mods.py --mod <name>` dry run, then `--apply`.
2. **Copy the content in** as `RM_Miasma` — the BiomeDef plus its terrain, plant, weather,
   condition and hediff defs, textures, and the kit C# under namespace
   `RimMandrake.<Mod>`. ⛔ Every `RSW_`/`SW_`/`RUT_` entry in `<wildAnimals>` stays OUT and
   goes to `src/RimUtinni/UtinniPatches/Patches/WildAnimals_<Biome>.xml` as a
   `PatchOperationAdd` onto `RM_Miasma`, with `MayRequire="mandrake.rsw.swbestiary"`.
   `WildAnimals_Pyrelands.xml` is the existing shape. Any donor `workerClass`
   (`AlphaBiomes.*`, `VanillaBiomes.*`, `BiomesPlus.*`, `ReGrowthCore.*`) becomes this
   mod's own `RM_BiomeWorker_<X>` — a donor type in `workerClass` is a hard dependency the
   RimMandrake tier may not assume.
3. **FREEZE the `RUT_` def, do not delete it.** It carries the player's world until the
   terminal paint. Byte-for-byte as it is, one header comment only: *"carrying the world
   until the terminal paint; content lives in `mandrake.rm.miasma`; do not edit here."* From that moment
   every content fix lands in `RM_Miasma` only.
4. **Retarget what does not need to be on the world** (kit specs, `_def_bindings_*.md`,
   queue items, `validation.py` `QUALIFYING_BIOMES`, kit C# string constants). Anything
   that must keep working on the live world (`BiomeNames_Ashkarr.xml`,
   `BiomeDescriptions_Ashkarr.xml`, doctrine patches, `race/wildBiomes`,
   `gen_cast_patch.py` output) gets a **second** op for `RM_Miasma` beside the `RUT_` one, so
   both behave identically until Phase B.
5. **Prove it loads and plays** — minimal list + this mod + `mandrake.rut.patches` +
   **all five expansions** (owner, 2026-09-19: every test list carries every expansion).

## verify

- Zero new Config errors in `Player.log` — and 🔴 grep the log, `validate_patch.py` cannot
  see config errors.
- `validate_patch.py <path> --live --defs` on the new Utinni fauna patch. An unmatched
  `PatchOperationAdd` is **silent**, so a clean run is not proof a row landed — confirm
  from a post-load def dump.
- A quicktest map on a **scratch** world whose landing tile is set to `RM_Miasma` through
  `jawa/world_*` at `Page_SelectStartingSite`. ⛔ Never the canonical save.
- `deploy_custom_mods.py` plan read before `--apply`; a `-` line is a deletion, look at it.

## criteria

`mandrake.rm.miasma` exists, deploys, and loads clean carrying `RM_Miasma` with its own content and its own
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
