## spec
Left by RIMMANDRAKE_TYPE_SIX_MORE_CONSUMABLES_READERS_IN_LIVE_LANES (critique 8 of
`design/specs/2026-11-18-pipeline-control-surface/02-gpt.md`: "Derive streaks from ordered, valid events"). Measured
2026-11-19: `testpilot_route.judge` already derives the Test Pilot streak (STREAK = 3 non-pass runs in a row) from the
item's ordered runs since its last sitting, with every voided run taken out; a voided middle run breaks it. What is
missing is the `pipe` line: no `pipe set|add|reset|limit <ITEM> pilot_streak` moves it. Not small, so not done there:
the account is an ITEM (not a mod: pipeline_control.ACCOUNT_KEY needs an item-id subject), its measure reads the ledger
(model.load and judge's run filter), and `pipe show` lists mods only.
Build: a RESOURCES row `pilot_streak` keyed by item id (ACCOUNT_KEY, as `refusals`), judge() comparing
PC.used(item.id, "pilot_streak", max(whole, worst)) with PC.limit(item.id, "pilot_streak", STREAK), an unreadable store
routing nothing new (say so in the verdict), a promise on `design/specs/2026-11-19-consumable-readers/boundary.md` with
its same-named test in selftest_pipeline_control.py, and the census token STREAK.
Acceptance test: `python3 src/RimMandrake/rimflow/acceptance/pilot_streak_account_accept.py` (exit 0, 6 checks). Seen
failing on base 2026-11-19 (3 failures: pipe refuses `pilot_streak`, judge ignores the store); its two control checks
(base streak, voided middle run) pass on base.

## refs
file: src/RimMandrake/rimflow/testpilot_route.py
file: src/RimMandrake/rimflow/pipeline_control.py
file: src/RimMandrake/rimflow/acceptance/pilot_streak_account_accept.py

## criteria
- `pipe limit|add <ITEM> pilot_streak` changes testpilot_route.judge's verdict, each with its undo.

## verify
python3 src/RimMandrake/rimflow/acceptance/pilot_streak_account_accept.py
