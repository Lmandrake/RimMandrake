# LANTERNDEEPS_RM_MOD_BUILD_1 — build RM_LanternDeeps as its own RimMandrake mod

**the Lantern Deeps - an INJECTION layer, no RUT_ twin; skips Phase A step 3**

Phase A row 2c of `design/RimMandrake/biome_mod_architecture.md`. Parent:
`BIOME_MOD_SPLIT_EXECUTION_1`. Governed by `BIOME_PAINT_ONCE_AT_THE_END_1`.

🔑 **Skips step 3.** There is no `RUT_` twin to freeze — this is a tier move of an
injection layer, so it does steps 1, 2, 4, 5, 6 only. Its host test is a biome-defName ALLOWLIST in Mod Settings (`LanternDeepsMod.cs:76-92`, `HashSet<string>.Contains(biome.defName)`), whose DEFAULT list was derived from the ≤ −40 °C rule — user-editable, not a hard biome dependency, which is what keeps it RimMandrake-tier. `Patches/RUT_LanternDeepGateKotorStygium.xml`
is the one Star Wars piece inside it and **stays in Utinni**.

## 🔑 STATE — MEASURED 2026-09-23

### 1. Step table

Steps per §5 Phase A. **Step 3 is skipped** (§4e: no `RUT_` twin — the whole mod changes tier).

| step | state |
|---|---|
| 1 scaffold | ⚠️ PARTIAL — the mod EXISTS and is DEPLOYED as `mandrake.rut.lanterndeeps` (`About/About.xml:5`; `test -e "/mnt/c/.../Mods/LanternDeeps/About/About.xml"` → present). A real `ModSettings` class ships (`Source/LanternDeepsMod.cs:20` `LanternDeepsSettings`, 7 settings + entrance-biome list). ⛔ OWED: the packageId is still `mandrake.rut.*`; there is no `Defs/BiomeDefs/` (the def lives at `Defs/Biomes/`); no §6a **master** toggle exists (the 7 toggles are per-mechanic, no single biome-master) |
| 2 copy content | ⛔ OWED — this is a `git mv` of 117 files (`find \| wc -l` = 117, incl. 11 `obj/` build artifacts + 4 `__pycache__`), not a copy. Nothing yet exists under `src/RimMandrake/LanternDeeps` (`test -d` → absent) |
| 3 freeze the twin | ⭕ N/A — §4e, no `RM_`/`RUT_` twin pair. Do NOT author a freeze header |
| 4 retarget | ⛔ OWED — see §7 below: 14 files hold real `RUT_LanternDeeps` work, the rest are prose/logs/artpipe records |
| 5 prove it loads | ⛔ OWED, Windows Desktop only (bridge + cold load). NOT a blocker of steps 1–4 |
| 6 commit/push | ⛔ OWED with step 5 |
| paint-list append | ✅ DONE and it is a **NO PAINT** row — `infrastructure/state/facts/biome_paint_list.md:51` (`RUT_LanternDeeps` … "none by design — no surface tile carries this def") and its summary line 75 counts it among the 6 NO PAINT rows. ⇒ step 6's "append to the paint list" reduces to **renaming that row's defName/packageId to `RM_LanternDeeps` / `mandrake.rm.lanterndeeps`, still NO PAINT** |

### 2. The def today

`src/RimUtinni/LanternDeeps/Defs/Biomes/RUT_LanternDeeps.xml` — **178 lines**, one `BiomeDef`,
`defName RUT_LanternDeeps`, label `lantern deeps`.

