# output/ — spent reports, held while the question is live

**These files are evidence, not doctrine.** An audit or an options paper is the
*record of a question being answered*. Once the question is answered, the answer
belongs in a durable home and the report is spent.

The tier exists because reports accumulate at the repo root, where they look
exactly like standing documents. A seat reading an audit beside `STRUCTURE.md`
cannot tell from position which one is a rule.

## What goes here

Audit reports, options papers, one-off analyses, measurement dumps — **anything
produced to answer a question rather than to state a standing rule.**

If a file tells you what is true, it is not an output. If it tells you what
someone found out on the way to deciding something, it is.

## Nothing here is authoritative

**No seat may cite a file in `output\` as a rule.** Not as a spec, not as a
precedent, not as "the doc says".

If a finding matters, **it moves to a real home** — a skill, a queue item, a
design doc — and the report keeps only the evidence behind it.
A conclusion that lives only in `output\` has not landed.

## Lifecycle

```
output\ → acted on → conclusion lands in its durable home → disposing\ → deleted after the 7-day dwell
```

`output\` is the step **before** `disposing\`, not a synonym for it. A file here
is still doing work: its question is open, or its evidence is still being read.
It moves on to `disposing\` only once the conclusion has a durable home.

## PROJECT sweeps it

Same as `disposing\`, and on the same cadence as the stale-file audit. **A report
still in `output\` after its question is answered is a report nobody closed** —
that is the signal this directory is built to make visible.

Move files with `git mv`, never `rm`, so history follows:

```bash
git mv output/spent_report.md disposing/spent_report.md
```

## Versus `disposing\`

`disposing\` holds files **believed dead**, awaiting a 7-day proof; `output\`
holds files **still useful**, awaiting the moment their conclusion is rehomed.
See `disposing\README.md`.

## Exclusions

- **Not gitignored.** These are small text files and worth having in the tree
  while the question is live — unlike `disposing\`'s payloads.
- **`Utils\doc_budget.py` per-class budgets do not reach here.** The patterns are
  rooted at the repo top, so a report stops counting against a class the moment
  it lands. A report's length is its content, not accumulation.
- **Counted in the `doc_budget.py` repo total, deliberately.** These files are
  live in the tree and any seat may read them, so their lines are real weight.
  This is the opposite of `disposing\`, whose doctrine is "treat as absent" and
  which therefore should *not* count — an open question flagged in
  `disposing\README.md`.
- **`Utils\check_refs.py` does not scan here.** Reports quote broken and
  superseded references on purpose; auditing them would be noise.
