## spec
Gimme Some Slack (Design Version 0.2.0). Rank 11 of the costly-acts study (`design/specs/2026-11-23-costly-test-acts/analysis.md` section 3; item RIMMANDRAKE_CENSUS_COSTLY_TEST_ACTS_REPEATED_HE_SAW_SHIP_FLY). Test-harness change only: no mod bar moves. This is the EXISTING item; the study's numbers are added here and no second item is filed.

**Measured (visits 1 and 2, six runs of 127 to 152 s):**
| part of a run | seconds |
|---|---|
| menu, map, scan, ship built, fuel | about 19 to 32 |
| boarding: one `jawa/order_pawn` with waitTicks=5000 (`src/RimMandrake/bridgetools/prove_gravship.py` lines ~286-287, timeoutSeconds=180, unpause=True) | 83.4 in all six runs |
| masts, cords, links | about 4 to 8 |
| take-off, travel, landing, reading | about 20 to 28 |
The wait loop ends only at the tick limit or time limit, never on arrival (`JawaBenchTerrainTools.cs`): 5,000 ticks at 60 a second is 83.3 s whether colonists arrive in 5 s or never. 167 s of Slack's 341 s of waiting is boarding. Two flights is the least that decides the bars (the switch is read once per lift): one flight needs the Conductor to accept an offline test for "off" (no such test exists; [guess ~70%] it would suffice). Whole saving: about 175 s per visit [guess ~70%]; the boarding wait alone is 167 s [measured] and ending it on arrival saves it without any grouping. First step: end the wait on arrival (small).

**What the one ship carries** (the grouped scene must have all of it; items 1, 3 and 7 are the wrong-check fault filed as RIMMANDRAKE_REPAIR_SLACK_GRAVSHIP_SCENE_PASSES_ON_ONE_LAMP):
1. two wall-bracket anchors joined by a span (today: masts): switch on, link up after landing; off, link gone.
2. a pair of masts with a second span, one span cut before take-off: a cut span aboard is kept too (no live reading today).
3. battery and two consumers on floor conduit, one net asserted (today: 7 conduits and one lamp): one net after landing; cords lie on the new net.
4. a wall lamp, a styled lamp, a wall plug, a switch, a tangle and a run in each look: true-to-grid after landing, stub joins, looks.
5. a floor conduit run crossing the ship's edge to the ground: two nets after take-off; no cord crosses the edge on the landed map.
6. a mast on the ground strung to the ship, a second ground mast and a GravAnchor on the ground: link gone, ground end reads coiled, origin map kept (guess ~85%).
7. the pre-launch cord set saved by the probe: the scene's own control (must FAIL against the landed map). Not run today.
8. two picture points: take-off at the edge, and the landed ship.
The two flights share one staging: save the boarded ship, fly with keepWiresOnGravship on, reload that save, fly with it off. (A second lift from the landing tile will not do: the launch cooldown makes `launch_check` refuse [guess ~85%].) Not decided here: whether the wire should break at a launch; the mod takes it down and coils it by design, and that is a design question for the Conductor, filed nowhere.
Files: `src/RimMandrake/bridgetools/prove_gravship.py`, `src/RimMandrake/GimmeSomeSlack/northstar/gravship_scene.py`, `design/concepts/GimmeSomeSlack/scenes.json`, `design/concepts/GimmeSomeSlack/version/test_table.json`. Waits on the scene library for the fixture save (`scene.open(needs={"map":...})`; `s.stage`, a launch verb and a land verb are NOT_BUILT).

**Recommendation: current Design Version** (harness only; the bar decision does not move). The Conductor decides.

## verify
Acceptance test (offline part): `bash infrastructure/state/items/RIMMANDRAKE_MERGE_SLACK_GRAVSHIP_CHECKS_ONE_SHIP_TWO_FLIGHTS.acceptance.sh`
- Reads the AST of prove_gravship.py: no `jawa/order_pawn` waitTicks above 600 (our own rule: 10 s, colonists arrive in about 5 s [guess]). WATCHED FAIL today (2026-11-24): worst waitTicks 5000, limit 600, exit 1. `--selftest` prints SELFTEST OK (planted faults: a long wait -> red, a short wait -> green, no boarding call -> could not look, unreadable file -> could not look). Watched green.
- Part 2, UNRUN and not built (live: Odyssey, a game): `gravship_scene.py both --out RESULT.json`: 2 rows (`_on`, `_off`) and exactly 1 ship build in the bridge log, with the control row of item 7 seen red on a planted fault.

## criteria
- Offline part exits 0, AND the live run reads 2 flights from 1 ship build with the 8 carried things present.
