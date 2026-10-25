# AGENTS.md — operating RimFlow in RimMandrake

Instructions for an AI coding agent that reads or writes RimFlow, the work ledger in this
repository. They apply to this repository and its shared-working-directory workflow; they
illustrate the current deployment and are not an installation guide. Read this before your first
`rimflow` call.

**Vocabulary.** A *seat* is a named workflow identity; `BENCH` and `FOUNDRY` are the two agent
windows, and `OWNER` holds events that carry owner provenance. A *shard* is a seat's event file.
The *bridge* drives the running game. A *question card* presents choices to the owner; a
*standing ruling* is an earlier owner instruction cited by reference. For full verb syntax and every live-caught
trap, the operational source is `skills/using-rimflow/SKILL.md`; where that file and a verb's
`--help` disagree, **`--help` is authoritative** (the code is newer than the prose).

`rimflow` below means `python3 src/RimMandrake/rimflow/cli.py`, run from the repository root.

## What you are touching

- The **ledger** is the only source of work state: `infrastructure/state/ledger/events.jsonl`
  (frozen history, never appended) plus one shard per seat, `infrastructure/state/ledger/events/<SEAT>.jsonl`.
  Read-only verbs (`next` aside, which reserves) change nothing; state-changing verbs append to
  **your seat's** shard, except that events carrying owner provenance go to the `OWNER` shard.
  Some verbs write more than one event (for example a successor spawned by the close-debt lint).
- **Item prose** is `infrastructure/state/items/<ID>.md` while open, `items/closed/<ID>.md` after.
- **Views** (`queue/BENCH.md`, `queue/FOUNDRY.md`) are generated and gitignored. Read them with
  `rimflow queue <SEAT>`; never edit or commit them. `queue/HUMAN.md` is the owner's inbox.

## The loop

1. `rimflow next --seat <SEAT>`: the one item to work now. It reserves the item for you. If it
   offers **RECONCILE**, published commits already name the item: judge them with
   `rimflow reconcile <ID> --verdict complete|partial|unrelated --sha <sha> [<sha> ...]` before
   building anything (`--remaining` says what a `partial` still owes).
2. `rimflow claim <ID> --seat <SEAT>`: takes a 45-minute lease and moves the item to `doing`.
   `rimflow renew` keeps the lease alive; `rimflow release` hands it back early.
3. Do the work. Commit it by explicit path and publish it (`./publish -m "<msg>" <paths>`).
4. `rimflow implemented <ID> --sha <published sha>`: refused unless the sha is an ancestor of the
   locally known `origin/main`. Records the item's level-tagged criteria and attests L0; the item
   becomes `built`, or `done` if nothing above L0 is owed. Run `rimflow show <ID>` to see what is
   still owed.
5. `rimflow verify <ID> --result pass|fail|partial --config "<what ran, where>" [--level L…] [--evidence <path>]`
   for each validation run. Each run is retained; a later run is a new event. A result describes
   the code and configuration that were tested, not later code. When the last owed criterion
   passes, the item becomes `done` on its own.
6. Only if the item is still open and nothing is owed, `rimflow close <ID> --sha <published sha>`.
   Use the explicit published sha of the implementing commit (the one `publish` reported), not
   `$(git rev-parse HEAD)`: in a shared directory `HEAD` may be another agent's commit. A second
   `close` is refused.
7. Commit your shard (and the `OWNER` shard if you wrote owner provenance) by explicit path.
   RimFlow reads git history but never commits or publishes; that is your job.

`rimflow show <ID>` prints everything known about one item; `rimflow why <ID>` explains why it is
not being offered.

## Invariants you must preserve

1. **Append only.** Never edit, reorder or delete a ledger line, by hand or by script. A wrong event
   is corrected by a new event. The pre-push `ledger_lint` hook refuses non-append changes. The one
   sanctioned exception is the torn-line repair tool (Traps, below).
2. **Read through the model.** To compute state, use `model.read()` (no path argument) and
   `model.replay(events, observe=cb)`. Do not merge shards yourself, sort by `(ts, event)`, or
   re-implement verbs. Hand-derived state has produced wrong counts here more than once (61 real
   `doing` items reported as 102).
3. **File position means nothing.** Shards merge with `merge=union`; order comes from the reader.
4. **Provenance is explicit.** Use `--owner-said`, `--by-card` or `--per-ruling` only when the
   owner's authority genuinely rests on that basis. Your own reasoning, including decisions within
   delegated scope, goes in `--why`, which grants nothing. These fields record asserted provenance;
   quotations are not checked against transcripts, so the honesty is yours.
