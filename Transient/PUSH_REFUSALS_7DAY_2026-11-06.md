# Push refusals to origin/main, 2026-10-30 12:17Z → 2026-11-06 12:17Z (7 days)

Item `PUSH_REFUSALS_MEASURE_BEFORE_BUYING_GITLAB` — measurement only, as asked: no design, no filing, no change made on the result.

**Source.** `./publish`, `land.sh` and `./sync` keep no log of their own pushes, so this reads their output where it survives: 4450 Claude transcripts touched in the window (`~/.claude/projects`), each landing call paired with its result and deduplicated by tool-call id. Made by `src/RimMandrake/Utils/push_refusal_census.py`.

## Time lost

Median clean landing (PUBLISHED, no rejection, n=3417): **9.0 s**. A call with rejections loses its duration minus that median; a call that gave up loses all of it.

- landing calls: **4075**; with ≥1 non-fast-forward rejection: **51** (1.3%)
- rejections in total: **52**; gave up after the retry budget: **0**
- calls that retried a push ERROR that was not a non-fast-forward: **96** (111 retries; 92 of them landed in the end). `publish.py` prints only git's last line (`error: failed to push some refs`), so the cause is not in the record: a local pre-push guard (`infrastructure/githooks/pre-push`) refusing and a GitHub-side error look the same.
- refused because origin moved under the work: rebase conflict **81**, upstream overlaps a dirty file **24** (each needs the writer to act again; not counted in time lost)
- time lost inside landing calls to retries: **35.5 min** over 7 days (5.1 min/day): 10.8 min on non-fast-forward rejections, 24.8 min on push-error retries
- time in all landing calls: 767.7 min

## Per day

(Pacific calendar days)

| day | landing calls | landed | calls with ≥1 rejection | non-fast-forward rejections | calls retrying a push error | push errors retried (not non-ff) | gave up (origin kept moving) | other origin refusals (conflict, overlap, raw push) | time lost (min) |
|---|---|---|---|---|---|---|---|---|---|
| 2026-10-30 | 273 | 235 | 1 | 1 | 1 | 1 | 0 | 13 | 0.2 |
| 2026-10-31 | 458 | 392 | 5 | 5 | 7 | 7 | 0 | 14 | 1.1 |
| 2026-11-01 | 581 | 500 | 6 | 6 | 16 | 17 | 0 | 11 | 3.7 |
| 2026-11-02 | 502 | 445 | 8 | 8 | 10 | 14 | 0 | 10 | 7.9 |
| 2026-11-03 | 832 | 733 | 13 | 14 | 22 | 28 | 0 | 27 | 7.3 |
| 2026-11-04 | 486 | 438 | 6 | 6 | 9 | 10 | 0 | 12 | 4.6 |
| 2026-11-05 | 797 | 686 | 11 | 11 | 29 | 32 | 0 | 34 | 9.9 |
| 2026-11-06 | 146 | 131 | 1 | 1 | 2 | 2 | 0 | 1 | 0.8 |
| **total** | 4075 | 3560 | 51 | 52 | 96 | 111 | 0 | 122 | 35.5 |

## Per writer

(clone family of the session's working directory; subagent transcripts marked)

| writer | landing calls | landed | calls with ≥1 rejection | non-fast-forward rejections | calls retrying a push error | push errors retried (not non-ff) | gave up (origin kept moving) | other origin refusals (conflict, overlap, raw push) | time lost (min) |
|---|---|---|---|---|---|---|---|---|---|
| bench seat clone | 443 | 363 | 1 | 1 | 2 | 2 | 0 | 16 | 0.2 |
| bench seat clone (subagent) | 717 | 617 | 5 | 5 | 11 | 11 | 0 | 34 | 2.2 |
| foundry clone | 72 | 62 | 0 | 0 | 0 | 0 | 0 | 0 | 0.0 |
| foundry clone (subagent) | 306 | 286 | 4 | 4 | 4 | 5 | 0 | 8 | 0.9 |
| relentless worker | 2533 | 2229 | 41 | 42 | 79 | 93 | 0 | 64 | 32.2 |
| scratch/pool clone | 4 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0.0 |
| **total** | 4075 | 3560 | 51 | 52 | 96 | 111 | 0 | 122 | 35.5 |

## Outcomes

- landed: 3560
- no-op (nothing to publish): 249
- local refusal (paths, message, state): 138
- origin: rebase conflict: 81
- origin: upstream overlaps a dirty file: 24
- origin: push error (not non-fast-forward), gave up: 17
- auth/transport failure: 5
- no verdict: 1

## Pushers without a transcript (user journal)

2 refusal/failure lines in the window (unit start lines excluded):
- `2026-11-04T03:06:08-08:00 Archmagi python3[2494333]: 2026-11-04T11:06:08Z ingest git: push failed (the commit stays local; the next ingest retries): git@github.com: Permission denied (publickey).`
- `2026-11-04T03:10:45-08:00 Archmagi python3[2524563]: tender: push failed: push to refs/tender/receipts/archmagi refused 3 times: git@github.com: Permission denied (publickey).`

## Blind spots

- The Relentless supervisor's own books `./publish` and other timer pushes log no retry lines; only their failures reach the journal (above).
- A transcript deleted or not yet flushed is not counted; a landing run through a wrapper whose command line names none of the landing tools is not seen.
- A result Claude saved to a file (output too large) carries no markers in the transcript: such a call reads 'no verdict' and is dropped, an undercount.
- The clean-landing median is taken over every landing command (a build chained before ./publish, ./sync) and a retried call's duration includes publish.py's back-off sleeps: time lost is an approximation, likely an understatement.
- Time lost counts the waiting inside the landing call only, not an agent's later re-run by hand (those appear as separate calls).
