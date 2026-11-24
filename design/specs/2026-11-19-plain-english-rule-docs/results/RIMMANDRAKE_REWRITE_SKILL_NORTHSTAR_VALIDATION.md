# Result: `RIMMANDRAKE_REWRITE_SKILL_NORTHSTAR_VALIDATION`

One session of batch 17 of `batch_plan.md` (`RIMMANDRAKE_REWRITE_SKILLS_IN_CURATION_SESSIONS_ONE_SKILL_EACH`).
File: `skills/northstar-validation/SKILL.md`. Run 2026-11-23.

Base: `581ade435f`
Also: skills/northstar-validation/references/history.md

## Scores

| measure | before | after |
|---|---|---|
| bytes | 17,389 | 23751 |
| words in linted prose | 1,664 | 2528 |
| STE violations per 100 words | 4.75 | 1.46 |
| sentences over 20 words | 33 | 4 |
| flagged lines (mechanical) | 3 | 2 |
| lines that a cold reader cannot act on (hand count, by the writer) | 11 | 0; 1 listed under "Could not determine" |
| dead paths in `check_paths.py` | 1 | 0 |

The long sentences that stay, by kind. Two are the owner's quote of 2026-10-13. Two are short sentences that the lint
joined at a bold lead ("Every interference …", "A north star reads DRAFT …"). Two ⚠️ marks cause the flags. The 🔑 mark is
gone.

The front matter (`description` included), every heading and every owner quote stay byte for byte.

## The hand count

| old line | what a cold reader lacks | state after |
|---|---|---|
| "every interference you meet" | what an interference is | defined at first use |
| "wraps every chain" | what a chain and a component are | defined at first use |
| "the first SURPRISE/FATAL captures evidence" | what SURPRISE and FATAL are | defined |
| "sidecar JSON" | what a sidecar is | defined |
| "The path the runner uses today" | which command uses it | the caller is named |
| the `setup` row, one clause with nine steps | the order | a numbered list |
| "a 95 000-tick wait that is not chunked" | what to do about it | `tick_cap=` is named |
| "Bound it" | what "it" is | "Bound each expectation" |
| the `situational_rerun` flags | which program takes them | the file itself; `run_next.py` passes only `--dry-run` |
| "the loop then needs `shows=` claims" | what the loop is | a component must claim; the full run refuses |
| "Measure with `northstar.validated_baseline` + loosenings" | where loosenings is | `northstar.loosenings` |

## Checks, with a planted loss first

| check | input | result |
|---|---|---|
| check 1 (`checkable.py compare`) | a copy without one `paint_pond` name, `NORTHSTAR_SITUATIONAL_ROLLOUT_1`, the 48 ms and the 59/59 | 2 lost (the 48 ms, the id), exit 1. Check 1 did not see the other two. |
| check 2 (`rule_doc_lint.py keep`) | the same copy | 5 lost, exit 1 |
| check 1 | the final rewrite, with `--also` | 41 items, 0 lost |
| check 2 | the final rewrite, with `--also` | 202 spans, 0 lost |
| `rule_doc_lint.py`, `checkable.py`, `batch_done.py` selftests | none | PASS; 19 of 19; GREEN, 12 cases |
| `selftest_skills_by_work.py`, `selftest_guiding_prose.py`, `selftest_skills_registered_or_listed.py`, `selftest_validate_skills.py`, `selftest_game_names_prose.py`, `selftest_retired_era_gone.py` | new text | PASS |
| `selftest_live_queue.py`, `selftest_rollout_gate.py`, `selftest_situational_pass.py`, `selftest_suite_set.py` | the docstring and title edits in `live_queue/` | PASS |

Names: no person is named in either text. The one animal name (Marina) is in both.

## What the meaning read found

One fresh Opus reader (rm-judge, model opus) read both texts without the writer's reasoning. It found 3 real and 18
trivial items. The reader wrote that the owner quotes are word for word, and that each deliberate contradiction is true in
the code.

| finding | repair |
|---|---|
| the spoiled-run line gave a wrong home and dropped the deciding rule | the classes are stated, with `standing_rulings.md` as the home |
| the queue doc gave `hostile_raid` no failure condition | the conditions of `abort_proof.py` are stated |
| `--by-card` lost "he must hear the lines" | the condition stands above the list, for both routes |
| trivial: setup steps, the reuse line, `suite.biome`, autosaves, the split of a wait, "enforced", the antecedent of "that detector", "Closing one", REFUSED, the folder of the judge verdict | repaired |
| trivial: stale docstrings in `abort_proof.py`, the title in `jobs.py` | repaired |

