# When to resume a session, and when to start a fresh run

Item: `RIMMANDRAKE_STUDY_SLEEP_AND_RESUME_AGAINST_FRESH_RUN_COLD_COST`. Written 2026-11-25 by a detached BENCH run (Opus 5.5).
Owner, 2026-11-25: "Sleeping/resuming agents is actually a really interesting option we seem to never want to do,
mostly for the cold token cost. I will leave that to you to analyze offline for optimality."

Every figure is in `weighted_v2` (one uncached Opus 5.5 input token = 1). Each number says **measured** or **guess**.
Evidence: `measure_pairs.py` (read-only; it reads the run records in
`D:\ClaudeWork\rimmandrake\dispatcher\detached\` and the transcripts in `~/.claude/projects/`) and its output
`pairs.json`, both in this folder. A pair is a continuation run and the run before it on the same item.

## 1. The cost of a resume

Weights from `MODEL_PRICES` in `src/RimMandrake/rimflow/role_launch.py` (measured, read 2026-11-25):

| model | input | cache write 1 h | cache read | output |
|---|---|---|---|---|
| Opus 5.5 | 1 | 2 | 0.05 | 5 |
| Sonnet 5.5 | 0.5 | 1 | 0.025 | 2.5 |
| Fable 5.2 | 2 | 4 | 0.05 | 10 |

- **Cache life is 1 hour.** Of 8,368 transcripts, 8,052 hold 1-hour cache writes (measured). 320 hold some
  5-minute writes; in the two opened, they are 2 of 135 and 2 of 76 main-thread lines (measured). The cost rows
  below fit the 1-hour weight to within 1% (measured, 10 rows checked: first-request cost = 0.05·read + 2·write + output).
- **Warm resume** (cache still alive): the first request reads the old context `C` from cache and writes only the new
  part `δ`. Cost ≈ 0.05·C + 2·δ. Measured on 24 Opus resumes: δ median 27k tokens, first request median **70k**
  (range 15k–154k), at C from 126k to 530k.
- **Cold resume** (cache dead): the first request writes the whole context again. Cost ≈ 2·(C + δ) for Opus,
  4·(C + δ) for Fable. Measured: 9 Opus cold resumes, first request median **566k** (375k–1.12M); 3 Fable, median
  **1.20M** (1.01M–1.30M). This matches the reason of the 150k rule (2026-11-21: 252k–362k contexts cost 0.72M–1.20M).
- **What makes a resume cold** (measured, 13 cold of 39 resumes whose parent context was readable):
  - 10: idle 88 min or more since the parent ended. Of the same-model resumes idle under 60 min, 26 of 27 were warm (up to 57.2 min); the one exception is below.
  - 2: a model change (Fable to Opus at 10.9 min, Opus to Fable at 1.4 min). A model change is always cold.
  - 1: unexplained, Sonnet, 1.0 min idle (`rm-detached-bench-rimmandrake-batch-knockback-scenes-fifty-1795568188`).
    Unknown cause; an account switch between the two runs would explain it (guess, ~50%). The account plan's history
    at that time would settle it.

## 2. The cost of a fresh run

65 continuations had a readable transcript and a first new act (an Edit, a Write, or a Bash call that publishes,
commits, writes a ledger note/close/file/wait/verify, deploys or starts a long wait). Of them, 23 were fresh, 26 warm
resumes, 13 cold resumes and 3 resumes whose parent context could not be read (measured). The cost "before the first new act" includes that act's request.

| class, Opus 5.5 | runs | parent context (median) | first request (median) | to first new act (median, range) | context at that act |
|---|---|---|---|---|---|
| fresh | 16 | 418k | 153k | **414k** (229k–1.10M) | 135k |
| warm resume | 24 | 275k | 70k | **320k** (27k–2.26M) | 365k |
| cold resume | 9 | 242k | 566k | **869k** (510k–1.52M) | 334k |

Sonnet fresh (5 runs): first request 51k, to first act 70k. Fable fresh (2): first request 272k, to first act 531k
(measured). Ten named pairs, with every field, are rows of `pairs.json`; for example
`…drive-explosiveknockback-in-1795625605` (fresh after a 494k parent: 236k first request, 1.10M to first act) and
`…tell-him-rot-spore-mushroom-1795413386` (warm resume of 142k: 15k first request, 27k to first act).

- **A fresh run in this repo has a floor.** Its first request holds 61k–129k tokens (median 84k), of which 11k–15k is a
  prefix cached across sessions and the rest is written (measured, 23 runs). The two CLAUDE.md files are 100 KB
  together and a detached brief is about 14 KB (measured); about 30k tokens (guess, ~4 bytes per token).
- **A fresh run drops dead context.** It reaches its first act with 135k (median), against 418k in its parent
  (measured). Every later request reads that smaller context.
- **Caveat.** The classes are not matched pairs: each continuation ran one way only, on its own task (measured). The
  medians compare classes, not the same work done twice. A matched test (one stopped run, resumed and also
  restarted) would measure the difference directly; it is unknown.

The rule that exists now (`src/RimMandrake/rimflow/left_open_continue.py`, `RESUME_WHOLE_MAX_TOKENS = 150000`): a
continuation resumes when the last context is under 150k, **whatever the time since it ended**; above that it starts
fresh from the PROGRESS and LEFT OPEN notes. Its reason (2026-11-21) was measured only on cold resumes.

## 3. Break-even for Case A (a fixer sets work down for a cause outside the work)

Two costs decide it (Opus 5.5; Sonnet scales by exactly ½ on every weight, so its thresholds are the same):

- **Start**: a resume pays its first request and its own orientation; a fresh run pays 414k to its first act
  (measured median).
- **Carry**: after that, each request of a resume reads `C − F` more tokens than a fresh run would, where F ≈ 135k
  (measured): 0.05·(C − F) per request. The remaining requests after the first act: median 40, quartiles 8 and 72
  (measured, 65 continuations).

| context C | warm resume: start saving | warm: carry per request | warm: break-even requests | cold resume: start cost |
|---|---|---|---|---|
| 100k | ≥ 94k (up to 354k) | 0 | always resume | ≈ 255k + orientation: about even |
| 150k | ≥ 94k (up to 352k) | 0.8k | 125–470 | ≈ 355k + orientation: loses (3 measured: 510k, 566k, 897k to first act) |
| 200k | ≥ 94k (up to 349k) | 3.3k | 29–107 | ≈ 455k +: loses |
| 300k | ≥ 94k (up to 344k) | 8.3k | 11–42 | ≈ 655k +: loses |
| 400k | ≥ 94k (up to 339k) | 13.3k | 7–26 | ≈ 855k +: loses |

The low saving (94k) is the measured median gap (414k − 320k); the high is 414k less the warm first request with no
orientation at all. Both are model figures from measured parts (guess, ~70%, for the break-even columns).

- **Sleep length**: a resume is warm only when the same model resumes within the cache life of 1 h of the last
  request. Use 50 min, for margin (measured: warm to 57.2 min, cold from 88 min).
- **Context**: warm, a resume wins up to about 150k, and is about even at 200k for a median continuation. Cold, a
  resume wins only up to about 100k, which is about the fresh floor itself; a session that did real work is past it.
- **Case A sleeps are mostly long.** A held game, a ruling or a held file usually clears after more than an hour
  (guess, ~70%; the wait records on items would measure it). So Case A is mostly fresh.
- **Files held is a special case.** The run that held the files changed them. A resume then holds stale copies of
  those files and trusts them. A fresh run reads them as they are now.
- **What a resume keeps that no record keeps**: the exact tool output it read (file text, logs, game readings), the
  failed attempts with their exact errors, the hypotheses it rejected and why, and the places it looked and found
  nothing. A PROGRESS note keeps the theory, the experiment, the reading and the next act. It loses the raw
  observations and the negative space. A resume also keeps what is now false (stale files, a game state that moved).
- **Keep-warm, untested.** A one-line request into a sleeping session every 50 min costs about 0.05·C (15k at 300k);
  it is cheaper than a cold rewrite (600k at 300k) for sleeps up to about 30 hours. Whether a `--resume -p` ping
  refreshes the cache life is unknown (Anthropic's caching documentation says a cache hit refreshes it; not measured
  here). One ping and one resume 50 min later would measure it.

## 4. Case B (an LLM ticket filer refuses, and the fixer files again)

The Conductor's guess: the filer needs only the ticket text and what it asked for, a few thousand tokens, so a fresh
filer with that record costs less than a resume and loses nothing.

- **No LLM filer exists now.** The filing gate, `src/RimMandrake/rimflow/filing_gate.py`, is a program: "No model,
  no tokens" (measured, its docstring and code). A refusal costs 0. Case B is a design question, not a measured run.
- **The record is smaller than guessed.** 44 refusal lines in 12 files under
  `D:\ClaudeWork\rimmandrake\dispatcher\filing_refusals\`: median 381 bytes, max 2.1 KB (measured); about 100–500
  tokens (guess). Each line holds the ticket, the reason and the path to pass. So the record loses little.
- **The cost part of the guess is wrong.** A fresh `claude -p` session in this repo starts at the floor of §2: a first
  request of 49k–58k (Sonnet) or 113k–236k (Opus), before it reads the record (measured). The record is 0.5% of it.
- **Within the hour, a resume is about 15 times cheaper.** A filer's context is about the floor plus the ticket,
  about 90k (guess). A warm resume costs 0.05·90k + 2·δ ≈ 9k (Opus); a fresh filer costs about 153k.
- **After the hour, fresh is a little cheaper.** A cold resume costs about 2·92k ≈ 184k; a fresh filer about 153k.
- **Independence favours fresh at any age.** A filer that judges a fixer's reason is a judge. A resumed judge remembers
  its first verdict and can anchor on it. The standing rule already starts every judge-like role fresh
  (`left_open_continue.py`, blind roles).
- **Verdict.** The guess is right on the record and right after the hour. It is wrong on the cost within the hour, by
  about 140k Opus per refusal. Fresh is still the right choice, for independence. The cheapest filer is the one we
  have, a program. If an LLM filer is built, a session without the repo's CLAUDE.md files would make "a few thousand
  tokens" true (guess; unknown until one is launched with a minimal prompt and measured).

## 5. The rule

1. A judge-like role (judge, reader, examiner, challenger, coverage judge, an LLM filer) always starts fresh.
2. Read C, the last main-thread context of the session, and the time since its last request.
3. Resume when the model is the same, the time is under 50 min, and C ≤ 150k.
4. Resume also when the model is the same and C ≤ 100k, at any time.
5. Resume also, at any C, when the run left no PROGRESS or LEFT OPEN note (nothing else would keep the work).
6. Otherwise start fresh from the brief, the notes and the header.
7. Before it stops, every run writes `PROGRESS: theory | experiment | reading | next`, plus each failed attempt
   with its error, and each file that the next act needs, with its path.
8. A model change is always cold: it resumes only by step 4 or 5. After "files held", the next run reads those files again.

Against the rule that exists now, only two things change: a cold resume between 100k and 150k becomes fresh
(steps 3 and 4), and a model change above 100k is fresh (steps 3 and 8).

## Minor findings (one line each, no ticket)

- Instrument trap: `grep '"ephemeral_1h_input_tokens": [1-9]'` reads 0 on the transcripts, because they are compact
  JSON with no space after the colon; and `*/*.jsonl` in `~/.claude/projects` fails because the folder names start
  with `-` (use `./*/*.jsonl`). Both returned a confident 0 before the fix.
- 2 of 83 resume records are second launches of a session that died before its first request (measured; `measure_pairs.py`
  counts each such session once).
