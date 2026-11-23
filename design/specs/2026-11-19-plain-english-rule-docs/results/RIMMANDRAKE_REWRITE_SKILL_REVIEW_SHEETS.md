# Result: `RIMMANDRAKE_REWRITE_SKILL_REVIEW_SHEETS`

One session of batch 17 of `batch_plan.md` (`RIMMANDRAKE_REWRITE_SKILLS_IN_CURATION_SESSIONS_ONE_SKILL_EACH`).
File: `skills/rimworld-review-sheets/SKILL.md`. Run 2026-11-23.

Base: `8a93d8a8a6c26f5e2f92e0d0323ece5d6a94810a`

No evidence left the active file, so this skill has no history file.

## Scores

| measure | before | after |
|---|---|---|
| bytes | 9,925 | 13,151 |
| words in linted prose | 1,314 | 1,836 |
| STE violations per 100 words | 4.64 | 2.23 |
| sentences over 20 words | 26 | 6 |
| flagged lines (mechanical) | 0 | 0 |
| lines that a cold reader cannot act on (hand count, by the writer) | 11 | 0 |

Each long sentence that stays holds an owner quote or
is a bold lead that other files can cite. The front matter (`description` included) and every heading are byte for byte.

## The hand count

| old line | what a cold reader lacks | state after |
|---|---|---|
| "the sidecar" | what the sidecar is | meaning at first use, from `serve_gated.py` and the general skill |
| "stamped" | what a stamp is, and why a hand edit breaks it | meaning from `scaled_review_gate.py` |
| "every letter he picked" | what a letter is | meaning added |
| "donor-only rows" | what donor art is | meaning from `references/art_requirements.md` requirement 3 |
| "the resolver" | which code | `Resolver` in `scale_panel.py` |
| "refuse a sheet without it" | what "it" is | the pre-review record |
| "the owner has the URL from you" | the act | "Give him the URL." |
| "a def half of a note" | what the other half is | a note that asks for a picture and a def change |
| "0 orphaned" | what an orphaned letter is | meaning from `remap_decisions.py` |
| "even for an owner pile" | what an owner pile is | meaning from `owner_doc_lint.py` |
| "Before serving … `curl` the served page" | how to fetch a page that is not served | the `curl` comes after the serve |

## Checks, with a planted loss first

| check | input | result |
|---|---|---|
| check 1 (`checkable.py compare`) | a copy without "16" (requirements), `game_art.py deliver <html>`, one date and "18" | 1 lost (the date), exit 1 |
| check 2 (`rule_doc_lint.py keep`) | the same copy | 6 lost, exit 1 |
| check 2 | the first draft | 1 lost: "per row" inside a span between two quotes had become "for each row". Restored. |
| check 1 | the final rewrite | 25 items, 0 lost |
| check 2 | the final rewrite | 95 spans, 0 lost |
| `rule_doc_lint.py`, `checkable.py`, `batch_done.py` selftests | none | PASS; 19 of 19; GREEN, 12 cases |
| `selftest_guiding_prose`, `selftest_skills_by_work`, `selftest_skills_registered_or_listed`, `selftest_validate_skills`, `selftest_game_names_prose`, `selftest_retired_era_gone` | new text | PASS |

Names: no person is named in either text.

## What the meaning read found

One fresh Opus reader (rm-judge, model opus) read both texts and the `lifecycle.md` corrections without the writer's
reasoning. The reader checked the added facts against the code. It found 6 items. All are repaired. No reader read the repairs, nor
six small sentence splits made after them for the STE target.

| finding | repair |
|---|---|
| `lifecycle.md`: a default refresh does not report `SERVER DOWN` for a dead server | `(not served)`; `SERVER DOWN` means that a restart failed |
| "Only a pass … moves the sheet into place" is false with `--allow-failing` | the exception is named |
| "He retires the current art …" lost the old rule's place and read as a description of him | the old words, back on the 2026-10-12 bullet |
| the `review_queue.py` marks read as the definition of "finished" | the marks do not prove that a sheet is open; check that the picks are not enacted |
| the phone line had no condition | the condition: his device cannot reach the URL; export, then publish privately |
| step 5 read as a guarantee | `--apply` skips a file with an orphaned letter; resolve that letter first |

The reader's small notes on `lifecycle.md` (requirement 9, the `subjects.json` row) are repaired too.

## Conflicts and stale lines: settled

Rules: 1 the code or the live tool; 5 the obvious answer. The item's step 2 says "list the conflict; do not pick".
`batch_plan.md` says to settle each conflict.

| conflict or stale line (side 1 / side 2) | decision | rule and evidence |
|---|---|---|
| the three tools refuse an unread sheet with exit 4 / `review_queue.py` exits 1 | exit 4 is stated for `serve_gated.py` and `sheet_to_artifact.py` only | 1: `review_queue.py:392`, `sheet_to_artifact.py` |
| only the builders can produce a stamp / `scaled_review_gate.py check --stamp` stamps a passing sheet | only the builders can make a sheet that earns a stamp | 1: `load_ctx` fails a sheet with no snapshot |
| "nothing else" than a `http://localhost` URL / the phone page | the phone page is the route for a device that cannot reach the URL | 1: `sheet_to_artifact.py`; `lifecycle.md` |
| `lifecycle.md`: refresh restarts a dead server / refresh restarts one only with `--restart-servers` | `lifecycle.md` corrected, two places | 1: `refresh_sheets.py` |
| `lifecycle.md`: "all 14 requirements" / 16 | `lifecycle.md` names no count | 1: `scaled_review_gate.py` |
| `lifecycle.md`: the sheet HTML and `subjects.json` are tracked / only when pinned | `lifecycle.md` corrected | 1: `Transient/.gitignore` |

Nothing goes to the owner.

## Seen and left

- The refusal text of `.claude/hooks/block_hand_edited_sheet.py` says "check all 12 rulings". Nobody acts on the count.
- `references/art_requirements.md` lists 14 requirements. The gate also checks 15 (freshness) and 16 (live writer).
- `game_art.py` names `.githooks/pre-commit` once in its docstring. The hook is `infrastructure/githooks/pre-commit`.

## Could not determine

Nothing in the active file.

## What this run did not test

- No sheet was built, served, refreshed, remapped or enacted.
- No measurement shows that an agent handles a sheet better with the new text.
- The trigger evals were not run, because the description did not change.
