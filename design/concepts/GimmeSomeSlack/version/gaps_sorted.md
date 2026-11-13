# Gimme Some Slack 0.1.0: open judge gaps, sorted

Source: the latest coverage verdict, `rm-coverage-judge-1794599377` (2026-11-13 11:49 PST), judged at the tree locked here; copied to `evidence/` because its only copy is uncommitted in `/home/mandrake/rm/bench`. 39 of its 47 checklist rows met; 5 gaps, every one rated "criterion sound, cost edit".

Sort rule (same in every mod): **PROBLEM** = without the fix a defect a player would reject (or find strange or disappointing) can ship unnoticed; stays in 0.1.0. **POLISH** = improves play, not part of passing, needs his confirmation. **NEXT VERSION** = shifts or extends the vision. **CORRECTION** = the bar's or test's own text is wrong, contradictory or reads something that does not exist.

⚠️ **All five are claimed fixed** by Designer run rm-role-designer-1794600246 and the exam then passed 26/26, but those edits (tree 5e3aa0d4, sheet 33b1cddc, 7 files) were never committed: they sit in `/home/mandrake/rm/bench`. Until they land, the committed bars still carry these five gaps.

| gap | bars it touches | sort | reason |
|---|---|---|---|
| g1 | floor_end_shock, floor_end_shocks_crossers | PROBLEM | The scene cannot catch a cord that shocks along its whole length; pawns jolted while crossing the middle of a cord would look like a bug. |
| g2 | floor_end_shock, floor_end_shocks_crossers, shock_reach_setting | PROBLEM (one part CORRECTION) | Five promised rules are untested: an unfinished run's end shocks, a pawn delivering steel is safe, a fuel puddle on a live end does not ignite, every live end shocks past the spark budget, FlowWorks' fallen-deck cords obey the setting. A delivering pawn shocked, or a fire from a puddle, is a defect a player rejects. Ruling (6) also reads two ways, which is a Correction of its text. Least sure: the FlowWorks cross-mod case could be Polish. |
| g3 | no_unforced_sharp_turn | PROBLEM | A taut straight cord passes the scene, and slack is the mod's whole look; taut cords would disappoint at once. |
| g4 | owner_change_cut, owner_change_coils_wires | PROBLEM | No span joins two of our own poles, so a build that cuts every wire when a neighbour claims one pole passes; losing your own wires would read as a bug. |
| g5 | game_statics_reset, statics_clear_between_games | PROBLEM | Two caches that leak between games in one session are never read; the judge names the symptom as missing cords or pawns avoiding cells that are not live. |

Counts: PROBLEM 5 · POLISH 0 · NEXT VERSION 0 · CORRECTION 0 (one part of g2).

## Other open lines (not judge gaps)

| line | where | suggested sort | reason |
|---|---|---|---|
| Which look a player picks is taste; none of the four is reject-level | `sheet.md` advisory | none | Already advisory, outside passing. |
| The pending note says "Stage 3 must fix the five gaps" | `stage.json` pending_decision | not a gap | Stale on origin; the fix exists in the uncommitted bench edits. |