- **`workerClass`: ABSENT** (parsed). ⇒ 🔑 **No `RM_BiomeWorker_X` is owed** — step 2's
  donor-workerClass clause has nothing to do here. The def is reached ONLY through
  `RUT_LanternDeepGenerator.pocketMapProperties` and carries no worldgen route at all, deliberately
  (file header lines 8–15: the sheet's hard ban 1 made structural).
- **`modExtensions`: ABSENT** (parsed). Deliberate — donor `BiomesCore.DefModExtensions.*` /
  `GeologicalLandforms.*` Types were not carried across at `CAVERNS_PARITY_BUILD_1` because a def
  naming an unloadable Type is discarded whole (header lines 17–24). ⇒ **no §2d shared-library type
  is referenced by this def**, so `loadAfter` needs none of
  `environmentalhazards`/`creaturebehaviors`/`flowworks`/`weathersuite`.
- **terrain** — `terrainsByFertility` `Gravel`; `terrainPatchMakers` `RUT_LanternstoneFloor`, `Soil`,
  `WaterShallow`; `extraRockTypes` `RUT_LanternstoneWall`. **weather** — `RUT_DeepCalm` 100 (ours).
- **diseases** — 6, all vanilla: `Disease_Flu` 100, `Disease_FibrousMechanites` 30,
  `Disease_SensoryMechanites` 30, `Disease_MuscleParasites` 50, `Disease_AnimalFlu` 100,
  `Disease_AnimalPlague` 100; `diseaseMtbDays` 60.
- **other** — `foragedFood RUT_PufferTendrils`, `constantOutdoorTemperature 17`,
  `wildPlantsAreCavePlants true`, `settlementSelectionWeight 0`, `texture World/Biomes/IceSheet`
  (vanilla path, no own atlas), `pollutionWildAnimals` empty.

### 3. wildAnimals split

MEASURED with `xml.etree` (`len(list(wildAnimals))` = **8**; all 8 use the shorthand
`<DefName>commonality</DefName>` form, zero `<li>` children — a `findall('li')` parser reads 0 here).

| defName | commonality | class | verdict |
|---|---|---|---|
| `RSW_BovineBeetle` | 0.1 | `RSW_` | → Utinni patch |
| `RSW_Gembug` | 0.1 | `RSW_` | → Utinni patch |
| `RSW_GlowSlug` | 0.2 | `RSW_` | → Utinni patch |
| `RSW_Megapleura` | 0.1 | `RSW_` | → Utinni patch |
| `RSW_ShatterjawBeetle` | 0.1 | `RSW_` | → Utinni patch |
| `RSW_FacetMothLarvae` | 0.05 | `RSW_` | → Utinni patch |
| `RSW_MossBeetleLarvae` | 0.1 | `RSW_` | → Utinni patch |
| `RSW_BloodropMoth` | 0.25 | `RSW_` | → Utinni patch |

🔴 **8 of 8 leave — `RM_LanternDeeps` ships an EMPTY `wildAnimals`.**
`src/RimUtinni/UtinniPatches/Patches/WildAnimals_LanternDeeps.xml` **does not exist** (that directory
holds only the CrackedLands/Greentide/Pyrelands files + `ZZZ_BiomeWildAnimalDuplicates_Generated.xml`)
— it must be created.

⚠️ **Two more `RSW_` rows ride the same patch:** `allowedPackAnimals` (4 rows, parsed) =
`Muffalo`, `Alpaca`, `RSW_BovineBeetle`, `RSW_ShatterjawBeetle`. The two vanilla stay; the two `RSW_`
need a second `PatchOperationAdd` onto `RM_LanternDeeps/allowedPackAnimals`.

⚠️ `Source/MapComponent_LanternDeepDarkness.cs:49-50` hardcodes `"RSW_BloodropMoth"` /
`"RSW_ShatterjawBeetle"` as the darkness mechanic's summon set — **franchise cast named inside the C#
that is about to become a RimMandrake assembly.** It degrades to a no-op without Bestiary (soft
dependency), so it is not a load hazard. **BENCH rules** whether it becomes a settings-driven list;
⛔ not for FOUNDRY to invent.

### 4. wildPlants split

MEASURED with `xml.etree` (`len(list(wildPlants))` = **12**; shorthand form, zero `<li>`).

All 12 are **ours, invented**, and **all 12 stay** (rename `RUT_`→`RM_`), with their commonalities:
`DeepMycelium` 5.0 · `ZivvitTaper` 1.0 · `QuorrFern` 0.5 · `ThrakkCap` 0.5 · `NurrikGill` 0.4 ·
`OsskBramble` 0.3 · `BrellikBulb` 0.3 · `KuvraSpout` 0.2 · `VellokReed` 0.05 · `TwitchingPuffer` 0.02
· `PrennaLace` 0.02 · `Lanternstone_Sowable` 0.1.

🔑 **The `RUT_` prefix is not evidence against them** — §7 **Q11a** (owner, 2026-09-22): an
**invented** exotic name is free in the `RM_` tier, only **genuine canon** is IP. None of the twelve
is canon; `lantern_deeps_flora_names.md` records the owner naming them himself (*"New names please
just in the style of Star Wars"*, and *"called twitching puffer"*).
⛔ **No owner rejection applies.** 0 vanilla rows in `wildPlants` (parsed) — the Greentide's
oak-and-poplar defect does not exist here. Do not invent a rejection.

### 5. Roster vs def diff

Roster: `design/Jawa/worldbuilding/biomes/rosters/the_lantern_deeps.json`, parsed with `json`:
**fauna 2**, **flora 0**, **evictions 1**, `new_defs` 0, `fish` ruled empty ("no fish — enclosed cave
map"), `injection_layer: true`.
⚠️ **fauna is 2, not 3** — the third (`RSW_CrystalCrab`) moved to `evictions` on 2026-09-23 under
`ROSTER_DEAD_BMT_NAMES_SWEEP_1` (hard ban 3, this sheet's scope only — it legitimately stays in the
Scarlands, cf. `BMT_CrystalFairyMole`). Any brief still saying "fauna 3" predates that edit.

**Roster fauna → def: 0 unwired.** `RSW_Gembug` (roster 0.5, def 0.1) and `RSW_FacetMothLarvae`
(roster 0.5, def 0.05) are both wired; only the commonality differs, and the roster's own
`confidence` block declares its 0.5 an UNMEASURED placeholder — the def is the better number. Both
defs are real: `src/RimStarWars/SWBestiary/Defs/BiomesTeamPort/ThingDefs_Races/RSW_BiomesTeamPort_Races.xml`.

**Def rows NOT in the roster: 6** — `RSW_BovineBeetle`, `RSW_GlowSlug`, `RSW_Megapleura`,
`RSW_ShatterjawBeetle`, `RSW_MossBeetleLarvae`, `RSW_BloodropMoth`. All 6 have defs in that same
SWBestiary file (MEASURED: `<defName>` search across `src/**/*.xml`, 8 of 8 found). They are
`DEEPS_FAUNA_VERDICTS_1`'s survivors (closed, owner ruling 2026-09-19); the roster was never brought
up to the def. **Bookkeeping, not a defect.** Their art: **UNMEASURED**.

**Flora: roster 0 vs def 12** — the `DESIGN-PASS-OWED` grade at
`Transient/biome_design_readiness_2026-09-23.md:63,95`. 🔑 **It does NOT block the tier move, which is
mechanical.** All 12 defs exist and **12 of 12 have art on disk** (MEASURED: every
`graphicData/texPath` resolved against `Textures/`, 0 missing; 2–4 variants each). ⇒ The design gap
blocks the **roster half only** — `rosters/the_lantern_deeps.json` cannot be brought to truth until
the flora pass runs, and its `RM_` rename is a follow-up, not step 2 work.

🔴 **`Transient/lantern_deeps_strange_life_2026-09-20.decisions.json` holds NO owner rulings.**
MEASURED from the file itself: `reviewStatus.state = "prefill"`, `by: null`, `at: null`,
`generatedBy: "build_sheet.py (agent pre-fill, 2026-09-20)"`, and its own evidence line calls it
*"one of the item's three named 100%-prefill-identical sheets"* — every one of its 22 `decision`
values equals its `prefill`. ⇒ The 8 `approve`s (drinker, gembug, glowbulb, grabber, megapleura,
mossbeetlelarvae, shatterjaw, soulchime), the 6 `file_next`s (cleavers, creep, kindled, lantern,
mindstone, shardminds), the `defer` (chorus) and the 3 `not_deeps` (creepstern, crystalflower,
crystalhorn) are an **agent's guesses, not decisions**. ⛔ Do not cite them as owner rulings and do
not build from them. The live design items are `DEEPS_FAUNA_REPOPULATION_1` (`proposed / needs
owner`, BENCH — owner asked for 10–14 alien hydrocarbon concepts, ruled 2026-09-19 that the keep/cut
sheet be served now) and `DEEPS_FAUNA_MECHANICS_2` (`proposed / needs bridge`, BENCH — grabber
crush comp, soulchime LoS trigger, drinker hydrocarbon-blood extension). **Cited, not re-planned.**
Nothing from either is built into the biome def; `DEEPS_FAUNA_MECHANICS_1` shipped at `0e0fa8bef`.

### 6. Content to move into the mod

All 117 files live under `src/RimUtinni/LanternDeeps/` — **there is no content for this biome in
`src/RimUtinni/UtinniPatches/` at all** (MEASURED: `grep -rl lanterndeep|lanternstone` across
`src/RimUtinni/` returns only files under `LanternDeeps/`; no fauna patch, no
`BiomeNames_Ashkarr`/`BiomeDescriptions_Ashkarr` row, no absorbed kit mod). ⇒ Step 2 is a `git mv`
of the folder, minus the carve-outs below.

**Do not move:** `Source/obj/` (11 files, incl. a stale DLL), `__pycache__/` (4 `.pyc`).
`Assemblies/RimMandrake.Utinni.LanternDeeps.dll` must be **rebuilt**, not copied.

**C#** — 10 files, **every one** `namespace RimMandrake.Utinni.LanternDeeps` (MEASURED, one
`^namespace` each) → `RimMandrake.LanternDeeps`.
⚠️ **`Source/RimMandrake.Utinni.LanternDeeps.csproj` sets `EnableDefaultCompileItems false` and lists
all 10 files explicitly.** Rename = `AssemblyName` + `RootNamespace` + the file rename, **and** the
`<Compile Include>` block must keep matching — a file added or renamed without touching it compiles
into nothing, silently. Build is Windows-native `dotnet.exe` (csproj header).

🔴 **The spec names ONE Star Wars piece. There are FOUR files; three are not the one named.**
MEASURED by sweeping `RSW_|SW_|kyber|KOTOR|stygium|pyrinth|lightsaber|Jawa` across the mod's `Defs/`,
`Patches/` and `Source/*.cs`:

| file | verdict | reason |
|---|---|---|
| `Patches/RUT_LanternDeepGateKotorStygium.xml` | **STAYS Utinni** | the named one. `PatchOperationFindMod` on "Star Wars KotOR Resources and Materials", removes `KOTOR_CrystalFormation` from `Base_Player` |
| `Patches/RUT_LanternstoneKotorCrystals.xml` | **STAYS Utinni** 🔴 NEW | adds 14 `KOTOR_*` crystal defs (Star Wars KotOR IP, incl. `KOTOR_StygiumCrystal`) into `RUT_LanternstoneFormations`' scatter groups, `FindMod` "Jawa Armoury Rebalance". §3a: a reviewer of a franchise-free mod asks *"what is Stygium?"* |
| `Patches/RUT_LanternDeepGateKyber.xml` | **STAYS Utinni** 🔴 NEW | kyber is canon Star Wars; patches `lee.theforce.lightsaber`'s live `Force_CrystalFormation_*` defs |
| `Defs/MapGeneration/RUT_LanternDeepKyberScatter.xml` | **STAYS Utinni** 🔴 NEW | its `thingDefs` are `Force_CrystalFormation_{Small,Medium,Large}` `MayRequire="lee.theforce.lightsaber"` — a scatter group that exists only to place kyber |

⚠️ **Consequence:** `Defs/MapGeneration/RUT_LanternDeepGenerator.xml:54-55` lists **both**
`RUT_LanternDeepPyrinthScatter` and `RUT_LanternDeepKyberScatter` in `genSteps`. With the Kyber
scatter in Utinni, `RM_LanternDeepGenerator` must **not** list it — Utinni adds it back with a
`PatchOperationAdd` onto `RM_LanternDeepGenerator/genSteps`.

**Moves WITH the mod (not Star Wars):** `Defs/MapGeneration/RUT_LanternDeepPyrinthScatter.xml` +
`Patches/RUT_LanternDeepGatePyrinth.xml` — pyrinth is `det.epochspyrinth` ("Epochs - Pyrinth"), a
non-Star-Wars donor referenced with `MayRequire`, which §3a permits in the RimMandrake tier.
⚠️ BENCH may still prefer them in Utinni as donor coupling; a judgement, not a rule.

⚠️ **Two patches target a donor that is NOT in the load — assess, do not move:**
`Patches/RUT_LanternDeepEvictCrystalFauna.xml` (removes 6 `BMT_Crystal*` rows from
`BMT_CrystalCaverns/wildAnimals`) and `Patches/RUT_LanternstoneFictionRename.xml` (relabels
`BMT_ResourceBlueCrystal` + 5 `BMT_Crystal_Blue*` as "lanternstone"). MEASURED: **zero** activeMods
ids contain "cavern" in the newest snapshot (623 active, parsed), and `CAVERNS_PARITY_BUILD_1` (done,
`ad1ab9336`) made the Deeps donor-free so Biomes! Caverns *could* be cut. Both are `FindMod`-guarded
⇒ silent no-ops today, not errors, but **DEAD-PATCH candidates for BENCH to rule on**.

**What `CAVERNS_PARITY_BUILD_1` left behind:** a complete donor-free replacement — the Deeps' own
BiomeDef, `RUT_DeepCalm`, lanternstone floor/walls, the 4 formation sizes + their scatter GenStep,
the sowable line and 11 cave plants (`About.xml` description) — plus the deliberate absences (no
`workerClass`, no `modExtensions`), the two dead donor patches above, and
`Source/Patch_PocketMapGrowthRate.cs`: a Harmony prefix on `MapPlantGrowthRateCalculator.BuildFor`
stopping pocket-map `FinalizeInit` crashing on grazable flora with no valid parent tile. It is the
mod's only Harmony patch, is why `0Harmony` is in the csproj, and **must move with the mod**.

### 7. References to `RUT_LanternDeeps` across the repo

`grep -rl` (excluding `.git`, `obj/`, `__pycache__`): **111 files**. Each class below was read, not
counted.

🔑 **(b) "needs a SECOND op for `RM_LanternDeeps`" is EMPTY — zero files.** The whole second-op rule
exists because a def carries the player's painted world. **No tile has ever carried
`RUT_LanternDeeps`** (`biome_paint_list.md:51`, "none by design"; NO PAINT). So every reference is a
plain retarget and step 4 is much smaller here than on a painted biome.

**(a) Retarget outright — 20 files, 18 of them inside the mod folder:** the 8 `Defs/` files (Biomes,
MapGeneration/`RUT_LanternDeepGenerator`, TerrainDefs, ThingDefs_Items, ThingDefs_Natural ×2,
ThingDefs_Plants ×2) · `Patches/RUT_LanternDeepIncidentSuppression.xml` (**9 vanilla `IncidentDef`s ×
`disallowedBiomes` — a missed one lets Aurora/ColdSnap/Eclipse fire underground**) · `About/About.xml`
· `ART_JOBS.md` · 5 `.cs` (`DeepFloraPlanter.cs:35`, `GenStep_DeepFloraGate.cs:31-42` — 12 plant
literals, `GenStep_LanternstoneRock.cs:31-32`, `GenStep_ScatterLanternstone.cs:39`,
`MapComponent_LanternDeepDarkness.cs:49-50`) · 4 tool scripts (`validation.py`,
`build_species_sheet.py`, `tint_organics.py`, `wire_art.py`). **Outside the mod:**
`infrastructure/state/facts/biome_paint_list.md:51` (row rename, stays NO PAINT) and
`design/Jawa/worldbuilding/biomes/lantern_deeps_flora_names.md` (its §Style rule 6 specifies the
`RUT_` prefix — one-line amendment, not a sweep).

⚠️ **`validation.py` is the north-star checker and needs FOUR edits, not one:** `SETTINGS_TYPE`
(line 82, `RimMandrake.Utinni.LanternDeeps.LanternDeepsSettings`), `BOOT_ERROR_NEEDLES` (line 90,
`"Config error in mandrake.rut.lanterndeeps"`), `EXCEPTION_NEEDLES` (line 95,
`"RimMandrake.Utinni.LanternDeeps"`), and the `RUT_LanternDeep*` def-name constants (lines 84–87,
135–166). `QUALIFYING_BIOMES` (line 83, `{"BiomeGRimond","RUT_NightsideIce","RUT_PropaneLake"}`) is
the HOST set, not this biome — it follows `NIGHTSIDEICE_RM_MOD_BUILD_1` /
`BLUEDESERT_RM_MOD_BUILD_1`, **not this item**. ⛔ Do not rename it here.

**(c) Comment / prose / immutable record — leave (91 files):**
`src/RimMandrake/Utils/ecosystem_pyramid_check.py:49` — inside the header comment explaining that the
script derives the biome set **live** rather than from a pinned list; there is no pinned list to fix.
⛔ Do not retarget a comment. · `design/RimMandrake/biome_mod_architecture.md` (the spec) ·
`design/Jawa/worldbuilding/biomes/rosters/the_rot.json:47` and
`rosters/the_lantern_deeps.json` (prose inside `law`/`reason` fields recording *why* a species moved —
historical provenance, and the roster's own rename is a separate follow-up) ·
`design/Jawa/worldbuilding/review/creature_register_rows.json` (the creature art register was
RETIRED 2026-09-11) · 3 live item files (`BIOME_MOD_SPLIT_EXECUTION_1`,
`MIASMA_FEVERWOOD_GREENTIDE_BMT_1`, `ROSTER_DEAD_BMT_NAMES_SWEEP_1`) + 2 closed ones + 3 handoffs ·
`infrastructure/state/ledger/events.jsonl` · **56 `infrastructure/artpipe/done/*.json`** job records
(the defName sits in `style_notes`/`rimflow_item_id` — never edited) · 21 `Transient/` reports and one
`Player.log`. **None of these is owed work.**

### 8. Mechanics/kit state

**SHIPPED — assembly `RimMandrake.Utinni.LanternDeeps` (this mod), 10 C# files:**
two entrance scatters + their buildings and map-gen patches (`LANTERN_DEEPS_INJECTION_1`, **done**,
closed `2eb08d1a4`) · the pocket-map generator and persistent Deep · the **darkness mechanic**
(`MapComponent_LanternDeepDarkness`) · the cave-flora gate, planter and regrowth
(`GenStep_DeepFloraGate`, `DeepFloraPlanter`, `MapComponent_DeepFloraRegrowth`) · lanternstone rock,
formations and their scatter (`GenStep_LanternstoneRock`, `GenStep_ScatterLanternstone`) · the
pocket-map growth-rate Harmony prefix (`Patch_PocketMapGrowthRate`) · **Mod Settings**
(`LanternDeepsSettings`, 7 fields + the `entranceBiomes` list, `DEEP_ENTRANCE_BIOMES_SETTING_1`) ·
incident suppression on 9 vanilla incidents. `CAVERNS_PARITY_BUILD_1` **done**, closed `ad1ab9336`.

**SHIPPED ELSEWHERE — `mandrake.rm.creaturebehaviors`:** `DEEPS_FAUNA_MECHANICS_1` (`doing`,
FOUNDRY) landed the Grabber grapple, Soulchime proximity psychic stun and tame-soothe aura, and
shard armor as `RM_Comp*` classes in `src/RimMandrake/CreatureBehaviors/Source/` (MEASURED: 9 files).
⇒ 🔑 **Those comps are already RimMandrake-tier and move nothing.**

**UNBUILT — must NOT be waited on:** `DEEPS_FAUNA_MECHANICS_2` (`proposed / needs bridge`) ·
`DEEPS_FAUNA_REPOPULATION_1` (`proposed / needs owner` — the 10–14 alien-concept portfolio) · the
crystal-life cast the sheet's `## Owed` names (the Kindled `RUT_Kindled`, the Mindstone
`RUT_Mindstone`, the Creep, the Cleavers, the Shard-minds, the Forgotten Sentinels) ·
`KYBER_TRADE_PLOT_1` (`ready / BLOCKED` on the Heat/Hutt blackboard) · the collapse hazard.
⛔ **None of these is a precondition for the tier move.** The mod is complete and deployed today; the
move renames it.

### 9. Dependencies & items building INTO this mod

| item | state line | blocks step 2? |
|---|---|---|
| `BIOME_MOD_SPLIT_EXECUTION_1` | `doing  needs offline  target v1` — parent, BLOCKED on §7's owner questions | **No.** §7 **Q6 is RULED** ("MOVE IT UP"), so this biome is not held by the parent's block |
| `DEEPS_FAUNA_REPOPULATION_1` | `proposed  needs owner  target v1` (BENCH, design) | No — lands later, into `RM_LanternDeeps` |
| `DEEPS_FAUNA_MECHANICS_1` | `doing  needs bridge  target v1` (FOUNDRY) | No — ships in `creaturebehaviors`, already RimMandrake |
| `DEEPS_FAUNA_MECHANICS_2` | `proposed  needs bridge  target v1` (BENCH) | No — lands later |
| `ROSTER_DEAD_BMT_NAMES_SWEEP_1` | `proposed  needs offline  target v1` | No — already did this roster's step 1 (the crystal-crab eviction) |
| `MOD_OPTIONS_RETROFIT_1` | `ready  BLOCKED  needs offline  target v1` | No, but it owns the §6a **master toggle** this mod lacks — add it during step 1 rather than filing a second pass |
| `DONOR_DEFS_PORT_TO_OURS_1` | `proposed  needs offline  target v1` | No. It is the stream that would eventually retire `lee.theforce.lightsaber`/`det.epochspyrinth` couplings; **not** sped up or slowed by this move |
| `WORLD_REMAKE_FINAL_STEP_1` | `proposed  needs owner  target v1` | No — step 6 only renames this biome's existing **NO PAINT** paint-list row |
| `NIGHTSIDEICE_RM_MOD_BUILD_1`, `BLUEDESERT_RM_MOD_BUILD_1` | sibling tier moves | No — but they own `validation.py:83`'s `QUALIFYING_BIOMES` host names. ⚠️ Once they land, this mod's `entranceBiomes` **default** must follow, or every entrance silently stops scattering (the `LANTERNDEEPS_GENSTEP_ALLOWLIST_DEAD_1` failure mode again, recorded in `About.xml:34-44`) |
| `KYBER_TRADE_PLOT_1` | `ready  BLOCKED  needs offline  target v1` | No — it consumes the Utinni kyber carve-out, which this move preserves |

**Live mod-list context (MEASURED, `ET.parse` of `activeMods` in
`infrastructure/state/modlists/ModsConfig_backup_before_rustcathedral_enable_2026-09-23T211528Z.xml`
= 623 active):** `mandrake.rut.lanterndeeps` ✅ active · `mandrake.rut.patches` ✅ ·
`mandrake.rsw.swbestiary` ✅ · `grimterra.biomesmod` ✅ · `det.epochspyrinth` ✅ ·
`lee.theforce.lightsaber` ✅ · `guy762.mm.kotorcore` ❌ **absent** · any "cavern" id ❌ **absent**.

### 10. Blockers

**None.** FOUNDRY can start step 1 tomorrow morning offline.

- Steps 1, 2, 4 are all offline file work in `src/`.
- Step 5 is Windows-Desktop-only (deploy + cold/quick load + bridge); per the brief that is **not**
  a blocker of steps 1–4.
- The flora design gap (§5) blocks the **roster file** only, never the move.
- ⚠️ **Two decisions FOUNDRY must NOT make alone, and neither stops step 1:** (i) the three extra
  Star-Wars carve-outs in §6 — the item's own spec says "one", so BENCH confirms the four-file split
  before the `git mv`; (ii) the two dead donor patches. Both are Defs/Patches-level calls made
  *during* step 2, not preconditions.
- ⚠️ **One safety check owed before `RUT_LanternDeeps` stops existing (UNMEASURED, Desktop):** the
  Deeps are **persistent pocket maps**. If `CANONICAL_ASHKARR_START_2026-09-12.rws` (or any keeper
  save) already contains an entered Deep, that map's `biome` is `RUT_LanternDeeps` and renaming the
  def gives a Scribe `Could not load reference to` that no mod change fixes
  (`~/.claude/skills/rimworld-savegame`). ⇒ Confirm no keeper save holds a generated Deep, or keep a
  `RUT_LanternDeeps` compat shim (the `RUT_Umbra` precedent, `biome_paint_list.md:47`). ⛔ This is a
  savegame question, not a tile question — do not answer it from the tiles CSV.

### 11. Concrete step plan

1. **Scaffold = rename in place.** `git mv src/RimUtinni/LanternDeeps src/RimMandrake/LanternDeeps`.
   `About/About.xml`: `packageId` → **`mandrake.rm.lanterndeeps`**, `name` drops "RimUtinni:".
   **`loadAfter` (derived, not copied):** keep `brrainz.harmony` (Harmony is a real `modDependency`
   and `Patch_PocketMapGrowthRate` uses it), `m00nl1ght.GeologicalLandforms`, `det.epochspyrinth`,
   `mandrake.rut.patches`, `grimterra.biomesmod`; **drop `guy762.mm.kotorcore` and
   `lee.theforce.lightsaber`** — both exist only for the Kotor/kyber patches that move to Utinni, and
   belong on `mandrake.rut.patches`' `loadAfter` instead. ⛔ **Add NO §2d shared library**: none is
   referenced (§2 — `modExtensions` ABSENT, no `RimMandrake.EnvironmentalHazards.*` /
   `.CreatureBehaviors.*` type in any def or `.cs`).
   **Settings (§6a):** add the missing **master toggle** `lanternDeepsEnabled` (default on; off ⇒
   both scatters no-op, the def still loads) above the 6 existing per-mechanic fields
   (emergence, mineshaft, darkness, formations, flora + their multipliers); keep `entranceBiomes`.
2. **Rename the content.** `RUT_`→`RM_` on the BiomeDef, `DeepCalm`, `LanternstoneFloor`,
   `LanternstoneWall`, the 4 formation sizes, the lanternstone items + chunk, the **12 plants**,
   `PufferTendrils`, `LanternDeepGenerator`, `LanternDeepEmergence`(+`_Scatter`/`_MapGenPatch`),
   `LanternDeepMineshaft`(+ditto), `LanternstoneFormations`, `LanternDeepFloraGate`, `DeepAmbience`
   — and the texPath root `Textures/RUT_LanternDeeps/` → `Textures/RM_LanternDeeps/`
   (🔴 **texture binds by `texPath`, not defName** — folder + every `texPath` in the same commit or
   the art renders nothing). C#: namespace and assembly → `RimMandrake.LanternDeeps`, csproj
   `AssemblyName`/`RootNamespace` + all 10 `<Compile Include>` lines. `wildAnimals` → **empty**;
   `allowedPackAnimals` → `Muffalo`/`Alpaca` only.
   **Create** `src/RimUtinni/UtinniPatches/Patches/WildAnimals_LanternDeeps.xml`
   (`WildAnimals_Pyrelands.xml` is the shape): `PatchOperationAdd` onto
   `/Defs/BiomeDef[defName="RM_LanternDeeps"]/wildAnimals` with the 8 rows at their current
   commonalities + a second op onto `.../allowedPackAnimals` for `RSW_BovineBeetle` and
   `RSW_ShatterjawBeetle`, all `MayRequire="mandrake.rsw.swbestiary"`.
   **Move to `UtinniPatches/Patches/`** the 4 §6 files, retargeting the kyber pair's generator /
   `LanternstoneFormations` references at the `RM_` names and adding a `PatchOperationAdd` that puts
   the kyber scatter back into `RM_LanternDeepGenerator/genSteps`.
   **`git rm`:** `Source/obj/`, `__pycache__/`. **Rebuild** the DLL.
3. ⭕ **SKIPPED** — §4e, no twin. ⛔ Do not author a freeze header.
4. **Retarget** the 20 files in §7(a); touch nothing in §7(c). ⛔ Leave `validation.py:83`'s
   `QUALIFYING_BIOMES` alone (it is the HOST set, owned by the Nightside Ice / Blue Desert items).
5. **Prove it loads** — minimal list + this mod + `mandrake.rut.patches` + `mandrake.rsw.swbestiary`
   + **all five expansions**. Grep `Player.log` for Config errors (`validate_patch.py` cannot see
   them); `validate_patch.py --live --defs` on the new fauna patch, then confirm the 8 rows from a
   post-load def dump — an unmatched `PatchOperationAdd` is silent. Then a **quicktest** on a scratch
   world: enter a Deep, check darkness, flora and formations. ⛔ Never the canonical save.
6. **One commit, explicit paths**, the message naming what the move corrected (packageId tier, the
   four Star Wars carve-outs, the missing master toggle). Same commit: update
   `infrastructure/state/facts/biome_paint_list.md:51` to `RM_LanternDeeps` /
   `src/RimMandrake/LanternDeeps` / `mandrake.rm.lanterndeeps`, **still NO PAINT**.

### False statements found elsewhere

- 🔴 `design/RimMandrake/biome_mod_architecture.md:129` (§2c table) — *"Its host test is TEMPERATURE,
  not a biome list."* **False about the code.** There is no temperature comparison anywhere in the
  mod (MEASURED: no `Temperature`/`≤ -40` test in any of the 10 `.cs` files; only comments say it).
  The host test is `LanternDeepsSettings.IsEntranceBiome(map.Biome)` — a `HashSet<string>` membership
  test on `biome.defName` (`Source/LanternDeepsMod.cs:76-92`), called from
  `Source/GenStep_ScatterCavePortal.cs:31-34` and its mineshaft twin. It is a **Mod Setting** whose
  DEFAULT is the three biomes the frozen sheet's temperature rule picked
  (`Source/LanternDeepsMod.cs:57-61`). §4e of the **same document** says this correctly (*"note that
  the FROZEN sheet says the host test is temperature, so a biome allowlist in the code is already a
  departure"*), and `Transient/biome_split_factcheck.md` §F4 already measured it. ⇒ The tier argument
  survives (the list is user-configurable, "any biome selectable"), but the sentence does not.
- 🔴 **This item's own header, line 9** repeats it: *"Its host test is TEMPERATURE, not a biome
  list; that is what makes it RimMandrake-tier."* Same correction. BENCH to fix both in one commit.
- ⚠️ `design/Jawa/worldbuilding/biomes/the_lantern_deeps.md:13-15` (FROZEN sheet, opening paragraph)
  — *"using Biomes! Caverns' `BMT_CrystalCaverns` as the cave-map def"*. Superseded by
  `CAVERNS_PARITY_BUILD_1` (done, `ad1ab9336`): the Deeps are donor-free and `BMT_CrystalCaverns` is
  not in the load (0 activeMods ids contain "cavern"). An **amendment line** under the freeze banner
  (the 2026-09-18 flora amendment is the precedent) — not a ruling change.
- ⚠️ `src/RimUtinni/LanternDeeps/Patches/RUT_LanternDeepGateKotorStygium.xml:11` — *"guy762.mm.kotorcore's
  own LIVE def … still active in ModsConfig"*. `guy762.mm.kotorcore` is **absent** from the
  2026-09-23 snapshot's 623 activeMods. ⚠️ The patch guards on the mod's display NAME, so whether a
  mod titled "Star Wars KotOR Resources and Materials" is active under another packageId is
  **UNMEASURED** — but the sentence's cited evidence is stale either way.
- ⚠️ `src/RimUtinni/LanternDeeps/Patches/RUT_LanternDeepEvictCrystalFauna.xml:31` — *"This mod already
  declares that mod \[Biomes! Caverns\] a hard modDependency (About.xml)"*. **False**: `About.xml`'s
  `modDependencies` holds exactly one entry, `brrainz.harmony` (parsed).

### UNCERTAIN / UNMEASURED

- Art for the 8 `RSW_` fauna: **UNMEASURED** (their defs live in SWBestiary; not checked).
- Whether any keeper savegame holds a generated Deep pocket map: **UNMEASURED** (§10).
- Whether a mod displaying as "Star Wars KotOR Resources and Materials" is active: **UNMEASURED**.
- Whether the pyrinth pair is better placed in Utinni than RimMandrake: a BENCH judgement, not
  measurable.

## spec

🔑 **`biome_mod_architecture.md` §5 Phase A is the authority — read it, do not re-derive
it from here.** Steps 1–6, restated only far enough to start:

1. **Scaffold** `About/About.xml` with `mandrake.rm.lanterndeeps`, `loadAfter` on the §2d shared libraries,
   a `ModSettings` class with the master toggle (§6), an empty `Defs/BiomeDefs/`.
   `deploy_custom_mods.py --mod <name>` dry run, then `--apply`.
2. **Copy the content in** as `RM_LanternDeeps` — the BiomeDef plus its terrain, plant, weather,
   condition and hediff defs, textures, and the kit C# under namespace
   `RimMandrake.<Mod>`. ⛔ Every `RSW_`/`SW_`/`RUT_` entry in `<wildAnimals>` stays OUT and
   goes to `src/RimUtinni/UtinniPatches/Patches/WildAnimals_<Biome>.xml` as a
   `PatchOperationAdd` onto `RM_LanternDeeps`, with `MayRequire="mandrake.rsw.swbestiary"`.
   `WildAnimals_Pyrelands.xml` is the existing shape. Any donor `workerClass`
   (`AlphaBiomes.*`, `VanillaBiomes.*`, `BiomesPlus.*`, `ReGrowthCore.*`) becomes this
   mod's own `RM_BiomeWorker_<X>` — a donor type in `workerClass` is a hard dependency the
   RimMandrake tier may not assume.
3. **FREEZE the `RUT_` def, do not delete it.** It carries the player's world until the
   terminal paint. Byte-for-byte as it is, one header comment only: *"carrying the world
   until the terminal paint; content lives in `mandrake.rm.lanterndeeps`; do not edit here."* From that moment
   every content fix lands in `RM_LanternDeeps` only.
4. **Retarget what does not need to be on the world** (kit specs, `_def_bindings_*.md`,
   queue items, `validation.py` `QUALIFYING_BIOMES`, kit C# string constants). Anything
   that must keep working on the live world (`BiomeNames_Ashkarr.xml`,
   `BiomeDescriptions_Ashkarr.xml`, doctrine patches, `race/wildBiomes`,
   `gen_cast_patch.py` output) gets a **second** op for `RM_LanternDeeps` beside the `RUT_` one, so
   both behave identically until Phase B.
5. **Prove it loads and plays** — minimal list + this mod + `mandrake.rut.patches` +
   **all five expansions** (owner, 2026-09-19: every test list carries every expansion).

## verify

- Zero new Config errors in `Player.log` — and 🔴 grep the log, `validate_patch.py` cannot
  see config errors.
- `validate_patch.py <path> --live --defs` on the new Utinni fauna patch. An unmatched
  `PatchOperationAdd` is **silent**, so a clean run is not proof a row landed — confirm
  from a post-load def dump.
- A quicktest map on a **scratch** world whose landing tile is set to `RM_LanternDeeps` through
  `jawa/world_*` at `Page_SelectStartingSite`. ⛔ Never the canonical save.
- `deploy_custom_mods.py` plan read before `--apply`; a `-` line is a deletion, look at it.

## criteria

`mandrake.rm.lanterndeeps` exists, deploys, and loads clean carrying `RM_LanternDeeps` with its own content and its own
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
