# Result: `RIMMANDRAKE_REWRITE_SKILL_USING_RIMFLOW`

Part of batch `RIMMANDRAKE_REWRITE_SKILLS_IN_CURATION_SESSIONS_ONE_SKILL_EACH` (`batch_plan.md`, order 17). Run 2026-11-23.
File: `skills/using-rimflow/SKILL.md`.

Base: b2ca04c54e601f72a53d327eb992ad45bb3c7b4e

Also: `skills/using-rimflow/references/history.md`

The front matter is byte-identical, the `description` included. The headings are the same.

## Scores

| measure | before | after |
|---|---|---|
| bytes | 19,912 | 25,629 |
| words in linted prose | 2,439 | 3,257 |
| STE violations per 100 words | 4.39 | 1.78 |
| sentences over 20 words | 52 | 22 |
| flagged lines (mechanical) | 15 | 14 |
| hand count (lines a cold reader cannot act on) | 10 | 0 |

The file grew by 29%: the rewrite adds the `--publish` flag, the missing verb flags and the missing `close` refusal kinds.
The 14 flagged lines are 12 marker emoji on slogans and 2 copies of one cited heading. The 22 long sentences are owner
quotes, sentences that hold a command, or a bold slogan that the lint joins to the next sentence.

## The hand count

| old line | what a cold reader lacks | state after |
|---|---|---|
| "this seat's shard" | what a shard is | defined |
| "The ledger is SEVERAL files ... never what you want" | one subject for each sentence | a list |
| "a gate citing an item by name" | what a gate is here | defined |
| "brief harvesters to do this per question" | what "this" is | named |
| "`--why` lifts neither" | neither of what | named |
| "the visible escape", "a dead promise" | what a promise is | defined |
| "repeat 2 reads NEEDS FOLD" | what a fold is | "the first fix did not last" |
| "the window half" | why only that half | `CLAUDE_CODE_SESSION_ID` is unset, so the script cannot set the other half |
| "never from a stale seat clone's view" | what a projection is | defined at the top of the section |
| "a live holder holds" in one paragraph of 12 rules | which rule applies | a table and a list |

## Conflicts and stale lines, settled

Each is settled by rule 1 of `batch_plan.md` (the code decides).

| old line | decision | evidence |
|---|---|---|
| rimflow has "no git integration at all" | false: `--publish` lands the written paths | `ledger_landing.py` |
| four flags on every verb | eight | `build_parser` in `cli.py` |
| verb syntax "exact, from `--help`" | the flags that were missing are added (`drop`, `next`, `verify`, `bridge`, `close`, `claim`, `file`) | `--help` |
| `sweep` lists stale `TRANSIENT_*` files; `--transient` optional | lists `Transient/` too; the flag is required | `cmd_sweep` |
| `bridge who` "reads/repairs the mirror" | it reads the driver lock | `_bridge_who` |
| every `bridge` verb takes `--host` | except `give` | `_bridge_other_host_locked` |
| `next --seat <OTHER SEAT>` takes a lease | a read when the window has its own seat; `RIMFLOW_SEAT` decides when set | `_other_seats_read`, `resolve_seat` |
| `next` quotes only `## spec` | `## spec`, `## verify`, `## criteria` | `cmd_next` |
| bare positional targets are refused | true of `reassign` and `needs`; `bridge give` and `retarget` take one | `build_parser` |
| an owner flag lifts **fail** only | also guard and cited paths | `close_refusals`, `_close_gate` |
| the `live` verb is "the one way out of `done`" / a `verify` fail reopens (same file) | two ways out | `_apply_live`, `_earned_run` |
| recovery puts the item back | not when a guard is owed, not from `doing` | `_apply_live` |
| `unblock` refuses another seat's item | not BENCH on an OWNER item, not an owner flag | `_who_refusal`, `_may` |
| the hook checks the LOCAL HEAD; a stale clone cannot push | the hook checks the pushed commit; `./publish` replays first | `block_ledger_lint.py`, `publish.py` |
| `./publish` refuses when origin also changed OWNER.jsonl | it merges live appends, and warns | `publish.py` |
| a process holder is free at once, every game | a SteveDesktop game taken from another machine keeps a 45-min heartbeat | `_bridge_other_host_locked` |
| any OWNER ledger event restarts his clock | only one that his own hands wrote; a card answer counts | `is_his_act` |
| the item "list the conflict; do not pick" / `batch_plan.md` "settle each conflict" | settled | the item says "Do the work as the plan says" |

