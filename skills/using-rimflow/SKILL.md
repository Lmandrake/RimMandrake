---
name: using-rimflow
description: "Use before ANY rimflow / src/RimMandrake/rimflow/cli.py call — file, claim, start, close, drop, supersede, note, next, seat, sweep, bridge take/release/who — and before passing --owner-said, committing a ledger shard (infrastructure/state/ledger/events/<SEAT>.jsonl), or reading the ledger or queue/*.md projections. Covers the sharded ledger layout, exact verb syntax from --help, the close --sha literal-string and silent-HEAD-fallback traps, the four provenance flags (--owner-said / --by-card / --per-ruling / --why), --seat on the Mac laptop, ledger commits being local-only, merge-order projection, and the bridge lock."
---

# Using rimflow

## What rimflow is

rimflow is one master queue. rimflow makes the queue from an append-only ledger. No other file is the source of truth.

- 🔴 **The ledger is SEVERAL files since 2026-09-23** (`EVENTS_JSONL_SHARDING_1`, landed `2b5947555`).
  - `infrastructure/state/ledger/events.jsonl` is frozen history. Nothing appends to that file any more.
  - Each `file`/`claim`/`close`/etc. call appends to the shard of the calling seat,
    `infrastructure/state/ledger/events/<SEAT>.jsonl`. A shard is the part of the ledger that one seat writes. So two
    seats can never get a rebase conflict in one git-tracked file.
  - `model.read()` with no path merges the history and every shard. `model.read(model.EVENTS)` reads only the frozen
    history. You almost never want that.
- The prose of an item (spec, context, decisions) is in `infrastructure/state/items/<ID>.md` while the item is open. On
  close/drop/supersede, rimflow moves the prose file to `infrastructure/state/items/closed/`.
- An id has the form `PROJECT_VERB_INTENTION_TWIST`, 4–9 words, ≤ 64 chars. Check an id with `rimflow namecheck <NAME>`.
  Legacy `…_1` ids stay valid. An id is guessable cold, never a number.
- `file` and `spawn` refuse only two kinds of id: an id that exists, and an id that is not UPPER_SNAKE. These
  two verbs file any other bad name with a `NAME NOTE:` line and a `name_note` field on the event.
- `rimflow next --seat <SEAT>` is the one command that you need to start work. Each other view command (`show`, `why`,
  `render`, `reindex`) derives a view from the same ledger.

## Verbs

- Write each flag AFTER the verb. The flags are per-verb, not global. `cli.py bridge take --seat BENCH` works.
  `cli.py --seat BENCH bridge take` is refused.
- Every verb takes `--seat`, `--target`, `--mode`, `--owner-said`, `--by-card`, `--per-ruling`, `--why` and `--publish`.
- The syntax below is exact, from `--help`. Before you rely on a flag that is not listed here, run `--help` again.
- The CLI has more verbs. Their syntax is not in this skill (`block`/`unblock`/`finding`/`spawn`/`needs`/`retarget`/
  `reassign`/`reclaim`/`lint`/`artifact`/`render`/`reindex`/`game`/`capability` and others). `rimflow --help` lists them.

