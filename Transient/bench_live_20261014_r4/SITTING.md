# BENCH live round 4 — ratchet pilot at ONE HEAD, 2026-10-14/15

HEAD **1cf47d90ee** (re-exported before any deploy: the perf investigator landed cf73c55411 UtinniPatches fixedLeaderKinds,
53595b2d45 companion own-preset, 9a4852f50a clockgate harness fix; all included). git archive -> ext4
`/home/mandrake/.seat-tmp/BENCH/r4_export`, whole export minus Transient copied to `D:\Luke\dev\_rmscratch\bench_live_20261014_r4`.
Tier `ratchet_pilot` via modset_builder (23 mods); owner list backup md5 ee01dae9 (550 active).
- Deploys (VERIFIED in sync; re-plans show no +/~): FlowWorks 3 (ladder DLL c238935c98 + FindMod by-name rewrite, 5 guards
  rewritten), SWBestiary 496 (donor-pack port waves W3-W4), UtinniPatches 10 (fixedLeaderKinds, 2 rewrites), composed
  biomes 3 (FireEcologyHook DLL, 3 rewrites). GSS, LuminousPigment, WeatherSuite, MandrakePatches, PyrelandsMechanics in sync.
  dll_source_stamp FlowWorks / FireEcologyHook / PyrelandsMechanics MATCH; deployed FlowWorks DLL md5 == export (4b1022252c56).
- Companion `build.py --gm --apply` from the export: surface 398, jawa/health present; selftest_tool_metadata 1/1.
- Launch via Steam READY 137 s (pid 17676). Census 398/399 live (phantom jawa/revoke, as r3). Test profile until
  2026-10-15T12:00Z. Armed jawa/health 240 min, telemetry_tier test 240 min, health_observer --for 14400.

## HEAD 1 (1cf47d90ee) abandoned after C1: a MOD fix landed, so the round restarted at a new HEAD
- GSS proof_all at 1cf47d90ee: **109/110**, wall 384.8 s, aerial **43.2 s** (perf probe 1
  CLOCKGATE_STATUS_REPAIR_NULL_WENT_MISSING: PASS, r3 was 137 s). FAIL `Z_log_budget` class MOD: 9x
  `Tried to maintain ended sustainer: RM_WindOnMetal` (Warscar Geiger choir, composed into biomes; the engine ends a
  sustainer whose source despawns, and MapComponentTick maintained it until the next 30-tick Refresh). Evidence `live/head1_1cf47d90ee/`.
- Fixed at **d25e1c95cd** (choir drops an ended sustainer). Game killed, re-exported, biomes redeployed (Warscar DLL md5
  20c5619fc8f0 = export, all other mods 0 drift), companion rebuilt from the same export, relaunched READY 102 s (pid 28904).

## ONE HEAD for the round: **d25e1c95cd** (`deploy2/`)
- C1 at d25e1c95cd: run 1 aerial block disturbed by uninvited Toughspikes (GovernorStop hostile_arrival, class HARNESS
  in the JSON) -> restarted; run 2 **110/110**, wall 266.6 s, aerial 20.1 s, log budget PASS (0 RM_WindOnMetal this session).
