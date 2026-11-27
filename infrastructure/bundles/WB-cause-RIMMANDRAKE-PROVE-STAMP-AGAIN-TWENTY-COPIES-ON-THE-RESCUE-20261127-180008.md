# WB-cause-RIMMANDRAKE-PROVE-STAMP-AGAIN-TWENTY-COPIES-ON-THE-RESCUE-20261127-180008

System: cause:RIMMANDRAKE_PROVE_STAMP_AGAIN_TWENTY_COPIES_ON_THE_RESCUE (stamp again, row R3 of `src/RimMandrake/bridgetools/prove_scene_repeats.py`).
State: ENDED, 2026-11-27. Every member has an outcome.

## Members

| member | outcome | commit | live reading |
|---|---|---|---|
| `RIMMANDRAKE_GIVE_ONE_MOD_A_DIGEST_HOOK_SO_A_DIRTY_RESET_CAN_SHOW` | REAL, fixed | `7822187aaf` (item prose), `bb3e00e228` (hooks, proof step) | ArchSmall 2026-11-27: R1, R2, R3 PASS; prove_mod_hooks rows 1 to 3 PASS |

## What the next context needs

- The hooked mod is LuminousPigment, not FlowWorks: FlowWorks is the one advancing mod (his order of 2026-11-27 ~9:47 AM PST) and
  had a blind judge live, so its DLL was not touched.
- The state: `GameComponent_Deepfire` godCoatEvents and impressedQuadrum (per-game counters that carry from one staged copy to the next).
  Reset clears both; Digest renders them with `Kernel/RM_DeepfireSceneDigest.cs` (fuzz family `testhooks`).
- A hooked mod's digest is unproven after every game start, and an unproven digest stops a first stamp RESET_UNVERIFIED. So
  prove_scene_repeats proves each hooked mod with its act in `DIRTY_ACTS` before every series. A new hooked mod needs its act there.

## Context size

Under 200k of a 1M window at the end (one group).
