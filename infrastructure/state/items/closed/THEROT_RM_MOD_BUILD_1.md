# THEROT_RM_MOD_BUILD_1 — build RM_TheRot as its own RimMandrake mod

**the Rot - absorbs mandrake.rut.rotsporekit (151 files)**

Phase A row 3 of `design/RimMandrake/biome_mod_architecture.md`. Parent:
`BIOME_MOD_SPLIT_EXECUTION_1`. Governed by `BIOME_PAINT_ONCE_AT_THE_END_1`.


## 🔑 STATE — MEASURED 2026-09-23

Forensics done on the Mac, offline. Every count below was produced by `xml.etree`/`json` parsing or
`git grep`, never `grep -c` on XML. ⛔ No tile count is cited as evidence of anything.

🔑 **The design side is FINISHED and both owner decision files are fully applied.** All nine kit
mechanics are `done`. What is owed is the *mod*, not the content — plus ONE tier question (below)
that BENCH/the owner must answer before step 2's fauna split can be written.

### 1. Step table

| step | state |
|---|---|
| 1 scaffold | ⛔ OWED — `src/RimMandrake/TheRot` does not exist (`test -e`, ABSENT); not in `/mnt/c/.../Mods/TheRot` either (`test -e`, ABSENT) |
| 2 copy content | ⛔ OWED — nothing of the Rot lives in `src/RimMandrake/` yet. Source material measured and listed in §6 |
| 3 freeze the twin | ⛔ OWED — `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_TheRot.xml` is 242 lines, unfrozen, no freeze header (its header comment block, lines 4–52, is authorship provenance, not the Phase A freeze notice) |
| 4 retarget | ⛔ OWED — 2 live XML ops + 1 live data list need a second `RM_TheRot` form; ~10 docs/generators retarget outright. §7 splits them |
| 5 prove it loads | ⛔ Windows Desktop only — not a blocker of 1–4 |
| 6 commit/push | owed with 5 |
| paint-list append | ⛔ OWED — `infrastructure/state/facts/biome_paint_list.md` has the `RUT_TheRot` row (line 43) but **no `RM_TheRot` row** in the `RM_` block that starts at line 53 (parsed the table; `RM_Greentide` at line 53 is the shape to copy) |

### 2. The def today

`src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_TheRot.xml` — **242 lines**, one `BiomeDef`.