- C2 at d25e1c95cd: v2 **57/3/1**, P4/P4f/P5n FAIL unchanged from r3 although c238935c98 was deployed. Cause traced in
  code: `RM_CliffMask` re-checks the climb-generation key only inside `AfterIncremental`, which vanilla runs only on a path
  cell delta; a Standable pathCost-0 ladder makes none. Fixed at 63ecf8e874 (ladder pushes `Notify_CellDelta` on spawn,
  despawn, raise/lower; C# selftest case added, 323/323). Also added `jawa/storyteller_comps` (ce40347df6) for anima A1.
- Probes at d25e1c95cd, fresh quicktest (`live/probes/`): Plant_TreeAnima 0 of 44,725 things; Base_Player genSteps (67)
  has no AnimaTrees and DOES carry RM_DesalPlant/DetoxWorks/TarRefinery/PumpingStation_RuinScatter (FindMod by-name rewrite
  works); the map had 0 liquid bodies, so the self-gating scatter placed 0 markers (scatter UNMEASURED there).

## Round HEAD 3: **ce40347df6** (`deploy3/`): FlowWorks 4 (ladder fix + tank looks), SWBestiary 25 (art + About), biomes 1,
companion 399 incl. jawa/storyteller_comps; all re-plans 0 drift; DLL stamps MATCH. Relaunched READY 105 s (pid 6820).

## Suites at ROUND HEAD ce40347df6 (harness clockgate 78f534c9e5 from Pyrelands p4 on)
| suite | result |
|---|---|
| C1 GSS `proof_all --live` | **110/110 PASS**, wall 387 s, log budget PASS (`live/gss/proof_all_20261014T230239.json`). `modcheck record` REFUSED: the tier now omits `mlie.starwarsanimalcollection` (SWBestiary dropped the donor, 3898fe6212) while the 23-mod list applied at round start still loads it |
| C2 FlowWorks `validation_v2 --live --fresh-map` | **57 PASS / 3 FAIL / 1 UNMEASURED**: P4/P4f/P5n still FAIL after both ladder fixes; live mask read shows masks now current (pit bits 0x0F, gen==built), so the refusal is downstream (ForPawn/LadderLetsOut or RM_PitPathing). Lead on V2_LADDER_ROWS_DIAGNOSE_STAGE_FRIGHT |
| C3 Pyrelands, FRESH site r5, 10 pieces | **34 PASS / 0 FAIL**; embergrass_regrows INFERRED (256->0->21->60), furnacebeast_warmth tool gap (STATIC_CALL_WIDEN_PAWNS_NEED_NOT_APPLY); modcheck floor Pyrelands VALIDATED 21/21 |

## Section H at ce40347df6
1 **MET** · 2 **NOT MET** (v2 ladder rows) · 3 **MET** · 4 **NOT MET**: PYRE_SITE_TEMP_REPAIR_PROBE_HIT_ROCK and ANIMA_TREE_FIX_TAKES_THE_SIDE_DOOR now **done** (live); still open: POND_BED_BUILD_HOLLOW_KEEPS_ITS_SHAPE (deep middle + walk-out not staged), POND_ELEVATION_BUILD_LAKES_RUN_DEEP (unbuilt, owner card: next week), WEIR_WASH_ITEM_LOSS_MEND_PLACE_FIRST (A2 needs a no-room proof hook), PYRELANDS_GRASS_SATURATION_1 (ready) · 5 **NOT MET**: targeted selftests GREEN (clockgate 54/54, FlowWorks stock+C# 323/323, rivers, climb, tool_metadata 1/1) but `code_review_status` 67 of 133 changed pilot files DIRTY (`code_review_dirty.txt`) · 6 owner-only.
Pilot NOT closed.

## Worklist and probes
- Closed/done: PYRE_SITE_TEMP_REPAIR_PROBE_HIT_ROCK (gate B 3.8.8 PASS, 3404 rock things), ANIMA_TREE_FIX_TAKES_THE_SIDE_DOOR (census 0, no genstep, 0 storyteller comps via new `jawa/storyteller_comps`), FINDMOD_GUARDS_REPAIR_GHOSTS_BY_NAME_TOO (genSteps registered live), CLOCKGATE_STATUS_REPAIR_NULL_WENT_MISSING (aerial 20-47 s), ARTBOARD_PAWNS_HARDEN_IDS_ARE_NOT_PEOPLE (S3), VITALS_SPECIMENS_FIX_GHOSTS_REHOMED (S4).
- PASS recorded, item open: RAID_DETECTOR_REPAIR_FLOOD_NOT_A_RAID (flood half; real-raid half owed).
- FAIL: V2_LADDER_ROWS_DIAGNOSE_STAGE_FRIGHT A1 (twice); TESTENV_WILD_DOWNED_REPAIR_STOPS_CLOCK A1 (a wild fight's hurt triggers blocked the resume; fixed 78f534c9e5, live re-proof owed).
- Partial: FACTION_LEADER_REPAIR_SIX_EMPTY_THRONES (no per-tick repeat; Free Droid Enclaves still null without Droid Depot), FLOWWORKS_QUARRY_DIGGING_1 A5 (find drops; letter unmeasured, rock chunk).
- UNMEASURED: liquid-works ruin SCATTER (both quicktests had 0 liquid bodies; MAYREQUIRE A1), spike origin (settle 3x clean, 0 arrivals; GSS run-1 spikes arrived late), pond-bed deep middle, S1 (blocked by ladder rows), S2 burrow.
- Perf probes: 1 PASS, 2 partial (above), 3 PASS (own preset shows Pyrelands + GSS comps).
- Fixes landed this round: d25e1c95cd Warscar choir ended-sustainer (GSS log budget), 63ecf8e874 ladder cell delta, ce40347df6 jawa/storyteller_comps, 78f534c9e5 clockgate wild-fight resume.

## Teardown
Monitors disarmed (health 1.68 s hook total over the session, bridge busyShare 0.037; telemetry campaign; awareness off). Game killed by PID 6820.
`modset_builder --restore` REFUSED (its swap marker lived in the wiped export dir); restored from the bench before-copy instead:
ModsConfig md5 **ee01dae9**, 550 active, verified. Observer stopped. Game recorded DOWN. Bridge released.
