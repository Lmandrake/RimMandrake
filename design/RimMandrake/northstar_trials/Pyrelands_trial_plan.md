# Pyrelands — north-star trial plan (the biome template)

Owner, 2026-09-30 (typed): *"Yes. Write out comprehensive northatar plans for all three and ticket
them out as trials for full completion. Use gpt reviews for their validation plan especially site
preparation that's often overlooked before a proper test setup. I'd like this to go very well. Then
use ultra fast python to drive the bridge to validate. Make it happen!"*

Pyrelands is the first biome carried end to end through the north-star ladder. About twenty other
biomes will copy it, so every choice here is made to generalise (§6).

**Ladder:** DRAFT → VALIDATED (owner's word) → WIRED (every bar has `shows=`) → GREEN on the
minimal list → GREEN on the full list → SHIPPED (deployed, superb Mod Settings with per-feature
toggles, art complete, code review CLEAN).

**Tickets:** `PYRELANDS_NORTHSTAR_TRIAL_1` (parent, FOUNDRY), with one child item per rung (§9).
Every rung depends on `BIOME_MOD_UNIFICATION_1`'s current packaging (§1.1).

Evidence tags: **MEASURED** means read on 2026-09-30 from origin/main or the deployed Mods folder,
with the instrument named. **UNMEASURED** means nobody has looked yet.

---

## 1. Current state per rung

### 1.1 Packaging — Pyrelands now ships inside `mandrake.rm.biomes`

- **MEASURED** (`src/RimMandrake/Biomes.compose.json`): the `Pyrelands` entry has `wave: 2`, and
  `compose_wave` is 2. That makes it **COMPOSED**: it ships inside *RimMandrake: Baroque Biomes*
  (`mandrake.rm.biomes`), and deploying it standalone is refused.
- **MEASURED** (ledger `FOUNDRY.jsonl`, commits `c3a1e3fd1`/`88a4339a9`): `BAROQUE_BIOMES_WAVE2_FOLD_1`
  closed on 2026-09-28. Its record: "All 29 folded biomes/kits now live inside mandrake.rm.biomes;
  17 packageIds retired in the same swap". The new `FULL.LATEST` holds 614 mods.
- **MEASURED** (listing of the deployed Mods folder): `Mods/RimMandrake.Biomes/` exists with
  `LoadFolders.xml`, `Biomes/`, `Biomes.roster.xml` and `Assemblies/RimMandrake.Biomes.dll(.srchash)`.
  There is no standalone `Mods/Pyrelands`. `Mods/UtinniPatches` and `Mods/PyrelandsMechanics` are
  separate mods, because the five mechanic mods stayed OUT of the merge.
- ⇒ **The dev folder `src/RimMandrake/Pyrelands/` is still the source.** The thing deployed and
  tested is the composed `mandrake.rm.biomes`. Every list, deploy check and fingerprint in this plan
  targets `mandrake.rm.biomes`, never `mandrake.rm.pyrelands`.
- ⚠️ **Three things are stale and must be fixed in rung W, outside the hashed section:**
  1. The walk header's `subject:` line says packageId `mandrake.rm.pyrelands`.
  2. The walk's `list:` line says `minimal+mandrake.rm.pyrelands+mandrake.rut.patches`.
  3. The `validation.py` docstring describes the pre-fold world.

  `modcheck run Pyrelands` built from that `list:` would ask for a packageId that no longer exists.
  The modcheck key stays `Pyrelands`, because the dev folder still exists, so no `rename-key` is
  needed. 🔴 **MEASURED** (`modcheck/runner.py` `compose_test_list` + `_package_id`): `modcheck run`
  takes the packageId from the **dev folder's** `About/About.xml` (`mandrake.rm.pyrelands`). It
  appends that id to MINIMAL with **no dependency closure**. A composed mod has no standalone
  deploy, so RimWorld silently drops that id and the run lands on a list **without the biome**.
  ⇒ Until modcheck learns about the compose, the trial drives its own tier (§3.1) and never calls
  `modcheck run` (which also rewrites the live ModsConfig). File this as a modcheck defect.
- Per-biome toggle: **MEASURED** (`BiomesShell/Source/RM_BiomesMod.cs`). Today
  `RM_BiomesSettings.Enabled("Pyrelands")` gates **worldgen placement only**. A toggled-off biome
  keeps its defs. Pyrelands' own 20+ feature toggles live in `RM_PyrelandsSettings`
  (`RM_PyrelandsMod.cs`) and are all `public static`.

### 1.2 Rung status

| rung | state | evidence |
|---|---|---|
| **DRAFT** | ✅ 10 bars drafted | **MEASURED** with `modcheck.northstar.parse()` on origin's walk: 10 must-show ids, 0 cannot-show |
| **VALIDATED** | ❌ **Effectively DRAFT** — the header says VALIDATED but the hash does not match | **MEASURED** with `northstar.parse()`: recorded hash `90a286aa83f1`, current hash `15e3d4df4583`, reason "section edited since validation". Bisected per commit: `7690c96fb` (2026-09-17, owner validates 2 bars) → `1cbb4e7dc` → `f5ce015e7` all hash `90a286…`. Then `b3457a829` (the same day, 18:43) added 8 fire-ecology bars, and its own message says "reverts to DRAFT by hash until the owner re-validates the full ten". **The owner has validated only 2 of the 10 bars** (plant and animal distribution). The local shared-tree copy gives the same result: DRAFT, 10 bars. Origin's header line is a stale declaration, not a validation. |
| **WIRED** | ❌ 0 of 10 | **MEASURED**: `validation.py` passes no `shows=` to any component. It has 3 chains and 6 components, all toggle-floor checks |
| **GREEN minimal** | ❌ never | **MEASURED** (`Transient/modcheck/Pyrelands_summary.json`, 2026-09-13): 3 of 6 components passed, on a **plain quicktest map, not a Pyrelands map**. The failures were `ash_ladder_escalation`, `ashfall_accumulates` and `biome_def_wiring`. §2.3 shows that all three are suite bugs |
| **GREEN full** | ❌ never | — |
| **SHIPPED** | ❌ | §5 |

### 1.3 What the biome is, measured from source (the census targets)

- **Flora** (`Defs/BiomeDefs/Pyrelands.xml` `<wildPlants>`, element-name form): `RM_FE_Plant_EmberGrass`
  9.0 and `RM_FE_Plant_Quickgrass` 3.8. `RM_FE_Plant_ScorchFruit` is **fire-born only**: the
  fire-tick postfix creates it, and it is not in `wildPlants`. The census allowlist is therefore
  {EmberGrass, Quickgrass, ScorchFruit}.
  - **MEASURED** `plantDensity` 16 and `wildPlantsCareAboutLocalFertility` false. The def's own
    comment expects about 96% of plantable cells covered.
  - `RM_PyrelandsDensityEnforcer.cs` re-asserts that density after Map Designer rewrites it.
  - `WildPlantAllowlist.cs` filters foreign wild plants out, gated by `wildPlantAllowlistEnabled`.
- **Fauna — patch-added, read by `PatchOperation` xpath** (`UtinniPatches/Patches/WildAnimals_Pyrelands.xml`).
  The patch has three ops:
  1. A **Replace** of the whole node with `RUT_FireHawk` 0.15 and `RUT_FurnaceBeast` 0.08. This
     drops the def's 13 vanilla placeholders: Hare, Rat, Gazelle and so on.
  2. An **Add** under `MayRequire="mandrake.rsw.swbestiary"` of `RSW_Anooba` .35, `RSW_Iriaz` .5,
     `RSW_Nuna` .5, `RSW_Orray` .25, `RSW_Zeer` .6, `RSW_Dalgo` .18 and `RSW_Gizka` 1.0.
  3. An **Add** under `MayRequire="mandrake.rm.biomes"` of `RUT_Emberscythe` .05, `RUT_Sytheclaw` .2,
     `RUT_Barbslinger` .15, `RUT_FireWasp` .4, `RUT_Flamefang` .5 and `RUT_Ashwallow` .18.

  ⇒ **The expected live roster is 15 kinds. Vanilla Hare/Rat/Gazelle appearing is a FAIL, not
  baseline.**
  - 🔴 **Both `MayRequire`s sit on top-level `<Operation>` nodes, where the engine ignores them**
    (CLAUDE.md, `PATCH_MAYREQUIRE_GUARD_INERT_1`). If `mandrake.rsw.swbestiary` is missing from a
    test list, the seven `RSW_` keys dangle. That is exactly walk step 1's
    `CommonalityOfAnimal` NRE. The test tier must therefore carry swbestiary (§3.1). File this as a
    finding on `PATCH_MAYREQUIRE_GUARD_INERT_1`. It is not this trial's to fix.
  - ⚠️ The file's header comment lists the herd as bare `Anooba`/`Iriaz`…, but the live value says
    `RSW_*`. The comment is stale and the value is authoritative. Fix it under the
    correctness-outranks-seat rule.
- **Weather** (`baseWeatherCommonalities`): Clear 40, DryThunderstorm 20, `RM_FE_Weather_AshFall` 14,
  `RM_FE_Weather_Cinderfall` 4, `RM_FE_BlackRain` 3, Fog 2, GrayPall 1, Windy 2, Overcast 2. This is
  consistent with ban #2 (no ordinary rain). `AshStorms_Pyrelands.xml` patches it further.
  **UNMEASURED:** the post-patch table. Read it live with `jawa/get_def`.
- **Terrain**: `terrainsByFertility` → `RM_FE_Ground_{Sand,Gravel,Soil,SoilRich}`, all burnable,
  all `burnedDef` → `RM_FE_Ash_Trace`. A patchmaker lays Ash Trace, Light and Heavy at mapgen.
  Deep is reachable only by burning. `ScorchableGround.xml` documents **4 expected `Config error …
  burnedDef is flammable` lines per load**. They are allowlisted for the log-clean bar and are not
  a defect.
- **Heat**: the sheet records the Ash'karr Pyrelands at sun median **+56°**, median temperature
  **53.6 °C** (range 39–65) and elevation ~257 m (`the_pyrelands.md` §0). This is an extreme-heat,
  **overhead-sun** biome under the one-heat ruling. `SOLAR_HEAT_EXPOSURE_1` (open) will give it a
  heat-kind extension. Until then the test records the heat kind it *would* carry and never adds a
  Pyrelands-specific heat effect. `RM_FurnaceWarmth` is the furnace-beast aura, a warmth buff,
  which is not a heat kind.

---

## 2. The bars

### 2.1 Conventions

- **Where each bar runs.**
  - **[O] offline:** a def or source read with no game.
  - **[D] def read-back:** a live read of the loaded def through `jawa/get_def`/`get_defs`.
  - **[L] live:** the bridge on the trial site.
  - **[V] visual:** a screenshot graded by `modcheck.judge`, with a YES required.
  - **[H] human pass:** the owner looks.
- **`shows=` binding.** Each bar gets **exactly one** component that claims it. The component's
  name is the bar id minus `pyre_`, so the component `plant_distribution_correct` claims
  `shows=["pyre_plant_distribution_correct"]`. A component with a [V] half must call
  `t.screenshot()` inside it so the judge has its image.
- **Statistical bars use pooled samples.** Animals and plants are sampled across **K = 3
  independently generated sites** (§3.4). A bar never rests on one map: the walk's own 2026-09-17
  lone-tile census is the cautionary example.
- **Thresholds come in two kinds.** A *hard* threshold gates GREEN. A *calibrating* threshold is
  recorded on the first two runs and becomes hard only once the owner sees the numbers. Each
  calibrating threshold is marked ⚖. Predictions are written before the run, as
  `rimworld-debug-testing` §7 requires.

### 2.2 The ten bars

| # | bar id | kind | assertion and route | PASS predicate | how it could false-pass / false-fail |
|---|---|---|---|---|---|
| 1 | `pyre_plant_distribution_correct` | L+V | On each fresh site, before any tick, census every `Plant`-category thing with `jawa/list_things` (`ThingRequestGroup` Plant, whole map, read `isCompleteList`). Take the allowed set from `jawa/get_def RM_Pyrelands` `wildPlants`, read back at run time, plus ScorchFruit. | **Hard:** foreign plant defs = 0 on all 3 sites. Total plants ≥ 0.85 × plantable cells (bar 4 shares the same census). ⚖ EmberGrass:Quickgrass ratio within 2× of 9.0:3.8 (≈2.4). | **False pass:** an empty or partial list (`isCompleteList` false, or `scanned` = 0). It must also be shown able to see a foreign plant: as a sanity probe, spawn one vanilla `Plant_Grass` and confirm it is counted, then destroy it. **False fail:** neighbour-biome bleed. The tier excludes `biometransitions`, but tile mutators still apply (MixedBiome hands patches to a secondary biome), so mutators must be stripped (§3.4). Edge band: report the four quadrants separately. |
| 2 | `pyre_animal_distribution_correct` | L+V | Same sites, at tick 0 after mapgen: census of factionless pawns with `jawa/list_pawns`. Take the allowed set from live `get_def … wildAnimals` keys. | **Hard:** foreign kinds = 0. Every live wildAnimals key resolves (no null `animal`). ≥ 12 wild animals per site. ⚖ Pooled over 3 sites: ≥ 7 distinct roster kinds seen, `RSW_Gizka` in the top 3 by count (ECOSYSTEM_PYRAMID_LAW_1, "grain = most-seen"), and Spearman ρ(commonality, count) ≥ 0.4. Report ρ, and gate on it only once ⚖ is ruled. | **False pass:** the census reads the colonists' faction or the quest pawns. Filter `faction == null && RaceProps.Animal`. **False fail:** a manhunter or visitor incident during the settle ticks. Disable the storyteller (§3.8). Big species are rare by design, so per-kind presence is never hard. |
| 3 | `pyre_ground_ash_ladder` | L+V | (a) Gen-time terrain census with `jawa/get_terrain_batch`, whole map: the RM_FE ground family is present, and Ash Trace/Light/Heavy are present from the patchmaker. (b) **Burn-down:** on a 20×20 grassed `RM_FE_Ground_Soil` patch, fire → wait for out → regrow → fire, 3 cycles. | **Hard:** (a) stock `Sand`/`Soil`/`Gravel` = 0 cells, RM_FE_Ground_* ≥ 60% of land cells, and at least 2 of the 3 ash rungs present. (b) After cycle 1, ≥ 50% of patch cells are on an ash rung. After cycle 3, ≥ 1 cell is `RM_FE_Ash_Deep`. The screenshot shows the gradient. | **False fail (seen 2026-09-13):** the old suite burned **bare sand with no fuel**. A fire with no fuel goes out and `TryBurnFloor` never fires. Burn **grass on ground**. **False pass:** none of note. |
| 4 | `pyre_grass_chokes_ground` | L+V | Shares bar 1's census. Plantable cells are land cells with fertility > 0, not water, not `RM_FE_Ash_Deep`, unroofed and not under a building. | **Hard:** covered/plantable ≥ 0.85 on every site (the def predicts ~0.96). Judge YES on "the ground is carpeted in grass with no bare-dirt expanses". | **False fail:** sampling after a burn. Census at tick 0. Map Designer is absent from the tier, but if it is present `RM_PyrelandsDensityEnforcer` must have run: read back `plantDensity` = 16 via get_def. |
| 5 | `pyre_embergrass_regrows` | L+V | Clear a 30×30 grassed patch by fire, record the plant count (≈0), then tick. | ⚖ Plant count in the patch ≥ 25% of its pre-burn count by **day 3** and ≥ 60% by **day 7** (`wildPlantRegrowDays` 9, `growDays` 0.8). | **False fail: TEMPERATURE.** Vanilla plant growth factor falls to 0 at about 58 °C and is about 0.3 near 54 °C (**UNMEASURED** for these defs, so read `PlantUtility` through RimSage before the run). The test runs at the **campaign-representative** temperature (§3.5). If grass does not regrow there, that is a **real finding about the shipped world**, never a reason to cool the test tile. Also run one control site at 30 °C so a temperature failure can be told apart from a spawner failure. |
| 6 | `pyre_scorchfruit_produces` | L+V | Spawn `RM_FE_Plant_ScorchFruit` (n = 10) at growth 1.0 with `jawa/set_plants`, designate harvest, and let 1 colonist work. | **Hard:** ≥ 1 `RM_FE_ScorchFruitYield` exists after harvest. When ordered to ingest one, the colonist's food need rises. Also prove the fire route (n ≥ 1 ScorchFruit spawned by a burn within 11,600 ticks, per the old suite, which passed). | **False fail:** at 53 °C the colonist gets heatstroke or an unrelated mental break. Give colonists heat-proof apparel, or time-box the run. The plant **rots in 1.1 days on the stalk** (`daysToRotStart` 1.1): spawn and harvest inside one day. |
| 7 | `pyre_scorchfruit_spoils_fast` | O+L | [O] `RM_FE_ScorchFruitYield` has `daysToRotStart` **4** and the plant has **1.1** (MEASURED from XML), so the plant is faster, as the bar says. [L] Spawn a yield stack outside, unrefrigerated, and tick. | **Hard:** the yield is rotted or destroyed by day 4.5. An unharvested plant is destroyed by day 1.5. | **False pass:** heat accelerates rot in vanilla, so at 53 °C it spoils even faster. That is fine, because the bar is "within days". **False fail:** spawning it inside a cooled room or a stockpile. |
| 8 | `pyre_ashfall_darkens_drifts` | L+V | `jawa/weather_set RM_FE_Weather_AshFall lockWeather`, settle for the weather transition (§3.6), then count `RM_FE_Filth_LooseAsh` over the **whole map** at t = 0, 2500, 5000 and 7500 ticks. Take a luminance screenshot pair: Clear versus AshFall, same camera, same hour. | **Hard:** the ash count increases monotonically and is ≥ 20 at 7500 ticks. Mean frame luminance under AshFall ≤ 0.85 × Clear. Judge YES on "visible ash drifts". | **False fail (seen 2026-09-13):** counting inside a 24×24 rect. Deposits land on `CellFinder.RandomCell(map)` across the whole map, so a 576-cell rect on a 62,500-cell map expects ≈0 hits. Roofed or water cells are skipped. **False pass:** a pre-existing fire dusting ash. No fires may burn during this step. |
| 9 | `pyre_cinderfall_distinct` | D+V | [D] Cinderfall's def differs from AshFall in at least one of: overlay classes, `skyColors*`, particle mote. [V] Screenshot pair AshFall vs Cinderfall under the same conditions. | **Hard:** [D] at least one rendering field differs. Judge YES on "cinderfall is visibly a different weather from the ash-fall frame beside it". **[H]** owner glance at the first GREEN. | **False pass:** two defs that differ only in label. [D] catches it. **False fail:** capturing before the 4000-ish-tick weather lerp has finished (§3.6). |
| 10 | `pyre_blackrain_reads` | D+V | Same as bar 9, for `RM_FE_BlackRain` versus vanilla `Rain`. | Same predicate. The judge statement is "rain that reads as black or dark, not ordinary blue-grey rain". | Same. |

### 2.3 Fixes the existing suite needs (the 2026-09-13 RED, re-read)

1. **`biome_def_wiring`** asked about `RM_FE_Pyrelands`, a defName retired by
   `PYRELANDS_DEFNAME_RENAME_1`. `get_def` may also not serialise `terrainPatchMakers`. Re-target it
   to `RM_Pyrelands`, and fall back to an [O] XML read if the field is not exposed.
2. **`fulgurite_armed_only`** expects the log prefix `[RimMandrake.StarWars.FireEcology]`, but the
   source now logs `[RimMandrake.Pyrelands] fulgurite-spawn`. It passed in September and **will
   false-fail** on the next run. Match on `fulgurite-spawn` alone.
3. **`ash_ladder_escalation`** burned fuel-less sand. Use bar 3's route instead.
4. **`ashfall_accumulates`** counted inside a rect. Use bar 8's route instead.
5. **Static settings fields.** The suite stopped short of toggling because they are static.
   `jawa/mod_settings_field` now exists ("any public field, static OR instance"; closed
   `BRIDGE_STATIC_SETTINGS_FIELDS_1`). The OFF-arm floor checks therefore become possible:
   - toggle off → no effect;
   - toggle on → effect;
   - always restore.

### 2.4 Proposed bar-text changes (for the owner — the hashed section is not edited here)

None of the ten needs rewording to be testable. The predicates above quantify "within days" and
"densely" without touching the prose. Proposed **additions**, all owner-ruled content already in
code:

- `pyre_mapgen_log_clean` — generating a Pyrelands map logs no `CommonalityOfAnimal` NRE and no
  unresolved cross-reference. Its only allowed errors are the 4 documented `burnedDef is flammable`
  config errors. *(This is walk step 1, promoted.)*
- `pyre_burn_line_present` — somewhere on a Pyrelands map a standing burn line exists and moves
  (sheet §5 "the burn exists somewhere, always"; `MapComponent_BurnLine`).
- `pyre_firehawk_carries_ember` — fire-hawks carry burning twigs ahead of the fire and start new
  fires (`CompFireHawkSpread`, `JobDriver_RUT_FireHawkCarryEmber`). ⚠️ Prove it by a **job/state
  read**: a `JobDef` of `RUT_FireHawkCarryEmber` observed, and a new Fire within N cells. **Never**
  by a flight or screenshot hunt (flyer ruling, said three times).
- `pyre_furnacebeast_warmth` — a furnace-beast warms the cells and pawns near it (`CompFurnaceWarmthAura`,
  hediff `RM_FurnaceWarmth`).
- `pyre_burrowers_dive` — burrow-on-fire animals go under ahead of the flame (`RM_Burrowed`).
- `pyre_no_ordinary_rain` — the weather table holds no ordinary rain ([O]/[D]; sheet §6 ban 2).

Also propose **one `### cannot show`** line: `pyre_cannot_vanilla_fauna` — "a hare, rat, gazelle or
any other vanilla-Earth animal on a Pyrelands map". This catches the Replace op silently failing.

---

## 3. Site preparation

Most of the effort goes here, because in this project false REDs have mostly come from the test
site, not the mod.

### 3.1 Mod tier — a new `modset_builder.py` tier, `pyrelands`

- `want`: `[BRIDGE, "mandrake.rm.biomes", "mandrake.rut.patches", "mandrake.rsw.swbestiary",
  "mandrake.rut.pyrelandsmechanics"]`. The last is MEASURED from
  `src/RimUtinni/PyrelandsMechanics/About/About.xml`, which itself depends on `mandrake.rut.patches` and
  `mandrake.rm.biomes`. Add `dlc: True`: all five expansions, always, by owner
  ruling. Transitive dependency closure comes from `modset_builder`.
- **Exclude explicitly:**
  - `m00nl1ght.geologicallandforms` and its `biometransitions` module (neighbour bleed);
  - `zylle.mapdesigner` (rewrites `plantDensity`);
  - `kopp.biomecompatibilityproject`, `sarg.alphabiomes` and any mod whose `AdditionalWildPlants`
    injects flora.

  The pre-flight asserts their absence through `jawa/mod_inventory`.
- **Why the swbestiary entry is load-bearing:** §1.3's inert `MayRequire`. Without it, seven
  wildAnimals keys dangle and GenStep_Animals NREs.
- The **full-list** rung (GREEN full) instead uses `ModsConfig.FULL.LATEST.xml` (614 mods) and
  accepts that biometransitions is present. On the full list, bars 1, 2 and 4 are censused **only
  on the interior tile of a ≥ 2-ring Pyrelands patch**, and bleed is diagnosed with the quadrant
  split. ⛔ Never run `start_debug_game_ready` on the full list (skill §1: it has crashed the
  process). The full-list site comes from a full-list boot to menu, then **loading the trial-site
  save** made on the tier (§3.4). **UNMEASURED:** whether a tier-made save loads cleanly on the full
  list. If not, the full-list site is made from a campaign-independent new colony built through the
  menu. That needs the owner present (owned by the full-list child item).
- `modcheck run` **rewrites the live `ModsConfig.xml`** (CLAUDE.md). The trial never calls it.
  The driver applies the tier with `modset_builder.py --tier pyrelands --apply`, with the game
  closed and only under the bridge lock.

### 3.2 Deploy freshness

The pre-flight refuses on any mismatch:

1. **Compose current:** `deploy_custom_mods.py --compose biomes` (plan only) reports **0 changes**
   against `Mods/RimMandrake.Biomes`. Same for `--mod UtinniPatches` and for PyrelandsMechanics.
2. **DLL stamps:** for each of `FireEcologyHook.dll`, `RimMandrake.Biomes.dll`,
   `RimMandrake.Utinni.PyrelandsMechanics.dll` and the UtinniPatches DLLs, the deployed `.srchash`
   equals the repo's `.srchash`, and the repo's `.srchash` equals `dll_source_stamp.py` recomputed
   on the source.
3. **Loaded, not just on disk:** `jawa/mod_inventory filter=biomes` lists `mandrake.rm.biomes` with
   `FireEcologyHook` among its loaded assemblies. Disk truth is not runtime truth.
4. **Defs as loaded:** `jawa/get_defs` for `BiomeDef/RM_Pyrelands`, the 15 PawnKindDefs, the 3
   plants, 3 weathers, 4 ground terrains and 4 ash terrains. Read `success`/`foundCount`/`notFound`;
   a failed call is UNMEASURED, never ABSENT. Record a **def fingerprint**: a sha of the sorted
   `(defName, modContentPack)` pairs. Store it with the run, so a later GREEN can be tied to the
   exact content.
5. The game must have started **after** the newest deploy mtime of any of those files. Otherwise
   the defs in memory are older than the disk (skill `rimworld-live-review`: "restart the game").

### 3.3 Mod Settings and toggles

- Read every `RM_PyrelandsSettings` field with `jawa/mod_settings_field`, plus
  `RM_BiomesSettings.Enabled("Pyrelands")`. **Assert shipped defaults:**
  - all features ON;
  - `crossBiomeEnabled` and `crossBiomeEverywhere` false;
  - `ashfallRateMultiplier` 1;
  - `scorchFruitMapCap` 40.

  A stale `Mod_*.xml` in the Config folder from an earlier session would otherwise silently change
  the experiment.
- Floor arms set a toggle, act, read back and restore. **The restore runs in a `finally`**, and the
  post-flight re-asserts defaults.
- **UNMEASURED:** whether toggling a static field mid-session affects already-running
  MapComponents. Each OFF-arm must assert on behaviour, not just the field value.

### 3.4 How the Pyrelands map is obtained — without painting Ash'karr

The biome holds 0 tiles on today's planet, which is expected (CLAUDE.md), and nothing here touches
the campaign world. The site is a **scratch quicktest world** on the `pyrelands` tier:

1. `rimworld/go_to_main_menu` (if needed), then `rimworld/start_debug_game_ready` with
   `readiness=mapData` and a long timeout. Poll `get_ui_state` until it reads `Playing`. Use
   `prove_quicktest_world.py`'s pattern. Never retry on a timed-out socket.
2. **Choose the site tile** with `jawa/world_tile_get` and `world_neighbors`:
   - a land tile at least 10 tiles from the quicktest colony;
   - flat or small hills;
   - no river, no coast, no road, no landmark;
   - every tile within **2 rings** also land and non-water.
3. **Re-tile** with `jawa/world_tile_set` on the centre and 2 rings (≈19 tiles): set biome
   `RM_Pyrelands`, temperature, rainfall 0, elevation ~257, hilliness flat. Write the temperature
   **before anything reads that tile**: `Tile.MinTemperature`/`MaxTemperature` caches never
   invalidate (world-editing skill, trap 2).
4. `jawa/world_mutators_set` → **clear every mutator** on the centre tile. MixedBiome-family
   mutators hand map patches to a secondary biome (`WildPlantAllowlist.cs` header). Then
   `jawa/world_commit`.
5. `jawa/world_tile_map_generate tile=<c> sizeX=250 sizeZ=250`. It now finalizes the map itself
   (`BRIDGE_MAPGEN_STALE_FINALIZE_1`). Assert `success`, `mapSize`, `failedSteps == []`.
6. **Make it a home map:** spawn 3 colonists (`faction:"PlayerColony"`), otherwise stepping time
   culls it. Then `jawa/set_current_map`.
7. **Assert the site** via `jawa/map_info`:
   - `map.Biome == RM_Pyrelands`;
   - tile mutators empty;
   - the size is right;
   - the temperature matches the target within ±3 °C (`jawa/cell_temperature` at 3 cells).
8. **Freeze the census at gen** (bars 1, 2 and 4 read here, before any tick).
9. **Save** as `NS_Pyrelands_site_<k>_<fingerprint>.rws`. Back up `Saves/` first and stat
   afterwards (CLAUDE.md: `save_game` has written the wrong slot). Then
   **`load_game_ready` that save**. This is the one reliable entry path, and it cures the
   "pure-black generated map" render. Every [V] bar is captured only on the **reloaded** site.
10. Do steps 2–9 for **K = 3** tiles. Sites 2 and 3 can come from the same quicktest world: three
    separated tiles, three maps, one map current at a time. Reloading site *k* for the fire bars
    reuses the fixture. A changed def fingerprint invalidates all fixtures.

**UNMEASURED:** whether `world_tile_map_generate` on a re-tiled scratch tile honours
`extraGenSteps` (`RM_FE_ScorchRuins`) and `preventGenSteps`. The census reads the log for the
genstep's line as a by-product.

### 3.5 Climate, latitude and heat kind

- **Latitude:** choose site tiles at |lat| ≤ 25°, the hot band, and record each tile's
  latitude. **Heat kind:** record the would-be heat kind as `overhead` (sun +56° median). No
  Pyrelands-specific heat logic exists or may be added (the one-heat ruling). When
  `SOLAR_HEAT_EXPOSURE_1` lands, add a bar for it then.
- **Temperature:** set the tile mean to **50 °C**, inside the campaign's 39–65 range and near its
  53.6 median. Record the actual map temperature at each sampling instant. Also set up **one
  control site at 30 °C**, used only to tell temperature from mechanism on bar 5 and never for
  GREEN.
- **Season and time of day:**
  - set the date to mid-summer for the hemisphere (`time_set_ticks`, which simulates nothing);
  - before any [V] capture, set the hour to **11:00–13:00**, so night darkness never reads as
    "AshFall dims the map";
  - luminance pairs use the same hour.
- **Colonists:** heat-proof apparel or a cooled tent. They must stay alive. Downed or dead
  colonists un-home the map, which is then culled (live-review §3).

### 3.6 Weather, fog, settle and speed

- **Lock** the weather to Clear during census, fire and growth steps. That stops
  `DryThunderstorm` lightning (fulgurite, random fires) and BlackRain (it extinguishes fire) from
  contaminating the result. Unlock only for the weather bars.
- **Weather transition:** after `weather_set`, settle **≥ 4,000 ticks** before a [V] capture
  (**UNMEASURED** constant; read `WeatherManager.TransitionLerpFactor` through RimSage). Assert
  `jawa/weather_get` shows `curWeather == target` and `transitionProgress == 1`.
- **Fog:** `jawa/set_fog` off on the site (never `unfogAll`, which wedges the game).
- **Settle before sampling:**
  - gen census at tick 0, with no settle;
  - behaviour bars run after **500 ticks** of settle, so MapComponents have initialised and the
    first `TickLong` has passed.
- **Speed:** `jawa/time_pin_normal_speed` off; drive time in **≤ 2,000-tick `step_game_ticks`
  chunks**, because a bigger step times out and a timeout poisons the socket. On a timeout, open a
  new connection and poll; never retry on the dead one.
- **Tick budget per site:**

  | step | ticks |
  |---|---|
  | census | 0 |
  | bar 3 | 3 × (burn ~2,500 + regrow ~60,000) ≈ 190 k |
  | bar 5 | 7 days = 420 k |
  | bars 6–7 | ~270 k |
  | bar 8 | 12 k |
  | bars 9–10 | 10 k |

  ⇒ **≈ 900 k ticks per site.** Run the long bars (3, 5, 7) on **site 1 only**. Sites 2 and 3
  carry the statistical gen census (1, 2, 4) only.
- **Stale modals:** before every phase, `jawa/window_list_close`, and assert there are 0 open
  dialogs. Suppress the log auto-open (`jawa/log_autoopen_suppress`). One stale modal blocks every
  later call (memory: stale-modal).

### 3.7 RNG and isolation

- Record `Find.World.info.seedString` and each site's tile ids. That makes a failing site
  reproducible from its fixture save, but it is not used to tune.
- **Isolation:**
  - the storyteller is set to a no-incident storyteller (`jawa/storyteller_swap`) and the incident
    queue is cleared (`jawa/incident_queue_clear`), so there are no raids, manhunters or eclipses;
  - `fireClockEnabled` stays ON, because it is a Pyrelands feature, but its incidents are logged
    and a fire raid during a census voids that site.
- **Furnace-herd world migration** (`furnaceWorldMigrationEnabled`) may walk herds onto the map.
  The census subtracts pawns whose `spawnedTick > 0`. Gen census is at tick 0 anyway.
- **Pyrelands mechanics that start fires** (the burn line, fire-hawks) are on by default. During
  bars 1, 2, 4 and 8, `burnLineEnabled` and `fireHawkSpreadEnabled` are toggled off via
  `mod_settings_field` and restored afterwards. Otherwise the map is burning while it is being
  measured.

### 3.8 Pre-flight script — refuses a dirty site

`northstar_driver` runs `preflight(pyrelands)` and **exits non-zero naming the first failed
precondition**. In order:

1. The bridge lock is held by this seat (`rimflow bridge who`).
2. `Player.log` was opened after the newest deploy mtime.
3. `mod_inventory`: the tier's packageIds are present, the excluded ones are absent, and all five
   DLCs are active.
4. `.srchash` agrees across source, repo and deployed (§3.2).
5. `get_defs` finds all of §3.2 item 4, and the def fingerprint is recorded.
6. The Mod Settings are the shipped defaults (§3.3).
7. The log since load contains no `CommonalityOfAnimal`, no `Could not resolve cross-reference`
   naming a roster key, and no `Exception` from `RimMandrake.Pyrelands`. The only allowed errors
   are the 4 `burnedDef is flammable` lines.
8. Site assertions (§3.4 step 7): biome, mutators, size, temperature, latitude.
9. Weather is locked and reads back. Fog is off. 0 dialogs. The game is paused.
10. The storyteller is quiet and the incident queue is empty.
11. ≥ 3 living colonists, none downed.
12. `loadavg` < 10 (do not eat the owner's frames).

Each check returns `{name, ok, observed, expected}`, and the whole set is written into the run's
evidence JSON.

---

## 4. Run sequence and wall-clock

All of it runs under Windows `python.exe` (the bridge is unreachable from WSL), with the
`BENCH`/`FOUNDRY` bridge lock and the game announced to the owner.

| phase | what | wall-clock (estimate, UNMEASURED unless stated) |
|---|---|---|
| 0 | Offline: [O] reads, `northstar.parse`, lint `shows=` coverage (`floor.uncovered_shows` = []) | < 1 min |
| 1 | Close the game; apply the `pyrelands` tier; cold-load | 1–4 min (13-mod minimal list is 22 s MEASURED; the full biomes mod plus UtinniPatches plus swbestiary closure is bigger) |
| 2 | Pre-flight (§3.8) | < 30 s |
| 3 | Quicktest world (78.5 s MEASURED on 580 mods; less on a tier) | ~1–2 min |
| 4 | 3 sites × (re-tile, generate, census, save, reload) | ~3 × 1.5 min |
| 5 | Site 1 behaviour bars: 3, 5, 6, 7, 8, 9, 10 (~900 k ticks at ≈1–2 k ticks/s on a near-empty tier) | ~8–15 min |
| 6 | Floor OFF-arms (6 toggles × short act) | ~3 min |
| 7 | Post-flight: restore defaults, release the bridge, `judge` pass over screenshots (`claude -p`, ≤ 180 s each × ~10) | ~5–15 min, offline |
| 8 | Report → `Transient/modcheck/Pyrelands_<ts>.html` and summary JSON | < 1 min |

**≈ 25–45 min for a minimal-list GREEN attempt.** The full-list rung adds one ~15 min cold load
(MEASURED 2026-09-07 on 599 mods).

---

## 5. Gaps blocking SHIPPED

| gap | state | owner of the fix |
|---|---|---|
| **Re-validation of all 10 bars** (plus the §2.4 additions if he takes them) | owner's word needed; only 2 are validated | BENCH card → `modcheck validate Pyrelands --owner-said` |
| `shows=` wiring + suite fixes §2.3 | 0/10 | FOUNDRY |
| **Art: `RUT_Ashwallow` has NO texture** | **MEASURED**: texPath `Things/Pawn/Animal/Pyrelands/Ashwallow/Ashwallow`. No file in the repo, no folder in the deployed `UtinniPatches/Textures/…/Pyrelands/`, no artpipe job found. It renders as the missing-texture error. | art queue (search `_artsrc`/`done` first, per the art-reuse rule) |
| **Art: `RUT_Emberscythe` on PLACEHOLDER vanilla Megascarab art** | **MEASURED** (its XML says "Art: PLACEHOLDER"). `emberscythe_v1_{east,north,south}` already sit in `infrastructure/artpipe/done/`, so check whether the owner ruled on them before queuing any regen | art |
| Art: Barbslinger scorpion redesign | open, `BARBSLINGER_SCORPION_REDESIGN_1` | art |
| Art: FireHawk flight flip-book | frames exist (`FireHawk_Flying_1..5_*`, MEASURED in the repo). The live visual check needs the owner present (`FIREHAWK_FLIGHT_BEHAVIOR_1`) | joint session |
| **Code review** | **MEASURED** `code_review_status.py check`: Pyrelands `Source/` has 6 DIRTY .cs files (`RM_PyrelandsMod.cs`, `RM_JobGiver_BurrowOnFire.cs`, `RM_JobDriver_Burrow.cs`, `RM_BurrowOnFireExtension.cs`, `PyrelandsTuning.cs`, `PyrelandsMechanicsDefOf.cs`); the other 20 are CLEAN. `validation.py` is CLEAN (it will dirty on wiring). The 8 PyrelandsMechanics .cs are CLEAN. `BiomesShell/RM_BiomesMod.cs` is DIRTY. UtinniPatches' Pyrelands XML is UNMEASURED (the tool covers code) | `DIRTY_CODE_REVIEW_STANDING_LOOP_1` |
| **Mod Settings "superb"** | 20+ toggles and sliders exist (MEASURED). Owed: the per-biome toggle gates **worldgen only** (Wave 0 note in `RM_BiomesMod.cs`); one-line mechanic gating on `RM_BiomesSettings.Enabled("Pyrelands")` is still owed. Also needed: confirm every toggle is labelled, with worldgen-affecting ones marked as such (`MOD_OPTIONS_RETROFIT_1`) | FOUNDRY |
| Packaging header/`list:` stale (§1.1) | stale | rung W |
| `PATCH_MAYREQUIRE_GUARD_INERT_1` instance in `WildAnimals_Pyrelands.xml` | inert guard ×2 | note on that item |

⛔ **Not gaps:** 0 world tiles on Ash'karr (expected until the one painting pass), and missing DLC
fallbacks.

---

## 6. Template — what generalises to the other ~20 biomes

1. **Packaging first.** Read `Biomes.compose.json`: a composed entry is tested as
   `mandrake.rm.biomes`. Fix the walk's `subject:`/`list:` lines outside the hash.
2. **Hash before anything.** `northstar.parse()` the walk and bisect the hash per commit. "Declared
   VALIDATED" is not VALIDATED.
3. **Roster from the PatchOperation xpath.** Watch for Replace-then-Add sequences and top-level
   `MayRequire`s; every inert guard becomes a tier requirement.
4. **One tier per biome:** `mandrake.rm.biomes` + `rut.patches` + whatever the roster's keys
   resolve into, with biometransitions, Map Designer and flora injectors excluded.
5. **Site recipe §3.4, unchanged:** a scratch quicktest world → re-tile a 2-ring patch → strip
   mutators → generate → home it → census at tick 0 → save → reload → [V] on the reloaded copy.
   K = 3.
6. **Temperature at the campaign value from the biome sheet's §0,** plus one control site.
   Latitude band and heat kind recorded.
7. **Generic bars every biome gets:** plant purity + coverage, animal purity + pyramid-rank,
   mapgen log clean, terrain family present, weather table matches the ruled bans.
   Biome-specific bars sit on top.
8. **Suite hygiene:** count over the whole map unless the mechanism is local. Give fire fuel. Read
   `isCompleteList`. Sanity-probe every census with a planted foreign def.
9. **Pre-flight is shared code** with a per-biome dict of expectations: defs list, settings
   defaults, allowed log errors, target temperature and latitude.

---

## 7. Requirements on the shared driver (`src/RimMandrake/Utils/northstar_driver/`)

Listed here, not built here:

1. **Session.** A persistent socket with auto-reconnect and post-condition polling. After a timeout,
   never resend: reconnect and poll the post-condition. Every call returns parsed JSON and checks
   `success`.
2. **Long ops.** `start_debug_game_ready`, `load_game_ready` and `save_game` as
   fire → reconnect → poll `get_ui_state` / `list_pawns`, with a timeout budget.
3. **`advance(ticks)`.** Chunked `step_game_ticks` ≤ 2,000, with an optional `every=N` callback
   for time-series sampling and a wall-clock budget. It reports achieved ticks/s.
4. **Site builder.**
   - `make_site(biome, ring=2, temp, rain, elev, hilliness, lat_band, size)` → tile id, map id;
   - `save_fixture(name)` with `Saves/` backup and stat verification;
   - `load_fixture(name)`.
5. **Census primitives.**
   - `plants(map)` → `{def: count}` plus quadrant split plus `isCompleteList`;
   - `wild_animals(map)` → `{kind: count}`;
   - `terrain_hist(map)`;
   - `things(def, rect|map)`.

   Each refuses on `scanned == 0`.
6. **Def read-back.** `defs(type, names)` returns found and notFound, and refuses on
   `success:false` (never reads it as absent). Plus `def_fingerprint()`.
7. **Settings.** `get/set/restore_settings(class, fields)` via `jawa/mod_settings_field`,
   restored in a `finally`.
8. **Environment.**
   - `weather(def, lock, settle_until_transition_done)`;
   - `fog_off()`;
   - `set_hour(h)`;
   - `quiet_storyteller()`;
   - `close_dialogs()`;
   - `log_since(mark)` with an allowlist.
9. **Fire.** `burn(rect)` with grass-present assertion, and `wait_fire_out(rect, budget)`.
10. **Evidence.** `screenshot(name)` with the camera on a rect at a fixed zoom; `luminance(png)`;
    the run JSON in the `modcheck` summary schema, with `shows` per component, so
    `modcheck.judge`/`report` consume it unchanged.
11. **Pre-flight framework.** It runs §3.8-style checks from a per-biome spec and writes them into
    evidence.
12. **Platform.** Pure python.exe-safe: no WSL paths, `tr -d '\r'`-safe outputs. Never touches
    `ModsConfig.xml` except through `modset_builder --apply` with the game closed.

---

## 8. GPT review

*(filled after the Codex review — see below)*

---

## 9. Tickets

- `PYRELANDS_NORTHSTAR_TRIAL_1` — parent (FOUNDRY), carrying the whole trial to SHIPPED.
- Child items, one per rung: see the parent item for the list and acceptance criteria.
