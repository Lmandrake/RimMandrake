# BOUNDARY: the item packet in each detached brief (item_packet.py), Design Version 0.1.0

Code: `src/RimMandrake/rimflow/item_packet.py` (all of it), and `brief_message`, `item_history` and `mark_fresh` of
`src/RimMandrake/rimflow/detached_helper.py`. Item: `RIMMANDRAKE_PASTE_ITEM_HISTORY_INTO_BRIEFS_1503_SHOWS_CUT`. Why: in
the week to 2026-11-23 agents ran `cli.py show` in 1,615 turns, and cut its output by hand in 1,503 of them. Each promise
has a test of its name in `src/RimMandrake/rimflow/selftest_item_packet.py`. Acceptance:
`design/specs/2026-11-23-agent-work-to-code/acceptance/rank6_item_packet_accept.py`.

## ACCEPTS (the only inputs this is built for)

- **an-item-name.** A non-empty string. Anything else is a `ValueError`.
- **the-facts-of-gather.** `packet(item, facts)` takes `state`, `title`, `prose`, `notes`, `runs`, `linked`, `commits`,
  `as_of` (the contract in the head of the acceptance script), and what `gather` adds: `criteria`, `ledger`, `known`,
  `why`, `prose_path`, `bookkeeping`, `commits_more`. A part that is `None` (or not there) could not be read. `[]` or `""` was read and is
  empty.
- **a-clone-of-this-repo.** `gather(item, clone)` reads the ledger, the prose and the commits that the clone holds.

## DOES NOT SURVIVE (not promised)

- **a-write-after-the-reading.** A note written after `as_of` is not in the packet. The packet gives the time of the
  reading, and says when the clone's ledger is behind origin/main as the clone last fetched it. It does not fetch.
- **a-decisive-note-with-no-mark.** A note that decides the work and carries none of the kept marks is dropped when it is
  old and the packet is over its budget. The packet names it among what it left out, with the command that shows it.
- **bookkeeping-events.** Claims, leases, starts, homes, shapes and the like are counted in one number, not shown.
- **a-blind-role-that-nothing-names.** A hand-written brief that gives one of the fresh-start roles in words that `role_of`
  does not know, with no `--env RM_FRESH_ROLE=<role>`, carries the packet.
- **a-run-that-is-not-detached.** A window, a subagent and a role run do not get a packet.

## PROMISES (each one is owed a test of the same name)

- **holds-the-item.** The text holds the state, the title, the prose, the notes, the runs with their evidence, the linked
  items with their states, the open criteria, the commits that name the item, and the time of the reading. An item spawned
  from a finding links to the source item once, with its state, even when the finding names a run and the prose never names
  the source. A run keeps its time, result and clean evidence when spend language is removed from its configuration.
- **decisive-notes-are-kept.** Over the budget these are never dropped: the last note, each note with the owner's words,
  each `LEFT OPEN:`, `PROGRESS:`, `RULING` and `REFUSED` note, each run that is not a pass, the open criteria.
- **oldest-routine-notes-go-first.** Over the budget the oldest routine notes go first, then the oldest commits, then the
  linked items that are closed, then the oldest runs that passed, then the other linked items. Prose goes last, and only
  when the prose alone is longer than the budget.
- **a-note-is-whole-or-left-out.** No note is cut, shortened or reworded.
- **left-out-is-counted.** `left_out` names each dropped part. The text gives the count, names the parts, and prints the
  command that shows them (the ledger's, and `git log` for the commits).
- **could-not-look-is-said.** A part that is `None` reads "could not look", with its cause, and stands in `could_not_look`.
  An empty part reads as looked and found none. A linked item or run is never invented.
- **an-unknown-item-is-said.** An item that the ledger does not know gives a packet that says so.
- **a-stale-ledger-is-said.** A clone whose ledger is behind origin/main reads BEHIND in the packet, with the count.
- **no-spend-in-the-text.** Each text that a person wrote goes through `spend_talk.strip`, line by line. Each part that
  lost a sentence is in `left_out`, by name.
- **blind-roles-get-none.** The brief of a blind judge, a fresh reader, an examiner, a challenger and a coverage judge holds
  no packet and no `show` command from this module, and neither does its resume or its continuation (the first launch leaves
  the role on the run's env as `RM_FRESH_ROLE`). A manual resume converted to a fresh session carries that role from the
  earlier run and omits the packet and its `show` command. The pipeline stages `blind_challenge` and `pre_human` hold none
  either.
- **every-detached-launch-carries-the-packet.** `detached_helper.brief_message` holds the packet of every other run, and
  `_launch_locked` makes its message with it.
- **a-launch-never-fails-on-the-packet.** When `gather` or `packet` raises, the brief still goes out. It says could not look,
  with the cause and the command.

## LIMITS

- `BUDGET_CHARS = 12000`. Danger: the text is read again on every turn of a run (first load 83.0k on average, census of
  2026-11-23, `design/specs/2026-11-23-agent-work-to-code/analysis.md`). What is always kept can pass it: the most kept
  text of one item was 13,095 characters (measured on 2026-11-23, 22:15 PST, all 10,162 items).
- `COMMITS = 12`, the newest commits that name the item. Danger: the same; `git log` shows the rest.
- `GIT_S = 120`. A hang guard (the class of `call_deadline_lint.py`): a git that does not answer must not hold a launch.

Later lists beside this page: `polish.md`.
