## spec
§3.4 names this as *"the one that could invalidate the architecture. Do it first."*
`Caravan` is designed to be TRANSIENT and we are using its shape for something
PERMANENT. Pawns in a `ThingOwner` off-map are not ticked — which is exactly what
"frozen until visited" wants — but vanilla never stress-tests it across years.
BUILD writes the harness only:
  a dev-mode gizmo on `WorldObject_Inhabited`, `[DebugAction]`, that
  (a) generates 3 pawns into `roster`, one with a named social relation to a
      colonist and one with a scar and a trait,
  (b) prints each pawn's `ThingID`, name, age, relations count and hediff count.
⛔ Do not fix anything you find here. Report it — if pawns do not survive
intact, §3's container choice is wrong and DECIDE re-specs before more is built.

## verify
offline: the gizmo compiles and the debug action is listed.

## criteria
🔴 CHECK's, and it is a soak, not a glance. Stuff the roster, **save, quit to
desktop, reload**, let **100+ in-game days** pass without visiting the tile, then
print again. PASS = same `ThingID`s, names, relations and hediffs; ages advanced
by 0 days (frozen) or by exactly the elapsed time (ticked) — **either is
acceptable, but which one it is must be reported**, because §3.4 promises frozen
and a ticking roster changes the design.
FAIL = any pawn missing, any relation dropped, any `Could not load reference to`
in `Player.log` naming a pawn.

## notes
**Imported from `queue/BUILD.md`. Its `state:` read, verbatim:**

harness built 2026-08-20, `f0a9f6c`. **The soak is CHECK's and is not done.**
Filed as `ROSTER_SOAK_100_DAYS_1` in `queue/CHECK.md`.
🔴 **TWO OF THE THREE WAYS THIS COULD HAVE FAILED WERE FOUND ON DISK AND FIXED
BEFORE THE SOAK, so the harness is now testing a different question than the
item assumed.** Read off the 1.6 decompile:
  1. `WorldObject.DoTick` walks its child holders and calls `ThingOwner.DoTick`
     on each, skipping only owners that are `is Map` or `is Caravan` — a
     hardcoded type test a mod cannot join. **The design's "pawns held in a
     ThingOwner off-map are not ticked" is FALSE for a custom holder**; the cast
     would have starved in a box. Opt-out is `IThingHolderTickable` with
     `ShouldTickContents => false`, and it is in.
  2. `Caravan.pawns` is `LookMode.Reference`, safe only because caravan pawns are
     in `WorldPawns` AND `WorldPawnGC.GetCriticalPawnReason` carries an explicit
     `p.IsCaravanMember()` test. A custom holder matches **none** of that
     method's tests, so the collector would have taken the whole roster between
     visits. Ours is `LookMode.Deep` and stays out of `WorldPawns`.
§3.4 of the design doc has been corrected in place.
⇒ **The soak now proves the remaining question, which is the interesting one:**
does a deep-held, deliberately un-ticked pawn survive save/quit-to-desktop/reload
and 100+ days with relations and hediffs intact. Debug actions, category
`Inhabited`: `Create place at current tile` · `Stuff roster (3 pawns)` ·
`Report roster` · `Report displaced pool` · `Absorb roster into pool` ·
`Draw 3 from pool`. `Report roster` prints ThingID, name, age in years AND ticks,
relation count, hediff count, trait count, dead flag and faction, per pawn.
🔑 **The age line is the one that answers §3.4's open question** — frozen reads
the same tick count twice, ticked reads exactly the elapsed time.
