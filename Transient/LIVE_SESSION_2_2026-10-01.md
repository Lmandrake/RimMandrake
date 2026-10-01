# FOUNDRY live session round 2, 2026-10-01 (owner AFK, authorized by card 2026-10-01)

## Deploy
Deployed `origin/main` = `7caa6b5c9` from the private worktree `D:\Luke\dev\RimMandrake-wt-livedeploy` (game down):
`deploy_custom_mods.py --apply` (44 files) and `--compose biomes --apply` (80 files, "VERIFIED in sync").
Re-plan: no `+`/`~` lines left in either plan; only `-` game-only extras (kept). Plans: `Transient\livesession2_20261001\plan_after*.txt`.
Moved aside (not deleted) to `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\_aside_forsakencrags_20261001\`: five game-only
ForsakenCrags files orphaned by the Abyss rename (`a534284e4`). The SWBestiary pair duplicated both defNames of their `_Abyss` successors
(would have logged duplicate-def errors and muddied the load-safety read). `RimMandrake.Biomes\Biomes\ForsakenCrags` is not in
`loadFolders.xml`, so it does not load and was left. `RSW_SandSwimmer_Items.xml` and three `RM_Qorrax` textures left in place as in round 1.

## Decision strings (written before launch)

| check | string / read | pass | fail |
|---|---|---|---|
| load alive | `Bridge token:` | present | `Recovered from incompatible or corrupted mods`, `Caught exception while loading play data`, `Resetting mods config` |
| FIX1 load def errors | log: `Exception parsing RimWorld.TreeCategory from "Standard"`, `doesn't correspond to any field in type StartingHediff`, `animal has trainability = null`, `tries to use meat from Megascarab`, `No Verse.BodyPartGroupDef named FrontLegs`, `No textures found at path Things/Plant/RM_`; get_defs ThingDef/RM_KneelOllim | 0 hits each; KneelOllim foundCount 1 | any hit; notFound |
| FIX2 oorrik | log `No Verse.BodyDef named Rat`; spawn_pawn RM_Oorrik x3; `Error while generating pawn` + RM_Oorrik | absent; 3 spawned ok; none | present / spawn fails |
| FIX3 funnel | swimmer kill on Sand -> list_things RM_Filth_DisturbedSand near victim cell; letter text contains "struck" | >=1 | 0 |
| FIX4 soorrak | 5000 ticks with wild RM_Soorrak x several: `Exception ticking RM_Soorrak` / `Notify_JobStarted` NRE count in log delta; job sampled every 500 ticks | 0; job list recorded | >0 |
| FIX5 rimplace | log after Stillsand regen: `GenStep_RimplacePlan.Generate` NRE, `not found under any running mod` | absent | present. Note: proves only if a RimplacePlan genstep actually ran (positive log line needed, else UNMEASURED) |
| gale | dev-fire `RM_DuneGale`; log `[Stillsand] dune gale ended on` with non-zero delta; emergence letter; RM_DustDevil spawn moves + despawns | line present, delta != 0; dust devil position changes, later gone | absent / zero |
| event creatures | dev-fire `RUT_KraytAttack`, `RM_MuurrokEmergence` on Stillsand -> pawn of kind on map; on non-Stillsand map the incident refuses | pawn present; refusal | no pawn |
| precious caves | per Stillsand regen: `[Stillsand] precious cave:` / `precious cave roll:` lines | present on >=8/10 maps with rock | absent |
| sun | needs a ShadeGrid reader tool | tool exists -> read | no tool -> UNMEASURABLE |
| dead gates (9290b46db) | after load: first exception, every `Could not resolve cross-reference` and `Config error` line attributed to file; compare to round-1 `Player.load.log` | no new error naming a newly ungated def/ext (RM_SunHeatExtension, RM_SandSwimExtension, RM_PinnedSunExtension, RM_ShadeClothExtension, RM_FalseShadeExtension, CompProperties_FalseShadeAmbusher, the Rot fungi, RM_Sheen*, RM_DuneCrawler, RM_RustPuff, RM_Qorrax, RM_Nogtyl) | any such error / def discarded |
| smoke | get_defs ThingDef/RM_ChillCryoponicsVat, RM_ChillFloorBed, the five Contagion limbs, CrackedLands recede-feast comps, Cauldron nettles; `Config error` naming them | success, foundCount = asked, no config error | notFound / error |

