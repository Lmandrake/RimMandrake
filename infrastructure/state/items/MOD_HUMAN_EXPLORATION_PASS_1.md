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

## spec (written 2026-09-12, BENCH — un-thinning the item)
Per surviving mod (post-consolidation list), author a short scripted in-game
walkthrough the OWNER performs: what to spawn/build/look at, in what order,
and the one question per step he answers (looks right / reads right / feels
right). Group by domain (weapons, apparel, creatures, biomes, structures) so a
sitting covers a domain, not a mod at a time. Template + first domain first;
the owner corrects the register before the bulk pass.

## verify
The owner runs one domain's walkthrough in-game and reports it usable without
this seat explaining anything; every walkthrough names its spawn commands and
expected sights with real defNames (verified, never guessed).

## criteria
Every active non-library mod has either a walkthrough or a recorded exemption
(pure-code, invisible, or covered by another mod's walk).

## sequencing — why blocked
Owner's own framing: runs AFTER the art/normalization wave. Wave 8 regen is
generating right now; the fauna/flora verdict sitting and the commission build
follow. Authoring walkthroughs against mods whose art is mid-replacement
would need a full re-pass. Unblock when the art regen scope line goes quiet
(art tab on the hub: awaiting_verdict ≈ 0 and no queued lanes).
