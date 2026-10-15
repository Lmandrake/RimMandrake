# BENCH live round 2 + ratchet pilot, 2026-10-14

Code at **28247cdeff** (`git archive` to ext4 `/home/mandrake/.seat-tmp/BENCH/r3_export`; python copy at
`D:\Luke\dev\_rmscratch\bench_live_20261014`). Tier ratchet_pilot+patches, 23 mods (ModsConfig md5 0bab16fa).
- Deploys: FlowWorks 4 files (DLL+srchash, RM_LiquidLogistics.xml, XTall tank png) VERIFIED; PyrelandsMechanics and
  composed biomes in sync (the Pyre burrower fix d4a56f1ec0 DLL was already deployed). dll_source_stamp: FlowWorks and
  FireEcologyHook MATCH. Companion rebuilt from the export: identical to the deployed DLL.
- Launch via Steam READY 180 s (`launch.txt`).
- Census: 396 tools declared in the DLL, 396 live. `jawa/revoke` is not a tool: it is a phantom from the old
  name scanner reading "Grant/revoke" prose in jawa/royal_title (build.py docstring). Nothing to file.
- JawaBench test profile had expired (2026-10-13 18:00Z); renewed to 2026-10-15T12:00Z, same keys.

| item | check | result |
|---|---|---|
| SAFE_ADVANCE_MENU_DIAGNOSE_LUCKY_NULLREF | quicktest, safe_advance 20000 timeoutMs=0, go_to_main_menu, status (`menu_probe.json`) | **PASS** with a label deviation: aborted, tickTo 961 > tickFrom 1, 0 NRE / 0 "stepper exception" in Player.log. abortWhy reads `map_gone: start map #0 ...`, not `game_changed` - teardown drops the map before Current.Game changes |
| PYRE_BURROWERS_DIAGNOSE_FLEE_BEFORE_DIVE (run 1, 28247cdeff) | site `NS_Pyrelands_site_1_417df172fdb5_r2` (fresh, 52.8 C), fixture reloaded before EVERY trial, Ashwallow 5 cells from a 6x6 fire, job sampled every 10 ticks x40 (`burrow/burrow_cold_*.json`) | 11/16 dove at 50 ticks, 5/16 at 270-350 after a long GotoWander; Flee 0/16. **MOD bug found:** the nudge table was static; a reload re-issues the same thingIDNumber at the same tick (fireTick 376511 every trial) so the previous trial's entry blocked the first nudge for 250 ticks. Fixed in 0afba7de51 (per-component table) |
| same, run 2 (0afba7de51, restarted) | same probe (`burrow/burrow2_cold_*.json`) | **PASS** 10/10 dove at 50 ticks, incl. two repeated ids. Flee never preceded a dive (0/26 over both runs). "Flee can still win" is INFERRED: the nudge only calls CheckForJobOverride, so the think tree keeps AnimalFlee above the burrow giver; night 2026-10-13 cold_2 showed Flee ending a dive |

Restart at 0afba7de51: FlowWorks (tank defs/textures 9fece3b324), PyrelandsMechanics DLL, composed Pyrelands (FireEcologyHook + RM_LightningBreaker.xml) deployed and VERIFIED; GSS in sync. Companion NOT rebuilt: it stays the 28247cdeff build (b59c434462's jawa/health tools are in source, undeployed). Launch READY 113 s (`launch_2.txt`).

## Ratchet pilot suites at ONE deployed HEAD 0afba7de51 (`suites/`)
GSS offline gate first failed only on MY scratch copy (missing src/Directory.Build.*, FlowWorks textures); green after copying them. HARNESS, mine.
| suite | result |
|---|---|
| C1 GSS `proof_all --live` | **110/110 PASS**, 392 s (`proof_all_20261014T190434.json`). `modcheck record` REFUSED: live set is ratchet_pilot + mandrake.rm.patches, not a declared tier |
| C2 FlowWorks `validation_v2 --live --fresh-map` | **52 PASS / 9 FAIL** (`v2.log`). Pond rows S3, E3, E3b, E3n want the old cap 5 for a 1-cell shallow pond, which reads 2 under the new yardstick -> `V2_POND_ROWS_REPAIR_STILL_COUNTS_FIVE`. Pit rows P1, P3, P4, P4f, P5n: D4 pits hold nobody and ladders free nobody, with pitRelativeClimbEnabled on by default (ae8d38f27c's first live deploy) -> `V2_PIT_ROWS_DIAGNOSE_NOBODY_STAYS_IN` |
| C2b river `extension_proof --site river` | 16 PASS / 4 UNMEASURED / 0 FAIL on a fresh river_site (tile 6250). Both UNMEASURED causes are SITE: nobody swept, and no placer mineral. Item: `FW_RIVER_SITE_DIAGNOSE_NOBODY_SWEPT_AWAY` |
| C3 Pyrelands north star | 5 pieces (`pyre_p1..p5`), fresh site r3 (fixture reloaded each piece): **27 PASS / 1 FAIL / 5 UNMEASURED**. FAIL scorchfruit_fire_born 2/2 (`PYRE_SCORCHFRUIT_DIAGNOSE_FIRE_BEARS_NOTHING`). UNMEASURED: ash_fertile_when_watered (the dry control reads wet, 2/2, `PYRE_ASH_CONTROL_DIAGNOSE_DRY_READS_WET`); scorchfruit_spoils_fast (a wild animal was downed mid-advance, 2/2, `TESTENV_WILD_DOWNED_REPAIR_STOPS_CLOCK`); fulgurite (0 sand cells, `PYRE_FULGURITE_BUILD_NO_SAND_TO_STRIKE`); herd_follows (no drive, `PYRE_HERD_DRIVE_BUILD_TWO_DAYS_LATER`); furnacebeast_warmth (no tool). The long splits were not run under the no-long-runs rule: burn_line, fresh_burn_bonus, embergrass_regrow. ullai_wired FAILed once only because my scratch copy had no Pyrelands Textures; after copying them it PASSed |

Section H at 0afba7de51: 1 MET · 2 NOT MET (v2 9 FAIL; the river half is met) · 3 NOT MET (1 FAIL plus gaps) · 4 NOT MET (BENCH pilot items still open, the new ones included) · 5 NOT CHECKED this sitting (owner ruling 2026-10-14: no full sweep; targeted Pyrelands selftest GREEN) · 6 owner-only, NOT MET.

## Worklist and teardown
- PYRE_SITE_TEMP_REPAIR_PROBE_HIT_ROCK: gate B on site r3 PASS, with the 3.8.8 line kept (`gateB_r3.json`). Verified partial: the PASS cannot show whether a rock cell was skipped, because `rock_skipped` is only reported on UNMEASURED.
- LAVA_LIQUID_BUILD_PROMISED_BY_CARD A3 L1 PASS: the startup log (`Player.0afba7de51.log`) has no RM_Liquid_Lava ConfigError and no excludeLiquids cross-ref error. A4 (Forge map) is still owed.
- Not reached: the other worklist rows (most need the golden site), and the pond-bed hollow proof (acfae20df4, needs a FlowWorks redeploy and a restart).
- Teardown: game killed by PID; `modset_builder --restore` verified ModsConfig md5 ee01dae9; game recorded DOWN; bridge released. Test profile left renewed until 2026-10-15T12:00Z.