- `workerClass` = `AlphaBiomes.BiomeWorker_MycoticJungle` (line 58) → **donor type. Owed: this mod's own `RM_BiomeWorker_TheRot`.**
- `texture` = `Biomes/AB_MycoticJungle` (line 67) → donor texture path, owed its own.
- **terrainsByFertility** (lines 111–122): `AB_MycoticGrass` (≤0.87), `AB_MycoticSoilRich` (>0.87) — **both donor (Alpha Biomes). Owed: two own TerrainDefs.** The kit already ships six of its own (`RUT_MushroomFloor`, `RUT_MushroomBridge`, `RUT_HeavyMushroomBridge`, `RUT_MoonlessCarpet`, `RUT_MycelialSoil`, `RUT_MycelialMatting`) but they are *built* floors, not the natural ground.
- **baseWeatherCommonalities** (123–129): `Clear` 8, `DryThunderstorm` 1 (vanilla) + `RUT_SheenFall` 10, `RUT_SheenStorm` 10, `RUT_SheenMist` 10 — all three ours, in the kit (`RotSporeKit/Defs/WeatherDefs/RUT_RotSporeKit_SheenWeathers.xml`), `MayRequire="mandrake.rut.rotsporekit"` → rename `RM_Sheen*`, drop the MayRequire once same-mod.
- **biomeMapConditions** (130–132): `RUT_SheenExposureLock`, gated on `mandrake.rm.environmentalhazards,mandrake.rut.rotsporekit`. Def lives in **UtinniPatches** (`Defs/GameConditionDefs/RUT_SheenExposureLock.xml`) — a kit mechanic filed at the wrong tier; moves.
- **diseases** (69–110): 10 rows — 8 vanilla (`Disease_Flu`, `_Plague`, `_GutWorms`, `_MuscleParasites`, `_FibrousMechanites`, `_SensoryMechanites`, `_AnimalFlu`, `_AnimalPlague`) + **2 donor** `AB_Disease_SporesAllergy`, `AB_Disease_AnimalSporesAllergy` (`MayRequire="sarg.alphabiomes"`). Donor diseases are content, not a `workerClass`; leaving them MayRequire'd is the Q9 shape, but the Rot's signature allergy then vanishes without Alpha Biomes — UNCERTAIN, flag for BENCH.
- **modExtensions** (229–239): `RimMandrake.EnvironmentalHazards.RM_AcceleratedRotExtension` and `RimMandrake.EnvironmentalHazards.RM_WarmGroundExtension` (with 4 `warmTerrains`) — **both shipped by `mandrake.rm.environmentalhazards`**, already RimMandrake-tier per §2d, no move, no rename.
- other fields: `foragedFood RawFungus` · `allowRoads`/`allowRivers`/`allowFarmingCamps` true · `animalDensity 1.9` · `plantDensity 0.6` (flagged interim in the def's own header line 26 — a quicktest tune is owed, **not** by this ticket) · `forageability 0.5` · `movementDifficulty 1` · `diseaseMtbDays 35` · `wildPlantRegrowDays 25` · `coastalWildAnimals` empty. Native `<label>`+`<description>` present ⇒ no description patch owed (§7).

### 3. wildAnimals split — 20 rows, 12 route out on a literal prefix read

`src/RimUtinni/UtinniPatches/Patches/WildAnimals_TheRot.xml` **does not exist** (`ls`, ENOENT) — owed. Existing shapes: `WildAnimals_Pyrelands.xml`, `_Greentide.xml`, `_CrackedLands.xml`.

| defName | commonality | class | verdict |
|---|---:|---|---|
| `AA_AngelMoth` | 0.5 | AA donor | stays in `RM_` def (Q9) |
| `AA_AnimaColossus` | 0.5 | AA donor | stays (Q9) |
| `AA_Swarmling` | 0.3 | AA donor | stays (Q9) |
| `AA_Agaripod` | 0.25 | AA donor | stays (Q9) |
| `AA_MycoidColossus` | 0.25 | AA donor | stays (Q9) |
| `AA_Agaripawn` | 0.2 | AA donor | stays (Q9) |
| `AA_Wildpawn` | 0.2 | AA donor | stays (Q9) |
| `AA_Wildpod` | 0.2 | AA donor | stays (Q9) |
| `Snoruuk` | 0.5 | `mlie.starwarsanimalcollection` | → Utinni patch. **Unambiguous: genuine Star Wars donor (Q11)** |
| `RSW_ShiroTrap` | 0.5 | `RSW_` (ours) | → Utinni patch. **Canon: `design/RimStarWars/canon_references/shiro` exists** |
| `RSW_ColonyPustuleHornet` 0.5 · `RSW_PustuleHornet` 0.5 · `RSW_SmogMoth` 0.5 · `RSW_Thrumbungus` 0.5 · `RSW_Yooka` 0.5 · `RSW_FungalWeevil` 0.4 · `RSW_PustuleHornetQueen` 0.3 · `RSW_ColonyPustuleHornetQueen` 0.2 · `RSW_PustuleHornetSpawned` 0.2 · `RSW_FungalMantis` 0.15 | (10 rows) | `RSW_` (ours) | ⚠️ **UNDECIDED — the tier question below** |

🔴 **The one tier question this ticket cannot answer itself — escalate, do not decide.** All 11 `RSW_`
rows are ours (MEASURED: 10 in `src/RimStarWars/SWBestiary/Defs/BiomesTeamPort/ThingDefs_Races/RSW_BiomesTeamPort_Races.xml`,
`RSW_ShiroTrap` in `Defs/Bodies/RSW_MlieWaveC_Bodies.xml` + its races file). That port file's own header
states the 10 are `biomesteam.biomescaverns`/`biomescore`/`biomespollutedlands` creatures **renamed
`BMT_` → `RSW_` throughout** — i.e. Biomes! Team inventions, **not Star Wars IP**. Under **§7 Q11a**
("the tier line is IP, not flavour"), 10 of the 12 are *not* IP and should not be exiled; under the
literal Q11 prefix/packageId reading, all 12 must go, leaving `RM_TheRot` with **8 Alpha Animals
rows** — which collides head-on with Q11a's *"rich enough to stand alone"* requirement.
⇒ **FOUNDRY starts steps 1 and 3 regardless; step 2's fauna split needs this answered.** Related open
item: `SW_FAUNA_NEVER_IN_RM_TIER_1` (proposed). ⛔ Do not derive a rule here — per
`BIOME_SPECIFIC_FAUNA_LAW_1` this is review work, one biome at a time.

### 4. wildPlants split — 30 rows, ALL 30 stay in the `RM_` def

Zero Star Wars names. Nothing routes to a Utinni patch.

- **17 `RUT_` rows, ours, in `mandrake.rut.rotsporekit`** → move into the mod, rename `RM_`:
  `RUT_Dewshrooms` 0.5, `RUT_FruitingBodies` 0.5, `RUT_Nuitae` 0.5, `RUT_Wrinklecap` 0.5, `RUT_Arpeau` 0.4,
  `RUT_FlakespireFungus` 0.3, `RUT_Pusmelon` 0.3, `RUT_Sagecrust` 0.3, `RUT_BleedingTooth` 0.2,
  `RUT_Brightbell` 0.2, `RUT_CrimsonCap` 0.2, `RUT_GreyLady` 0.2, `RUT_Shinecap` 0.2, `RUT_VioletWimple` 0.2,
  `RUT_MortalMorelPlant` 0.15, `RUT_Skulltop` 0.1, `RUT_BlastpodShroom` 0.05.
  **Art: 17 of 17 present** (MEASURED — parsed each def's `graphicData/texPath`, then globbed both
  `<texPath>.png` and `<texPath>/*.png` under `RotSporeKit/Textures/`; several are `Graphic_Random`
  directories, so a `<texPath>*.png` glob alone reports a false 0).
- **13 `AB_` rows, Alpha Biomes donors, no `MayRequire`** → stay inline per Q9:
  `AB_Bryolux` 10, `AB_Glowstool` 3, `AB_Agarilux` 2, `AB_GiantAgarilux` 2, `AB_GlowingAgarilux` 1,
  `AB_LilacBeacon` 0.5, `AB_WitchesOyster` 0.5, `AB_RecurvedStropharia` 0.3, `AB_ArbuscularMycorrhiza` 0.2,
  `AB_SlimyPholiota` 0.2, `AB_AgaricusDomeCap` 0.1, `AB_DribblingCap` 0.1, `AB_AgariluxPrime` 0.01.
  All 13 carry **our own** label/description/size/art via `RotSpecies_NamesAndSizes.xml` (§6); art
  under `src/RimUtinni/UtinniPatches/Textures/RotSpecies/` (13 flora + 5 fauna entries, MEASURED).
  ⚠️ These 13 rows are an **unconditional** hard dependency on `sarg.alphabiomes` — no `MayRequire` on
  any of them. Not a Q11 problem; note it against §6c ("all-off degrades gracefully").
- **Owner rejections I can cite** (roster `flora_purged`, 2 rows — already absent from the def, nothing owed):
  `BMT_Blastpod` (donor band 50–352 °C cannot reach the Rot's median; role passed to Boomshroom) and
  `Boomshroom` (`SHEET_ORPHAN_CONSUMPTION_1`, owner 2026-09-20 — *"I don't want new versions of these silly plants."*).
  ⛔ **No vanilla temperate filler exists here to reject** — unlike the Greentide, this def carries zero
  `Plant_Tree*`/`Plant_Grass`/`Plant_Bush` rows. Do not go looking for the Greentide's defect.

### 5. Roster vs def diff — ZERO drift

`design/Jawa/worldbuilding/biomes/rosters/the_rot.json` (712 lines, `sheet: the_rot`, `defNames: ["RUT_TheRot"]`,
authored 2026-09-09). Parsed both sides and set-diffed:

- roster `fauna` 20 rows vs def `wildAnimals` 20 rows — **0 unwired, 0 extra, 0 commonality mismatches**.
- roster `flora` 30 rows vs def `wildPlants` 30 rows — **0 unwired, 0 extra, 0 commonality mismatches**.
- **Defs of ours / donor split** (MEASURED by parsing every `.xml` under `src/RimStarWars`, `src/RimUtinni`,
  `src/RimMandrake` for each roster defName): 11 fauna are ours (§3), 9 are donor-owned
  (8 `AA_` Alpha Animals + `Snoruuk`); 17 flora are ours (RotSporeKit), 13 are `AB_` donors.
- Fauna art: 5 `AA_` patched to our own (`RotSpecies/Agaripawn|MycoidColossus|Swarmling|Wildpawn|Wildpod`),
  `RSW_FungalWeevil` at `SWBestiary/Textures/RotSpecies/FungalWeevil`, `AA_Agaripod` owner-ruled keep-with-rename
  (no art job). `AA_AngelMoth`, `AA_AnimaColossus`, `Snoruuk` and the 11 `RSW_` rows: **UNMEASURED**.
- `new_defs` (5: heat gene, guardian mushrooms, symbiont pairs, pale tree, health-share tagging) are the kit
  mechanics — **all nine tickets `done` (§8)**, so built, not owed. `fish`: roster rules **no fish** ("the milk
  ponds are not-water") ⇒ no `fishTypes` owed. `evictions`: 64 historical rows, not owed work.

### 6. Content to move into the mod

**Moves (RimMandrake by §3a — none of it would make a reviewer ask "what is a Kreetle?"):**

| path | reason |
|---|---|
| `src/RimUtinni/RotSporeKit/` — **151 files** (MEASURED by `os.walk`, excluding `__pycache__`: **116 `.png`, 33 `.xml`, 2 `.py`**) | §3c: a biome mechanics kit filed at the wrong tier. **No C#, no `Assemblies/`, no `.csproj` — MEASURED absent**; the kit is pure XML + art and its C# lives in `mandrake.rm.environmentalhazards` already |
| `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_TheRot.xml` → `RM_TheRot` **copy** | step 2; the original is frozen in place, never moved |
| `src/RimUtinni/UtinniPatches/Defs/GameConditionDefs/RUT_SheenExposureLock.xml` | the Sheen exposure ladder — a kit mechanic, no campaign content |
| `src/RimUtinni/UtinniPatches/Patches/RotSpecies_NamesAndSizes.xml` (668 lines, **43 top-level ops over 19 distinct donor defNames** — 13 `AB_` + 6 `AA_`, MEASURED by parsing every `xpath`) | renames/resizes/re-arts Alpha Biomes + Alpha Animals defs. **Zero Star Wars names.** Q11a: invented exotic names are free in the `RM_` tier |
| `src/RimUtinni/UtinniPatches/Textures/RotSpecies/` (18 entries) | the art those ops point at; must travel with them |
| `src/RimUtinni/UtinniPatches/Patches/RotPaleTree_WildSpawn.xml`, `RotGuardianGroves_WildSpawn.xml` | each adds kit plants to `wildPlants`. In `RM_TheRot` these become **native `<wildPlants>` rows**, not patches — the patch shape existed only to avoid editing a def another agent held |

**Stays in Utinni:**

| path | reason |
|---|---|
| `src/RimUtinni/RotSporeKit/Defs/ThingDefs_Weapons/RUT_RotSporeKit_MantisScythe.xml:37` | 🔴 **the only genuine IP line in all 151 kit files** (MEASURED: grepped `RSW_`/`SW_`/star.wars/jawa/utinni/ashkarr/tatooine/wookie/kotor/mlie across every `.xml`+`.py`; 6 other files matched and **every one of those was a path or prose comment**). Its recipe ingredient is `<RSW_FungalMantisClaw MayRequire="mandrake.rsw.swbestiary">`. Same ⚠️ as §3 — the mantis is a BMT port, not canon, so this may be a misfile rather than IP. **Decide at the move, per creature, never in bulk (§3b).** Cheapest clean answer: leave the scythe def in Utinni |
| `src/RimUtinni/UtinniPatches/Patches/BiomeNames_Ashkarr.xml:46-51`, `BiomeDescriptions_Ashkarr.xml:88-94` | campaign label + description. ⚠️ **Both target the DONOR `AB_MycoticJungle`, not `RUT_TheRot`** — the `RUT_TheRot` mention on `BiomeDescriptions_Ashkarr.xml:94` is a trailing comment. `RM_TheRot` will carry its own native label/description as `RUT_TheRot` already does, so **neither file needs a second op** |
| new `src/RimUtinni/UtinniPatches/Patches/WildAnimals_TheRot.xml` | the Star Wars fauna rows §3 rules out (2 certain, up to 12 on the literal reading) |

**C#:** the Rot ships none of its own — no `Source/`, no `Assemblies/`, no `.csproj` in RotSporeKit (MEASURED
absent). Its mechanics live in `src/RimMandrake/EnvironmentalHazards/Source/` (`RM_AcceleratedRotExtension.cs`,
`RM_WarmGroundExtension.cs`, `RM_LivingProduceExtension.cs`, `GameCondition_EnvironmentalWeather.cs`,
`RUT_IncidentWorker_SporeCloud.cs`) and `src/RimMandrake/CreatureBehaviors/Source/` — both already
`mandrake.rm.*`, so **nothing moves and no `<Compile Include>` line is owed.** ⚠️ `RUT_IncidentWorker_SporeCloud.cs`
is a `RUT_`-prefixed class in the RM-tier `RimMandrake.EnvironmentalHazards` namespace — a naming-scheme
violation whose fix would break a shipped def's `workerClass` string. **Not this ticket.**

### 7. References to `RUT_TheRot` across the repo

`git grep -c "RUT_TheRot"` over the whole tree, then every live hit READ. Excluded as records, never
retargeted: `world/ASHKARR_WORLDMAP_tiles.csv`, the ledger, `Transient/**`, `Player.log*`,
`CODE_REVIEW_STATUS.json`, generated dashboards.

**(a) retarget outright** — target need not be on the world:
`design/Jawa/worldbuilding/biomes/rosters/the_rot.json` (`defNames`) · `biomes/_def_bindings_2026-09-09.md` ·
`biomes/kits/rot_kit_spec.md` (7) · `biomes/caverns_replacement_scoping.md` · `biome_flora_rosters.md` ·
`design/Jawa/mods/biome_flora.py:198` · `design/Jawa/fauna/biome_name_migration.py:27` ·
`design/Jawa/fauna/cast_assignment.csv` (28, generated — regenerate, don't hand-edit) ·
`infrastructure/state/facts/biome_rosters.md` · `infrastructure/state/canon.yml` · the live items that
name only the twin (`ECOSYSTEM_PYRAMID_LAW_1`, `BIOME_WORLD_SWITCH_WAVE_1`, `DONOR_DEFS_PORT_TO_OURS_1`,
`SW_FAUNA_NEVER_IN_RM_TIER_1`, `QUICKTEST_RIVER_WATER_MISSING_1`, `CUT_FALLOUT_GENERATED_DATA_1`,
`BMT_FAUNA_ABSORPTION_1`).
⛔ `world/biome_world_switch_apply.py:37` (`("AB_MycoticJungle", "RUT_TheRot")`) is **Phase B's** `MAP`
per §3b — leave it alone.

**(b) needs a SECOND op / row for `RM_TheRot`** — only three, all read and confirmed live:
1. `src/RimUtinni/UtinniPatches/Patches/RotPaleTree_WildSpawn.xml:34` — real `xpath` onto `RUT_TheRot/wildPlants`. Satisfied by a **native row** in `RM_TheRot`, not a second op.
2. `src/RimUtinni/UtinniPatches/Patches/RotGuardianGroves_WildSpawn.xml:34` — same shape, same fix.
3. `src/RimUtinni/RotSporeKit/Defs/GameConditionDefs/RUT_RotSporeKit_SporeCloud.xml:81` — `<li>RUT_TheRot</li>` inside the `RUT_SporeCloud` IncidentDef's `<disallowedBiomes>`. **This is live DATA, not a comment** — add an `RM_TheRot` `<li>` beside it, or the spore-cloud incident starts firing on its own home biome.

**(c) comment / prose — ⛔ leave, these are not owed work** (12 of the 18 live hits):
`RotPaleTree_WildSpawn.xml:7,8` · `RotGuardianGroves_WildSpawn.xml:5,10` · `SporeCloud.xml:36` ·
`BiomeFlora_Ashkarr.xml:47` (inside that file's own *"biomes this file deliberately does NOT patch"*
block — identical to the Greentide's cleared case; ⛔ do not add the Rot back in,
`BIOMEFLORA_PATCH_WIPES_WILDPLANTS_1`) · `BiomeDescriptions_Ashkarr.xml:94` ·
`RUT_SheenExposureLock.xml:13` · `RUT_Wasteland.xml:150` · `RUT_RotSporeKit_SheenWeathers.xml:6` ·
`RUT_RotSporeKit_Flora.xml:24` · and all three `EnvironmentalHazards/Source/*.cs` hits
(`RM_WarmGroundExtension.cs:20`, `RM_AcceleratedRotExtension.cs:15`, `RM_LivingProduceExtension.cs:8`) —
example XML and flavour notes inside comments, zero string literals. ⛔ **Do not retarget a comment.**

No `validation.py` `QUALIFYING_BIOMES` entry names the Rot (zero hits) — nothing owed there.

### 8. Mechanics / kit state — ✅ ALL NINE SHIPPED

`rot_kit_spec.md`'s eight FOUNDRY tickets plus M9, checked one by one with `rimflow show`. **Every one is `done`:**
`ROT_SPORECLOUD_PORT_1` · `ROT_SHEEN_WEATHER_1` · `ROT_DECAY_HARVEST_1` · `ROT_WARM_MAT_1` ·
`ROT_LIVE_PREPARATIONS_1` · `ROT_GUARDIAN_GROVES_1` · `ROT_HEALTH_SHARING_1` · `ROT_PALE_TREE_1`.
Assemblies: `mandrake.rm.environmentalhazards` (the map components, extensions, RC1–RC6, the spore-cloud
worker) and `mandrake.rm.creaturebehaviors` (`RM_CompWoundLink`, `RM_HediffComp_KinMending`). Content:
`mandrake.rut.rotsporekit`. ⇒ 🔑 **Nothing here is waiting on a mechanic. This is a MOVE, not a build.**

**The kit's real external dependencies, MEASURED** (`MayRequire` values and `Class=` attributes parsed out
of all 33 kit XML files): `mandrake.rm.environmentalhazards` ×29 · `Ludeon.RimWorld.Royalty` ×3 ·
`Ludeon.RimWorld.Biotech` ×3 · `vanillaexpanded.vplantsemore` ×3 · `Ludeon.RimWorld.Ideology` ×2 ·
`sarg.alphabiomes` ×1 · `mandrake.rsw.swbestiary` ×1. Plus `RimMandrake.CreatureBehaviors.*` class
references ×6. ⚠️ **Exactly ONE live donor C# dependency survives**:
`RUT_RotSporeKit_Flora.xml:68` `<li Class="AlphaBiomes.CompProperties_GasProducer" MayRequire="sarg.alphabiomes">`
(`RUT_Skulltop`'s spore defence). Every other `BMT.*`/`BiomesCore.*`/`BiomesCaverns.*` string in the kit is
in a comment recording that it was dropped — RE-MEASURED, including `BiomesCaverns.GameCondition_SporeCloud`,
which `ROT_SPORECLOUD_PORT_1` really did retire. ⛔ Do not re-open that as a live defect.

### 9. Dependencies & items building INTO this mod

| item | state line | blocks step 2? |
|---|---|---|
| `SW_FAUNA_NEVER_IN_RM_TIER_1` | `proposed · needs offline · v1` — route 97 SW fauna rows out of `RM_` defs (Q11) | 🔴 **its tier question does** (§3). Not the item — the answer |
| `BIOME_MOD_SPLIT_EXECUTION_1` | `proposed · needs offline · v1` | parent; no |
| `BMT_FAUNA_ABSORPTION_1` | `doing · needs offline · v1` — port the 71 cast BMT creatures | no; §8's gate 3 is already clear |
| `DONOR_DEFS_PORT_TO_OURS_1` | `proposed · needs offline · v1` — port every donor def to ours | no — lands later, and is the long-term answer to the 13 `AB_` flora and 8 `AA_` fauna |
| `ECOSYSTEM_PYRAMID_LAW_1` | `proposed · needs deploy · v1` | no — its two Rot additions are already wired (def lines 142–149) |
| `NONCANON_BEAST_RENAME_1` | `proposed · needs offline · v1` | no |
| `MOD_OPTIONS_RETROFIT_1` | `ready · BLOCKED · needs offline · v1` | no — §6a settings are authored fresh here, not retrofitted |
| `BIOME_WORLD_SWITCH_WAVE_1` | `doing · needs bridge · v1` | no — Phase B territory |
| `CUT_FALLOUT_GENERATED_DATA_1` | `doing · needs offline · v1` — `biome_flora.py` BMT purge touches the Rot's generator row | no; overlaps §7(a) |
| `QUICKTEST_RIVER_WATER_MISSING_1` | `doing · needs game-up · v1` | no |
| `WORLD_REMAKE_FINAL_STEP_1` | `proposed · needs owner · v1` | no — receives this mod's paint-list row at step 6 |
| `BIOME_PAINT_ONCE_AT_THE_END_1` | `proposed · needs offline · v1` | governs; forbids painting |

**Owner decisions already taken — both FULLY APPLIED, nothing owed:**
- `rot_flora_fauna_review_2026-09-18.decisions.json` — frozen 2026-09-19, `reviewStatus.state: ruled`, 55/55
  decided (parsed: **46 regen, 7 keep, 2 cut**). ✅ **Applied** (closed `ROT_FLORA_FAUNA_VERDICTS_1`): both cuts
  reflected — `RSW_BovineBeetle` removed from `<wildAnimals>`, `RUT_Emberscythe` was never in the Rot, neither
  is in the def today (MEASURED). The ubiquitous "rename" note landed as **label/description edits, not defName
  changes** (27 `RUT_` defs direct + 19 donor defs via `RotSpecies_NamesAndSizes.xml`); 57 of 58 carry bespoke art.
- `rot_size_rejudge_2026-09-19.decisions.json` — frozen, 28 rows. ✅ **Applied** (closed `ROT_SIZE_REJUDGE_APPLY_1`):
  **11 of 11 resize rulings verified against the live XML** (e.g. `AA_MycoidColossus` drawSize 12;
  `AB_DribblingCap` 6.3~9, `AB_GiantAgarilux` 3.5~6 in the patch file; `RUT_CrimsonCap` 0.72~0.9,
  `RUT_Shinecap` 1.8~3, `RUT_BleedingTooth` 0.45~1.5 in the kit). The 5 blank rows (`AB_Agarilux`,
  `AB_GlowingAgarilux`, `AB_Glowstool`, `AB_LilacBeacon`, `AB_SlimyPholiota`) are undecided **on purpose** —
  the file's own `frozen_meaning` says blacklist posture, so undecided = size unchanged. ⛔ Nothing owed;
  ⛔ never regenerate either file. ⚠️ His note *"the Colussus art didnt wire up"* is wired now (MEASURED:
  `li[1..3]/bodyGraphicData/texPath` → `RotSpecies/MycoidColossus/MycoidColossus`, 3 facing PNGs on disk);
  whether it *looks* right is his eye, UNMEASURED.

`Transient/_rot/` is throwaway bridge scripts from 2026-09-17 — **no prior analysis worth citing.** Useful prior
reads: `Transient/rot_size_truth_2026-09-19.md`, `Transient/rot_art_landed_20260920/index.html`,
`Transient/biome_design_readiness_2026-09-23.md:42` (independently grades this row **WIRING-READY**, 0 open Qs).

### 10. Blockers

**None for steps 1, 3, 4 and the whole of §6's move.** FOUNDRY can scaffold, freeze and retarget tomorrow.

Two qualifications, neither a step-1 blocker:
1. 🔴 **Step 2's `<wildAnimals>` split needs the §3 tier answer** (10 BMT-port `RSW_` rows: exile or keep).
   Write the def with the **8 `AA_` rows + the 2 certain exclusions** (`Snoruuk`, `RSW_ShiroTrap`) and leave
   the 10 pending, or ask first — do not invent a rule.
2. Step 5 is Windows-Desktop-only (deploy + quicktest). Not a blocker of 1–4.

### 11. Concrete step plan

1. **Scaffold** `src/RimMandrake/TheRot/About/About.xml`: `<name>RimMandrake: The Rot</name>`,
   `packageId mandrake.rm.therot`, `supportedVersions 1.6`. **`loadAfter` derived from what the moved
   content actually references** (§2, §8, cited): `Ludeon.RimWorld`, `Ludeon.RimWorld.Royalty`,
   `Ludeon.RimWorld.Biotech`, `Ludeon.RimWorld.Ideology`, `mandrake.rm.environmentalhazards` (29 MayRequire
   + both modExtension classes), `mandrake.rm.creaturebehaviors` (6 class refs), `sarg.alphabiomes`
   (workerClass source, 2 terrains, 2 diseases, 13 flora, the one live donor comp), `sarg.alphaanimals`
   (8 fauna rows), `vanillaexpanded.vplantsemore` (3 MayRequire). ⛔ **No `loadAfter` on
   `mandrake.rm.flowworks` or `mandrake.rm.weathersuite` — nothing in this content references either
   (MEASURED, zero hits).** Then `Defs/BiomeDefs/`, `Source/RM_TheRotMod.cs` + `RM_TheRotSettings`, and
   `python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod TheRot` dry run, read the plan, `--apply`.
2. **Copy content in** as `RM_TheRot`. `Defs/BiomeDefs/RM_TheRot_Biome.xml` from the 242-line twin with: own
   `workerClass` `RimMandrake.TheRot.RM_BiomeWorker_TheRot`; own `texture`; `RM_`-renamed weather rows (MayRequire
   dropped); `RM_SheenExposureLock` in `biomeMapConditions`; **all 30 `wildPlants` rows, `RUT_`→`RM_`**; the
   `wildAnimals` rows §3/§10 allows; the two `EnvironmentalHazards` modExtensions **unchanged**; the two
   `AB_Mycotic*` terrains replaced by own TerrainDefs (or kept MayRequire'd as an explicit interim — say which in
   the commit). Move all 151 `RotSporeKit` files under `RM_`/`RimMandrake.TheRot` minus
   `RUT_RotSporeKit_MantisScythe.xml` (§6); move `RUT_SheenExposureLock.xml`, `RotSpecies_NamesAndSizes.xml`,
   `Textures/RotSpecies/`; fold the two `Rot*_WildSpawn.xml` patches into native `<wildPlants>` rows; add the
   `RM_TheRot` `<li>` to `RUT_SporeCloud`'s `<disallowedBiomes>` (§7b3). Then create
   `src/RimUtinni/UtinniPatches/Patches/WildAnimals_TheRot.xml` — `PatchOperationAdd` onto
   `/Defs/BiomeDef[defName="RM_TheRot"]/wildAnimals`, `MayRequire` **per row** (`mlie.starwarsanimalcollection`
   for `Snoruuk`, `mandrake.rsw.swbestiary` for `RSW_ShiroTrap`); `WildAnimals_Pyrelands.xml` is the shape.
   ⛔ Never `MayRequire` on the `<Operation>` — INERT, killed a cold load 2026-09-17.
3. **Freeze** `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_TheRot.xml` — byte-for-byte, **one** header
   comment: *"carrying the world until the terminal paint; content lives in `mandrake.rm.therot`; do not
   edit here."*
4. **Retarget** exactly §7(a); add the second op/row for exactly §7(b); ⛔ touch nothing in §7(c).
5. **Prove it loads** (Desktop): minimal list + `TheRot` + `mandrake.rut.patches` + **all five expansions**.
   `validate_patch.py src/RimUtinni/UtinniPatches/Patches/WildAnimals_TheRot.xml --live --defs`, then confirm
   the rows landed from a post-load def dump — an unmatched `PatchOperationAdd` is silent. Quicktest on a
   **scratch** world, landing tile set to `RM_TheRot` via `jawa/world_*`. ⛔ Never the canonical save.
6. **Commit + push**, explicit paths, and append the `RM_TheRot` / `mandrake.rm.therot` row to
   `infrastructure/state/facts/biome_paint_list.md` (the `RM_` block, `RM_Greentide`'s row at line 53 is the
   template) and to `WORLD_REMAKE_FINAL_STEP_1`'s paint list.

**Mod Settings (§6a) owed**, one toggle per shipped mechanic (all nine built, §8): master `theRotEnabled` ·
`sheenExposure` (reskin stays when off) · `acceleratedRot`+rate · `livingProduceHeat`+heat-per-unit ·
`warmMat`+warmth · `livePreparations` (strict/lenient viability) · `guardianGroves` · `healthSharing` ·
`paleTree` spawn · `sporeCloudIncident` weight · plus §6a's **cross-biome** block
(`enabled`/`everywhere`/allowlist/coverage, default off). ⚠️ The map components are gated in
`mandrake.rm.environmentalhazards`'s own settings today — wire this screen to those or move the gates, and
say which in the commit; ⛔ do not ship two screens that disagree.

### False statements found elsewhere

- `infrastructure/state/facts/biome_paint_list.md:43` — says `RUT_TheRot` is *"(215 lines)"*. It is **242**
  (`wc -l`). Stale.
- `rimflow` title of `BIOME_MOD_SPLIT_EXECUTION_1` — *"BLOCKED on 10 owner questions in its section 7"*.
  `biome_mod_architecture.md` §7 now ends *"All eleven questions in this section are RULED … Nothing in this
  spec is waiting on the owner. Every row can start."* The title's blocker is dead.
- `src/RimUtinni/RotSporeKit/build_review_sheet.py:325` — calls `RUT_Emberscythe` *"a Pyrelands
  fire-follower shipped in this same kit"*. It is **not in RotSporeKit**: its def is
  `src/RimUtinni/UtinniPatches/Defs/ThingDefs_Races/RUT_Emberscythe.xml`. The same false claim is quoted
  into closed `ROT_FLORA_FAUNA_VERDICTS_1`.
- `design/Jawa/worldbuilding/biomes/kits/rot_kit_spec.md:~88` — *"One known hole: `RUT_SporeCloud`'s
  `conditionClass` still points at the donor's compiled `BiomesCaverns.GameCondition_SporeCloud`"*. Fixed:
  `ROT_SPORECLOUD_PORT_1` is `done` and the live def carries
  `RimMandrake.EnvironmentalHazards.RUT_IncidentWorker_SporeCloud`; the donor name survives only in a comment.


## spec

🔑 **`biome_mod_architecture.md` §5 Phase A is the authority — read it, do not re-derive
it from here.** Steps 1–6, restated only far enough to start:

1. **Scaffold** `About/About.xml` with `mandrake.rm.therot`, `loadAfter` on the §2d shared libraries,
   a `ModSettings` class with the master toggle (§6), an empty `Defs/BiomeDefs/`.
   `deploy_custom_mods.py --mod <name>` dry run, then `--apply`.
2. **Copy the content in** as `RM_TheRot` — the BiomeDef plus its terrain, plant, weather,
   condition and hediff defs, textures, and the kit C# under namespace
   `RimMandrake.<Mod>`. ⛔ Every `RSW_`/`SW_`/`RUT_` entry in `<wildAnimals>` stays OUT and
   goes to `src/RimUtinni/UtinniPatches/Patches/WildAnimals_<Biome>.xml` as a
   `PatchOperationAdd` onto `RM_TheRot`, with `MayRequire="mandrake.rsw.swbestiary"`.
   `WildAnimals_Pyrelands.xml` is the existing shape. Any donor `workerClass`
   (`AlphaBiomes.*`, `VanillaBiomes.*`, `BiomesPlus.*`, `ReGrowthCore.*`) becomes this
   mod's own `RM_BiomeWorker_<X>` — a donor type in `workerClass` is a hard dependency the
   RimMandrake tier may not assume.
3. **FREEZE the `RUT_` def, do not delete it.** It carries the player's world until the
   terminal paint. Byte-for-byte as it is, one header comment only: *"carrying the world
   until the terminal paint; content lives in `mandrake.rm.therot`; do not edit here."* From that moment
   every content fix lands in `RM_TheRot` only.
4. **Retarget what does not need to be on the world** (kit specs, `_def_bindings_*.md`,
   queue items, `validation.py` `QUALIFYING_BIOMES`, kit C# string constants). Anything
   that must keep working on the live world (`BiomeNames_Ashkarr.xml`,
   `BiomeDescriptions_Ashkarr.xml`, doctrine patches, `race/wildBiomes`,
   `gen_cast_patch.py` output) gets a **second** op for `RM_TheRot` beside the `RUT_` one, so
   both behave identically until Phase B.
5. **Prove it loads and plays** — minimal list + this mod + `mandrake.rut.patches` +
   **all five expansions** (owner, 2026-09-19: every test list carries every expansion).

## verify

- Zero new Config errors in `Player.log` — and 🔴 grep the log, `validate_patch.py` cannot
  see config errors.
- `validate_patch.py <path> --live --defs` on the new Utinni fauna patch. An unmatched
  `PatchOperationAdd` is **silent**, so a clean run is not proof a row landed — confirm
  from a post-load def dump.
- A quicktest map on a **scratch** world whose landing tile is set to `RM_TheRot` through
  `jawa/world_*` at `Page_SelectStartingSite`. ⛔ Never the canonical save.
- `deploy_custom_mods.py` plan read before `--apply`; a `-` line is a deletion, look at it.

## criteria

`mandrake.rm.therot` exists, deploys, and loads clean carrying `RM_TheRot` with its own content and its own
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