## Results

### Load (cold, full list, 611 active, launched via Steam 03:06, `Bridge token:` 03:30) — log: `Transient\livesession2_20261001\Player.load.log`
- No load abort. Crossref + config-error lines: 124 (round 1: 133). **0 new** vs round 1; 9 gone, and they are exactly the round-1
  Stillsand defects (`errs_gone_vs_round1.txt`): Liikka/Veessa/Zuurrik Megascarab meat, Loomma/Vaalok trainability, `BodyDef Rat`,
  `FrontLegs`, `RM_KneelOllim` crossref, `TrainabilityDef Simple`.
- FIX1 strings: TreeCategory 0, StartingHediff 0, trainability null 0, Megascarab meat 0, FrontLegs 0; `No textures found at path Things/Plant/RM_`
  is 67 lines (round 1: 94) but **0 for any of Contagion's 12 plant texPaths**; the rest are other biomes' plants (Greentide trees, WeepingStones, ...).
  get_defs ThingDef/RM_KneelOllim found.
- FIX2: `No Verse.BodyDef named Rat` 0.
- First exceptions: two `Default constructor not found for type System.String` (line 75, 688; not ours, pre-existing), then
  `Exception in ConfigErrors() of RM_TheSump` NRE (pre-existing in round 1; TheSump biome held in DEPLOY_HOLD, LOAD_ERRORS_DEF_FIELDS_1),
  GiddyUp `same key ... RSW_VentStalker` in `BiomeDef.CommonalityOfAnimal` (pre-existing in round 1).
- Dead gates (9290b46db): no error line names any newly ungated def/extension. **Positive read** (`getdefs_ext.json`): RM_Stillsand now carries
  RM_SunHeatExtension + RM_PinnedSunExtension; RM_LongShade both; RSW_KraytDragon/GreaterKraytDragon/SandStalker carry RM_SandSwimExtension;
  RM_Mirrak carries RM_FalseShadeExtension + CompProperties_FalseShadeAmbusher. So the patches now apply and loaded clean.
- Smoke (`getdefs_smoke.json`, success true, 41/42; the miss was my wrong defName RM_IrqitTarruq, real `RM_Irqit` found 2/2): Chill vat/bed,
  the five Contagion limbs (HediffDef RM_PillarArm/Lash/Eyeburst/CaudalSpring/Bellows), RM_IrqitFloodBorn, RM_RavenNettle, the Rot fungi,
  RM_Sheen* weathers, RM_DuneCrawler/RustPuff/Qorrax/Nogtyl all resolved. No config error names them. Art gaps (not load errors):
  `Things/Plant/RM_RavenNettle/RM_RavenNettle_a` missing; RM_GenomeSample texPath `Things/Item/Special/Genepack` missing.


### Quicktest map (`start_debug_game_ready` 03:31 -> Playing 03:33)
- Rolled tile 56131 (lat 61.9, LargeHills) as RM_TheRot: generated with no exception of ours (bonus for the Rot fungi gates).
- `world_tile_set biome=RM_Stillsand temperature=48` + `Regenerate Current Map` -> mapBiome RM_Stillsand; 3 colonists planted; hostiles destroyed.
  Regen logged zero errors.

### FIX5 RimplacePlan (`rimplace_run.json`)
- `jawa/run_genstep RSW_GenStep_WhisperSarlaccSign` (a GenStep_RandomSelector whose only option is an inline GenStep_RimplacePlan,
  i.e. the null-def path the fix targets): `threw null`, no NRE, no `not found under any running mod`. Positive: the plan's three
  `SculptureSmall` THING rows were made (log `MakeThing error: SculptureSmall is madeFromStuff but stuff=null. Assigning default.` x3).
  **PROVEN.** Side defect: the plan file's THING rows carry no stuff for a stuffed def (filed).

### FIX2 Oorrik (`t1.json`)
- `spawn_pawn RM_Oorrik count 3` -> 3/3 spawned, alive and moving 5,000 ticks later; no `Error while generating pawn`, no `BodyDef named Rat`. **PROVEN.**

