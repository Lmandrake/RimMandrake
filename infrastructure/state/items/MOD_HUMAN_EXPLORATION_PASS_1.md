## the ask

Owner, 2026-09-07, splitting the retrospective in two: *"...and then a
human-executable exploration that verifies to a human interaction level
everything looks ok."*

**This is the SECOND half.** The automated walk is
`MOD_VALIDATION_PLAN_AUTHORING_1`.

## what it is

Per mod, a short scripted walkthrough **the owner performs in game** — set up by
an agent on a minimal mod list, then handed over: *look at this, click that, does
it read right?* It catches everything an automated check cannot: art that loads
but looks wrong, a mechanic that fires but feels bad, text that renders but reads
badly, scale and colour and timing.

🔑 **The division of labour:** the automated walk proves it WORKS; this pass
proves it is GOOD. A mod is only `checked-out` when both have passed.

## when

**After the art sheets and normalization wave** (owner's original framing: *"In
the next v1 phase, after we do all the full art sheets and normalization
efforts"*). Running it before the art lands would judge placeholder work.

## how to make it cheap for the owner

- **Batch by theme, not by mod** — all the food mods in one sitting, all the
  droid mods in another. Context-switching is the expensive part for a human.
- **Stage it before he sits down.** The agent brings the game to the exact moment:
  map loaded, pawn placed, thing spawned, camera framed. His time is spent
  looking and ruling, never setting up.
- **Prefer a saved game per batch** over screenshots, per the standing ruling —
  he can walk it, zoom it and read the tooltips. One map, options on a grid, with
  an item file giving the grid key.
- ⚠️ Verify each option is actually THERE before calling it a review; a placement
  log's `thingsSpawned` is a NET count and goes negative when a build clears plants.

## scope
All 76 mods, same as the automated half — the inactive 26 included, because
*"we are shipping everything, or else abandoning it."* This pass is where an
abandon call actually gets made, with the thing on screen in front of him.

## relationship to the dashboard
Feeds `PROJECT_MATURITY_DASHBOARD_1`. A pass here is what moves a system to the
top of the CONTENT axis — and, with the automated walk, to `checked-out` on
FUNCTION. ⛔ Never a gate on ordinary work.