The same reader then read the repairs. It found 1 real item (the queue doc lost two `hostile_raid` conditions) and 3
trivial. The real one and the APPARATUS FAULT line are repaired. No reader read those two repairs. No reader read three
small edits: "`setup()` then keeps", "The class is", and the bullet that holds the two homes of the spoiled-run rule.

Not repaired (trivial): a surplus pawn on the cell of a kept colonist stays; REFUSED also covers an unreachable bridge; the
hash leaves out the three validation header lines; "counts as unproven" beside "NOT IN THE TOTAL" (old wording).

## Conflicts and stale lines: settled

Rules: 1 the code or the live tool; 2 his later ruling; 3 root `CLAUDE.md`; 4 the thing is gone; 5 the obvious answer.

| conflict or stale line (side 1 / side 2) | decision | rule and evidence |
|---|---|---|
| the gate asks for "the current envelope" and "every on-disk suite" / it asks for its own commit and the minimal-list suites | the second | 1: `rollout_gate.py` (44d904c1cc, f96ff254c1) |
| `t.expect` takes `phase=` / only `w.expect` does | the second | 1: `suite.py` `TestContext.expect` |
| a chunked 95 000-tick wait passes / the chain needs `tick_cap` | the second | 1: `clockgate.py`, `watch.py`, `suite.py` |
| every hazard aborts / `hostile_raid` is recorded and removed. Also in the queue doc and the docstrings of `abort_proof.py` | the second | 1 and 2: his card of 2026-10-10; `abort_proof.py` |
| the focus fallback is the fix / `focus_game` refuses without the opt-in | the second; Run in background | 1 and 2: `game_focus.py`, 2026-10-04 |
| the runner uses `bland_world` / `modcheck run` does not pass it | the second | 1: `runner.run`, `situational_rerun.py` |
| one game cannot re-use the tile / `setup()` reuses the current map | both stated | 1: `bland_world.setup` |
| other saves did not change size / hashes | hashes; autosaves are not checked | 1: `save_guard.py` |
| §10 overrides §§3–6 / its heading says §§3–8 | §§3–8 | 1: `northstar_helpers_plan.md` |
| severities live only in `SEVERITY` / also in `LETTER_SEVERITY` | both | 1: `detectors.py` |
| the scoreboard reads only the summaries / also `checkout:` results | the second | 1: `required_checks_report.py` |
| a new bar needs him to hear the lines / four routes | four routes | 1 and 3: `cli.py` `validate`, `delegation_policy.md` §1 |
| an empty `northstar_driver` run has "no error" / it prints NOT GREEN with zero counts | the second; no error names the plan | 1: `northstar_driver/cli.py`, `bars.py` |
| naming dialogs come back every ~1000 ticks / ~600 ticks (code comments) | ~1000 | 1: `Faction.FactionTick`, `TicksGame % 1000 == 200` (RimSage) |
| a test-environment item for every threat / "Touching code" test 1 | the item stays | 2 and 5: his card of 2026-10-13 is specific, and `debug_process.md` and `governor.py` still hold it |
| the queue doc: the suite set comes from the status registry | from disk, `suite_set.py` | 1 |
| `bland_base.py`: NOT YET RUN LIVE / the save exists | the words are deleted | 1: the Saves folder |

Seen and left, with the reason: the comments "~600 ticks" in `modcheck/bland_world.py` and `modcheck/detectors.py`. Both files
are in the harness hash of `modcheck/gate.py` (`status.test_closure` of `runner.py` and `suite.py`). A comment edit there
would void each known-good live record. Correct the two comments with the next real edit of those files.

## Could not determine

| line | question | who would know |
|---|---|---|
| "the focus is also suspect" in the tick-rate row | if the 416 → 50 drop came from the maps or the focus | a live A/B probe (the time ledger calls it UNMEASURED) |

## What this run did not test

- No live game was driven. Each bridge claim that the code does not decide stands as written.
- No measurement shows that an agent runs a better pass with the new text.
- The trigger evals were not run, because the description did not change.
- The figures of 2026-10-01 were compared with the time ledger only. They were not measured again.
