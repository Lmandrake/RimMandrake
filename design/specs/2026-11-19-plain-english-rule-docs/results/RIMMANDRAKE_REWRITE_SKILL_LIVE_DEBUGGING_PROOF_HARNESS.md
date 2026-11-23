# Result: `RIMMANDRAKE_REWRITE_SKILL_LIVE_DEBUGGING_PROOF_HARNESS`

Part of batch `RIMMANDRAKE_REWRITE_SKILLS_IN_CURATION_SESSIONS_ONE_SKILL_EACH` (`batch_plan.md`, order 17). Run 2026-11-23.
File: `skills/live-debugging-proof-harness/SKILL.md`.

Base: 5d750f4059572f1c656ea6d4974d8f18badff111

Also: design/RimMandrake/CLAUDE.history.md

The front matter is byte-identical, the `description` included. No text moved to a new history file. One superseded quote
of the owner left the skill. `design/RimMandrake/CLAUDE.history.md` already held that quote.

## Scores

| measure | before | after |
|---|---|---|
| bytes | 22,055 | 26,019 |
| words in linted prose | 2,590 | 3,218 |
| STE violations per 100 words | 3.17 | 1.34 |
| sentences over 20 words | 33 | 4 |
| flagged lines (mechanical) | 11 | 10 |
| hand count (lines a cold reader cannot act on) | 17 | 0 |

Long sentences that stay: a bold slogan of 21 words (the void row); the `RULED OUT` line and its code spans; and two pairs of
short sentences that the lint joined (the log budget, Lightspeed). The flagged lines that stay are verdict words (PASS, FAIL,
UNMEASURED) and the row ids R1–R6 and L2.

## The hand count

| old line | what a cold reader lacks | state after |
|---|---|---|
| "stages sites" | what a site is | meaning added |
| "result JSON of rows" | what a row is | meaning added |
| "the full list" | whose list | "the owner's full mod list" |
| the anatomy block: blocks, tier, control-noise, Z | four terms with no meaning | a list "Terms in this block" |
| "site hold still runs" | what the site hold is | meaning from `targeting.py` |
| "A harness or site row in a shared session" | what a shared session is | meaning from `validation_core.SHARED` |
| "style_hose R1–R6" | what R1–R6 are | R1 and R6 named from `validation_style_hose.py` |
| "throw their own NREs" | NRE | NullReferenceExceptions |
| "Aim at the target's real footprint cell" | aim what | "Aim a hose at" |
| "Pass 7's" | which pass | "the Pyrelands live pass 7 (2026-10-13)" |
| "a sentinel warning" | what the sentinel is | "a marker warning" |
| "The tap is polled" | what the tap is, and who polls | meaning from `LogTap` |
| "a same-list control" | what the control is | meaning from `references/log-budgets.md` |
| "with a can-fail" | what a can-fail is | meaning from `references/perf.md` |
| "Back up the keepers" | which saves | "the saves that must not change" |
| "aborted v2 at L2" | which v2, which L2 | FlowWorks' `validation_v2.py`, row `L2_tier_live` |
| "the walk's `## anti-guessing notes`" | which walk | the page under `design/validation_walks/` |

## Conflicts and stale lines, settled

Rules: 1 the code · 2 his later ruling · 3 root `CLAUDE.md` · 4 the thing is gone · 5 obvious answer.

| old line / other side | decision | rule and evidence |
|---|---|---|
| "Avoid long runs of game time … unless it's a clear win" / `debug_process.md` "No long runs" | "Start no long runs"; his later words quoted; the pointer names `CLAUDE.history.md` | 2: ledger 2026-10-13 02:02Z against 04:34Z; settled already in `conflicts_settled.md` |
| `B.until` / `B.watch` "are PLANNED" / Python methods exist | the line says what exists: the Python half. `jawa/safe_advance` has no `until`, and no watch tool exists | 1: `validation_core.py`, `JawaBenchVitalsTools.cs` |
| the lead "`TryDraw` loses the level if `TryAddLiquid` refuses, and nothing asserts it" | "an example, since fixed", here and in `references/classifying-and-learning.md` | 1: `RM_LiquidTransfer.cs` reserves the tank leg first; `TransferChecks.cs` |
| "`rimflow file`/`close` refuse proof lines" | they warn and go on; `rimflow lint --proofs <ID>` exits 1. Corrected here and in `references/lightspeed-authoring.md` §2 | 1: `cli.py` `_prooflint_say`, `cmd_lint` |
| "The proof-line runner refuses flyer words outright" | the lint marks them refused; a vehicle item is the exception. Same in `references/lightspeed-authoring.md` §5 | 1: `proof_lint.py` `flyer_word`, `vehicle_item`; the runner was the retired lane (4) |
| `references/lightspeed-authoring.md`: the proof-line lint at filing is PLANNED | built | 1: `PROOFLINT_WIRE_AT_FILING_NOT_AT_RUN` is done |
| "(105 rows)", "(66 rows)" with no date | "as of 2026-10-11" | 1: `proof_all_20261011T*.json` and `proof_hose_20261011T*.json`; the later runs hold 150 and 68 rows |
| "Z" as the log-budget row | the row id `Z_log_budget` | 1: both scripts |
| `max_turns` (default 30) in a brief / "no launched agent is told its spend" | both stay: a turn count is not a spend figure, and the line names its danger (token burn) | 5 |
| `max_turns` 30 / the agent definitions' `maxTurns` 60 to 300 | both stay: one is the brief's budget, the other the harness's ceiling | 5; `subagent_budget.md` says both |

