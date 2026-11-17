# Pyrelands: next version (after 0.1.0)

Divergent work: anything that shifts or extends the 0.1.0 vision (`../vision.md`). Each entry is a pre-written ticket with its acceptance test, who proposed it, when, and why it was not taken now. **Protected: append-only for agents; removing an entry is his call.** Nothing here changes a 0.1.0 bar.

*Empty at entry on 2026-11-13: no open judge gap sorted as next version.* Watch: g2's inventory re-audit may find built behaviour outside the vision; such a find is filed here, not added to the 0.1.0 bars.

## Re-judge coverage under a calibrated brief when the next version opens

- **What:** this mod's coverage signature was made before the coverage brief read CALIBRATED (`coverage_judge.unproven_signatures` flags it; flagged, never voided). When its next Design Version opens, its coverage is judged again by a coverage brief that reads CALIBRATED at that time.
- **Who, when, why not now:** owner, by question card 2026-11-16 11:36 PM PST (point 19), picked "Leave them, re-judge at next version": "two of the three are already in live in-game visits, which find real failures better than a paper re-read. Buys: no spend or delay now; each gets a tested judge when its next Design Version opens." Filed by RIMMANDRAKE_LAND_JUDGE_PROMPT_CALLS_FOUR_ANSWERED_BY_CARD.
- **Acceptance test:** `python3 src/RimMandrake/rimflow/refusal_contract.py calibrate --no-run` reads `coverage_judge` CALIBRATED, and `python3 -c "import sys; sys.path.insert(0, 'src/RimMandrake/rimflow'); import coverage_judge as C; print([u['concept'] for u in C.unproven_signatures('.')])"` no longer lists `design/concepts/Pyrelands`.

## Black rain fills the moat and the water tanks

- **What:** a black rain is "a rare chance to fill your moat against the fire and fill your water tanks" (owner, 2026-11-13, walk_season_on_the_pyre). Today nothing fills: FlowWorks liquid tanks fill only over the liquid net, a limited water body refills about 0.06 units a cell over a 2.4 h black rain, and a moat dug dry into ash may not count as water at all. Owed: a Designer pass on how much a black rain fills (an open-sky tank; a dug moat or canal on the Pyrelands) and whether it is Pyrelands-only or any heavy rain; a change to FlowWorks' water code; a Mod Setting; a test; a live look. Build item: `RIMMANDRAKE_BUILD_BLACK_RAIN_FILLS_MOATS_TANKS_STAY_DRY`.
- **Who, when, why not now:** owner, by question card 2026-11-17 6:33 AM PST ("Rain fills" → "Next version (Recommended)", OWNER:1794926131273790638): 0.1.0 is not yet passing its own fire and grass bars, and this needs another mod's code changed; 0.1.0 ships on the bars it has, with no rain harvest at first release. Recorded by RIMMANDRAKE_REWORD_DESIGNER_BARS_PINNING_NUMBERS_NOT_HIS.
- **Acceptance test:** none yet: the fill amounts are unset until the Designer sets them, and the Designer's spec writes the red-first test (a FlowWorks kernel row: N hours at rainRate 1.1 fills an open-sky tank and a dug moat by the stated amount), then the 0.2.0 season walk reads it live.

## A choking-smoke weather of the Pyrelands' own

- **What:** "the choking smoke that sometimes comes as its own weather" (owner, 2026-11-13, walk_season_on_the_pyre). Today the RM_Pyrelands weather table holds no smoke weather; our one smoke weather, `RM_SmokeHazeCondition`, is the Long Shade's relief haze. Build a Pyrelands smoke weather that rolls on its own, reads as smoke, and hampers or harms pawns out in it with a readable sign; RM_FE_BlackRain stays the only rain-rated weather in the table; a Mod Setting (on/off, weight). Build item: `RIMMANDRAKE_BUILD_PYRE_SMOKE_WEATHER_ONLY_LONGSHADE_HAS_ONE`.
- **Who, when, why not now:** owner, by question card 2026-11-17 6:33 AM PST ("Smoke" → "Next version (Recommended)", OWNER:1794926132427945325): it is outside the locked bars and 4 of its 6 checks fail; 0.1.0 should first pass what it already promises, so the first release has no smoke weather. Recorded by RIMMANDRAKE_REWORD_DESIGNER_BARS_PINNING_NUMBERS_NOT_HIS.
- **Acceptance test:** `python3 src/RimMandrake/rimflow/acceptance/pyre_smoke_weather_accept.py` exits 0 with `PASS 6/6` (read `PASS 2/6` at a68d89e622 and again at 448168490b, 2026-11-17), and the 0.2.0 season walk sees it roll in once on its own.
