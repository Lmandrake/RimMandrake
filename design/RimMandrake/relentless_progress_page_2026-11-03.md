# Relentless progress page: a design to refer to

Owner, 2026-11-03: *"For the Relentless, this is something we should periodically make to ensure we're making
progress. Not sure on the cadence yet, but keep it as a design to refer to please."*

**Status: a kept design. Nothing builds or schedules it until he sets a cadence.**

The picture: `design/RimMandrake/relentless_progress_page_mock_2026-11-02.html`. A one-time mockup; judge its layout,
not its numbers.

**The question it answers:** how is the game coming along? `RUNNING_NOW.md` answers a different one (is the machine
healthy and moving?).

**What it shows:** a one-line headline, "Needs you", and progress by mod with who each stuck item is waiting on.

**Generated periodically, not live, and with no model in the path.**

## Known problems in the mock, from a fresh reader

- It undercounts "Needs you" (`src/RimMandrake/Utils/owner_queue.py` is the one answer to that list).
- It has a date bug.
- It uses terms it does not explain.

## Owed before it can be generated

Two facts are not recorded today:

- which mod each item belongs to (`src/RimMandrake/Utils/fleet_mods.py` is the existing attempt);
- whether an item's fix is actually installed in his game.

## Open

- Cadence: his, undecided.
