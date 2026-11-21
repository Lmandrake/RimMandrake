# What filled the context of the live sittings that the spend stop ended (2026-11-21)

Item: `RIMMANDRAKE_TRACE_LIVE_SITTINGS_HIT_SPEND_STOP_THRICE_ONE_NIGHT`. All spend is in weighted_v2 tokens
(`MODEL_PRICES` in `src/RimMandrake/rimflow/role_launch.py`). Every number here is measured from the transcripts
unless it is marked as a guess.

## Sources and method

- The transcripts:
  - `82ebad1e-0f23-455d-8747-6fc2bff2bded` (FlowWorks fallen raider), under the `RIMMANDRAKE-TRACE-FLOWWORKS-FALLEN-RAIDER-WAITS-FOR-NO-LADDER-det` project folder.
  - `288f91ef-136a-4cf4-beb7-249398a482e8` (FlowWorks moat swimmers). Two files have this id. The file under
    `RIMMANDRAKE-STAGE-FLOWWORKS-PIT-TRAP-RAID-NONE-FELL-det` holds all 341 lines of the file under
    `RIMMANDRAKE-TRACE-FLOWWORKS-MOAT-SWIMMERS-ONLY-IN-THE-CONTROL-det`, plus a third run. The third run is a
    FlowWorks holder run at 12:25 UTC that resumed this session. The table uses the longer file.
  - `e2e12962-81dc-4333-8a63-b4d262d2ad41` (Pyrelands fire-hawk).
- The script `design/specs/2026-11-21-live-sitting-context-burn/burn_table.py` reads each transcript once, line by line.
  It prints `design/specs/2026-11-21-live-sitting-context-burn/tables.md`. Run it again:
  `python3 design/specs/2026-11-21-live-sitting-context-burn/burn_table.py <session.jsonl>...`
- Each API request is counted once (by message id). Its spend is its input, cache writes, cache reads and output,
  each at its model's price.
- The tokens of a tool result are measured, not estimated. The context growth from request k-1 to request k, less
  the output of request k-1, is split over the results that entered at k by their characters. The median was 2.0
  characters per token on all three sessions (73 clean steps). So `bytes / 4` under-counts these texts by about 2x.
- A token that enters the context costs one cache write, then one cache read on each later request. A "share" charges
  each piece both costs. The per-session split matches the measured total to within 4%.

## Corrections to the brief

- The Pyrelands run 1 (`e2e12962`) ran on Opus 5.5 (142 requests), not Fable. Its resume ran on Fable 5.2.
- The filed theory was "bridge output read whole, screenshots, re-reads". The measurements do not support it.
  Bridge and game-driver output was 2.6% to 6.9% of each stopped run. The three sessions held 2 images (2,680 tokens).
  One file was read twice. Identical commands ran 5, 10 and 28 extra times, and these were small.

## The table: each run

| session | run | model | requests | minutes | context at start | median context | context at end | weighted_v2 |
|---|---|---|---:|---:|---:|---:|---:|---:|
| 82ebad1e fallen raider | 1 (stopped) | Fable | 70 | 53 | 104,931 | 217,321 | 287,642 | 2,518,586 |
| 82ebad1e fallen raider | 2 (resume, 1 h 40 min later) | Fable | 10 | 4 | 310,158 | 319,051 | 323,267 | 1,487,029 |
| 288f91ef moat swimmers | 1 (stopped) | Fable | 61 | 26 | 104,814 | 221,039 | 303,589 | 2,504,184 |
| 288f91ef moat swimmers | 2 (resume) | Fable | 28 | 11 | 306,055 | 325,844 | 345,229 | 863,312 |
| 288f91ef moat swimmers | 3 (holder run for the pit-trap item) | Opus | 26 | 19 | 373,771 | 394,256 | 408,944 | 1,383,896 |
| e2e12962 fire-hawk | 1 (stopped) | Opus | 142 | 29 | 73,775 | 224,339 | 302,784 | 2,542,036 |
| e2e12962 fire-hawk | 2 (resume) | Fable | 8 | 2 | 263,642 | 268,927 | 273,855 | 1,202,977 |

