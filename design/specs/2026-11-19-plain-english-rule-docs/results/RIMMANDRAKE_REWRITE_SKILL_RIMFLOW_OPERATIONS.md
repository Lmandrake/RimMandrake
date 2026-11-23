# Result: `RIMMANDRAKE_REWRITE_SKILL_RIMFLOW_OPERATIONS`

Part of batch `RIMMANDRAKE_REWRITE_SKILLS_IN_CURATION_SESSIONS_ONE_SKILL_EACH` (`batch_plan.md`, order 17). Run 2026-11-23.
File: `skills/rimflow-operations/SKILL.md`.

Base: 5a2abcec61f2ceb790ef556476a363a4e3f38a2b

Also: `skills/rimflow-operations/references/history.md`

The front matter is byte-identical, the `description` included.

## Scores

| measure | before | after |
|---|---|---|
| bytes | 11,129 | 14,847 |
| words in linted prose | 988 | 1,583 |
| STE violations per 100 words | 3.74 | 1.58 |
| sentences over 20 words | 14 | 2 |
| flagged lines (mechanical) | 2 | 0 |
| hand count (lines a cold reader cannot act on) | 11 | 0 |

The two long sentences hold a command or its output: the `next_pass` / `notice` test (§2), and the bare `systemctl stop`
(§6).

## The hand count

| old line | what a cold reader lacks | state after |
|---|---|---|
| "relaunches the Fleet" | what the Fleet is | the windows that `machine.json` names |
| "(Steven's is lent: see below)" | where "below" is | §2 and `references/accounts.md` |
| "ESTIMATE (... and blind)" | what blind means | it does not see what was spent since |
| "Dormant accounts are read from their vault" | dormant, vault | both defined |
| "above its line", "hard line", "a live run" | no definition | defined at the top of §2 |
| "the 10:58 soonest-expiry rule", "10:15 words", "11:2x" | the date | 2026-10-28 |
| "A switch the priority pulls (above the line)" | what pulls | a priority switch is defined |
| "owner 2026-11-20, as above" | where "above" is | the soft line row |
| "acts once per transition (markers)" | what a marker is | a marker file records each transition |
| "lift it when the escape condition changes" | the escape condition | "when its reason ends, for example when a fresh account exists" (`references/traps.md`) |
| "Only D/A tunables" | D and A | both defined (testing policy §0) |

## Conflicts and stale lines, settled

| side 1 / side 2 | decision | rule and evidence |
|---|---|---|
| Steven may go to 10% late in the week (owner, 2026-10-26) / "up to 50% after a fresh reset only" (owner, 2026-10-27) | the second; the old row and quote moved to `history.md` | 2: the later words, "narrows" in `slot_rules.json` `lent_accounts`; 1: the engine never had the 10% rule |
| the allocator gives 0 new helpers at the soft line, and the launch refuses a new run / the code | the allocator only reports the 0; the launch refuses only in a drain | 1: `slot_allocator.py` `_decide_core` (`advisory`), `detached_helper.py` `drain_refusal` |
| "At an account's soft line no new run starts" (`standing_rulings.md`) / no program refuses it | the rule stays a rule; the skill says that the agent must hold the start; the gap is a ticket | 1 for the behaviour; ticket `RIMMANDRAKE_REFUSE_NEW_RUN_AT_SOFT_LINE_DRAIN_TOO_LATE` |
| the table (Steven 52%, the order) / a dated exception in force until 2026-11-25 14:00 PST | the values of the exception bind while it stands | 1: `switching_plan.py` `at`, `status` |
| a stale vault cannot be switched to / `claude-account use` | `use` checks the sign-in deadline, the login and the email, not the token age | 1: `cmd_use` |
| "interrupted switch; run recover" / the printed refusal | the printed words | 1: `cmd_use` |
| "Nothing else should call `use`" / two programs call it | the two programs are named as exceptions | 1: `login_watch.py`, `account_handover.py` |
| the engine disarms after a switch / only when the machine was disarmed before | the second | 1: `armed_call` |
| `clear` and `set` with no authority named / the code | `set` needs his words or a Conductor instruction | 1: `slot_allocator.py` `main` |
| `--n 0` did not stop the retired FOUNDRY seat (no cause) / the code | `--n` without `--seat` sets only the Conductor's seat | 1: `_decide_core` |
| the 2026-10-28 pause (HOLD) line | moved to `history.md`: the pause is over | 4: no `HOLD` file; `account-plan.timer` active |
| `references/accounts.md` "switch-away floor 0%" | 1% | 1: `switching_plan.json` `floors` |
| `references/plan.md` `switching_plan.py install` | deleted | 1: `main` has `check` and `status` only |
| the item "list the conflict; do not pick" / `batch_plan.md` "settle each conflict" | settled | the item says "Do the work as the plan says"; the plan forbids a listed conflict |

No conflict goes to the owner.

## The checks, with a planted loss first

| check | input | result |
|---|---|---|
| check 1 (`checkable.py compare`) | a copy with `pull_drain_max_s (2 h)`, 8,749 and 4.73M removed | 2 h and 4.73M lost, exit 1 (and one span that the first draft really lost) |
| check 2 (`rule_doc_lint.py keep`) | the same copy | 3 lost, exit 1 |
| check 1 | the rewrite with `history.md` | 46 items, 0 unfindable |
| check 2 | the same | 103 spans, 0 lost |
| `selftest_skills_by_work.py`, `selftest_retired_era_gone.py`, `selftest_game_names_prose.py` | final | pass |
| `skills/validate_skills.py` | final | 0 errors, 0 warnings |
| `batch_done.py selftest` | — | GREEN: 0 failed (12 planted cases) |

No selftest names `skills/rimflow-operations`. Names of people: the diff was read; "Steven" and the account names stay.

## What the meaning read found

Four fresh Opus reads (rm-judge), one after the other. No reader got the writer's reasoning. Reads 1 and 2 were of the
whole file. Reads 3 and 4 were of the repaired bullets. (The plan asks for the same reader. A resumed reader runs in the
background, where the end of this run could kill it. So a fresh reader read the repairs.)

| read | finding | repair |
|---|---|---|
| 1 | the helper half of "no new start" was lost | "of a run or of a helper"; no program refuses a helper |
| 1 | "hold the new start yourself" named no signal | the `switching_plan.py status` test |
| 1 | "obey the exception, not the table" was too broad | only the values that it sets |
| 1 | `hold --until COND` contradicted "use only pause" and could not be acted on | the sentence is out |
| 1 | the two callers of `use` did not read as exceptions | "The two exceptions are" |
| 1 | `history.md`: "`use` refuses only" was false | "Of the vault checks, `use` refuses" |
| 1 | a drain refusal lapses with a notice over 20 min old | added |
| 2 | `next_pass` can read `switch` or `hold` while the notice is soft | the `notice` test added |
| 3 | the age of a notice is its `at` | added |
| 4 | true; nothing lost | none |

No line of `SKILL.md` was edited after the last read of that line.

## Could not determine

None.

## Polish (not fixed)

- Under a `HOLD`, `next_pass.do` is `passive` and the decision is under `would_do`.
- The 20-min reset lead does not apply while the engine respects a hand switch.
- `login_watch.py` calls `use` only when `auto_switch` is on, the machine is armed, and no `HOLD` or `PAUSE` stands.
- The warm also needs an answer from every remote.
- The docstring of `switching_plan.py` still says "the switch-away floor, 0%"; the value is 1.

## What this run did not test

- No agent used the new file in real work.
- No switch, stop, arm, allocator `set` or timer pause was run. Those lines were read in the code.
