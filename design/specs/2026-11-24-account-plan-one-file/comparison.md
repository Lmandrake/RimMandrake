# COMPARISON: today's switching plan against the account plan (`./acct`), and the decision

Written 2026-11-24 by the run that owns the item. Each figure is marked `[measured]` or `[guess ~N%]`. The census is
`census.md`; the replay is `replay.md` (made by `src/RimMandrake/Utils/account_plan_replay.py`, 30 s).

## The decision

**Go on with the new tool.** The rule of the brief: go on if the new tool removes a class of fault that happened and
its design shows no new way to lose runs.

- It removes four classes that happened: the stale marker (rows 9, 19); the rule with no field (rows 5, 6, 10, 11, 12,
  16, 20); the brake or allowance with no end and no why (rows 4, 5, 8); and the switch for the order alone, which
  caused three of today's faults (the wrong drain at 18%, the refused starts, the hand-written hold).
- No new way to lose runs: the switch, the save orders, the pause and the fleet stop are the old actuator's code,
  unchanged, and `tick` only hands it a decision. A switch above the line stops a live run in two cases only: the
  owner's `./acct switch <account> --now`, and a run that is still live 2 h after a weighed rescue drain began (the
  old actuator's own rule of 2026-11-20, which today applies to every switch for the order).
- Extending `switching_plan.py` in place was weighed (solution 1 of `01-design.md`). It keeps the markers and the
  rule "first eligible in the order", so it keeps the two classes that cost most. Not taken.

## The two measures, over 2026-11-10 to 2026-11-24 (`replay.md`)

| run | points erased at resets | switches | switches off an unfinished account | burn that found no account |
|---|---|---|---|---|
| what happened `[measured]` | 6 | 11 | not recorded | not recorded |
| the old rule, modelled | 18 | 16 | 8 | 20 of 698 |
| the new plan, a moment with no live run at each pass, modelled | 7 | 13 | 4 | 21 of 698 |
| the new plan, never such a moment, modelled | 7 | 11 | 2 | 21 of 698 |
| the new plan, never such a moment, and a rescue never refuses a start, modelled | 50 | 8 | 0 | 67 of 698 |

- The model: the burn of each interval is what the readings show; it lands on the account that the rule keeps live; a
  point is the same work on each account; a switch is instant. Both rules run on the same burn and the same old plan
  files of each day (18 versions from git), so the rows "modelled" compare like with like `[measured, in the model]`.
- The old rule against the new plan: 18 points erased against 7, and 16 switches against 11 to 13
  `[measured, in the model]`.
- What happened was better than the old rule alone (6 against 18) because people stepped in by hand: holds, hand
  switches, hand-written exceptions (census rows 9 to 16 and 19) `[measured]`. The new plan reaches about the same
  result (7) with none of those acts `[measured, in the model]`.
- Refused starts for a switch that no level forced `[measured]`: 39 min in 8 passes, all on 2026-11-24 (the drain of
  lukas at 18% to 20%). The new plan reads `normal` at each of those 8 passes (`replay.md`, cause STAY).
- The last row is the reason for the weighed drain (design rule 5). Measured from the control store, 2026-11-18 to
  11-24: 11.5% of the 5-min passes had no live detached run; the longest stretch with one always live was 50.8 h.

## The passes: 4,095 decisions of the old engine, decided again by the new plan `[measured]`

Same decision: 3,182. Different with a named cause: 913, in 22 episodes. Unexplained: 0.

