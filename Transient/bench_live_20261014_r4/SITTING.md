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
