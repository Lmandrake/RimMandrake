# Lane offline: no game

You work items that need no running game: needs=offline (or none) items outside the FlowWorks lane first, then
FlowWorks offline items the live loops have not taken (the shared claims table keeps you apart; never take an item
another loop claims). You never start, stop, load, deploy to or drive any RimWorld, on any machine, and never take the
bridge (the clone's gate hook refuses those commands). Writing mod files, building C# with
`python3 src/RimMandrake/Utils/winbuild.py` and running selftests, validators and def dumps on disk are all yours.

If an item turns out to need a live proof, finish the offline part, commit it, note the live step on the item
(`rimflow note`), set `rimflow needs <ID> bridge` if its needs is wrong (read `--help`), and give it back to BENCH: a
live FlowWorks loop takes it from there. That ending is `parked` when the live step is all that remains.

The machine runs other loops beside you: keep a selftest to the tests for what you changed, and do not run the whole
suite. A run that takes more than a few minutes uses `--workers 1` and a 540 s timeout.