| cause | passes | episodes | in whose favour |
|---|---|---|---|
| PLAN_DATA: the old engine's line was not the line of its committed plan file | 397 | 3 | neither: the old plan was changed by hand outside git, which the new file ends |
| NO_REFUSAL_ABOVE_THE_WARNING: the old soft notice above the warning line | 312 | 7 | new (his rule 3) |
| RESCUE: one episode, 2026-11-12 to 11-13, that follows from the first PLAN_DATA episode (the old engine left Steve's account at an unrecorded 62% line; the plan, reading 52%, would go back for 10 points) | 146 | 1 | neither: the cause is the unrecorded line |
| WARNING_LINE: the plan ends an account at its 2% warning line; before 2026-11-24 the old engine ended it at its 1% line | 42 | 8 | same as the old engine since the account-end build of 11-24 |
| UNREADABLE_LEVEL: the old engine went soft on an ESTIMATE at 52% and 86% left | 8 | 2 | new |
| STAY: the drain of lukas for the order, 2026-11-24 1:25 to 2:00 PM | 8 | 1 | new (today's fault) |

## Each census row: today against one command

Minutes are the time to change the rule, from his word to the rule in force. Today's minutes are from `census.md`
`[measured]` where a stamp exists. The new tool's time is one command that answers in under a second `[measured: 0.1 to 0.6 s]`.

| # | today: what was needed | minutes | the one command | verdict |
|---|---|---|---|---|
| 1 | two JSON homes (`slot_rules.json`, the plan), a date field by hand | unknown | `./acct step set steven leave=52 "when=hours_since_reset <= 48"` | better |
| 2 | a new engine; a relayed rule changed his order in code; reverted | 34, then hours | `./acct order steven system lukas` | better |
| 3 | hand JSON edits | 1 to 20 | `./acct set numbers.last_account_floor_pct=2 steps.steven.leave=52` | better |
| 4, 8 | a bare `HOLD` file, a stopped timer, a rename to lift | unknown | `./acct hold --for 2h --owner-said "..."` | better |
| 5 | a transient systemd timer with no expiry | unknown | `./acct line steven 20 --until-reset` | better |
| 6 | a number worked out by hand | unknown | `./acct line steven entry-50 --until-reset` | better |
| 7 | a code change after the engine undid his hand switch | hours | none needed (the live account stays); `./acct pin` to say so | better |
| 9 | a new code mechanism, then a hand-written JSON exception; a stale marker kept Steve out | hours | `./acct order system steven lukas --until-reset steven --line steven=35` | better |
| 10 | two hand JSON edits; time of day had no field | under 10 each | `./acct step add steven-overnight --use steven --leave 25 --when "clock >= 22:00 or clock < 06:00" --until-reset` | better |
| 11, 12, 16 | hand switches; 9 runs killed (4.73M weighted tokens); a line moved to force a switch | 110 | `./acct switch steven` (goes when no run is live) | better |
| 13 | a hand JSON edit and a hand delete | about 0 | `./acct line system 1` or `./acct order system lukas steven` | same |
| 14 | the actuator's drain | 14 | not the plan tool's; unchanged | same |
| 15 | two hand edits of one long JSON line in 14 min, fleet live | 7 and 7 | `./acct order system steven lukas --until-reset steven --line steven=3 --line system=3` | better |
| 17 | prose in `standing_rulings.md` and the skill | unknown | `./acct set numbers.evening_share_pct=0` (printed by `./acct plan`) | better |
| 18 | a code build, then 14 numbers in JSON | 68 | `./acct set numbers.account_end.warn_pct=2 ...` | same for the build; better for each later change |
| 19 | a code change to lift a marker | about 60 | none needed (the level is read each pass) | better |
| 20 | prose in briefs; older numbers in two files | unknown | `./acct line codex 25`; the reset-day rule is `numbers.reset_day`; `./acct can-use codex` | better |
| 21 | `slot_allocator.py set` | unknown | not the plan tool's; `./acct status` shows the burn and the Burn Mode target | same |

Counts over the 21 rows: plainly better 17 (rows 1 to 12, 15, 16, 17, 19, 20), the same 4 (rows 13, 14, 18, 21),
worse 0 `[measured: each "better" row has a passing check of its name in selftest_account_plan.py]`.

## What the switch costs and risks

- It sits under every running agent. A wrong decision moves the fleet to the wrong account, or stops it. Guards: 64
  promises with a check each and a planted fault each; shadow passes before the cut-over; the old engine stays in the
  repo, and the undo of the cut-over is one command.
- Two behaviours change on purpose, and the Conductor should know them before the cut-over:
  1. A reset no longer pulls the machine to the account that is first in the order. The 2026-10-28 ruling ("awkward":
     the machine was left on lukas when system reset) is replaced by his words of 2026-11-24. The week ahead still
     sends the machine to an account whose allowance a reset would erase, when that is worth a switch.
  2. The soft notice above the warning line is gone (312 passes in two weeks). New runs start until the warning line.
- The numbers `switch_cost_pts` = 3 and `rescue.drain_h` = 2 are delegated choices `[guess ~60% that he keeps both]`.
  Each is one command, and `./acct whatif -- set numbers.switch_cost_pts=5` shows the week ahead before the change.
- Not wired yet (one ticket, after the cut-over): the allocator and Codex's door do not read `burn_mode.json` or
  `./acct can-use codex`; the skill and `slot_rules.json` still hold their old rule text.
- UNMEASURED: whether one point of Steve's account is the same work as one point of the others; how many weighted
  tokens one point of a week is (so `switch_cost_pts` is a judgement, not a conversion).
