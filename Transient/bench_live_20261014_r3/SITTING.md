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
