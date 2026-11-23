# Result: `RIMMANDRAKE_REWRITE_SKILL_CLONE_LANDING_COMMITS`

Part of batch `RIMMANDRAKE_REWRITE_SKILLS_IN_CURATION_SESSIONS_ONE_SKILL_EACH` (`batch_plan.md`, order 17). Run 2026-11-23.
File: `skills/clone-landing-commits/SKILL.md`.

Base: eedce762515ed7d0f47b89347fb58b42ed0e7abd

The front matter is byte-identical, the `description` included. No text moved to a history file.

## Scores

| measure | before | after |
|---|---|---|
| bytes | 4,405 | 6,021 |
| words in linted prose | 362 | 575 |
| STE violations per 100 words | 3.04 | 0.70 |
| sentences over 20 words | 5 | 1 |
| flagged lines (mechanical) | 0 | 0 |
| hand count (lines a cold reader cannot act on) | 9 | 0 |

The file grew by 37%. Part of the growth is the corrected `./publish` behaviour (below). The one long sentence (line 25) is two
short sentences that the lint joined.

## The hand count

| old line | what a cold reader lacks | state after |
|---|---|---|
| "It refuses, naming the path … only on a real conflict or …" | the subject; the line was false too | rewritten from `publish.py` |
| "`land.sh` is for when you must not move HEAD … it then realigns" | when "then" is | "After the push" |
| "Installed as `/home/mandrake/.seat-tmp/land.sh`" | a file that is absent | the repo path |
| "land.sh" in the code block and the recovery table | `land.sh` is not on PATH | `src/RimMandrake/Utils/land.sh` |
| "patch- or content-equivalent" | what content-equivalent is | same bytes and mode at each path (`seat_sync.py` docstring) |
| "the N are duplicates … they go to a `backup/…` branch" | which thing goes there | "The N commits …" |
| "don't; use `./publish` or `./sync`" | what not to do | "Do not stash." |
| the scratch-clone sentence (four instructions) | where each instruction starts | four bullets |
| "The full list — … — is the **Traps** table" | there is no table now | "the section **Traps**" |

## Corrected facts (the old text was false against today's code)

| old text | today | source |
|---|---|---|
| the copy `/home/mandrake/.seat-tmp/land.sh` is installed | absent; `which land.sh` finds nothing | measured 2026-11-23 |
| `./publish` refuses only on a conflict or on an uncommitted edit to a file that origin changed | other refusals exist; red checks are the usual one | `publish.py` `_publish` |
| (nothing on red checks) | a red check undoes the commit of this run, unless HEAD moved | `publish.py` `_undo` |
| an uncommitted edit to a file that origin changed is refused | a clean merge is carried; a real overlap lands and prints `LANDED, CLONE NOT MOVED`; an overlap with a DLL rebuild is refused | `publish.py` `rebase`, `land` |
| `./sync` refuses any dirty file with other bytes | only a file that upstream also changed, and only when the edit does not merge cleanly | `seat_sync.py` `plan` |
| `REFUSED: dirty file(s) ... hold other bytes` | `REFUSED: N dirty file(s) really overlap upstream's change` (the old text stays beside it) | `seat_sync.py` `plan` |
| the **Traps** table of `GIT_WORKFLOW.md` | a section | the file |

`design/RimMandrake/GIT_WORKFLOW.md` held the same false lines (§`./publish`, §`./sync`, and one trap). This run corrected
those lines only. No span was lost there (`rule_doc_lint.py keep`: 0 lost; `checkable.py compare`: 0 unfindable).

## The checks, with a planted loss first

| check | input | result |
|---|---|---|
| check 1 (`checkable.py compare`) | a copy of the first draft with `LAND_REPO`, "~200 MB" and the `seat_sync.py` path removed | the path and the size lost, exit 1 |
| check 2 (`rule_doc_lint.py keep`) | the same copy | 4 lost, exit 1 |
| check 1 | the real rewrite | 10 items, 0 unfindable |
| check 2 | the real rewrite | 44 spans, 0 lost |
| `selftest_scratch_clone.py` (reads this file), `selftest_skills_by_work.py`, `selftest_retired_era_gone.py`, `selftest_game_names_prose.py` | final | pass |
| `skills/validate_skills.py` | final | 0 errors, 0 warnings |
| `batch_done.py selftest` | — | GREEN: 0 failed (12 planted cases) |

Names of people: the old and the new text name none.

## What the meaning read found

Two fresh Opus readers (rm-judge), one after the other. Neither got the writer's reasoning. The second read the repaired
text whole against the old text. (The plan asks for the same reader. A resumed reader runs in the background, where the
end of this run could kill it. So a fresh reader read the repairs.)

| reader | finding | repair |
|---|---|---|
| 1 | "If `./publish` refuses, your commit stays on HEAD" is false for a red check: the commit is undone | each refusal now says what happens to the commit |
| 1 | "The refusal names the path" for each cause: a red check names the check | split by cause |
| 1 | outcomes that land stood in a list of refusals | a separate bullet for the uncommitted edit |
| 1 | "The reset loses nothing when both of these are true" reads as sufficient | old colon form back |
| 1 | bare `land.sh` in the code block and the recovery table | full repo path |
| 1 | "or the newer text" understates that the old refusal text is gone | the new text first; "the old text was" |
| 1 | "same bytes" without the mode | "bytes and mode" |
| 1 | "but" lost in the first line | back |
| 1 | `GIT_WORKFLOW.md` still holds the old rules | corrected |
| 2 | no rule lost; each new fact in `SKILL.md` right | none |
| 2 | a trap in `GIT_WORKFLOW.md` contradicts its corrected bullets | trap corrected |
| 2 | the undo sentence in `GIT_WORKFLOW.md` lacks its exception and the pipeline checks | both added |
| 2 | "files that you did not write" now binds only to `checkout --`; the other commands are banned without it | kept: that is the plain reading of the old line |

No reader read these lines after their last edit: the second reader's repairs in `GIT_WORKFLOW.md` (the undo bullet, the
two "What happens" lines and the "Do instead" line of the peer-edit trap, "and mode" in §`./sync`).

## Conflicts (listed, not decided)

1. "Use `land.sh` when you must not move HEAD": after the push, `land.sh` runs `seat_sync.py`, which can move HEAD.
   `LAND_SYNC=0` stops that. The old line stays.
2. "For a brand-new file, run `git add` first": `./publish` runs `git add --all` on its paths, so the step is not needed
   for `./publish`. The step does no harm. The old line stays.
3. `skills/clone-landing-commits/references/traps.md` quotes the old refusal texts ("hold other bytes", "origin changed a
   file you have uncommitted edits to"). That file is not in the scope of this item.

## Could not determine

| line | question | who would know |
|---|---|---|
| "the session's attribution lines" | whether a detached helper's lines differ from a window's | the harness's system reminder of each session |

## Polish (not fixed)

- A red check prints "it stays on HEAD" (`publish.py`, `_run_tree_checks`). The appended note then says "this run's commit
  was undone". The note is the true one.
- The `./sync` list omits two more kinds of commit that count as upstream: ledger lines all upstream, and a landed twin.
  The old text omitted them too.

## What this run did not test

- No agent used the new file in real work.
- The `./publish` outcomes were read in the code and its selftests' names, not provoked live.
