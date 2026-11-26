# BOUNDARY: the control acts export to git, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/control_acts_export.py`, run by `rm-control-acts-export.timer` (units in
`src/RimMandrake/Utils/systemd/`). Item: `RIMMANDRAKE_EXPORT_CONTROL_ACTS_BELT_SPLIT_FROM_SLICE_FOUR`, the slice 4
belt of the control store (`design/specs/2026-11-18-pipeline-control-surface/boundary.md`). Why it exists: his ask of
2026-11-18 10:36 AM, *"Make all of this deterministic, easy, traceable, reproducable, testable"*. The store keeps
every act on this machine only, and this copy in git is the record that outlives the machine. Written 2026-11-19.
Each promise has a test of its name in `src/RimMandrake/rimflow/selftest_control_acts_export.py`. A deliberately
broken stand-in per promise is in `src/RimMandrake/rimflow/acceptance/control_acts_export_breaks_accept.py`, and it
turns that test red.

## ACCEPTS (the only inputs the export is built for)

- **the-store-read-only.** The control store at `control.db_path()` is read through `control.export_acts`, with read
  connections only. The export never writes to the store.
- **a-clone-with-a-pushable-origin.** The export runs in a git clone whose `origin` takes a fast-forward push to
  `main` without a prompt (the timer runs in the dispatch clone, `/home/mandrake/rm/dispatch`, with the SSH key).
- **one-writer-of-the-file.** Only this export commits `infrastructure/state/control/acts.jsonl`.

## DOES NOT SURVIVE (not promised; where the export notices, it says so and stops)

- **a-schema-change-to-acts.** A new column in `acts` changes every line. A run then refuses, as if it would lose acts
  (never-loses-a-published-act). The fix is one export checked and published by hand.
- **a-hand-edit-of-the-published-file.** A line edited in git is a line the store does not hold, so every run
  refuses, naming it.
- **two-runs-at-once.** The timer's service is a oneshot, and systemd does not start a running oneshot again. A hand
  run during a timer run is outside: the loser's push is refused as non-fast-forward and it rebuilds.
- **a-store-reset-that-keeps-its-ids.** A store set up again from nothing reuses `ct_000001`. Its first act differs
  from the published one, so a run refuses (never-loses-a-published-act). The export does not merge two stores.

## PROMISES (each one is owed a test of the same name)

- **export-holds-every-act.** A run writes every act in the store, in revision order, one JSON line each (the
  `pipe export` format), and pushes that file to `origin/main` as `infrastructure/state/control/acts.jsonl` when its
  bytes differ from origin's. It prints `PUBLISHED <sha>`. Tested by `t_export_holds_every_act`.
- **unchanged-store-makes-no-commit.** A run whose file equals origin's pushes nothing and prints `unchanged`.
  Tested by `t_unchanged_store_makes_no_commit`.
- **touches-no-working-tree.** The commit is built in a temporary index from `origin/main`. The clone's working tree,
  index and `HEAD` are not touched, and the commit changes that one path only. Tested by
  `t_touches_no_working_tree`.
- **never-loses-a-published-act.** An export that lacks a line the published file holds is not pushed. This covers a
  store set up again, replaced or rewritten. The run exits 2 and names the first missing act. Origin's file is kept.
  Tested by `t_never_loses_a_published_act`.
- **could-not-look-publishes-nothing.** A store that is missing or corrupt publishes nothing. The run exits 3
  with the cause and never pushes an empty file. Tested by `t_could_not_look_publishes_nothing`.
- **reading-only-on-success.** The reading (`D:\ClaudeWork\rimmandrake\control\acts_export.json`, or `--reading`) is
  rewritten only by a run that pushed or found nothing to push. A failed or refused run leaves it to age, so
  `rm-deadman` sees a dead belt by its age. Tested by `t_reading_only_on_success`.
- **push-race-rebuilds.** A push refused because origin moved is rebuilt on the new tip and pushed again, up to 5
  tries. Then the run exits 4, naming the push error. Tested by `t_push_race_rebuilds`.
- **fetch-race-retries.** A fetch that loses the ref update to a peer's fetch in the same clone ("incorrect old value
  provided", "cannot lock ref") is tried again, up to 3 tries. Any other fetch error exits 4 at once, naming the
  fetch. Tested by `t_fetch_race_retries`.

## LIFE CYCLES (a move not listed here is a defect)

- **a run:** read the store → (could not look: exit 3) → fetch origin (lost to a peer's fetch: again, at most 3 tries, then exit 4) → compare with origin's file → (a published
  line is missing: exit 2) → (equal: `unchanged`, reading written, exit 0) → commit on origin's tip → push → (refused
  as non-fast-forward: back to fetch, at most 5 tries, then exit 4) → `PUBLISHED <sha>`, reading written, exit 0.
