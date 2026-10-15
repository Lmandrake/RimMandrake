# MAP_STATICS_PRUNE_GHOST_MAPS

FlowWorks: static per-Map tables, NativeArrays and meshes outlive removed maps

Source: FlowWorks pre-release GPT consult, BENCH 2026-10-15 — `Transient/release_push_2026-10-15/gpt_FlowWorks/TRIAGE.md` (full rows) and the `answer_<slice>.md` named by each finding id.

## findings

- **C1-F2** CONFIRMED LOW — Static per-Map dictionaries keep removed maps alive until a cache miss. RM_LiquidNet.cs:252/431/823 prune only inside TryGetValue miss; a removed quest map stays referenced while home map stays cached (memory, stale things).
- **C3-F2** CONFIRMED LOW — RM_PitPathing static grids (Persistent NativeArrays) outlive removed maps. Superdeep/RM_PitPathing.cs:64,310 static Dictionary<Map,...>; disposal only in the miss branch (:195,:331). Cliff masks are fine (disposed by RM_Patch_PathFinderMapData_Dispose).
- **C5-F3** CONFIRMED LOW — RM_DigDiscovery static poolMap pins the last map. RM_DigDiscovery.cs:193-204; reference-equality keeps reuse correct, only memory is pinned.
- **C5-F4** CONFIRMED LOW — RM_LiquidSurface overlay meshes are never destroyed when the map goes. RM_LiquidSurface.cs:304 per-component meshPool of Unity Meshes; no MapRemoved/Destroy (materials have ForgetLook, meshes do not). Live: count RM_LiquidSurface meshes across 3 reloads.

## criteria

- Each CONFIRMED finding: a SelfTest/python case (or a live state read where the row says so) that goes red on today's code, then green with the fix.
- Each PLAUSIBLE finding: run the check written in its row first; close it as not-a-bug with the evidence if it stays green.
