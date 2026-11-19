## Summary

SteveDesktop's INVALID share reads 0.217 (20 of 92 jobs, 24 h to 2026-11-15T04:00Z, MEASURED by
`python3 src/RimMandrake/Utils/testq/invalid_class.py --since 2026-11-14T04:00:00Z`): GAME 15, UNKNOWN 5.
The single biggest cause is `world_start_no_map` (7 jobs at 20:00 PST, across Watchers, ExplosiveGrowth,
Rites, UtinniPatches x2, UnfinishedLine, Bacta). One signature over six unrelated mods points at the
quicktest world-start path or the host, not at any one mod `[guess ~70%]`.

Owner, 2026-11-14 (cited in the STEVE_INVALID_SHARE flag): *"Who made all these bad tests for stevedesktop
to run? Please fix that process. So much waste. And it just keeps happening."*

## Work

1. Pull the Player.log / harness output of each `world_start_no_map` job above and find the FIRST
   exception or the readiness step that timed out (`readiness .mapData` vs `quicktest world start FAILED`).
2. Decide: harness (timeout too short, start called before the world is ready), delivery (wrong mod list),
   or host (the periodic reboot, fault_monitor). Reclassify in `invalid_class.py` if it is not GAME.
3. Fix the biggest cause; the 5 UNKNOWN jobs get a signature too.

## Acceptance test

none, live-host behaviour. The reading that closes it: `steve.invalid_share_24h` below 0.15 in
`digest.md`, with `world_start_no_map` at most 1 in `invalid_class.py --since <24 h ago>`.
