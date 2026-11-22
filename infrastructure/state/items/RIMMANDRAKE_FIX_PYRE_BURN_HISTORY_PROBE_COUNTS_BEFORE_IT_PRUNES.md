## spec
Pyrelands 0.1.0, in-game visit 5 (ArchBig, his full list, 2026-11-22). Class HARNESS: a fault in a test probe that lives in
the mod's DLL (`MapComponent_BurnLine.ProbeBurnHistory`, src/RimMandrake/Pyrelands/Source/MapComponent_BurnLine.cs). The
probe reads `n = burnHistTicks.Count`, then calls `BurnCenterAgo`, which prunes samples older than BurnHistoryKeepTicks
(600000), then indexes `burnHistTicks[n - 1]` with the stale count. After two game weeks the prune removes samples and the
probe throws ArgumentOutOfRangeException. sc_walk's walk_master_off_then_on FAILed on it ("static_call ...ProbeBurnHistory
failed: ... Index was out of range"), so that walk part reads nothing about the mod. The shipped play path
(`BurnCenterAgo`, read by the herd giver) prunes before it reads and is not affected.
Fix: read the count and the first and last samples after `BurnCenterAgo` (one line moved). The change touches the mod's DLL,
so a deploy, a restart and the checks that read MapComponent_BurnLine.cs run again (build_match.py check names them).

## verify
Build and deploy the fixed DLL (game down), then on any Pyrelands scratch map with a burn history run the acceptance test
below; then the full-list walk (sc_walk) part walk_master_off_then_on reads the mod.

## criteria
- ProbeBurnHistory answers after its own prune empties the history (samples=0), never throws.
- walk_master_off_then_on gives a verdict about the mod on the full-list walk.

## Acceptance test
`python.exe design/concepts/Pyrelands/version/in_game/visit_5/scripts/probe_burnhist_red.py` (bridge held, a Pyrelands
scratch map with a burn history current): exit 0 PASS. Red now, watched: exit 1 on ArchBig, 2026-11-22 08:31 PST, build
e63595716c, "Invoke threw ArgumentOutOfRangeException" after BackdateBurnHistory(700000)
(design/concepts/Pyrelands/version/in_game/visit_5/evidence/script_probe_burnhist_red.log). Exit 2 when the map has no
history (UNMEASURED).

## refs
file: src/RimMandrake/Pyrelands/Source/MapComponent_BurnLine.cs
file: design/concepts/Pyrelands/version/in_game/visit_5/scripts/probe_burnhist_red.py
