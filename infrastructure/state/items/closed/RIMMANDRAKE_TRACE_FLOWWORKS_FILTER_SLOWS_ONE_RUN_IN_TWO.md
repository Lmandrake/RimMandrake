## spec
found-by: FlowWorks in-game visit 3 (continuation), game a, exact flowworks tier, calm site, 2026-11-21 9:04 AM PST.
sc_garden row GARDEN_filter_keeps_its_rate FAIL (design/concepts/FlowWorks/version/in_game/visit_3/evidence/sc_garden_20261121T085846.json):
the drip filter made 10 batches in 60,000 ticks against the window [32, 33] at converterRateMultiplier 4.1. It ran at about 4.1x for the
first three 2,500-tick chunks (2000, 4000, 6000 made), then one batch every 7,500 ticks to the end: exactly the base rate (1.0x), the
same reading the planted fault CALLER_CONV_RATE_SETTING_IGNORED gives (8 batches).
The same scene on the same build and list, 12 minutes later (sc_garden_20261121T091028.json), PASSed: 32 batches. A poll every 20 s
during that run read converterRateMultiplier 4.1 throughout (evidence/exp/garden_filter_poll.txt).
Ruled out [measured]: a mutant DLL in the game (deployed DLL md5 acf39ee9... equals the repo's; game a started 8:27 AM, after the
last deploy); the setting not landing (reads 4.1 after the FAIL run); the filter needing power or fuel (RM_DripFilter has neither);
a leftover python.exe from the runs killed at 8:42 and 8:47 driving the game (the client's reconcile read writer pid 44304 gone by
8:54; no python.exe on Windows at 9:07); game b sharing a settings file (game b has its own userdata folder).
Not checked: whether something re-reads the FlowWorks settings file mid-run (RM_MachinerySettings.ExposeData in LoadingVars would set
1.0 from disk, and the scene's restore at the end would write 4.1 back: that fits the reading [guess ~35%]); RM_ConsumerRotation
holding the filter back; RM_LiquidNet.Available or Room on the toxic store.
Class: MOD presumed [guess ~50%]; the cause is not known.

## verify
- A probe that reads converterRateMultiplier and the filter's accrued budget every chunk inside scene_garden shows which input drops
  when the rate falls; then fix that cause, test first.

Acceptance test: `python.exe src\RimMandrake\FlowWorks\northstar\concept_scenes.py --scene scene_garden --out <json>` exits 0 with
GARDEN_filter_keeps_its_rate PASS on 3 runs in a row on the flowworks tier (calm site). Seen red 1 run in 2 on 2026-11-21.

## criteria
- GARDEN_filter_keeps_its_rate PASS on 3 sc_garden runs in a row on one build, with the cause named and its fix tested red then green.

## refs
file: src/RimMandrake/FlowWorks/Source/Machinery/CompLiquidConverter.cs
file: src/RimMandrake/FlowWorks/northstar/concept_scenes.py