```
rimflow file <ID> --for FOR --title TITLE [--kind K] [--row N]
             [--target-field v1|v2] [--needs offline|deploy|game-up|bridge|harvest|owner]
             [--spec PATH] [--caused-by ID] [--replaces ID]
             [--not-now "<class>: <evidence>"] [--did-it SHA] [--not-worth-it "<why>"]
             [--effect CHECK] [--holds-why WHY]
             create work for ANY seat, including another's. FOR is a reader in
             src/RimMandrake/rimflow/alarm_routes.json.
             --replaces ID supersedes ID in the same act (parent closes, names successor).

rimflow claim <ID> [--token TOKEN]
             take ownership; lands in `doing` under a live lease (was `ready` before the 2026-10 lease redesign)
rimflow start <ID>          begin work, with no lease; never refused for missing prose

rimflow close <ID> --sha SHA | --no-code "<what>" [--evidence PATH] [--level LEVEL]
             [--config CONFIG] [--live LINE] [--remainder ID | --no-remainder "<why>"] [--reason REASON]
             close against a commit, any seat; --reason required in practice
             when the item is another seat's (see `close` is earned, below)

rimflow drop <ID> --reason REASON [--successor ID | --release-dependents]
             this will not be done (reason required). While open items wait on it, name the
             successor, or pass --release-dependents with --why.
rimflow supersede <ID> --by ID [--reason REASON]   a better item replaces it

rimflow note <ID> --text TEXT            a line of context; prose belongs in items/<ID>.md

rimflow show <ID>           everything the ledger says about one item
rimflow next [--peek] [--bench] [--ringed] [--acceptance]
             the one item to work now; --peek is read-only;
             --bench is the board-triage view (BENCH and OWNER only)

rimflow verify <ID> --result pass|fail|partial --config CONFIG
             [--evidence PATH] [--sha SHA] [--level LEVEL] [--outcome OUTCOME] [--criterion ID]
             record a RUN. Immutable — a fail stands forever.

rimflow seat {ready,busy,idle} [--reason R] [--item ID] [--note NOTE]
             announce what this seat is doing; --note is what a handoff reads

rimflow bridge {take,release,who,give,idle} [to] [--for PURPOSE] [--force]
             [--idle-ok] [--flyer] [--host HOST] [--mine] [--despite-hold WHY]
             `who` only reads; `idle` reports whether a take with --idle-ok would succeed, and takes
             nothing; `take`/`release`/`give` write the ledger. --force takes it from an awake other
             window (recorded). `give` is the owner's switch, for ArchBig only.

rimflow sweep --transient    lists what is in Transient/ and stray TRANSIENT_* files, with ages.
             LISTS ONLY, no ledger write.
```

More traps for this section: [references/traps.md](references/traps.md) § Verbs.

## Item hygiene

The incidents behind these rules: [references/history.md](references/history.md).

- 🔴 **An item's prose must not be the only copy of its inputs.** An item can name a `Transient/` file as its input.
  `Transient/` is untracked, so the file can be gone from every clone when the item comes up. Pin the file
  (`transient_pin.py add`), or copy what matters into the item. (The item `NORTHSTAR_PROCESS_RETRO_1` lost its input.)
- A list of helpers in an item goes stale. Before you build from an old list, `grep` the tree. The helpers can exist
  under other names.
- 🔴 **An item filed alongside a finished analysis must cite the report path.** Without the path, the next window does
  the analysis again.
- ⚠️ **An item's "NEXT:" note can be DISCHARGED by a later item.** The later item can record that the noted work is
  served and ruled. Before you act on any note, list the items filed AFTER the note that name the same subject.
  `ls -t infrastructure/state/items/` is enough. The newest item outranks an older note.
- 🔴 **`rimflow unblock` refuses another seat's in-flight item, and names the right move itself.** Correct the false
  prose in the item file of that seat. Commit by explicit path. Use `note` to nudge that seat. Do not force the state.
  (Two cases are not refused: BENCH on an item that OWNER owns, and an act with an owner flag.)
- ⚠️ **A gate citing an item by name should be treated as suspect the moment that item's own state changes, not just
  after weeks.** A gate here is prose that says "blocked by", "waits on", "until" or the like about an item.
  `rimflow lint --citations` reports such prose as STALE_GATE when the named item is closed, dropped or superseded. The sweep found prose that called an item "still open/blocked"
  when that item closed the SAME calendar day. One such item closed within the same session. A doc can go stale within
  hours, not only weeks.
- **An item is a claim about the past; read it to its END.**
  - Writers ship work without a change to the item file. Notes never expire. Prose keeps "open question" text after the
    ruling lands.
  - `rimflow next` quotes only the item's `## spec`, `## verify` and `## criteria` sections, and cuts long text. The
    answer is usually under a later dated heading.
  - Then run `git log --oneline -5` on the files and keywords that the item names. Silence in the item file proves
    nothing.
  - Treat a note that says "owed" as a `NEXT:` note. First look for a later item on the subject.
  - Before you put a harvested "open question" on a card, grep `infrastructure/state/ledger/events/*.jsonl` and sibling
    items for its topic (owner: "You had asked me those questions before."). Brief each harvester to do this for each
    question.
  - When you solve an item, fix both its `needs:` and its stale opening section. If you do not, the next window gets
    your dead theory as top-priority work.
  - Classify items by their `state:`, never by a name list.
- **Any seat closes dead items.** (owner) "when any queue item is found to have been completed, totally invalidated or superceded, or otherwise rendered into something no longer worthy of being considered for activity, ANY SEAT may denote this in its log, record which seat ruled this, and CLOSE it completely."
  - `close`/`drop`/`supersede` are `who: "any"` in `model.py`.
  - Pass `--reason` with the proof, and no owner-quote flag.
  - Done means proven. A subagent's verdict is not the proof.