### FIX3 funnel (`t1.json`)
- Sand pad, 3 vekka -> player chicken forced AttackMelee pairs. Two takes: letters `Taken under: Cassandra` (tick 317), `Taken under: Victor`
  (906); `RM_Filth_DisturbedSand` at (26,31) and (26,35), exactly both victim corpse cells. The third chicken died at tick 1 in a
  `Roof collapse` caused by painting/clearing over rock (setup artefact). The letter body text was not read (letter_list field), so the
  "struck it down" wording is UNMEASURED. Funnel bar **PROVEN**.

### FIX4 Soorrak (`t1.json`, `t2.json`, `t3.json`)
- 6 wild RM_Soorrak spawned; 5,000+ ticks; log since spawn: 0 `Exception ticking RM_Soorrak`, 0 `Notify_JobStarted`, 0 NRE. **PROVEN** (no NRE).
- 4 of 6 left the map within 700 ticks without a corpse (consistent with `canLeaveMapFlying`, the def's designed drinking trip; not verified
  as flight, and no readable sign is shown to the player).
- **Job list: the 2 remaining soorraks read `Wait_MaintainPosture` at every sample** (10 samples 500 ticks apart, 25 samples 4 ticks apart,
  12 samples 7 ticks apart) and never moved a cell over 5,000+ ticks, while oorriks/vekkas on the same map read `Wait`/`RM_ShadeDash` and moved.
  Engine (`Pawn_JobTracker` ~l.461): Wait_MaintainPosture is the 1-tick filler started after a job SUCCEEDS with the pather idle. Seeing it
  at every sample means the soorrak's next job also succeeds at once, every cycle: the instantly-ending job the item warned of. Which
  JobDef it is cannot be read (only the filler is ever current). Both carry Heatstroke 0.037. Filed as a separate defect.

### Dune gale (`t4.json`)
- `fire_incident RM_DuneGale` (canFireNow true) -> letter `Dune gale`, condition RM_DuneGale 107,569 ticks. Ended it (expires next tick) ->
  log `[Stillsand] dune gale ended on Map-1-PlayerHome: dune field mass 3.2 -> 3.2 (delta +0.0); cells moved past 0.20: 0; ...` + one letter
  `A caravan the dune took` (a zero-tick gale, expected zero).
- `game_condition start RM_DuneGale 6000`: weather RM_DuneGaleHerald (~4,000 ticks) -> RM_DuneGale; at end the log reads
  **`[Stillsand] dune gale ended on Map-1-PlayerHome: dune field mass 3.2 -> 7.6 (delta +4.4); cells moved past 0.20: 11; carried 0, abraded 10, stunned 0`**
  and exactly one emergence letter `A sealed cache` (tick 11386). Its four named things are on the map at the exact table counts
  (ComponentIndustrial 4, Silver 120, MedicineIndustrial 3, Steel 30) but at the extreme map corner (248-249, 0-1). Observation, not filed:
  the dune field is tiny (mass 3.2 on 62,500 cells) so the erosion face may genuinely sit there.
- Carried pawns: carried 0, so the drag-line / Carried-off / return bars were not exercised. UNMEASURED.
- Exposure ~0.2 during the gale: no ShadeGrid reader. UNMEASURABLE.
- `RM_DustDevil` spawned at (100,100): moved (96,100) -> (78,115) over 2,000 ticks, then gone; `list_things defName=RM_DustDevil` empty; no
  exception. PROVEN.

### Event creatures (`t5.json`-`t14.json`)
- Wild krayt: none on this map; BiomeDef wildAnimals is not readable through get_defs (non-public). UNMEASURED.
- `RUT_KraytAttack` and `RM_MuurrokEmergence` fired on Stillsand: letters `Krayt dragon` and `A line of glare` (tick 15000); RM_Muurrok on the
  map after ~1,000 ticks, RSW_KraytDragon after ~2,000. Both submerged sand-swimmers. Note: `fire_incident dryRun` said canFireNow=false
  for both BEFORE firing (unexplained; forcing ignores it), so the Visits read via the HasVisitFrom gate is not separable. Visits UNMEASURED.
