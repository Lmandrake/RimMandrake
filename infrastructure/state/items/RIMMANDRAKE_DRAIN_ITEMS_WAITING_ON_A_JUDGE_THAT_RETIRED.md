## spec
Found by the pipeline sleeper census (`design/RimMandrake/pipeline_sleepers_census_2026-11-15.md`). Relentless was
retired 2026-11-13 with nothing to resume, and with it the only program that ran its binding-repair judge
(`RELENTLESS_WIRE_BINDING_JUDGE_NOBODY_RUNS` already said no program launched it). 46 open items were still blocked
with kind `judge` by a Relentless snag (43 `binding_repair`) on 2026-11-15; most of their block reasons say the work
already landed (a sha on origin) and only the proof line was unrunnable in Relentless's box. Nothing will ever lift
these blocks, and `rimflow next` never offers a blocked item.

For each item listed by the acceptance test: if its block names a landed sha on origin/main, run its proof in a plain
shell (the rebind the block describes), record `rimflow verify --sha <sha> --level L0`, unblock and close on that sha;
if the proof fails, unblock to ready with the corrected proof line in the item; if the item is dead, drop it with the
probe. `ARENA_TRIAL_RETIRE_HUNDRED_GIGS_IDLE` is the worked example (landed 1f0e666566dc, pass recorded 2026-11-07).
Mod-content items in the list go through the same steps; they are listed because their block is pipeline machinery.

Acceptance test: `python3 src/RimMandrake/rimflow/acceptance/judge_blocked_drained_accept.py` exits 0 printing
`PASS 0 open items wait on the retired judge`. Watched failing on 464c69ccf0 (45 listed after the census's drops).
