# BENCH live round 3 — ratchet pilot at ONE HEAD, 2026-10-14

HEAD **695812d5ec** (git archive -> ext4 `/home/mandrake/.seat-tmp/BENCH/r3_export`; whole export minus Transient copied to
`D:\Luke\dev\_rmscratch\bench_live_20261014_r3`). Tier `ratchet_pilot` via modset_builder (23 mods, rm.patches declared);
backup of owner list md5 ee01dae9.
- Deploys (all VERIFIED in sync): FlowWorks 8 (MayRequire rewrote 4), SWBestiary 89, UtinniPatches 14 (rewrote 2),
  PyrelandsMechanics 2, composed biomes 26 (rewrote 2). GSS, LuminousPigment, WeatherSuite, MandrakePatches in sync.
  dll_source_stamp: FlowWorks, FireEcologyHook, PyrelandsMechanics MATCH; deployed FlowWorks DLL md5 == export.
- Companion rebuilt `build.py --gm --apply` from the export: tool surface 398, jawa/health + jawa/health_profile present;
  selftest_tool_metadata 1/1.
- Launch via Steam READY 104 s (pid 12768). Census 398/399 live; the 1 is the known phantom `jawa/revoke`.
- Test profile valid until 2026-10-15T12:00Z. Armed: jawa/health (240 min), telemetry_tier test (240 min),
  health_observer.py --for 14400 (external).

## Suites at ONE deployed HEAD 695812d5ec (`live/`)
| suite | result |
|---|---|
| C1 GSS `proof_all --live` | **110/110 PASS**, wall 499.5 s (r2 392 s; all of it in the aerial block, 50 -> 137 s). `modcheck record` accepted (ratchet_pilot now declares rm.patches) |
| C2 FlowWorks `validation_v2 --live --fresh-map` | **57 PASS / 3 FAIL / 1 UNMEASURED.** Pond rows S3/E3/E3b/E3n/E4 PASS (V2_POND_ROWS closed); pit hold P1/P3 PASS (V2_PIT_ROWS closed). FAIL P4/P4f/P5n ladder rows (MOD presumed) -> `V2_LADDER_ROWS_DIAGNOSE_STAGE_FRIGHT`; P4b UNMEASURED HARNESS |
| C2b river `extension_proof --site river` (fresh river site, tile 15061) | 18 PASS / 0 FAIL; swept returns_home disturbed by ToxicBuildup, restarted -> PASS; flood_refill UNMEASURED by design |
| C3 Pyrelands north star, FRESH site r4, 10 short pieces | **34 PASS / 0 FAIL**, incl. burn_line, fresh_burn_bonus, compressed regrow. embergrass_regrows INFERRED (0->28->73 plants, override restored); furnacebeast_warmth = tool gap (STATIC_CALL_WIDEN_PAWNS_NEED_NOT_APPLY). modcheck floor: Pyrelands VALIDATED |

Monitors: jawa/health hook cost over the session 1.79 s total (~0.04% of ~70 min; bridge-occupancy 1.39 s of it, frame-hist 0.22 s), bridge busyShare 0.039; recorded on HEALTH_METRICS_JUDGE_EARN_THEIR_KEEP. health_profile "own" preset during Pyrelands timed only FlowWorks comps (LiquidSurface 3.65 us/tick, Excavation 0.65, Hoses 0.25, RiverCurrent 0.08); no Pyrelands comp is in the preset.

## Section H at 695812d5ec
1 **MET** · 2 **NOT MET** (v2 3 FAIL ladder rows; river half met) · 3 **MET** (0 FAIL, both non-PASS labelled) · 4 **NOT MET** (PYRE_SITE_TEMP_REPAIR_PROBE_HIT_ROCK built, live owed; ANIMA_TREE_FIX_TAKES_THE_SIDE_DOOR owner-held) · 5 targeted selftests **27/27 GREEN** (`selftests_targeted.txt`); code_review_status not run · 6 owner-only, prepared not claimed.
Pilot NOT closed.

## Worklist
- PASS/closed: V2_POND_ROWS_REPAIR_STILL_COUNTS_FIVE, V2_PIT_ROWS_DIAGNOSE_NOBODY_STAYS_IN, FW_RIVER_SITE_DIAGNOSE_NOBODY_SWEPT_AWAY, PYRE_SCORCHFRUIT_DIAGNOSE_FIRE_BEARS_NOTHING, PYRE_ASH_CONTROL_DIAGNOSE_DRY_READS_WET (rejection path on old site r3), PYRE_HERD_DRIVE_BUILD_TWO_DAYS_LATER, PYRE_FULGURITE_BUILD_NO_SAND_TO_STRIKE, PIT_CLIFF_MASK_BUILD_ASTAR_LEARNS_WALLS (climb_proof 11/11).
- Criterion PASS, item stays open: PIT_RAMP_BUILD_STAIRS_BEAT_LADDERS A1 (owes owner L4), SURFACE_RIVER_WEIRS_1 A2 (flood False->True, weir drift rolls 2), FLOWWORKS_QUARRY_DIGGING_1 A1+A2, MAYREQUIRE_REPAIR_GUARDS_NAME_A_GHOST A2 (Ollathrix spawning).
- FAIL: MAYREQUIRE_REPAIR_GUARDS_NAME_A_GHOST A1 (GenSteps resolve, but the register patch's PatchOperationFindMod names the folded mod by NAME) -> FINDMOD_GUARDS_REPAIR_GHOSTS_BY_NAME_TOO.
- Partial: POND_BED_BUILD_HOLLOW_KEEPS_ITS_SHAPE (lakebed D2 after draw, one cell rewet exact; deep middle + walk-out not staged); TESTENV_WILD_DOWNED_REPAIR_STOPS_CLOCK (no wild down happened; a downed COLONIST did stop the clock as designed).
- UNMEASURED: quarry A5 dig_finds (toxic disturbance x2 on the river map), F1-F3 pond fill/sluice rows, H1-style pond capacity covered by v2.
- Look (owner): `look/r3_pyre_art_look.png` (5 rotted Pyrelands corpses draw their own husks, core + sprayer present), `look/r3_tall_tanks_look.png`; texture_audit biomes/FlowWorks/SWBestiary: no Pyrelands or tank path missing.
- Filed: V2_LADDER_ROWS_DIAGNOSE_STAGE_FRIGHT, TESTENV_TOXIC_DIAGNOSE_RIVER_SITE_SNIFFLES, RAID_DETECTOR_REPAIR_FLOOD_NOT_A_RAID, TESTENV_QUICKTEST_DIAGNOSE_SPIKES_UNINVITED, FINDMOD_GUARDS_REPAIR_GHOSTS_BY_NAME_TOO, RONTO_PACK_TEXTURE_REPAIR_SADDLEBAGS_MISSING.

## Teardown
Monitors disarmed (health, telemetry tier campaign); game killed by PID 12768; `modset_builder --restore` md5 ee01dae9, 550 active, verified; game recorded DOWN; bridge released. Artboard clear never called (coordinator warning re 92ada47568).
