## spec
`NEEDS_HAS_NO_SETTER_1` is closed (`4c1cba6`): **the verb now exists.**

    rimflow needs <ID> --to offline|deploy|game-up|bridge|harvest|owner --reason "<why>"

It is `(DECIDE, owner)`, so CHECK can set it on his own items. It refuses a value outside
the vocabulary, so a typo cannot silently park an item forever.

That item's own spec says the setter was the deliverable and **re-stamping is CHECK's**.
As of 2026-08-21 all 38 CHECK items still read `needs: offline` at the filing default, and
his `WAITING ON A WINDOW` section is empty. Seven were named there as certainly wrong:

    ROSTER_SOAK_100_DAYS_1      100 in-game days
    CAST_ROSTER_269_LOAD_1      a load
    W9                          the 21,872-tile import over the bridge
    MORNING_RELOAD_PLAN_1       two loads
    PRELOAD_PREDICTIONS_578_1   a load
    LOAD2_TARGET_IS_SUB7B_1     a load
    INHABITED_ROUTE_ONE_DAY_1   a live day

⚠️ **Do not bulk-set.** `needs` is the difference between "offer this now" and "hold it for
a window", and getting it wrong in the safe direction (`offline`) is what produced this
mess, while getting it wrong in the other direction hides real work. Read each item and
stamp what it actually wants. ⛔ `blocked` is a DIFFERENT axis — `needs` means the window
is closed, `block` means something is wrong. Do not use one for the other.

🔑 BUILD has already stamped one item this way as the proof: `B55 --to game-up`. It now
renders under WAITING ON A WINDOW and `rimflow why B55` explains it is a closed window
rather than a fault. That is the shape to copy.

## verify
`rimflow next --seat CHECK` with the game DOWN returns only items that can actually be
worked with the game down, and every item it declines to offer for that reason appears
under `WAITING ON A WINDOW` in `queue/CHECK.md`.

## criteria
CHECK's board distinguishes "ready now" from "waiting for a window" for all 38 items, and
`rimflow why <ID>` gives a true answer for any item it is asked about.