5. **`needs` is not `block`.** `needs` says when an item can be worked (`offline`, `deploy`,
   `game-up`, `bridge`, `harvest`, `owner`). `block` says something is wrong.
6. **Names are retrieval keys.** New ids are `SUBJECT_INTENT_TWIST`, 3 to 7 words, at most 44
   characters, saying what is wrong or wanted. Check with `rimflow namecheck <NAME>` before `file`.

## Provenance flags

| flag | field | acts as OWNER? | what goes in it |
|---|---|---|---|
| `--owner-said "…"` | `ownerSaid` | yes | the human owner's own words; light typo fixes only. A question or bare assent ("yes") is refused. |
| `--by-card "question → option"` | `byCard` | yes | a decision he made by picking a question-card option (the option text is ours, so it never goes in `--owner-said`) |
| `--per-ruling <item-id or event>` | `perRuling` | yes | a standing ruling cited by reference, not re-quoted |
| `--why "…"` | `why` | no | your reason, in your words |

A decision delegated to agents (`design/RimMandrake/delegation_policy.md`) is
`--why "delegated: <class>"`. Never cite the delegation item with `--per-ruling` to make your call
read as the owner's.

Events with owner provenance are written to the `OWNER` shard. Commit that shard too.

## Traps (each one has happened)

- `close --sha` does **not validate**: a literal `HEAD`, or any typo, is stored verbatim, and an
  unparsable flag silently falls back to the HEAD *at call time*, which in a shared directory may be
  another agent's commit. Always pass the explicit sha that `publish` reported for your commit.
  (The skill file still suggests `$(git rev-parse --short HEAD)` straight after your own commit;
  that is only safe if no other agent committed in between.)
- Closing against a sha that `publish` later rebases away leaves a dangling reference. Close against
  the **published** sha.
- `file --replaces <ID>` makes the parent terminal in the same act. There is no undo verb; check
  the parent id before you run it.
- `infrastructure/state/MODE` (owner mode, for example `afk`) has no CLI setter and can be stale. If
  `needs=owner` items are suppressed while the owner is plainly present, check that file.
- A view rendered in a clone that is behind origin shows closed items as open. `git fetch` alone
  does not update the working ledger files; counts reflect the files in this clone. Before
  comparing counts across clones, either update the clone's files from origin or count from a
  fresh checkout of `origin/main`, and note the revision you counted. (A single documented
  procedure for doing this in a shared, dirty working directory does not exist yet
  [AUTHOR TO CONFIRM].)
- A torn line in any ledger file stops `rimflow` for every seat. The repair is
  `src/RimMandrake/Utils/repair_torn_ledger.py` (dry-run by default), never a hand edit.
- A stale clone cannot push its shard; rescue its events with `src/RimMandrake/Utils/ledger_sync.py`
  before any recovery.
- `unblock` refuses another seat's in-flight item: fix the false prose, commit, and `note`.

## Reservations, leases and shared resources

Item reservations (`next`) and leases (`claim`) coordinate assignment within one clone only; they
do not give exclusive assignment across clones.

**[RimMandrake-specific]** `rimflow bridge take --for "<purpose>"` before driving the live game;
`release` the moment you stop. The bridge holder record is overridable: a holder silent for 45
minutes is stale, and `--force` works and is recorded. A separate process-keyed driver lock
(b821520446) is what actually refuses a second driver process. Check `rimflow bridge who` rather
than waiting to be told; agents do not message each other.

## Do not (RimMandrake workflow policy)

- Do not `git add -A`, `git add .`, `git stash`, `git checkout -- <path>`, `git reset --hard` or
  create worktrees: other agents share this working directory, and hooks refuse these commands.
- Do not send messages to other agent windows. The queue and the owner are the only channels.
- Do not put your own words in `--owner-said`, or a question-card option label in it.
- Do not commit generated views.
- Do not call an item done on offline evidence when its criteria owe a live level. The close-debt
  lint will spawn a successor or warn.
- Do not hand the owner anything you have not read and checked yourself (standing ruling, 2026-10-22).

## Testing changes to RimFlow itself

Self-tests live beside the code: `src/RimMandrake/rimflow/selftest_*.py`. Run only those touching
your change:

```bash
python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/rimflow/selftest_model.py src/RimMandrake/rimflow/selftest_cli.py
```

Concurrency tests must run on the real ledger filesystem, not `/tmp`. The first one passed on `/tmp`
while the real disk lost 83% of writes (b7894ad768).
