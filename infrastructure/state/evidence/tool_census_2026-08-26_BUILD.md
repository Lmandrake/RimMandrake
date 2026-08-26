# Live tool census — 2026-08-26, seat BUILD, config full-582

Taken the moment the game came up, against the RUNNING game, with
`python.exe D:\Luke\dev\Rimworld\src\RimMandrake\bridgetools\prove_stat_and_room.py --census`.

```
1. CENSUS - what the RUNNING GAME registered
  PASS jawa/ tools registered                         166 (expected 166)
  PASS registered: jawa/pawn_stats
  PASS registered: jawa/room_get
  PASS registered: jawa/thing_stats

ALL CHECKS PASSED
```

Baseline it replaces: `[JawaBench] ready: 121 tools, build c88df17ff577` (load of 06:35).
Deployed DLL this scores: build stamp `70b3b1173918`, tool-name surface 166, deployed in the
2026-08-26 down window with `build.py --gm --apply`.

## What this DOES prove
The companion the game loaded is the one that was deployed, and all 166 tool names are
REGISTERED with the bridge — including the three written in that window. This is the proof
`COMPANION_DLL_42_TOOLS_BEHIND_1`, `PAWN_STAT_READ_HAS_NO_TOOL_1` and
`ROOM_ROLE_AND_TEMP_HAVE_NO_TOOL_1` were each explicitly held open for: *"close only after the
live tool list shows the name."*

## What it does NOT prove
⛔ **Registered is not working.** No tool here has been CALLED. The readings that grade
`LIVE_HALF_OF_LOAD_1` T1/T2/N1/N2, `TEMPLATE_ENGINE_ACCEPTANCE_1` 1 and 2, and
`STAT_ON_INSTANCE_TOOL_1`'s own ground-vs-held comparison are all still owed, and they are why
those items stay open while these three close.