Seven false lines in `skills/using-rimflow/references/traps.md` are corrected in the same run, as `batch_plan.md` asks. They
are: the OWNER.jsonl publish refusal, a hook that does not exist (shard alone in its commit), `./publish` against a peer's
dirty file, the transcript guard on `--owner-said`, the refused machine alarm names, the hook on another seat's item file
(it only warns), and the two BENCH windows in `handoff.py`. The bridge idle-time bullet was narrowed to what is true now.

No conflict goes to the owner.

## The checks, with a planted loss first

| check | input | result |
|---|---|---|
| check 1 (`checkable.py compare`) | a copy without `25`, `95%`, one `45 min`, the `live_sweep.json` path and `uncheckedLifted` | 45 min, 95% and the path lost, exit 1 |
| check 2 (`rule_doc_lint.py keep`) | the same copy | 5 lost, exit 1 |
| check 1 | the rewrite with `history.md` | 39 items, 0 unfindable |
| check 2 | the same | 213 spans, 0 lost |
| `selftest_retired_era_gone.py` | a draft with a retired seat name | red on that line; pass on the final text |
| `selftest_skills_by_work.py`, `selftest_game_names_prose.py` | final | pass |
| `skills/validate_skills.py` | final | 0 errors, 0 warnings |
| `batch_done.py selftest` | - | GREEN: 0 failed (12 planted cases) |

No selftest names this skill. Names of people: the diff was read; the only one is the name in the game and machine names.

## What the meaning read found

Four fresh Opus reads (rm-judge), one after the other. No reader got the writer's reasoning. Read 1 was the whole file and
the changed traps. Reads 2 to 4 were the repaired places. (The plan asks for the same reader. A resumed reader runs in the
background, where the end of this run could kill it. So a fresh reader read the repairs.)

| read | finding | repair |
|---|---|---|
| 1 | `unblock`: the exception was named as the only one | two cases named |
| 1 | owner flags also lift the cited-paths refusal; `--why` and guard unsaid | the paragraph says each |
| 1 | guard: a record alone is not enough; `--no-code` too | added |
| 1 | recovery does not always put the item back | the two cases added |
| 1 | `retarget` also takes a positional target | added |
| 1 | "pass `--publish` on every write" was a new duty | "the short way"; a detached helper's brief asks for it |
| 1 | Exit 4 does not always print a command; RECONCILE and decay lost; SteveDesktop locks; the flyer exception | repaired |
| 1 | traps: move or delete of an item file, machine names, causes of a failed landing | repaired |
| 2 | guard: the test runs in the clone; a built item can owe one; `RIMFLOW_SEAT` beats `--seat` in `next` | repaired |
| 2 | the label `sha` also covers refusals that no flag lifts | the kind is named "cited paths" |
| 2 | STALE_GATE words, his hold's own take, the WARNING's scope, UPPER_SNAKE, the hook's limit, `who` | repaired |
| 3 | none | none |

The first landing's prose check named 9 sentences: 7 pronouns, "class guard test" and "RECONCILE or decay sweep". Each was
repaired in a second landing, and read 4 read those repairs: none. After read 3, one sentence of §Done means running became
its own bullet, with no changed word. Reader 2's point on
`bridge release --force` (a game other than ArchBig refuses it) is below, under Polish.

## Could not determine

- Whether `CLAUDE_CODE_SESSION_ID` is still unset on the Mac laptop. The line stays. A session on that machine knows.

## Polish (not fixed)

- The skill gives RECONCILE and decay sweeps one meaning. `cmd_reconcile` judges the commits that name one item and changes
  no state. A decay sweep closes or drops dead items. The instructed act is the same for both.
- `bridge release --force` on a game other than ArchBig does not cut a live holder; `take --force` does.
- `./pipe off game:<g>` beats `--force`; the skill does not say so (`game_lock.py` does).
- A verb that fails after it writes keeps its own exit code and prints `NOT PUBLISHED`, not exit 4.

## What this run did not test

- No agent used the new file in real work.
- No `close` refusal, bridge take, owner flag or torn-line repair was run. Those lines were read in the code or in `--help`.
