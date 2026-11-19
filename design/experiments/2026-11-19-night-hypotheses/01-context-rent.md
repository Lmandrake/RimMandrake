> HISTORY: retired era, see design/RimMandrake/retired_eras_index_2026-11-18.md. This file's mentions of Relentless, Artisan, Whittle, FOUNDRY, RimPulse or rimflow v3 are history (that machinery no longer runs); the rest is as current as its own status says.

# Experiment: how much of a run's spend is re-reading its own past ("context rent")

Item: `RIMMANDRAKE_TRY_NIGHT_HYPOTHESES_ON_RUNNING_FACTORY_BETTER`. Tests hypotheses
`RIMMANDRAKE_CUT_RUNS_AT_CONTEXT_LINE_RENT_GUESSED_HALF`, `RIMMANDRAKE_TRIM_RULEBOOK_PER_ROLE_FIXER_CARRIES_ART_RULES`
and (found on the way) `RIMMANDRAKE_SHARE_STARTING_CONTEXT_ACROSS_RUNS_EACH_REWRITES_IT` in `00-hypotheses.md`.
(The section below named them by working titles when it was written; only this header was renamed afterwards.)

**Context rent**, as used here: the weighted tokens a session pays for cache reads, that is, for the model to
read again, on each request, everything the session already holds. It is not new work.

## Written before running (2026-11-19, 12:50 AM PST)

- **Instrument.** `tools/context_rent.py` reads Claude Code session transcripts (`~/.claude/projects/<clone>/<session>.jsonl`),
  read-only. It takes one usage record per API request (deduplicated by message id), weighs each field with
  `role_launch.model_weights` (weighted_v2, the price table is imported, not restated), and splits a session's
  spend into: cache reads (rent), cache writes (new context entering), uncached input, and output.
- **Population.** Every transcript in a detached-helper clone (`...-rm-relentless-clones-*-det`) and in the seat
  clone (`-home-mandrake-rm-bench`) last written on or after 2026-11-18 00:00 PST.
- **Counts FOR the hypothesis:** rent is over half of all weighted tokens in detached runs, and the rent share
  rises with session length (the longest fifth of sessions pays a clearly higher share than the shortest fifth).
- **Counts AGAINST:** rent under 30% overall, or no rise with length. Then the cut of work does not matter much
  for spend, and "one agent keeps context" is the right default.
- **Rulebook charge FOR:** the context held at a session's first request (rules, skills list, brief), re-read on
  every later request, is over 10% of the run's spend. **AGAINST:** under 3%.
- **Counterfactual (a model, not a measurement).** Replay each session as if it were cut whenever its context
  passed a line L, restarting with the first-request context plus a handoff, and re-acquiring a fraction r of
  the dropped context. Reported for L = 100k and 150k tokens, r = 0, 0.25, 0.5. All such figures are [guess].
- **My guess before looking:** rent share about 55% [guess ~50%]; rulebook charge about 8% [guess ~40%].
- **Known blind spots, stated before running:** subagent side transcripts are separate files and are not
  counted; a transcript rewritten by a resume may repeat requests (deduplicated by message id); the transcript
  total is compared with the Conductor log's figure for three runs as a sanity probe before any share is trusted.

## Result (2026-11-19, 12:55 AM PST)

**Could the instrument see?** Yes. 106 detached sessions and 19 seat-window sessions were found, all with usage
records, none with an unknown model. The same tool pointed at a path that matches nothing prints
`VERDICT could-not-look` and exits 3. Four runs that never resumed were compared with the Conductor log: 471,026
and 1,351,852 and 439,172 and 194,229 logged; 0.471, 1.352, 0.439 and 0.194 million from the transcripts
[measured]. (The same probe exposed the resumed-run double count: see `02-relaunch-and-log.md`.)

**Where 309.6 million weighted tokens of detached-helper spend went** [measured]:

| part | weighted tokens | share |
|---|---|---|
| cache reads (context rent) | 129.8 million | 41.9% |
| cache writes (entry cost) | 112.1 million | 36.2% |
| output | 67.7 million | 21.9% |
| uncached input | under 0.1 million | 0.0% |
| of the rent: re-reading the starting context | 33.2 million | 10.7% |

| sessions by length | sessions | requests each | spend | rent share | median largest context |
|---|---|---|---|---|---|
| shortest fifth | 21 | 1 to 31 | 7.0 million | 17% | 96,000 tokens |
| middle | 64 | 32 to 162 | 179.6 million | 33% | 283,000 |
| longest fifth | 21 | 163 to 342 | 123.0 million | 57% | 459,000 |

| model | sessions | spend | rent | entry cost | output |
|---|---|---|---|---|---|
| Opus 5.5 | 67 | 168.2 million | 55% | 26% | 19% |
| Fable 5.2 | 31 | 138.9 million | 26% | 49% | 25% |
| Sonnet 5.5 | 8 | 2.4 million | 41% | 39% | 20% |

The seat window (19 sessions): 28.2 million, rent 34%, entry cost 41%, output 25%. The window is 8% of the two
populations together, so the helpers, not the window, are where spend is decided.

**Against my written lines.**
- *Rent over half of spend:* **no.** 41.9%. It is over half only in the longest fifth of sessions (57%) and for
  Opus (55%). My guess of 55% was wrong for the population.
- *Rent rises with length:* **yes**, 17% to 33% to 57%.
- *Rulebook charge over 10%:* **yes, barely.** 10.7% as rent; 15.5% with the first write of it (14.7 million,
  from `tools/entry_and_ttl.py`). My guess was 8%.

**The replay with cuts [model, not a measurement].** Cut at a context line L, restart with the starting context
plus a 6,000-token note, re-acquire a fraction r of what was dropped, pay one cache write for each restart:

| line L | r = 0 | r = 0.25 | r = 0.5 |
|---|---|---|---|
| 100,000 tokens | 131% of real spend (875 cuts) | 166% | 249% |
| 150,000 tokens | 96% (298 cuts) | 112% | 144% |

Cutting saves 4% in one corner, where nothing dropped is ever needed again, and costs more everywhere else. The
model is crude: it prices a restart, not the work a restarted agent does to find its place. A better model would
make cutting look worse, not better.

**What I did not expect.** Entry cost is nearly as large as rent, and for Fable it is twice the rent. A token
entering context costs Fable 80 times what re-reading it costs, and Opus 40 times [from `MODEL_PRICES`]. So the
lever is *what a run reads into context and how often it starts*, not how long it runs. Two more readings follow
from that, both [measured]:
- `tools/what_fills_context.py`: tool results put 40.5 million characters into helpers' contexts, each result counted
  once; `Read` carries 40.5% in 581 calls, and 88% of that is in results over 20,000 characters; `Bash` carries 59.3%
  in 9,505 calls. (The tool's first version counted 9.6 million characters twice; `06-large-reads.md`.)
- `tools/entry_and_ttl.py`: every session writes its starting context new (median 56,625 tokens written, 11,266
  read at the first request).

**A second replay, a null [model].** Would a 5-minute cache life (cheaper writes, but a silence over 300 s
re-writes the whole context) cost less than the 1-hour life in use? Over all sessions: 100.2% of real spend, a
wash. By model: Fable 83%, Opus 115%, Sonnet 95%. 146 of 10,048 requests followed a silence over 300 s, in 41 of
106 sessions. I do not know that the cache life can be chosen per run, and weighted tokens follow list prices,
which may not be how the subscription meters cache writes. No action follows from this.

**Not looked at.** Subagent side transcripts (their spend is in the log figure when a run used them; the four
probed runs matched without them). Why the starting context differs between runs. Sessions older than the window.
