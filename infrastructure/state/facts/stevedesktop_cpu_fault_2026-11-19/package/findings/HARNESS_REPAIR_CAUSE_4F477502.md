# HARNESS_REPAIR_CAUSE_4F477502: class ENVIRONMENT (SteveDesktop host fault), no harness change

Sighting: testq `J20261106T122857Z-88bde4.a1`, Graffiti, stevedesktop. Run 12:30:10Z..12:31:22Z, game died in
cold load at 12:31:16Z. Read 2026-11-06 from SteveDesktop's
`C:\Users\sjlewis\AppData\Local\Temp\Ludeon Studios\RimWorld by Ludeon Studios\Crashes\Crash_2026-11-06_123116960\`
(`Player.log`, `crash.dmp` exception stream).

## What crashed

A native abort inside the mono JIT, not a managed exception: exception code `0xE0000001`, raised through
`KERNELBASE RaiseException` <- `mono-2.0-bdwgc` (`mono_unity_jit_cleanup`, `mono_unity_class_has_failure`,
`mono_jit_set_domain`; symbols are nearest exports). The note's `mono_profiler_init_etw` is only the thread-start
tail printed last, shared by every crash on that thread; it names no cause.

## Why the host, not the harness, the mod or the site

| crash (Steve UTC) | code | managed caller being JITted | against fault_windows.json |
|---|---|---|---|
| 10-26 02:47 | E0000001 | SHA256Managed.HashFinal | before the monitor's first window |
| 10-26 19:58 | E0000001 | RimWorld.Ideo.GetNewDescription | before the monitor's first window |
| 10-28 22:18 | E0000001 | RM_LiquidNet.FillPlan | before the monitor's first window |
| 10-31 07:35 | E0000001 | RegionListersUpdater.RegisterInRegions | before the monitor's first window |
| 11-03 22:45 | E0000001 | MonoMod MonoRuntime.Compile (Harmony) | 6 min before first_bad, F20261103T195921Z |
| 11-06 12:31 | E0000001 | LunarLoader Enumerable.ToList | 7 min before first_bad, F20261106T110035Z |

- One abort, six unrelated methods: the JIT dies, not any one caller. The same folder also holds access violations
  and, on 11-01 19:09Z inside a known window, `0xC000001D` (illegal instruction) in freshly JITted code.
- Both E0000001 crashes the monitor could time fell 6-7 min before a fault onset. Of 147 Steve jobs with a load
  phase started since the first window, 10 (6.8%) fall within 15 min before a first_bad, so two of two by chance is
  about 0.5%. In-window jobs are absent from `done/` (quarantined), which does not change that lead count.
- The same list then loaded: re-run `J20261106T124537Z-ff306a` cold-started the game twice in `.a1` (pids 3412 and
  25772) with no crash, after the 12:53:41Z reboot, and `.a2` carried verdicts. So not the mod, and the crash precedes
  any map, so not the site.

## What this does not prove

- The run itself lies outside the window as recorded: the monitor read clean at 12:33:20Z, two minutes after the
  crash. That is why ingest filed this item. The link is the timing above plus the fault's known shape (clean cycles
  occur inside a window), not a reading taken during the crash.
- Whether a load provokes onset or merely precedes it is unmeasured.
- Archmagi as a healthy-CPU control is UNMEASURED: its Crashes folders hold no logs.

## Verify (no fix exists, so no fix sha)

`retest.py passed J20261106T124537Z-ff306a HARNESS_REPAIR_CAUSE_4F477502` exits 0 (6 rows with a verdict, runner
b7d7dd55b0, same mod, chains, lane, profile). Its 5 UNMEASURED rows do not carry this cause.
`retest.py passed J20261106T122857Z-88bde4 HARNESS_REPAIR_CAUSE_4F477502` exits 1.
