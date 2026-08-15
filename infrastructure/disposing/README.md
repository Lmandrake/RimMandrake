# disposing/ — quarantine for files on their way out

A file lands here when it is **believed dead but not yet proven so**. This is the
step between "the audit flagged it" and "it is gone", and it exists so that
cleaning the repo never requires anyone to feel brave.

## What goes here

A file judged **DUPLICATED**, **SUPERSEDED**, **SPENT** or **ORPHANED** — the four
kinds in `output\STALE_FILE_AUDIT.md` — **that nothing currently references.** Check
the reference side before moving anything:

```bash
grep -rn "<basename>" --include='*.md' --include='*.py' . | grep -vE '^\./(disposing|output)/'
```

A live reference means it is not dead yet. Fix the reference or leave the file
alone; do not move it and break the pointer.

**Not the same as `output\`.** That tier holds reports still doing work, waiting
for their conclusion to reach a durable home; this one holds files believed dead.
A report normally passes through `output\` first. See `output\README.md`.

## Moving is not deleting

Use `git mv`, never `rm`. History follows the file, and the move is reversible in
one command:

```bash
git mv path/to/doomed.md disposing/doomed.md     # out
git mv disposing/doomed.md path/to/doomed.md     # back, one command, no archaeology
```

## Nothing here is authoritative

**No seat may cite, follow, or copy from a file in `disposing/`.** It is not
doctrine, not a spec, not a source. Treat it as absent.

**If you find yourself needing one, that is the evidence it was not dead.** Move it
back with the command above and say why in the commit message — that "why" is the
reference the audit missed, and it is worth more than the file.

## Dwell time: 7 days, and PROJECT empties it

Nothing leaves `disposing/` for real until it has sat here **unreferenced for 7
days**. Deleting is **PROJECT's to enforce** as part of the stale-file audit; no
other seat empties this directory, and no file skips the wait.

**Seven days, not thirty, because this project moves fast enough that a 30-day
quarantine would hold files long past the point anyone could still judge whether
they were needed.** The window has to be short enough that the person deciding
still remembers the context that put the file here.

## Why a directory and not just a delete

**Git history is invisible to a working agent.** A deleted file leaves nothing in
the tree to trip over — the next seat cannot notice what it never sees, and would
have to already suspect the file existed in order to go looking for it.

A directory named `disposing/` says "this is on its way out" at a glance, to a
human and to a seat alike. That legibility is the entire point, and it is the one
thing a deletion cannot provide.

## Exclusions

- **`Utils/doc_budget.py` per-class budgets do not reach here** — the patterns are
  rooted at the repo top (`agents/*.md`, `queue/*.md`), so a moved file stops
  counting against its class the moment it lands. ⚠️ The script's **repo-total**
  line globs `**/*.md` recursively and *does* still count these lines; it needs a
  `disposing/` filter to match this rule.
- **Excluded from the doctrine delta** (`Utils/whats_new.py`). Quarantined files
  must never be handed to a seat as news.
- **Excluded from search by default.** Scope greps to the live tree and add
  `| grep -v '^./disposing/'`, unless you are deliberately asking what was retired.

## Dropped 2026-08-13 — the restructure's own paperwork, question answered

Seven-day dwell, then delete. The migration is **done and pushed**; these
described how to do it, and nothing now needs them.

| file | why it is spent |
|---|---|
| `RESTRUCTURE_PLAN.md` | executed. The tree IS the plan now — read `<tier>/README.md` |
| `RESTRUCTURE_OPTIONS.md` | option B was chosen and built; the rejected options teach nothing |
| `RESTRUCTURE_LOG.md` | a running narration of a finished move |
| `do_restructure.sh`, `fix_refs.py` | one-shot scripts, already run |
| `agents_redesign_options.md` | the five-seat structure shipped; this was its options doc |

⚠️ **Kept in `output/` deliberately:** `STALE_FILE_AUDIT.md` (§E is owner decision
#7, still open) and `REF_AUDIT.md` (18 broken refs still live).

## Quarantined 2026-08-14 — the restructure left these behind (dwell to 2026-08-21)

- `BOARD.md` — render output of `board.py`, deleted in `47743fa`. Nothing regenerates
  or reads it. Superseded by `status_matrix.json` + `status_server.py`.
- `V1_CHECKLIST.md` — PROJECT's ordering doc, built from the five retired queues.
  Zero inbound references. Asserts `V1_SCOPE.md` wins the v1/v2 line, which
  `V1_CHAIN.md` reverses.
- `status.py` — parses `V1_SCOPE.md` for a burn-down table. Unreferenced by any
  doctrine but still executable, so running it reports the pre-expansion scope.
  Live path is `derive_matrix.py` → `V1.md` → `status_matrix.json`.
