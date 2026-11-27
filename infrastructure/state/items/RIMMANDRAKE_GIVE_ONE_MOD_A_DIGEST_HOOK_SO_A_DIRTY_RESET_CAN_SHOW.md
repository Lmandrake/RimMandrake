## spec
Row R3 of `src/RimMandrake/bridgetools/prove_scene_repeats.py` (boundary `design/specs/2026-11-23-bridge-v2/boundary.md`
§STAMP AGAIN) read UNRUN on 2026-11-25: no loaded mod of ours had a digest hook (41 loaded, 0 hooked). Give one mod of ours
an `[RMReset]` and an `[RMDigest]` hook (`src/RimMandrake/_Shared/TestHooks/RMTestHooks.cs`) over a real per-scene state, and a
dirtying act a bridge tool can do. Then run R3 live: the dirty state must stop the repeat RESET_DIGEST_DIFFERS on that mod.

The mod: FlowWorks (`mandrake.rm.flowworks`, assembly `RimMandrakeFlowWorks`; not held). Its state: `RM_WakeCount` in
`src/RimMandrake/FlowWorks/Source/RM_WakeMath.cs`, the count of wakes thrown per terrain since the last reset (read live by
`FlowWorks/northstar/wakes_checks.py`). Reset clears it; Digest renders it. The dirtying act: `jawa/static_call
RimMandrake.FlowWorks.RM_WakeCount.Note <terrain>`, the same call that RM_LiquidSurface makes for one wake.

A hooked mod whose digest is unproven makes the first stamp of every series stop RESET_UNVERIFIED (scene_repeats.Series.stamp),
so prove_scene_repeats proves each hooked mod's digest with its known dirtying act before R1 and R2 too.

## verify
Offline: `python3 src/RimMandrake/bridgetools/prove_scene_repeats.py --selfcheck`; the FlowWorks C# selftest (the hooks file).
Live on a free game with FlowWorks loaded: `python.exe src\RimMandrake\bridgetools\prove_scene_repeats.py --game <game> --rows R3`
reads `PASS R3`; `jawa/mod_hooks action=list` lists RimMandrakeFlowWorks with build RELEASE and both hooks.

## criteria
- FlowWorks carries one [RMReset] and one [RMDigest] hook over RM_WakeCount, and the companion lists them with no problem.
- R3 reads PASS live, and the boundary page records it (`R3 PASS`).

## refs
file: src/RimMandrake/FlowWorks/Source/RimMandrake_FlowWorks.csproj
file: src/RimMandrake/bridgetools/prove_scene_repeats.py
file: design/specs/2026-11-23-bridge-v2/boundary.md
