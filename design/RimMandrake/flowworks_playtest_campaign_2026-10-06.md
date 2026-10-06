# FlowWorks playtest campaign — running log (from 2026-10-06)

Item: `FLOWWORKS_PLAYTEST_CAMPAIGN_1` (owner's direction verbatim there). Plan background:
`flowworks_playtest_automation_2026-10-06.md`. Owner's open question (not a ruling): do we need all four methods —
A in-game runner, B offline kernel, C agent-plays, and northstar — for four different classes of bug?

## Method tally (cheap; one row per finding)

| Finding | Found by | Cost to find | Old suite saw it? | Status |
|---|---|---|---|---|
| Water and tar merge into one body | GPT source read → A live (7 s run) → B offline seed | seconds per run | no (59/59 green) | ruled: stay separate; fix in progress |
| Scarce supply allocation changes after reload | GPT source read → B offline | 1.7 s fuzz | no | ruled: fixed by position; fix in progress |
| Friendly cannot climb out of a pit by its lowered ladder | A live (pit scene) | seconds | no | diagnosis queued |
| Bridge `step_game_ticks` stops early; `play_for` "busy" | C (canal mission) | 130 s mission | n/a | bridge-side, logged |

## Timing baseline (MEASURED 2026-10-06)

Old core checkout 176 s / 861 calls (≈85% waiting on ticks at ~60/s). A pilot 5–7 s / 5–6 calls at ~2,090 ticks/s.
B 245,000 sequences in 1.5 s. C canal mission 130 s, 89 s of it agent thinking. Sessions overall: 66% agent
thinking, 4% bridge, <2% screenshots+image reading.

## Gimme Some Slack trial — scoping (2026-10-06)

- Northstar/D baseline: `proof_all.py` 143 PASS + 1 SKIP in 622 s (run 20261005T085243).
- **Every owner-found GSS defect in review rounds 1–7 came from him looking at the review map; none from a check.**
  Checks caught two regressions historically (no cords on any loaded save; a MapComponent written into saves).
  ⇒ GSS's dominant bug class is appearance — the rich-screenshot pre-review thrust is the method to try there.
- Pure logic (CordGraph/Planner/Builder, HoseMath) is already offline C# ⇒ B fuzz is cheap (started).
- Cheapest trial order: B fuzz → A soak recipe (wind/cuts/explosions + mid-run save) → one C hose mission → D as is.
