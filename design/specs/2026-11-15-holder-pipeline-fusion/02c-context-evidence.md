# 02c context evidence: fixes landing late in context (Relentless era)

## Step 1: written measurement
Not found [measured: grep of /mnt/d/ClaudeWork/rimmandrake *.md, infrastructure/state/handoffs, ledger events, for 250k / 250,000 / past 200k / late in context / after compaction / context size].
Nearest hits, none about fixes:
- /mnt/d/ClaudeWork/rimmandrake/artisan_now_build/out/ARTISAN_NOW.md:260 "Context: 170k; warned at 250k, must wrap up at 350k." (artisan wrap-up limit)
- infrastructure/state/handoffs/BENCH_REBOOT_HANDOFF_202611060419.md:103 "Agent spawns are refused once the window drains past 200k tokens" (spawn rule)
- base/design/RimMandrake/baseline_two_seat_system_2026-10-26.md:77 (cost is the whole context; not fixes)

## Step 2: measured from transcripts
Method: /tmp/ctx.py over /home/mandrake/.claude/projects/*relentless-clones*/*.jsonl. Context at a turn = input + cache_read + cache_creation of the latest assistant usage. A landing = a user tool_result containing "PUBLISHED " dated 2026-11-02..11-12; context = the preceding assistant turn's size.
- Files scanned: 3260 [measured]; with usage: 3221; with >=1 landing: 2015 [measured]. Landings: 2825 [measured].
- Context at landing: p10 61k, p50 92k, p90 176k [measured].
- Share of landings above: 100k 41.8% (1181); 150k 16.9% (477); 200k 7.4% (208); 250k 3.9% (111); 300k 3.2% (91); 400k 2.2% (63) [measured].
- Peak context per session: p50 83k, p90 168k, max 750k [measured]. Sessions peaking >200k: 207; >250k: 105; >300k: 54 [measured] (of 3221, about 3.3% pass 250k).
- Models by assistant turns: opus-5-5 195k, sonnet-5-5 1.9k, fable-5-2 484 [measured]. No "[1m]" in the names; peaks of 750k show the window was at least that large (1M likely) [guess ~80%].

## Caveats
- Peak figures count all relentless-clones sessions, not date-filtered; landings are date-filtered.
- "PUBLISHED " match is loose (any tool_result containing it); may count a few reads of text that mentions it [guess ~5% inflation].
- Landing is not a fix: a PUBLISHED can be a ledger or doc commit. I did not separate fixes from other commits.

## Reading
The data does not show "significant numbers of fixes after ~250k": 3.9% of landings (111 of 2825) were above 250k. Most landed under 100k-176k. Late-context landings exist, but they are a small tail; the 250k lesson as the owner states it is not supported by this proxy. A narrower cut (fix commits only, long-lived holder sessions only) was not run.

## Conditional measure (added by the design run, `/tmp/ctx2.py`, same transcripts, same landing rule)

The fleet-wide share above is diluted by the many short capped helpers that never grow large (session peak p50 83k). The
question that bears on a holder is: **in sessions that did grow large, when did their work land?** `[measured]`

- Sessions that peaked above 200k and landed anything: **74**, with **249** landings.
- Of those 249 landings, **208 (84%) came after 200k** and **111 (45%) after 250k**.
- **51 of the 74 sessions (69%) landed nothing before 200k**: a 200k cap would have ended them before their first landing.
- Sessions peaking above 250k: 105.

Limits: a landing is any `PUBLISHED` (code, docs and ledger alike), not a verified fix; long sessions may be long *because*
their problem was hard, so this shows that late work happens, not that a restart with a packet would have failed to do it.
Where our 200k lives: `src/RimMandrake/rimflow/dispatcher_schedule.json` (window backstop: `backstop_ctx_tokens` 110000
soft, `backstop_hard_tokens` 200000 hard; `_why_backstop`: his card of 2026-11-01, "Same limits as Foundry"). It is our
setting, not the model's: the sessions above ran on `claude-opus-5-5` with a peak of 750k.
