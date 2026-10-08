# FlowWorks 50/9/0 repro (live helper, 2026-10-07 ~14:00-)
## Run 1 (as-is, no overrides)
`python.exe src/RimMandrake/FlowWorks/northstar/validation_v2.py --live --fresh-map --out Transient/fwrepro_run1.json` (log `Transient/fwrepro_run1.log`)
Result: **50 PASS / 9 FAIL / 0 UNMEASURED**, assembly eeeba804299f, 11512 ticks. REPRODUCIBLE. Same 9 rows: P3, P4, P4b, P5n, X1, X2, X3, X4, X5.
## Incident
First attempt died at SITE_paint (game process vanished with no Player.log error, during the fresh-map's second new game). I relaunched via steam://rungameid/294100 (11-mod flowworks list still active), run 1 then worked.
~14:12:30 the game died again after run 1 and RimWorldWin64 was started 14:13:10 NOT by me, on the FULL ModsConfig (614 mods, ModsConfig.xml mtime 07:48). Someone else (batch/modcheck/restore) swaps ModsConfig and relaunches the game under this helper.
## Run 2 (pitLipOcclusionEnabled=False) - wrapper Transient/fwrepro_wrap.py (scratch; overrides site_spec table at runtime, restores setting via bridge afterwards)
NOT RUN. From 14:13 the game is a 614-mod full list WITHOUT RimBridgeServer (no bridge port, Player.log has no RimBridge init, 'Bridge token' absent after 27 min); process Responding, window title 'RimWorld by Ludeon Studios'. Started by someone else (not this helper), likely the owner's own session; I did not kill it. Steps 2-4 are blocked until the bridge/flowworks tier is back.

## Ready to run once the 11-mod flowworks tier is up
`python.exe Transient/fwrepro_wrap.py pitLipOcclusionEnabled=false --out=Transient/fwrepro_run2.json` (add `--phases=L,site,S,P,X,tail` for a subset; other toggles as `field=false`).
