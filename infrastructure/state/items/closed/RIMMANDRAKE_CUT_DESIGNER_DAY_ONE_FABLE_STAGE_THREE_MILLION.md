# RIMMANDRAKE_CUT_DESIGNER_DAY_ONE_FABLE_STAGE_THREE_MILLION

Filed by the headless Conductor quick check of 2026-11-26 20:00 PST (run rm-role-conductor-1795752087), on the
Dispatcher escalation `role:Designer:overspend_day` of 2026-11-27T04:01:27Z ("RAISE FIRST: file an item and cut its
cost now; never starve it").

## spec

The Designer's advisory day is 8,000,000 weighted tokens (`dispatcher_schedule.json`, `roles[name=Designer]
.daily_token_cap`). Measured from `D:\ClaudeWork\rimmandrake\dispatcher\journal.jsonl` [measured]:

| run | concept | weighted used | budget |
|---|---|---|---|
| rm-role-designer-1795748853 | WreckedMachines (the all-Fable experiment, his go 2026-11-26 2:33 PM PST) | 3,396,273 | 7,940,000 |
| rm-role-designer-1795751318 | ExplosiveKnockback stage 3 | 1,204,328 | 3,940,000 |
| rm-role-designer-1795752087 | WreckedMachines stage 1, launched 04:01Z, live | running | 4,221,067 |

The runs draw on account `lukas`, whose runway reads 0.19 (alarm RUNWAY_LOW open since 2026-11-26T13:44Z), while
`system` reads runway 10 with 100% of the week left [measured, ops_watch 2026-11-27T04:02Z].

Cut the cost without starving the Designer. Candidates for the Conductor window to weigh:
- route Designer runs to the account with the most runway (`system`) while `lukas` reads RUNWAY_LOW;
- size the WreckedMachines stage budgets to the measured need of a Fable stage (3.4M), not 7.9M;
- keep the all-Fable experiment as he ordered it; a model change is not a cost cut here, it ends his experiment.

Not done in the quick run: the live run holds the concept, and the live Conductor window launched the experiment.

## verify

The next Designer day stays under its advisory cap, or the window records why the overspend is the price of his
experiment (a `--why` note on this item).

## criteria

Acceptance test: none, the cut is a Conductor call on a live experiment of the owner's (account route, budget size),
not code with a checkable output.