More traps for this section: [references/traps.md](references/traps.md) § Item hygiene.

## `close` is earned (RO3, ruling D1(b), 2026-11-01)

A close needs evidence, not only a commit. The code of the gate is `_close_gate` in `src/RimMandrake/rimflow/cli.py`.

- `close` needs `--sha <published sha>` or `--no-code "<what>"`. rimflow never assumes HEAD.
- rimflow refuses a sha that does not resolve here, and a local commit that is not on origin/main.
- rimflow also refuses a sha that touches only the ledger, the item prose or the queue views.

Then rimflow reads the item. A refusal prints its reason and changes nothing. The kinds are:

- **owed:** a criterion is still outstanding, or the criteria passed on another sha. No word lifts this refusal. Verify
  the criterion, or drop the item.
- **unchecked:** no level-tagged pass is on that sha. Since 2026-11-20, rimflow does not refuse such a close. The close
  goes through with a note, and the event carries `uncheckedLifted`. Record a pass where you have one:
  `rimflow verify <ID> --sha <sha> --level L0 --result pass --config <what ran> --evidence <path>`. A pass on another
  sha does not count.
- **fail:** the newest deciding run is a fail. A pass on that sha after the fail clears this refusal.
- **guard:** this fix died: its live promise broke after the fix was built or closed. No newer guard is on record.
  - A guard (a class guard test) is a test for the whole class of this fault. `rimflow guard` must see the guard fail on this
    instance of the fault.
  - This kind refuses a `--no-code` close too. Record the guard with `rimflow guard`. The close runs the recorded test in
    your clone, and the test must pass. Which commit must hold the test: see the traps file.
- **cited paths** (rimflow prints `sha`): the sha touches none of the paths that the item cites. This close needs `--why`.

`--owner-said`, `--by-card` or `--per-ruling` on the close lifts **fail**, **guard** and **cited paths** only. `--why`
lifts only **cited paths**. `--why` does not lift **owed**, **fail** or **guard**.

A `verify` moves state both ways:

- A fail on the built sha moves `validated` to `built`, and the item owes the criterion again.
- A fail on a closed sha REOPENS the same item (`done` -> `ready`). So does a fail on a later commit that contains that sha.
- A pass on any sha but the built one counts for nothing.
- A run before `model.EARNED_FROM` replays as it was written.

More traps for this section: [references/traps.md](references/traps.md) § `close` is earned (RO3, ruling D1(b), 2026-11-01).

## Done means running: `--live`

A promise is a line that says what must stay alive. These closes need a promise that holds right now:

- a commit that touches a hook, a systemd unit, `dispatcher_schedule.json` or `ops_watch_rules.json`;
- an Operations alarm (`OPS_*`, `LIVE_RESTORE_*`). If its commit changes only design prose, rimflow writes the line;
- any item that already holds a promise.

    --live "unit=rm-foo.timer reading=<path> max_age=6h"     the reading must be newer than the commit
    --live "unit=rm-foo.timer max_age=6h"                    the timer's own last firing
    --live "hook=block_foo.py"
    --live "role=Operations max_age=2d"
    --live "once: <why this is a real one-off>"              the visible escape; never swept

- `close` and `implemented` take `--live` alike. A refusal changes nothing.
- `rm-deadman.timer` (no AI, every 15 min, from the dispatch clone) rechecks every promise on the ledger and in
  `src/RimMandrake/rimflow/live_baseline.txt`.
- A dead promise reopens the SAME item through the `live` verb. Only the seat RUNNER may use that verb. Recovery puts
  the item back. Two items stay where they are: one that still owes a guard, and one that is in `doing`.
- The `live` verb and a `verify` fail on closed work are the two ways out of `done`.
- A promise with no item files `LIVE_RESTORE_<NAME>`. That id is fixed, so a return counts on one item. At repeat 2,
  `show` prints NEEDS FOLD: the first fix did not last. Operations owns that item.
- To remove a promise, retire its item or its baseline line by hand, or put its subject in
  `src/RimMandrake/rimflow/live_retired.txt`.
- The last pass is `D:\ClaudeWork\rimmandrake\ops_watch\live_sweep.json`.

## The filing gate: `--not-now`, `--did-it`, `--not-worth-it`

