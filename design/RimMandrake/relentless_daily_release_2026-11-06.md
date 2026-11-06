# One pinned daily release of Relentless, with a way back (2026-11-06)

Item: RELENTLESS_BUILD_DAILY_RELEASE_WITH_ROLLBACK. Owner card 2026-11-06, the Subtract plan. Code:
`src/RimMandrake/rimflow/relentless_release.py`; test `selftest_relentless_release.py`; units
`src/RimMandrake/Utils/systemd/rm-relentless-release.{service,timer}`.

**`relentless_selfbuild.py` did not fit and was not wired.** It decides whether a candidate may replace the builder (a
protected-path check, pass^k on frozen sets). It has no notion of a tree, a pin, a record or a way back, so there was nothing
in it to reuse for this. It stays as it was.

## How the tick runs now

Before: `rm-relentless.service` ran `books/src/.../relentless.py`, and the tick fast-forwards books, so every push redeployed
it. Now it runs `<root>/release/<sha12>/src/.../relentless.py`, the path `<root>/release/current` names when the unit starts
(`readlink -f` once in ExecStart, so a run and every child it starts stay in one tree when `current` moves).

A release tree is a farm: every `.py` under `rimflow`, `Utils` and `contracts`, `bridgetools/companion_identity.py` (the one module there the tick imports), plus `rimflow/relentless*.json`, is a real file at
the sha; everything else is a symlink to the same path in books, `.git` included. So the ~20 places that derive the repo from
their own `__file__` still read the live ledger, items, mods and design. `BOOKS` in `relentless_live`, `relentless_names`,
`relentless_stage` and `relentless_broker` is the directory holding the real `.git`, so they hand books, not the farm, to tools.
Books still levels to main every tick: **a push moves the data, not the code.**

The record is `<root>/release/log.jsonl`, append only: `{at, date, sha, id, kind, why, by, from}`, kinds `daily`, `emergency`,
`rollback`. The way back is computed from it (a release pushes, a rollback pops), so there is no second state to disagree.

## Commands

```
relentless_release.py cut --daily                   04:30 local, rm-relentless-release.timer; a second run the same date does nothing
relentless_release.py cut --emergency --why "..."   early, named and logged; --sha picks any commit landed on origin/main
relentless_release.py rollback [--why "..."]        back one; twice walks back two. --dry-run names the target and smoke-tests it
relentless_release.py status                        pinned sha and date, the tick's own /proc reading, how far main has moved
```

A new tree must pass a smoke test before `current` moves: its entry points import from the tree itself, it finds the real
books, and one real tick runs on a scratch root (`selftest_relentless_tick_once.py`). A failure leaves the tick where it is, records
nothing and fails the unit, so the log ages past the deadman's max_age. **A real rollback runs no test**: the way back must not
depend on anything that may be what broke. Any release or rollback that date counts as the day's, so the same date's daily
cannot undo a rollback; the next date's daily goes forward from main again.

## What is pinned, and what is not

Pinned: the tick and every module it imports, `cli.py` when the tick calls the ledger, the detached live round, broker, exam and
dispute jobs, the wake, the detached jobs, the nightly store diff, and the limits in `relentless*.json`.

Not pinned, on purpose:

- **`relentless_owner_pause.json`**: his switch, thrown by a commit. It must reach the tick at once.
- **Machine tools the tick shells out to from books**: `scratch_clone.py`, `deploy_custom_mods.py`, `modlist_swap.py`, `testq`. They
  walk or manage the real tree, every seat uses them, and they are not Relentless. A push to one of them reaches the tick.
- **Other data files beside the code** (`Utils/*.json`, `dispatcher_schedule.json`): data, through the symlinks.
- **Any new file in a real directory** (`rimflow`, `Utils`, `contracts`) after the cut: the tree's list is fixed at build. New code cannot want it before the next release, and `.py` files never leak across, but a new data file a tool writes beside its own code stays on that side (`circling.py replay --write` is the one seen).
- **Worker verbs** (`beat`, `contract`, `finish`, `boxrun`) run from the worker's clone, as they always did. A worker can
  be up to a day ahead of the tick that launched it, and both read the same store.

Consequences: a limit in `relentless_rules.json`, including `share`, reaches the tick only by a release. To change one now, cut an
emergency release. A fix lands on main and waits for 04:30 unless someone cuts one.

## Known limits

- **ext4 can miss one lookup during the swap**: measured 3 misses in about 116k reads under 5,000 renames on this disk, none on
  tmpfs, and a second look finds it. A tick starting in that instant fails and the timer starts the next one 15 s later.
- A cut fetches for itself, so a dead tick can still be released to. A crash between a swap and its row is healed at the next act: `current` is the truth.
- A tree is kept for two days after nothing new could start in it (`GONE_AFTER_S`), so a live round started from it can finish. The up-to-eight on the way back are kept regardless.
- The smoke test is one scratch tick, not a full sweep. It catches what stops a tick from running, not a wrong decision.
