# Boundary: `./now`, one screen of state in place of the poll round, Design Version 0.1.0

Item RIMMANDRAKE_BUILD_NOW_SCREEN_935_POLLS_IN_A_WEEK (script candidate 2 of
`design/specs/2026-11-26-script-candidates/one_page.md`: 935 state polls in 7 days, model time 77.9 min, wall 6.2 h).

Code: `src/RimMandrake/rimflow/now.py` (all of it) and the wrapper `now` at the repo root.

`now.py` adds two readers to the readers of the run-end wake and prints them through `run_end_wake.state_block`. The
wake's own readers and the block keep their promises on `design/specs/2026-11-23-wake-carries-result/boundary.md`.

## ACCEPTS

- **a-reader.** A function with no argument that returns text, a list of lines, an empty answer or None. The readers of
  the screen are `locks`, `pipe` and `accounts` (`run_end_wake.default_readers`), `runs` (`live_runs`) and `queue`
  (`queue_head`).
- **the-run-records.** `detached_helper.all_records()`: one record per run, with `unit`, `item`, `model`, `status`,
  `at` and an optional `host`. `detached_helper.live_status` says whether its unit is gone.
- **the-ledger.** `cli.load()` and `priority.rank(world, "BENCH", "v1", {})`, the order that `rimflow next` offers.

## DOES NOT SURVIVE (not promised)

- **a-reader-thread-that-never-ends.** A hung reader thread is left behind as a daemon thread. The process ends when the
  screen is printed. The thread does not end before that.
- **a-ranked-queue-that-moves.** The queue head is one reading. An item that a seat claims after the reading still shows.

## PROMISES (each one is owed a check of the same name)

- **each-reader-has-a-line.** Each reader of the screen gives at least one line, stamped with the local time of its
  reading and its name. An empty answer reads `none (looked)`. `./now` at the repo root is executable and has the five
  readers `locks`, `pipe`, `accounts`, `runs` and `queue`.
- **a-reader-that-raises-reads-could-not-look.** A reader that raises or returns None reads `COULD NOT LOOK (<cause>)`
  with its name. The other readers keep their lines.
- **a-hung-reader-does-not-hold-the-screen.** A reader that does not answer before the deadline reads
  `COULD NOT LOOK (no answer in N s)`. The screen prints, and the process ends, in spite of the hung reader.
- **live-runs-listed-with-age.** Each run whose record reads launching or running has one line: unit, item, model, state
  and age. A run whose unit is gone reads DEAD, with the command that finishes it. A finished run has no line.
- **queue-head-listed.** The first five items of the Conductor's queue, in rank order, each with its state and title.
  One line counts the rest and names the command that lists them. The screen never sends the reader to
  `rimflow next`, because `rimflow next` reserves a lease.

## LIMITS

- `DEADLINE_S` 45 s: a hang guard, never a speed bar. Danger: a hung reader (a ledger load on a stuck disk, the ssh of a
  remote run) holds the screen with no end. Measured need: 3.7 s, the ledger load (SteveDesktop, 2026-11-27).
- `QUEUE_HEAD_N` 5: a cut of what is shown. It ends no work. The rest is counted, with its command.
- `TITLE_N` 100: a cut of a shown title (`fulltext.clip`). The line says that it is cut and names `rimflow show <ID>`.

## LIFE CYCLES

- **a Conductor look:** `./now` → `now.screen()` → `run_end_wake.state_block(readers)` → each reader in its own thread
  → one printed block.

Later lists beside this page: `polish.md` (none yet).