In a run with `RM_ROLE_UNIT` (a helper, and a headless Conductor run too), `file` and `spawn` refuse a work ticket with
exit 6. Only the kinds `owed`, `design`, `notice` and `alarm` pass with no flag. `--owner-said` or `--by-card` lets a
filing pass; `--per-ruling` alone does not. The refusal is recorded in
`D:\ClaudeWork\rimmandrake\dispatcher\filing_refusals\<unit>.jsonl`. Resolve each refusal with the same id, in one of
three ways (give only one; two at once exits 2):

| flag | when | what happens |
|---|---|---|
| `--did-it <sha>` | you did the work in this run and landed it | files nothing, exit 0. The sha must be on origin/main and change more than the ledger. |
| `--not-now "<class>: <evidence>"` | this run cannot do it now | files the ticket, with the class and the evidence on the event. The refusal text lists the classes. |
| `--not-worth-it "<why>"` | it fails test 1 (CLAUDE.md §Touching code has a cost) | files nothing, exit 0. The why needs 12 characters or more. |

The Stop hook `.claude/hooks/filing_refusal_before_stop.py` blocks the run's end (at most 2 times) while a refusal has
none of these. The run-end text of `detached_helper` names each one to the Conductor. A program that files sets
`RM_FILING_PROGRAM` in the env of its own cli call. Never set it, or `RM_UNDER_SELFTEST`, in your shell. Page:
`design/specs/2026-11-24-filing-gate/boundary.md`.

## Provenance: `--owner-said`, `--by-card`, `--per-ruling`, `--why`

The owner ruled these flags by question card, 2026-10-11. The transcript-proof guards were deleted that day. The
guards had found 0 forgeries, and 95% of their refusals were his real words. Each kind of authority has one field. So
nothing lands in `ownerSaid` by mistake:

| flag | event field | acts as OWNER? | what goes in it |
|---|---|---|---|
| `--owner-said "…"` | `ownerSaid` | yes | **his words.** You may fix typos and join two of his own sentences, if the meaning is unchanged. Never your words. |
| `--by-card ["question → picked option"]` | `byCard` | yes | a decision that he took by a click on a question-card option. The label is OUR text, so it never goes in `--owner-said`. Words that he TYPED into the card's notes/Other may go there. A bare `--by-card` takes the card that he answered last. |
| `--per-ruling <item-id\|event>` | `perRuling` | yes | a standing ruling of his, cited by its item id or ledger event (e.g. `OWNER.jsonl:<tsn>`). You do not quote the ruling again. **A ruling stands until he changes it.** rimflow refuses a value with spaces (that is a quote, not a reference). rimflow also refuses a reference that names no item and no ledger event. |
| `--why "…"` | `why` | **no** | your own reason in your own words (a restart that you decided, an investigation note). It grants nothing. You may combine it with any other flag in this table. |

- **A delegated decision** (`design/RimMandrake/delegation_policy.md`, owner 2026-10-22) is `--why "delegated: <class>"`.
  The decision is ours, not his. ⛔ Never pass `--per-ruling` with the delegation item to make the call read as OWNER.
  The ruling authorises the class, not the call.
- rimflow checks only the **shape** of the quote. rimflow refuses an empty quote. rimflow records a question or a bare assent
  ("yes") as he typed it. For a bare assent with no `--why`, rimflow prints a note that asks for one (owner 2026-11-20).
- `note --owner-said` stamps the WHOLE event as OWNER-authored. For your own text, use a bare `note` (plus `--why` if
  useful).
- `rimflow show <ID>` prints each field with a label (`owner said “…”`, `decided by card:`, `per standing ruling`,
  `agent's reason:`).
- `./game` takes the same four flags. `--said` is its spelling of `--owner-said`. Stamp a restart that you decide with
  `./game --why "<your reason>" <state>`.

More traps for this section: [references/traps.md](references/traps.md) § Provenance: `--owner-said`, `--by-card`, `--per-ruling`, `--why`.

## Seat identity

- `RIMFLOW_SEAT` beats `--seat`. rimflow refuses a write when nothing names the seat (an owner flag names OWNER). rimflow
  also refuses a seat that it does not know.
- On the Mac laptop, neither rimflow nor `handoff.py` can derive the seat. That machine has no seat profile.
  `CLAUDE_CODE_SESSION_ID` is unset there, so `set_agent_window.sh` does only the window half. So pass an **explicit
  `--seat`** on every ledger call there. If you do not, the ledger trail of a whole sitting can land under the wrong
  seat. rimflow does not know the seat `MACBENCH`. Only the handoff tools use that name.
