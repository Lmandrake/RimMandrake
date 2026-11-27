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
- **a-ticket-with-no-home-is-named.** Each open list ticket with no home is counted and named. A program puts it in a
  home only by a rule of `rule_home` (the next promise), never by a reading of its prose.
- **an-old-ticket-takes-a-home-by-rule.** `rule_home` gives an old ticket with no test and no home of its own (filed
  before `shape_from`, not one mod's work) a real home by the first rule that places it, with no model run: (1) the
  home of the nearest ancestor in its chain of causes that has one (its mod by `mod_work`, or its own home that is not
  `unplaced`); (2) else the mod that its id or title names (`list_dispatch.mod_of`, the word rule of the lane's switches
  and holds). The group names the rule (`by-rule-cause`, `by-rule-name`), the flag is `CANNOT TELL` (nobody read the
  prose), and the reason names the ancestor or the mod. A ticket that no rule places gets no home: the lane names it for
  Shape (`list_dispatch.no_home_names`). Why: the pass of 2026-11-23 took its set from the page's word rule, which
  calls such a ticket mod work, while `mod_work` calls a mod named by a word alone list work; so neither placed 266
  old tickets (measured 2026-11-26, `design/specs/2026-11-26-testless-tickets/holes_check.py`).
- **place-writes-only-rule-homes.** `list_home.py place` prints the rows that `rule_home` makes; `--apply` writes them
  in one `rimflow home --from` act. A ticket with a home of its own (`unplaced` included), a test, a mod reading, or a
  filing at or after `shape_from` is never a row. A second run writes nothing new.
- **the-list-is-by-home-and-group-with-counts.** The list prints each home, its count, its groups with their counts, and
  the count of each flag. The counts sum to the count of open list tickets.
- **a-closed-ticket-leaves-the-list.** An item that is done, dropped or superseded is not in the list.
- **could-not-look-is-not-an-empty-list.** A ledger or a page set that could not be read exits 2 with the cause.
- **a-parked-ticket-is-not-offered.** `list_home.py offer` offers no ticket whose block holds (`priority.block_holds`) or
  whose dated wait is still ahead. It counts each one as parked and names its reason. A block that ended, or a wait
  that passed, offers the ticket again.
- **a-home-never-launches-or-closes.** A home event changes no state, no naming for Shape, no check, no claim and no wait.
