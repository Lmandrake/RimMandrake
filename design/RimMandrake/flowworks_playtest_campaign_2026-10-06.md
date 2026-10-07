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

## Rich-screenshot art pre-review — offline half built (2026-10-06, `05ee16921`)

Design `rich_screenshot_art_prereview.md`; code `src/RimMandrake/Utils/artboard/` (selftest 26/26). First real trial
on `Transient/xenotype_review/xeno_grid_v2.png` (13 pawns): 3 real staging defects (pawns shifted a cell by the
staging script), 2 false "holes" (body colour = ground; fixed by a clean empty plate), and one mosaic read raised 2
owner-worthy questions (one pawn near-invisible, four skins grey). Owed: bridge tools `jawa/artboard_stage` +
`jawa/artboard_capture` (queued behind the runner owner of bridgetools/).

| Finding | Found by | Cost | Old method saw it? | Status |
|---|---|---|---|---|
| Xenotype grid: 3 pawns staged one cell off | artboard tier-a checks | one existing screenshot, seconds | no | staging script defect to fix |

## Owner decisions, 2026-10-06 evening (question cards)

- **Next mod for the new methods: Gimme Some Slack** (decision taken by question card).
- **Screenshot pre-review policy** — owner typed: *"(1) plus regen the art if you already know how, only go to human
  if you need judgement to fix it"*. So: staging faults are fixed silently; art faults with a known fix are regenerated
  without asking; only faults needing judgement reach him, marked on the page.
- **Which methods every mod gets: not decided.** Owner asked for the evidence first (relative costs, bug kinds found,
  and plain live Claude debugging as the baseline), without a research project.
- **Method mix — owner, 2026-10-06 19:0x, typed (verbatim):** *"Seems like we need a LOT more data then. So yes, we
  have to implement them all to really figure out what works and what doesn't, except for the AI player itself. Very
  critical we test out the interface buttons and the like too though, so that might point toward AI player
  eventually... that will come later if it gets too onerous for a human player to do it. We need to figure out if we
  even want Northstar. So let's go get lots of data, and see how far we can push runner + fuzz + human review sheets
  like this. MUST implement the looks screenshot auto-review too. GPT source read + GPT validation plan read (once
  everything seems done and good) are also a given now. Do not eliminate any pathways yet."*
  ⇒ Every mod in the campaign gets: in-game runner, offline fuzz, human review sheet/map, looks screenshot auto-review
  (mandatory), GPT source read, and a GPT read of the validation plan once it looks done. Interface buttons (gizmos,
  float menus, settings) must be exercised. AI-player missions wait. Northstar stays, under evaluation. Nothing dropped.

## Gimme Some Slack — all methods built (2026-10-06 evening, offline; nothing run live)

What was built:
- **A, the in-game runner.** `JawaBenchGssPlaytest.cs` provides `jawa/gss_playtest_start`, `jawa/gss_playtest_status` and
  `jawa/gss_playtest_collect`. The launcher is `GimmeSomeSlack/northstar/gss_playtest_runner.py`, which reuses FlowWorks'
  verdict and journal code. There are seven scenes:
  - `cords`: connect, disconnect, reconnect, and a wall 4 away (C1).
  - `hose_bend`: 12 lays with and without the outlet.
  - `hose_carry`: work-giver deploy, move and retract, plus a draft mid-carry.
  - `soak`: 8 explosions in wind, over cords, a span and a hose.
  - `ui`: every reel and anchor gizmo through `ProcessInput` and the Targeter's own callback; the hose float menu through
    `FloatMenuMakerMap`; three build-designator style menus; every settings field flipped and restored; the settings
    window drawn on every tab.
  - `save_reload` and `save_reload_b`: cords, a laid hose, a hose mid-carry, spans up and cut, and a styled reel, compared
    line by line.

  Any red error logged during a scene turns its PASS into a FAIL. The GSS DLL is referenced directly, the same way
  Droidworks is. The companion compiles; it is not deployed.
- **B, the offline fuzz, extended** with two pure-logic probes. The G2 locator finds where the tight hose bend sits. The
  G6 probe (cost vs length) reproduces GPT finding B2.
- **E, the looks pre-review**, set up for GSS:
  - recipe `artboard/recipes/gss_states.json`: 18 subjects;
  - `jawa/gss_stage`, which applies the GSS state ops;
  - `artboard/autofix.py`, which triages each finding under the owner's policy: staging fixed silently, known art
    fixes applied, only judgement reaches him;
  - selftest: 18/18 passed.

  Design: `gss_looks_prereview.md`.
- **GPT source read.** The source went out in two halves, using gpt-6.1-sol at high effort; they took 7 and 10 minutes
  of wall time. It produced 35 findings: 31 confirmed against the code, 4 plausible, 0 refuted.
  See `gss_gpt_source_read_2026-10-06.md`.

| Finding | Found by | Cost to find | Old suite saw it? | Status |
|---|---|---|---|---|
| The 9 live hose FAILs (bend ~0.19 against 1.14) are the outlet blend: 951 of 965 tight bends sit inside it; without the outlet, 964 of 965 are fine | B (G2 locator), confirmed by GPT B5 | 5 s fuzz | D saw the symptom only | design call (G2) |
| The reel's port cache never initializes (`int.MinValue` overflow), so reels read "Not connected" and no inlet feed is drawn | GPT read (B4) | about 7 minutes of GPT wall time, plus a 1-minute code check | no: every live check called the probe's `Port(true)` first | open, real defect |
| Unpowered power strips are drawn twice as tall (aspect 1 against a 64×32 texture) | GPT read (A19) | same read | no (a visual defect nobody had looked at) | ART_FIX, catalogued in autofix |
| A fitting hose route is refused because the search prefers a cheaper, longer route (water cost) | GPT read (B2), then B (G6 probe) | GPT plus a 3 s probe | no | open |
| A laid hose can be longer than the hose (G1) | B (earlier); GPT B3 agrees | — | no | design call |
| Hose validation and relay flow only run once the hose has been drawn (map not viewed means no retract) | GPT read (B1) | same read | no | open |
| Taps: several can double-claim one surplus, and a tap that is switched off still drains | GPT read (A1, A2) | same read | no | open |
| 24 more findings, each confirmed or plausible (orders left dangling, cache keys, mesh leak, auto-link of enemy masts, …) | GPT read | same read | no | listed in the read doc |

**Costs, measured.** The fuzz with the new probes: hose family 5.1 s, all families 13.6 s, 690 of 690 checks.
The GPT read: two calls, 7 and 10 minutes of wall time, no tokens counted on our side. Building the companion: about
1 minute through `winbuild`. Not yet measured, because nothing has run live: the runner's live cost and the artboard
capture.

**Owed live** (game up on a GSS tier, bridge held, companion deployed with the game DOWN):
- `python.exe D:\Luke\dev\RimMandrake\src\RimMandrake\GimmeSomeSlack\northstar\gss_playtest_runner.py --recipe full`
- `python3 -m artboard.live gss_states --origin X,Z`, then `python3 -m artboard.autofix <out> --vision answers.txt`
