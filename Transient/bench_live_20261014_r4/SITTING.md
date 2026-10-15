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