- Muurrok beam: refused (`IsStillUsableBy` false) under RM_DuneGale and under Sandstorm weather; accepted under Clear. **Accepted 4 times with
  no exception in Player.log, but it damaged nothing**: one moving muffalo and three downed (stationary) muffalo 12 cells away on a cleared
  gravel pad, Clear weather, 270 ticks per cast: no `Burn` (RM_MirrorGlare's hediff) on any target or any pawn on the map. FAILED (filed).
- Take on sand: muurrok took a colonist: letter `Taken under: Perroford` (25955), `RM_Filth_DragMark` line (124,121)->(126,118), a 3x3
  `RM_Filth_DisturbedSand` funnel at (125-127,117-119); the muurrok then left the map (dive). The dive message is not state-readable. PROVEN.
- Settings panel listing: UI, not state-readable. UNMEASURED.
- Long Hunger: `RUT_LongHungerSurfaces` dryRun canFireNow=false on this map; not forced. NOT DONE.

### Sun side-observation
- Colonists in open sun on the 48 C Stillsand carry `RM_GlareBlind` (Human86069, Human86072); they are non-Jawa. Supports the glare-blind
  gain bar only; the goggles/Jawa halves were not run.

### Precious caves (`caves.json`)
- 10 RM_Stillsand maps: the home quicktest + 9 made with `jawa/world_tile_map_generate` on hilly land tiles 56053-56098 (set to
  RM_Stillsand, 48 C), each removed after reading. 10/10 log `[Stillsand] precious cave:` and `precious cave roll:`. Mouth facing-away
  dot 1.00 on 8 maps, 0.86 and 0.71 on the two whose outcrop is "as generated". Every cave is in a named yardang (rock).
  Rolls: Seep 6, SealedCache 2, Taken 1, GuzzkaLair 1.
- Guzzka lair map regenerated: `RM_Guzzka` at (199,83) on `RM_GuzzkaEggFertilized` at (199,82). PROVEN.
- `Rock island` letter once on the home map (tick 120); body (outcrop + bearing) not read. UNMEASURED.
- The only error on these maps: `MineralsFramework.ThingDef_StaticMineral.settlementDistProbFactor` NRE (third-party; maps made by tool).

### Long Hunger
- `RUT_LongHungerSurfaces` force-fired on the Stillsand map: letter `The Long Hunger surfaces`, no exception. (Colony then Game Over:
  all colonists were downed by 48 C heat and the krayt/muurrok.)

### Sun
- SHADEGRID_BRIDGE_READER_1 is unbuilt; nothing reads ShadeGrid/PinnedSun. Every cave line says `sun from pinned sun`. A SolarGenerator
  on the LargeHills map read 0 W (probably under mountain roof; inconclusive).

Game closed (force-kill after save-less session) and bridge released 03:58. Session log: `Transient\livesession2_20261001\Player.session.log`.

## Verdicts
| item | verdict |
|---|---|
| STILLSAND_FIXES_LIVE_PROOF_1 | PARTIAL (verify partial): fixes 1, 2, 4 (no NRE), 5 PROVEN; 3 funnel PROVEN, letter wording UNMEASURED. Not closed |
| STILLSAND_DUNE_GALE_LIVE_1 | PARTIAL: log line with delta +4.4 / 11 cells, one emergence letter + its things, dust devil PROVEN; exposure UNMEASURABLE; carry/return not exercised |
| STILLSAND_EVENT_CREATURES_LIVE_1 | FAILED (verify fail): beam does no damage (MUURROK_BEAM_NO_DAMAGE_1). Fire on Stillsand / refuse elsewhere, take + dive, Long Hunger fire PROVEN |
| STILLSAND_PRECIOUS_CAVES_LIVE_1 | PARTIAL: 10/10 caves, all mouths away, guzzka on clutch PROVEN; Rock island letter body UNMEASURED |
| STILLSAND_SUN_LIVE_VERIFY_1 | UNMEASURABLE (no ShadeGrid reader) |
| 9290b46db dead gates, load safety | PROVEN: 0 new crossref/config errors vs round 1; extensions now present on RM_Stillsand, RM_LongShade, krayts, sand stalker, mirrak |
| Smoke: Chill vat/bed, 5 Contagion limbs, recede feast, Cauldron nettle | PROVEN loaded clean; art gap RM_RavenNettle texture, RM_GenomeSample texPath |

Filed: MUURROK_BEAM_NO_DAMAGE_1, SOORRAK_INSTANT_JOB_LOOP_1, RIMPLACE_STUFFLESS_THING_ROWS_1.
