## spec
From CHECK (`8adf65a`), routed by REP. C41 was paired with C39 in TWO places —
§1.0's deploy row 3, and §5's live row **L5** — and only one of them was the
deploy. C41 has no artifact at all: B62 is still `ready`, and
`src/Jawa/DesertVehicleReskin/` holds 12 PNGs where C41 needs 24, with its 13
extra defs absent.

🔴 **The §5 half was the dangerous one.** L5's pass condition asked for `dewback
cart` · `ronto wagon` · `bantha dray` · `dewback war cart` verbatim, with
`Ox cart`/`Chariot` at zero. Those labels cannot exist next load. Left as
written, whoever ran L5 would see the vanilla labels, score C41 FAILED, and file
a defect against a mod that was never built — and it would read as a deploy
regression, which is the expensive kind of wrong. CHECK has rescoped L5 to C39
only, stated that the vanilla labels ARE the expected pre-B62 result, and kept
the original wording in the cell marked valid only after B62 ships.

**The convention this asks you for:** pairing two items on one manifest row is
fine, but it hides the case where one of them has no artifact. When a row names
two items, each needs its own artifact named, or the row says which item the
artifact belongs to. And a fix in §1.0 is not a fix — check §5 for the same
pairing.

## verify
no row in `NEXT_RELOAD.md` names two items without naming an artifact for each.

## criteria
EMPTY — offline.

## notes
**Imported from `queue/DECIDE_ARCHIVE.md`. Its `state:` read, verbatim:**

⛔ v2 — **OWNER RULING 2026-08-15, blanket triage.** Produces no content and does not
reach the frozen world. Parked, not lost.
