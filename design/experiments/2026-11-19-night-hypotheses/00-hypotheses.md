# Night hypotheses on running this factory better, 2026-11-19

Item `RIMMANDRAKE_TRY_NIGHT_HYPOTHESES_ON_RUNNING_FACTORY_BETTER`. Written by a detached designer (Fable) on the
owner's night order of 2026-11-19 12:43 AM PST: *"Take some risks and keep things going slowly and thoughtfully
overnight. Maybe make some new hypotheses on how we could do this all better and run a few experiments to play
around with possibilities. Tell me about it in the morning."* Nothing here is a ruling. Nothing live was changed.

**How to read a tag.** [measured: source] is a number this run read or counted tonight. [guess ~N%] is an estimate
with my confidence. A [model] figure is a replay under stated assumptions, not a measurement.

**The data all of it rests on** (read-only): 106 session transcripts of detached helpers and 19 of the seat window,
last written between 2026-11-18 12:00 AM PST and 2026-11-19 12:50 AM PST; the Conductor log from the same start
(354 timed entries, 129 run reports); the detached run records; the ledger; the card store (127 cards, 303
questions). Scratch outputs: `D:\ClaudeWork\scratch\night_hypotheses_20261119\`. Tools: `tools/` beside this file.

**Three terms, each with one meaning here.**
- **Starting context:** everything a session holds at its first request, before it has done anything: the tool
  definitions, both `CLAUDE.md` files, the skills list, the brief. Median 68,118 tokens for a detached helper
  [measured: `tools/context_rent.py`, 106 sessions, range 60,686 to 73,601].
- **Context rent:** the weighted tokens a session pays for cache reads, that is, to read again on every request
  what the session already holds.
- **Entry cost:** the weighted tokens a session pays for cache writes, that is, for text entering its context for
  the first time (a file read, a command's output, its own earlier replies), or again after the cache went cold.

**Searched before proposing.** `design/RimMandrake/innovations.md` (two lines, neither overlaps);
`design/RimMandrake/perpetual_orchestrator_context_2026-10-26.md` (a cost rule for when the *Conductor window*
continues, hands off or compacts: prior art for the window, silent on helpers); the review-growth design
(boundary page, two looks, shadow and drill: not restated below); `ticket_preflight.py`, `left_open_continue.py`,
`spend_watchdog.py`, the Evidence-for-Ask ruling and the daily digest (existing machinery the hypotheses below lean
on or argue with). No file in `src/RimMandrake/rimflow` or `design/` mentions sharing the starting context between
runs or measuring first-request cache writes [measured: `grep`, 0 hits in `detached_helper.py`; the three design
files that mention cache prices do so for the window only].

---

## The ten hypotheses

Each has: the claim, the belief it overturns, the measured fact that makes it plausible, what would prove it false,
the cheapest experiment, and where it stands this morning.

### `RIMMANDRAKE_CUT_RUNS_AT_CONTEXT_LINE_RENT_GUESSED_HALF`

- **Claim.** A helper should be cut and restarted from a short note whenever its context passes a fixed size,
  because a long run spends most of its tokens re-reading its own past.
- **Overturns.** "One agent keeps context" is the cheap way to do a lane of tickets (the name of last night's item
  `RIMMANDRAKE_FIX_OPEN_CODEX_FINDINGS_ONE_AGENT_KEEPS_CONTEXT`).
- **Fact.** Several runs in the log show millions of weighted tokens in a few hundred seconds, and the longest
  sessions reach 968,289 tokens of context [measured: `tools/context_rent.py`].
- **False if.** Context rent is under 30% of spend, or a replay with cuts costs more than the real sessions.
- **Cheapest experiment.** Replay the transcripts. **Run tonight: `01-context-rent.md`.**
- **Stands.** **Refuted as stated.** Rent is 42% of detached spend, not over half, and the replay with cuts costs
  more in five of six settings. The reason is the next two hypotheses: starting is expensive.

### `RIMMANDRAKE_SHARE_STARTING_CONTEXT_ACROSS_RUNS_EACH_REWRITES_IT`

- **Claim.** If every helper started from a byte-identical prefix (same working path, same rule text, the brief
  last), a run starting within an hour of another would read its starting context from the cache, not write it.
- **Overturns.** A run's start is free; only its work costs.
- **Fact.** At its first request a helper writes a median 56,625 tokens to the cache and reads only 11,266 from it;
  105 of 106 sessions read between 11,000 and 14,000, so about 11,000 tokens are shared today and the rest is
  written new by every run. Those first writes total 14.7 million weighted tokens, 4.8% of detached spend; read
  from cache they would cost 0.28 million [measured: `tools/entry_and_ttl.py`]. What makes the prefix differ is
  not measured; each helper runs in a clone named for its item, and that path appears in its context [guess ~60%
  that the path is the main cause].
- **False if.** Two trivial runs launched from one fixed path, minutes apart, still each write the full starting
  context.
- **Cheapest experiment.** Exactly that: two one-turn runs from one bind-mounted path, read the first request's
  usage. It needs a launch, so it was not run tonight (the night brief forbids launches).
- **Stands.** Plausible, untested. The ceiling on the saving is measured: about 14 million weighted tokens a day.

### `RIMMANDRAKE_TRIM_RULEBOOK_PER_ROLE_FIXER_CARRIES_ART_RULES`

- **Claim.** A helper should start with the rules of its role only. Today a fixer of a Python selftest starts with
  the rules for art judging, flyers, sea biomes, Slack and the owner's publication list.
- **Overturns.** Rules are free to carry, so every agent should carry all of them.
- **Fact.** The starting context is re-read on every later request. That standing charge is 33.2 million weighted
  tokens, 10.7% of detached spend; with the first write it is 47.9 million, 15.5% [measured:
  `tools/context_rent.py`, `tools/entry_and_ttl.py`]. The two `CLAUDE.md` files are 77,486 bytes together
  [measured: `wc -c`], about 20,000 of the 68,000 tokens [guess ~60%].
- **False if.** A helper run with a role-sized rulebook breaks a rule that the full rulebook would have stopped,
  at a rate that costs more than 15% of spend to repair.
- **Cheapest experiment.** Run ten ordinary fix tickets twice, full rulebook and role-sized, and compare closes,
  refusals at `./publish`, and spend. About 20 million weighted tokens [guess ~40%]. Not run.
- **Stands.** The charge is measured; whether the rules earn it is not.

### `RIMMANDRAKE_DIGEST_BIG_READS_WHOLE_FILES_FILL_HALF`

- **Claim.** A helper should never read a file over about 20,000 characters into its own context. A script or a
  cheaper reader returns the lines that matter.
- **Overturns.** Reading the whole file is the careful thing to do.
- **Fact.** Tool results put 50.1 million characters into helpers' contexts. 923 `Read` calls carry 49.4% of that,
  and 86% of what `Read` carries is in results over 20,000 characters. 9,893 `Bash` results carry the other half
  [measured: `tools/what_fills_context.py`]. Entry cost is 36% of detached spend, and 49% for Fable, whose cache
  write is priced at 80 times its cache read [measured: `01-context-rent.md`; the ratio is from `MODEL_PRICES`].
- **False if.** Runs that digest big files miss facts a whole read would have caught. The biome second-reader runs
  are the hard case: their job *is* to read every file to the end, and the owner had already caught trimmed
  readings (`RIMMANDRAKE_CHECK_RESUMED_READERS_PAGES_FOR_TRIMMED_READING`).
- **Cheapest experiment.** Replay: for each big `Read`, count how many of its lines the session later quotes or
  edits. A low share means the digest loses little. About an hour of scripting. Not run.
- **Stands.** The fact is measured. The claim is risky exactly where reading in full was his order.

### `RIMMANDRAKE_RESTART_FRESH_AFTER_LONG_STOP_COLD_RESUME_REWRITES`

- **Claim.** After a stop of more than an hour, a helper should start fresh from its note, not resume its session.
- **Overturns.** Resume is the cheap way back, because the agent keeps what it learned.
- **Fact.** 26 runs resumed a session. 16 resumed cold and wrote their whole context back to the cache at the first
  request: 12.5 million weighted tokens, a median 0.50 million each, 19% of those runs' own spend. A fresh start
  writes a median 0.11 million (Opus) or 0.22 million (Fable) [measured: `02-relaunch-and-log.md`].
- **False if.** Fresh starts re-read more than 0.3 to 0.4 million weighted tokens of files to get back to where the
  note says they were.
- **Cheapest experiment.** At the next fleet stop of over an hour, resume half the lanes and restart half from
  their notes; compare spend to the next close. Free, but it needs a stop. Not run.
- **Stands.** The cold-resume cost is measured; the fresh-start cost to catch up is not.

### `RIMMANDRAKE_TYPE_LEFT_OPEN_NOTES_FOUR_RELAUNCHES_IDLE`

- **Claim.** A `LEFT OPEN:` note should name who acts next (a helper, the Conductor, the owner, a date) as a field
  the launcher reads, and only "a helper" relaunches.
- **Overturns.** An item left open should be relaunched; the brief's prose about putting a wait on it is enough.
- **Fact.** Of 18 relaunches that ended, 4 landed nothing because nothing was a helper's to do ("still blocked by
  the SteveDesktop soak", "Nothing was redone", "Nothing was left for a helper to do") [measured count; the label
  is my reading of each run's own report, ~80%].
- **False if.** Such relaunches are under 1 in 20, or cost nothing worth a rule.
- **Cheapest experiment.** Count them in the log. **Run tonight: `02-relaunch-and-log.md`.**
- **Stands.** **True in count, trivial in cost:** 4 of 18, but 1.3 million weighted tokens, 0.4% of spend. One of
  the four found and fixed the relaunch defect itself. Not worth building.

### `RIMMANDRAKE_SPLIT_LOG_ACTS_FROM_RECORD_HALF_ASK_NOTHING`

- **Claim.** The Conductor's log should be two streams: lines that ask for an act, and the record. The Conductor
  reads only the first at the start of a turn.
- **Overturns.** One log that holds everything is the safe design, because nothing is lost.
- **Fact.** Of 354 timed entries, 126 (36%) are a second "clone returned" line for a run already reported, and 47
  (13%) are escalations that say "It goes by itself once this clears". Together they are 49% of entries and 59% of
  characters [measured: `02-relaunch-and-log.md`]. The Conductor reads the last 40 lines of this log every turn.
- **False if.** Under a quarter of entries ask for nothing, or a Conductor acted usefully on an echo line.
- **Cheapest experiment.** The count above (run). Next: replay ten Conductor turns with a filtered tail and see if
  any answer changes. Not run.
- **Stands.** Supported by count (one point under my own "over half" line by entries, over it by characters).

### `RIMMANDRAKE_SEND_CARDS_AS_NOTICES_WITH_UNDO_OVERRULED_OFTEN`

- **Claim.** A card with a recommended option should not block: the factory acts on the recommendation at once and
  the card becomes a notice he can undo.
- **Overturns.** A real choice must wait for him.
- **Fact (before measuring).** The last cards in the store all show "(Recommended)" picked.
- **False if.** He departs from the recommendation more than about 1 time in 10.
- **Cheapest experiment.** Count the card store. **Run tonight: `03-cards-tickets-and-product-share.md`.**
- **Stands.** **Refuted.** Of 221 questions that carried a recommended option he picked it plainly 127 times (57%).
  He picked another option 38 times, answered in his own words 48 times, and added words to the recommendation 8
  times. A card he overrules 4 times in 10 is a real question.

### `RIMMANDRAKE_BUDGET_FACTORY_SHARE_TICKETS_BORN_IN_RUNS`

- **Claim.** Work on the factory's own machinery should have a fixed share of each night's tokens, set by him. The
  queue cannot set it, because the queue of factory work refills itself.
- **Overturns.** Fix every pipeline defect when found (the standing ruling), and the queue will drain.
- **Fact.** From 2026-11-12 to 2026-11-18, 1,309 tickets were filed and 869 of them (66%) were filed from inside a
  run. Filed tickets outnumbered ended ones on six of the seven days; only the 2026-11-18 sweep of old tickets
  (540 ended) made the week net down by 126. Of detached helper spend in the data window, 58% went to items about
  the factory and 42% to items about the game's design; no detached run built mod code [measured: ledger and log;
  the factory-or-game label is mine, by item name, ~85%; mod builds run in the Maturation Pipeline and are not in
  this count].
- **False if.** With no budget, the filed-to-ended ratio stays under 1 for a week without a hand sweep.
- **Cheapest experiment.** Watch that ratio for the week after the boundary-page rule took hold (it should cut
  births from reviews). Free. A budget itself would be his decision, and a change to a standing ruling.
- **Stands.** The numbers are measured; the remedy is his call, and I would not enact it from one week of data.

### `RIMMANDRAKE_AUDIT_ON_SURPRISE_ONLY_PREDICTION_SEALED_FIRST`

- **Claim.** Before it works, a builder writes a sealed prediction: files it will touch, lines it will add, tests
  it will add, tokens it will need. A second look happens only when the result leaves the prediction.
- **Overturns.** Every change of a kind gets the same checking, and a reader is the only detector of a risky fix.
- **Fact.** Lines written by a review repair drew 14 to 25 claims per 1,000, older lines about 3, and each repair
  added 370 to 420 lines [measured by the analyst: `design/specs/2026-11-18-review-growth-cycle/01-design.md`].
  A repair's size was a louder signal than anything a reader said, and nothing read it.
- **False if.** Builders' predictions are so loose that nothing is ever a surprise, or so tight that everything is.
- **Cheapest experiment.** Replay: for last night's closed fix tickets, take the ticket text as the prediction and
  the commit's line count as the result; see whether the largest overshoots are the fixes that later drew claims.
  Only one file has per-round claim data, so tonight it would have been four data points. Not run.
- **Stands.** Untested. The most speculative of the ten, and the one I would most like to see tried.

---

## One finding that is not a hypothesis

While checking experiment one's totals against the Conductor log, the log's figures for resumed runs did not fit.
**A resumed run's recorded weighted tokens are the whole session so far, so the earlier runs are counted again:**
26 of 26 resumed runs, 81 million weighted tokens over-counted in a logged 374 million [measured twice, from
transcripts and from run records]. Filed, with its acceptance test seen to fail, as
`RIMMANDRAKE_COUNT_RESUMED_RUN_TOKENS_ONCE_SESSION_TOTAL_LOGGED`. Detail: `02-relaunch-and-log.md`.