Each stopped run ended at about 2.5M weighted_v2. The Fable runs got there in 61 and 70 requests. The Opus run got
there in 142 requests: Opus costs half as much as Fable per cache write and per output token.

## (1) What filled the context

Where the spend of each stopped run went (run 1, charged inside run 1):

| where | 82ebad1e | 288f91ef | e2e12962 |
|---|---:|---:|---:|
| start context (system prompt, tools, both CLAUDE.md files, skill list, MCP notes, the brief), read by every request | 29% | 28% | 25% |
| tool results | 27% | 29% | 35% |
| output generated (thinking and the commands that the agent wrote) | 27% | 27% | 18% |
| that output, read again by every later request | 15% | 14% | 20% |
| other added context (reminders, user text) | 2% | 2% | 1% |

The tool results, split by kind (share of run 1):

| tool results | 82ebad1e | 288f91ef | e2e12962 |
|---|---:|---:|---:|
| reading code or text (Read, `sed`/`cat`/`grep` on source files, RimSage) | 16.8% | 10.4% | 19.6% |
| other (ledger, git, the pilot's own scripts and logs) | 7.5% | 11.9% | 10.7% |
| bridge or game-driver output | 2.6% | 6.9% | 4.6% |
| results over 8,000 characters (6, 8 and 5 calls) | 11.1% | 12.5% | 10.5% |
| ... the characters of those past 8,000 | 5.3% | 4.4% | 5.1% |
| the role file `rm-testpilot.md`, read whole as the first step | 2.9% | 2.8% | (not a pilot) |

The output, measured:

- Thinking was 30%, 30% and 44% of the output tokens of run 1.
- The Bash commands that the agent wrote were 69,922, 76,701 and 61,834 characters. Heredoc scripts were 47,380,
  64,096 and 23,070 characters of that.

The start context, measured with three one-request probes on 2026-11-21 (`claude -p`, Sonnet, "Reply OK"):

- In this clone: 68,888 tokens. In an empty folder (only the global CLAUDE.md): 49,397 tokens. So the project
  `CLAUDE.md` is about 19,500 tokens at each request.
- The FlowWorks brief (the mod ledger packet and the pilot lines, 69,470 characters) is about 31,000 tokens more than
  the Pyrelands brief (12,766 characters). This is the difference of the two start contexts, with the same CLAUDE.md
  files. That is about 1.8 characters per token.
- `modledger.tokens()` counts `bytes / 4`, so the "15k" packet bound (`packet_budget_tokens`) admits a packet of
  about 31,000 to 38,000 real tokens.

Cache writes against cache reads, whole sessions:

| session | cache write tokens | cache read tokens | spend on writes and input | spend on reads | spend on output |
|---|---:|---:|---:|---:|---:|
| 82ebad1e | 588,165 | 17,643,638 | 58.7% | 22.0% | 19.2% |
| 288f91ef | 730,813 | 31,943,736 | 44.8% | 33.6% | 21.6% |
| e2e12962 | 554,127 | 31,762,864 | 43.6% | 42.4% | 14.0% |

The writes are large because each resume wrote the whole context again in one request:

| resume | first-request cache write | weighted_v2 of that one request | why the cache missed |
|---|---:|---:|---|
| 82ebad1e run 2, 12:15 UTC | 298,786 | 1,195,148 | 1 h 40 min after the stop; the cache lives 1 h |
| 288f91ef run 3, 12:25 UTC | 362,399 | 724,800 | 11 min after the last run, but Fable to Opus |
| e2e12962 run 2, 16:02 UTC | 252,386 | 1,009,548 | seconds after the stop, but Opus to Fable |

These three requests are 29.8%, 15.3% and 27.0% of their whole sessions. Each of these three runs spent 86% to 92% of its spend on the context
that it took over. The one resume that hit the cache (288f91ef run 2, same model, 2 min after the stop) spent 50% on
it, as cache reads.

## (2) How many turns ran at what context size

| session | 50-100k | 100-150k | 150-200k | 200-250k | 250-300k | 300k+ | median |
|---|---:|---:|---:|---:|---:|---:|---:|
| 82ebad1e (80 requests) | 0 | 8 | 20 | 17 | 25 | 10 | 238,073 |
| 288f91ef (115 requests) | 0 | 7 | 19 | 14 | 18 | 57 | 297,320 |
| e2e12962 (150 requests) | 7 | 26 | 27 | 23 | 62 | 5 | 234,713 |

No run compacted. The role file says that the pilot compacts at 150k tokens. That is true for a subagent only. A
detached sitting is a top-level session, and the agent file's frontmatter does not apply to it.

## (3) The three changes that would cut the most

1. **A resume that does not write the whole context again.** Measured cost: 0.72M to 1.20M weighted_v2 in the first
   request of each resume, 15% to 30% of each session, and 29% to 48% of a 2.5M cap. Two of the three misses came
   from a model change on resume; the cache was still warm for the old model. The third came after the cache expired.
   The fix is in the resume launch (`modledger.resume_plan`, `left_open_continue.py`, the Conductor's resume): resume
   only on the session's own model inside the hour, or else start fresh from the item notes. Not changed in this run:
   it is a choice between his "resumed session per mod" card and a fresh start, so it goes to the Conductor (ticket
   below).
2. **A smaller start context.** Measured: 25% to 29% of each stopped run. The parts that are ours: the FlowWorks brief
   (about 31,000 tokens, about 11% of a FlowWorks run 1), the project `CLAUDE.md` (about 19,500 tokens, about 6% of a
   run 1) and, for a pilot, the role file read as a tool result (about 10,000 tokens, 2.8% to 2.9%). A probe measured
   one fix for the last part: `claude --agent rm-testpilot` makes the role file the system prompt (24,282 characters)
   and narrows the tool list. The start context fell from 68,888 to 63,523 tokens, and the role file then needs no
   Read: about 15,000 tokens less at each request, about 4.5% of a run 1. CLAUDE.md still loads with `--agent`
   (`omitClaudeMd` does not apply to a top-level session). Not changed in this run: `maxTurns: 300` and
   `autoCompactWindow` may then apply to a detached sitting, and that is not tested (ticket below).
3. **Fewer large tool results.** Measured: results over 8,000 characters were 10.5% to 12.5% of each stopped run,
   from 5 to 8 calls. The part past 8,000 characters was 4.4% to 5.3%. Changed in this run, in the role file.

Output was the largest single part (33% to 42% of each stopped run, with its later reads). Its levers are the model
(Fable output costs twice the Opus price; the pilot is Fable by his ruling of 2026-11-16) and shorter commands. The
model is not ours to change here. Shorter commands went into the role file.

## Changes made

`.claude/agents/rm-testpilot.md`, section "Context discipline":

- New lines: what a sitting spends, with the measured shares; keep each tool result under 8,000 characters (`grep -n`
  first, then at most 80 lines; no whole-file Read of a source file; no `sed -n` range over 100 lines); keep commands
  short (a script used more than once goes to a file once).
- Corrected: "Your context auto-compacts at 150k tokens" is true only for a subagent. A detached sitting reached 288k to
  409k tokens.
- Corrected: the heading "CLAUDE.md is NOT loaded" is true only for a subagent. A detached sitting loads it (measured: 86,172 to
  87,358 characters of CLAUDE.md at the first request of each detached transcript).

Replay of one real tool result under the new rule: run 1 of `82ebad1e` read
`src/RimMandrake/FlowWorks/Source/Superdeep/RM_RaiderFetchFallen.cs` whole (10,595 characters, 4,943 measured tokens,
about 37,000 weighted_v2 inside run 1). The rule's way on the same file today (`grep -n` outline of 19 lines, then 80
lines): 4,392 characters against 12,419 for the whole file today, 35%. At the run's price that is about 13,000
weighted_v2 instead of about 37,000 for this one call.

Untested: whether a real sitting follows the new lines. The check: run `burn_table.py` on the next pilot sitting
and compare the row "results over 8,000 characters".

## Not changed

- The spend watchdog and its cap. They are his.
- Bridge and driver tools. Their output was 2.6% to 6.9% of each stopped run, and no single bridge call was large.
  Test 1 does not pass.
- `skills/`.
