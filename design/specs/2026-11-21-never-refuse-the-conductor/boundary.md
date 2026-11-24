# BOUNDARY: a gate of form never refuses the owner or the Conductor window, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/principal.py` (the one helper), and the gates that ask it: `rimflow/cli.py` (`close`
evidence, `namecheck`), `rimflow/control.py` (`pipe undo` of a stop, `pipe on|off unit:`), `rimflow/maturation_hands.py`
(`fold`), `rimflow/detached_helper.py` (launch origin check, resume clone). Rules: root `CLAUDE.md` §A fault of form is repaired
where it is found (its case "His word and the Conductor's act are not refused"). Owner, 2026-11-21 about 1:25 AM PST:
"Great. So conductor is being refused by the pipeline. This will not stand." Item
`RIMMANDRAKE_NEVER_REFUSE_THE_CONDUCTOR_SEVEN_REFUSALS_ONE_NIGHT`. Each promise has a test of its own name (`t_` +
the name, dashes as underscores) in `src/RimMandrake/rimflow/selftest_never_refuse_conductor.py`.

## ACCEPTS

- **the-caller-mark.** The process environment: `RIMFLOW_SEAT` (else `AGENT_SEAT`), or the seat a tool already
  resolved, and `RM_ROLE_UNIT`. The Conductor window is seat BENCH (typed BENCH or CONDUCTOR) with no `RM_ROLE_UNIT`;
  the owner is seat OWNER with no `RM_ROLE_UNIT`. The seat is a mark, not authentication.
- **a-fault-of-form.** A gate's own sentence for what is missing or ill-shaped, and the refusal text it gave before.

## DOES NOT SURVIVE

- A process that sets `AGENT_SEAT=BENCH` and unsets `RM_ROLE_UNIT` by hand reads as the Conductor window (as
  `mod_owner_hold.conductor_window` always did; every launcher here sets `RM_ROLE_UNIT`).
- A gate that refuses for form without calling `principal.form` still refuses the Conductor. The planted-gate test
  proves the path, not that every gate takes it.

## PROMISES

- **principal-is-the-conductor-window-or-the-owner.** `principal.who` answers `conductor` for seat BENCH or CONDUCTOR
  and `owner` for seat OWNER, each with no `RM_ROLE_UNIT`; any `RM_ROLE_UNIT`, or any other seat, answers None, an
  explicit `--seat BENCH` inside a launched run included. `mod_owner_hold.conductor_window` answers through it.
- **a-planted-form-gate-waives-for-the-conductor-only.** A gate that calls `principal.form(what, refusal)` goes on for
  a principal, with one NOTE line and `what` in the event's `form_notes`; for anyone else it refuses with its own
  refusal text, unchanged. Ask-only (`refusal=None`) answers None for a non-principal.
- **replay-close-no-code-free-text.** `rimflow close <owed ID> --no-code "<a measured fact and its time>"` (no sha,
  run id, path or `told him at`) closes for the Conductor, the event noted `evidence form: free text`; a helper run is
  refused as before.
- **replay-long-names-file-spawn-namecheck.** `file` and `spawn` take a name over 64 characters or 9 words with a
  NAME NOTE; `namecheck` prints the problems and exits 0 for a principal, 1 for anyone else.
- **replay-note-positional-text.** `rimflow note <ID> "<text>"` and `--text "<text>"` both write the note; no text at
  all is still a usage error.
- **replay-pipe-undo-stop-and-on-unit.** `pipe undo <stop act>` withdraws every order of that stop its run has not
  obeyed: one not yet read is withdrawn silently; one read is withdrawn and the run's hook tells it once; a scope stop's
  switch is lifted. An obeyed one (its run ended) says so and prints the resume command. His stop (`--owner-said`) is
  withdrawn only with his words. `pipe on|off` accept `unit:<unit>` and a bare `rm-…` unit as `stop` does; `on` also
  withdraws the scope's unobeyed stop orders.
- **replay-fold-before-the-act-is-recorded.** `maturation_hands.py fold <id> --item <ID>` for an id the tick has not
  recorded yet keeps the fold (`pending_act`), and the act reads folded once the tick records it. An item off the
  ledger is still refused (that is substance: the follow-up does not exist).
- **replay-launch-publishes-the-ledger-shard.** `detached_helper.py launch` of an item filed only in this clone's
  shard (OWNER.jsonl from a ruling, say): for the Conductor the launcher runs the exact `./publish -m "ledger: <ITEM>
  filed" <shards> --ledger` itself (it waits for no peer's publish: design/specs/2026-11-22-ledger-write-lands-its-shard/boundary.md), notes it, checks origin again and goes on; a helper run is refused with the command, as
  before, and nothing is published.
- **replay-launch-continues-when-the-item-is-already-published.** When the launcher's own `./publish` exits non-zero
  (`REFUSED: nothing to publish: HEAD is already on origin/main`, another publish having landed the shard) the launcher
  fetches and reads origin/main again: the item found there, the launch goes on with a NOTE; absent, it refuses with the
  publish's own words. Item `RIMMANDRAKE_CONTINUE_HELPER_LAUNCH_WHEN_ITEM_ALREADY_PUBLISHED_NOTHING_TO_LAND`, 2026-11-22.
- **replay-resume-takes-a-fresh-clone-and-restores-the-bundle.** `launch --resume <session>` when `<ITEM>.det` is held
  only by FINISHED runs (a return that kept the clone) takes a fresh pool clone `<ITEM>.r<epoch>.det`, carries the
  transcript there, restores the bundle the session's newest run record names (run_store's restore_bundle), and the
  record's `clone_how` says what it restored. The fresh clone is the run's own (`owns_clone`), so its return gives it
  back. A clone a live or dead run holds gets no fresh twin. This repair is the tool's own and serves every caller.
- **real-ledger-unchanged.** A run of the test leaves the real ledger shards byte for byte as they were.

## STILL BINDS EVERY CALLER (never routed through principal.form)

His five acts, his holds, his OWNER bridge hold (cut only as the rule says), a `./pipe` stop of his, the spend stop he
ordered, the account order and leave lines, machine-safety brakes, no `push --force`.

Later lists beside this page: `polish.md`.
