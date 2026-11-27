# Boundary: the stops that only the Conductor ends (`src/RimMandrake/rimflow/conductor_stops.py`)

Item RIMMANDRAKE_BUILD_STUCK_STOP_REPAIRS_HE_RULED_SIX, parts 1, 3 and 4 of the stuck-items study
(`design/specs/2026-11-26-stuck-items-study/one_page.md`). His words, 2026-11-26: "The conductor is always told 1st. It
decides if owner is needed or conductor can do it itself." and "Conductor sorts after 1 hour."

Why: at the 3:13 PM PST tick of 2026-11-26, 4 tickets sat at the chain limit, 2 were stopped, 1 had a check too heavy to
attach, 2 were left out of their work bundle, and 4 tickets waited on mods that rest after their pass (Gimme Some Slack
45 h). No program ended any of them, and none showed on a list that the Conductor reads first.

Code: `src/RimMandrake/rimflow/conductor_stops.py` (all of it), `src/RimMandrake/rimflow/owed.py` (`view`: its `stops` and `asks` blocks).

## ACCEPTS

- **the-lane-reading.** The Workshop Pipeline's `reading.json` (`list_dispatch.tick`): per item `decision`, `why` and
  `since` (when the item took that decision); a `mod_work` row also carries `mod` and the ticket's own `wait_until`.
- **the-rests.** `{mod folder: epoch}` from each `design/concepts/<Mod>/version/stage_record.json` whose `stage` is
  `passed` (its `since`).
- **the-sorted-list.** `design/concepts/<Mod>/version/next_version/tickets.md`: one ticket id per line that the
  Conductor sorted to the mod's next version.

## DOES NOT SURVIVE

- **a-tick-that-stopped.** A reading older than `READING_STALE_S` is not read: the view says "could not look" with the
  age. The rows of a stopped tick are not shown as now.
- **a-kind-left-and-taken-again.** `since` restarts when the decision changes, even for one tick.

## PROMISES

- **the-four-kinds-go-to-the-conductor.** `rows` lists each item whose decision is `chain_stop`, `stopped`,
  `no_bundle`, `adopt_too_heavy` or `close_refused` (its reason names the cause and repair, part 6), at once (no clock first), with its kind, its reason and its age in the kind.
  Each kind's hint names an act that lifts that stop: `clear` for `chain_stop` and `stopped`; for `no_bundle` the
  host's own reason (a clear of the lane's state cannot change what the host's sort read).
- **a-resting-mod-sorts-after-an-hour.** When a mod has rested `REST_S` (1 hour) and open `mod_work` tickets wait on
  it, `rows` gives one line for that mod with its tickets and the rest's age. A ticket with a dated wait of its own
  ahead, and a ticket on the mod's sorted list, is not on the line.
- **the-owed-view-shows-them.** `owed.view(..., stops=...)` prints a `STOPS FOR YOU (n)` block with each row, and a
  `could not look` line when the stops could not be read. It never prints these on his page.
- **unread-asks-go-to-the-conductor.** `asks` lists each lane ask to him that no program and no `ASK HIS:` note has
  read against now (`owner_queue.needs_you()["unvetted"]`); the owed view prints them under `ASKS TO READ (n)`.
- **the-sort-is-one-line.** `conductor_stops.py sort <ID> --to lane` gives the ticket the home `fix:<Mod>` (a
  correction of the passed version that moves no bar; `mod_work` then reads it as the ticket lane's).
  `--to next` adds the id to the mod's sorted list. Each prints the command it ran, and refuses a ticket that is not
  mod work of a resting mod.
- **each-limit-names-its-danger.** `REST_S` and `READING_STALE_S` are written beside their dangers.

## LIFE CYCLES

- **a lane tick (every 10 minutes):** `list_dispatch.tick` → `reading.json` with `since`.
- **a Conductor wake:** `rimflow queue CONDUCTOR --owed` → `owed.view` → `conductor_stops.load` and `asks`.

Later lists beside this page: `polish.md` (none yet).
