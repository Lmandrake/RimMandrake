# BOUNDARY: the home of a list ticket (list_home.py, `rimflow home`), Design Version 0.1.0

Code: `src/RimMandrake/rimflow/list_home.py` (all of it), the `home` verb in `src/RimMandrake/rimflow/model.py`
(`VERBS["home"]`, its `_apply_item_verb` branch, `Item.home`), `rimflow home` in `src/RimMandrake/rimflow/cli.py`
(`cmd_home`).
Item: `RIMMANDRAKE_GROUP_OLD_TICKETS_BY_HOME_AND_KEEP_THE_LIST_FOR_GOOD`. Why: the owner, 2026-11-23: *"group/sort them
into their associated mods vs. pipeline repair ... and then we should KEEP that list so we stop needing to keep
regenerating it for old tickets."*
Each promise has a test of its name in `src/RimMandrake/rimflow/selftest_list_home.py`.

## How it works, in one paragraph

A `home` event on the ledger gives an open ticket its home, its group and its flag. The last event stands.
`list_home.py` reads the ledger and prints the open list tickets by home and group, with counts. It takes its set from
the Maturation Pipeline page (`maturation_nonmod.section`), so the page and the list count the same tickets. A ticket
that closes leaves the list by itself. A ticket that has no home is named in the no-home count. Nothing launches a run,
and nothing closes or drops a ticket.

## ACCEPTS (the only inputs this is built for)

- **an-open-ledger-item.** `rimflow home <ID>` takes an item that is not done, dropped or superseded.
- **a-home-as-kind-and-name.** A home is `mod:<folder>`, `pipeline:<part>`, `game:<need>`, `machine:<name>` or
  `unplaced`. A mod that does not exist yet is named by its planned folder.
- **a-rows-file.** `rimflow home --from <file>`: one line for each ticket, a tab between the fields: ID, HOME, GROUP,
  FLAG, REASON. A line that starts with `#` is a comment.

## DOES NOT SURVIVE (not promised)

- **a-wrong-home.** Whether a home is the right one is a reading, not a program's check. A later `rimflow home` corrects it.
- **a-flag-that-went-stale.** `LOOKS CURRENT` was true of the prose on the day that it was read. A run that takes a ticket
  reads the ticket again.
- **a-mod-name-misspelled.** A `mod:` home with no folder of that name is kept and marked `planned` in the list.
- **the-mod-pipeline-set.** The tickets that the Maturation Pipeline page calls mod work are not in the list.

## PROMISES (each one is owed a test of the same name)

- **the-ledger-carries-the-home.** A `home` event replays into `Item.home` (home, group, flag, reason, when, who). The
  last event stands. The state of the item does not move.
- **a-bad-row-writes-nothing-and-names-the-repair.** An unknown kind, an empty name, a group that is not a lower-case
  slug, an unknown flag, `LOOKS OVERTAKEN` with no reason or `unplaced` with no reason: nothing is written, the exit is
  not 0, and the message names the fault. One bad row in a rows file stops the whole file.
- **a-rows-file-may-run-again.** A row that the ledger already carries is skipped. A row of a closed item is skipped and
  said.
- **a-ticket-with-no-home-is-named.** Each open list ticket with no home is counted and named. It is never put in a home
  by the program.
- **the-list-is-by-home-and-group-with-counts.** The list prints each home, its count, its groups with their counts, and
  the count of each flag. The counts sum to the count of open list tickets.
- **a-closed-ticket-leaves-the-list.** An item that is done, dropped or superseded is not in the list.
- **could-not-look-is-not-an-empty-list.** A ledger or a page set that could not be read exits 2 with the cause.
- **a-home-never-launches-or-closes.** A home event changes no state, no naming for Shape, no check, no claim and no wait.