- Pass the target of `reassign` and `needs` with `--to` (for example `reassign --to BENCH`, `needs --to bridge`). These
  verbs refuse a bare positional target. Two verbs do take a positional target: `bridge give <seat>` and
  `retarget <ID> v1|v2`.
- **`rimflow next --seat <OTHER SEAT>` is a read when the window has a seat of its own** (`AGENT_SEAT` or the session role
  file). That read takes no lease.
- In a window with no seat of its own, that command takes a real lease as `<OTHER SEAT>` in YOUR clone. When
  `RIMFLOW_SEAT` is set, `next` reads and leases for the seat in `RIMFLOW_SEAT`, whatever `--seat` says.
- A wrong lease in another seat's shard blocked `./publish` once. A diagnostic
  `next --seat FOUNDRY` (a seat now retired) wrote that lease into the local `FOUNDRY.jsonl`.
- For a read that writes nothing, use `next --seat X --peek` with `RIMFLOW_SEAT` unset (the Dispatcher uses `--peek`).
  `blind_view.py queue <SEAT>`, `rimflow why` and `rimflow show` are also reads. Run the command in THAT seat's clone. The Dispatcher peeks there, because the local
  reconciles of a seat are not on origin.

More traps for this section: [references/traps.md](references/traps.md) § Seat identity.

## Committing ledger writes

rimflow writes the shard of this seat, `infrastructure/state/ledger/events/<SEAT>.jsonl`, to disk at once on every
`claim`/`start`/`close`/`note`/etc. call. Without `--publish`, rimflow commits nothing, and the commit is the job of the
calling seat.

- The short way to land a write is the flag `--publish`. The brief of a detached helper asks for it on every write.
  rimflow then lands exactly the paths that the call wrote: the shard, OWNER.jsonl
  for an OWNER event, and moved item prose. rimflow prints `PUBLISHED <sha>`. Exit 4 means that the write stands and the
  landing failed. The printed line then names the cause, and the command that lands the write where rimflow can make one.
- A write without `--publish` is easy to miss. CLAUDE.md says "explicit paths, never `git add -A`". So a commit that
  names only the code and content files of a fix never includes the ledger change. The queue history of a full session
  can stay uncommitted, and is lost if the machine goes down.
- If you write without `--publish`, commit the shard `infrastructure/state/ledger/events/<SEAT>.jsonl` by **explicit
  path**. Do that with each close, or at least once per work wave, not only at session end.
- Prefer a separate "ledger sync" commit to a code commit that also holds the shard. Then the message of the code commit
  stays on its subject, and the ledger has a readable commit history.
- Never commit the rendered `queue/<SEAT>.md` files (gitignored since 2026-10-02). Read them with
  `rimflow queue <SEAT>`, which renders first.
- ⚠️ **A stale or dirty clone cannot push its own shard** with a plain `git push`. The pre-push `ledger_lint` hook checks
  the commit that you push. If the clone is behind origin, the hook refuses that commit as `NOT_APPEND` against the
  shards of other seats. `./publish` first replays your commits onto origin/main. So use `./publish`.
- If `./publish` cannot land the events, `src/RimMandrake/Utils/ledger_sync.py` rescues them onto origin/main. Run
  `ledger_sync.py` before any recovery of a stale clone. If you do not, the events are lost with the clone.
- 🔴 **A torn/invalid line in ANY ledger file breaks `rimflow`/`./game` entirely for every seat.** A torn line has no
  admin-event fix, because rimflow cannot finish the read of the file to append one. Since the sharding, a torn line is far
  more likely in a shard than in the frozen file. (One came from a bad `git stash pop`: history file.)