The item limits the rewrite to `SKILL.md`. The plan says "Edit both places in one commit". So this run edited only the false
lines in two reference files. In `classifying-and-learning.md` the span `TankToFill` is gone on purpose: no such method is left.

## The checks, with a planted loss first

| check | input | result |
|---|---|---|
| check 1 (`checkable.py compare`) | a copy with a save name, "~53 ms" and "10,000 messages" changed | the save name and ~53 lost (check 1 did not see "10,000") |
| check 2 (`rule_doc_lint.py keep`) | the same copy | 4 lost, exit 1 |
| check 1 | the real rewrite | 51 items, 0 unfindable |
| check 2 | the real rewrite | 170 spans, 0 lost |
| check 2 | `lightspeed-authoring.md` / `classifying-and-learning.md` | 0 lost / 1 lost (`TankToFill`, above) |
| `selftest_retired_era_gone.py`, `selftest_skills_by_work.py`, `selftest_game_names_prose.py`, `selftest_rule_homes_in_briefs.py`, `selftest_prooflint_at_filing.py` | final | pass |
| `skills/validate_skills.py live-debugging-proof-harness` | final | 0 errors, 0 warnings |
| `batch_done.py selftest` | — | GREEN: 0 failed (12 planted cases) |

Names of people: the old and the new text name none.

## What the meaning read found

Two fresh Opus readers (rm-judge), one after the other. Neither got the writer's reasoning. The first read both texts whole.
The second read the repaired parts and the two reference diffs. (A resumed reader runs in the background, where the end of this
run could kill it. So a fresh reader read the repairs.)

| reader | finding | repair |
|---|---|---|
| 1 | long runs: the "clear win" exception is gone | none: the correction is his later ruling |
| 1 | the fresh-context audit became an instruction | none: `classifying-and-learning.md` orders it |
| 1 | "Their game half does not exist" overstates: `jawa/cond_eval` is built | "is not complete", with what is absent |
| 1 | the `TryDraw` lead is fixed, and the reference still says live | reference corrected |
| 1 | flyer words: the lint at file and close only warns | rewritten |
| 1 | the vehicle exception is incomplete | the two conditions added |
| 1 | "Z is the id" is false | the row id named |
| 1 | the row-count date is not verified | verified from the result files |
| 1 | `rimflow file`/`close` refuse: false in the old text too | rewritten |
| 2 | the lint reads the title and the criterion too | added |
| 2 | `file` cannot see a cut criterion; no verb checks a `live-site` line | added to `lightspeed-authoring.md` §2 |
| 2 | `lightspeed-authoring.md` says the filing lint is PLANNED, and "the runner refuses" | both corrected |

No reader read these lines after their last edit: the three lines that the `./publish` prose check asked to
define (the functional script, chains, R1–R6), the two flyer-lint bullets of §Flyers, the "Two rows are seen less" lines,
the poll-loop line and the §5 line of `lightspeed-authoring.md`.

## Could not determine

| line | question | who would know |
|---|---|---|
| "93% of test units qualify" | today's share; the count is the census of 2026-11-05 | a new census (`design/RimMandrake/lightspeed_2026-11-06.md`) |
| the owner called that validation "mostly ceremony" | `owner_rulings.py` holds no such row; the words came from the session of 2026-10-11 | the owner, or that transcript |

## Polish (not fixed)

- The text of `cli.py lint --proofs` says "the live lane would refuse". That lane is retired.
- `jawa/safe_advance` describes its `timeException` with the superseded words ("long runs only when clearly worth it").
- The C# half of `references/lightspeed-authoring.md` §3 lists two closed items among the PLANNED ones.

## What this run did not test

- No agent used the new file in real work, and no live game ran.
- The bridge calls and the measured figures (ms, ticks) were read, not run again.