- `src/RimMandrake/Utils/repair_torn_ledger.py` repairs a torn line:
  - The default is a dry run. Pass `--apply --owner-said "…"` to write.
  - `--seat <SEAT>` targets the shard of that seat. The value is a seat name, never a path.
  - The tool removes only lines that fail to parse. The tool keeps a whole event that is joined to a torn fragment.
  - The tool first makes a backup in `D:\ClaudeWork\rimmandrake\ledger_repair\`. The tool stops at more than 25 bad lines.
- **`--owner-said` (and `--per-ruling`/`--by-card` acts) write `infrastructure/state/ledger/events/OWNER.jsonl`, not your
  seat shard.** A commit of only `<SEAT>.jsonl` leaves those events uncommitted (17 raise/note events sat ~8 h once).
  `./publish` prints a WARNING when OWNER.jsonl has uncommitted events and you named other paths. After any such act, land
  OWNER.jsonl too.

More traps for this section: [references/traps.md](references/traps.md) § Committing ledger writes.

## Reading projections

A projection is a view that a program makes from the ledger, for example `rimflow show` or `rimflow queue`.

- Every ledger file is append-only. Since 2026-10-02, git merges the shards with `merge=union` (`.gitattributes`). Union
  keeps duplicate lines, and mixes the appends of two clones in any order. So **file position means nothing**.
- `model.read()` with no path is the one reader that is correct under union. `model.read()` collapses identical events, and orders by
  `(ts, subject, model.VERB_RANK, seat, content)`, with `tsn` (nanoseconds) before the subject. `model.read()` never orders by file.
- **Never re-sort on `(ts, event)` yourself.** A sort by `event` name inverts a `start`+`close` pair of the same second.
  Such a sort once turned 61 real "doing" items into a reported 102. `VERB_RANK` exists to prevent that.
- If you make your own view (instead of `rimflow show`/`next`/`queue <SEAT>`), call `model.read()`. Do not merge by hand.
- When two windows claim one item at the same time, the earliest ts wins. `rimflow next` prints a CONTESTED CLAIM notice
  with both timestamps. The window with the later claim stands down.
- `ledger_lint.py` (selftests + a push guard) refuses torn lines, missing newlines and any non-append edit.
- 🔴 **A view is only as current as the clone it renders from.** `rimflow queue` in a clone behind origin replays an old
  ledger, and shows closed or changed items as open. A RECONCILE or
  decay sweep is any pass that checks if open items are already done or stale. Such a sweep checks each item again in a
  fresh origin clone (`git fetch` and compare, or `scratch_clone.py`), never in the view of a stale seat clone.
- 🔴 **Never re-derive item state from raw events by hand — fold through `model.replay(events, observe=cb)`.** A reader
  that knew only the `needs` verb missed `implemented` and `file --needs owner`. So the old RimPulse board hid 29 owner
  items, and listed one item 9.5 h after it moved (2026-10-11).
- `model.replay` calls `observe(ev, world, ok)` after every folded event. So `observe` tells you which event moved a
  field, and you do not write the verbs again.

More traps for this section: [references/traps.md](references/traps.md) § Reading projections.

## Bridge lock

There are several games. Each game has its own lock, and one holder at a time:

| game | what it is | lock |
|---|---|---|
| ArchBig | Steam's install on Archmagi, with the full list | `archmagi` (the default) |
| ArchSmall | its own install on Archmagi | `archmagi.b` |
| Steve1, Steve2 | the games on SteveDesktop | `stevedesktop`, `stevedesktop.b` |

- Every `bridge` verb takes `--host <lock>`, a game name or a lock key, except `give` (ArchBig only).
  `RM_GAME_INSTANCE=b` with no `--host` means the ArchSmall of this machine.
- A held ArchBig is not a reason to wait. Take ArchSmall, and name the game in every note (CLAUDE.md "There are several
  live games").
- Who drives each game is that game's driver lock. `game_lock.py query|claim|release|run` and
  `rimflow bridge who|take|release` read and write that lock. `rimflow bridge` also writes the history in the ledger.
  Nothing decides from that history.
- `take --for "<what for>"` says what you drive the game for. `release` the moment you stop.
- A holder is a process. When the process ends, the game is free at once. A live holder holds. `--force` cuts a live
  holder, and is recorded. (A SteveDesktop game that you take from another machine is different: run `take` again within
  45 min to keep it.)
- 🔴 **His OWNER hold is the exception** (owner, by card 2026-10-30: *"45 minutes after my last interaction, or I deliberately release it"*).
  - No take, `--force` or release by a seat works until 45 min after his last deliberate interaction.
  - His deliberate interactions are: an OWNER ledger event that his own hands wrote; `./bridge`; `./game`; his chat prompt
    to any seat; his answer to a question card. The take of his hold starts the clock too. An
    event that an agent relays for him does not count.
  - An unmeasured signal refuses (`rimflow/owner_interaction.py`).
  - Only the Conductor window may cut his hold sooner, and never for a flyer's flight. The flags of that act are in
    CLAUDE.md "The bridge is passed through one file".
- Nothing announces a release. Run `game_lock.py query all` again, or take another free game.

More traps for this section: [references/traps.md](references/traps.md) § Bridge lock.
