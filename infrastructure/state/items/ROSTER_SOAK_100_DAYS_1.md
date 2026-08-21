## spec
`Inhabited` holds a place's cast as real `Pawn` objects in a `ThingOwner<Pawn>`
on a `WorldObject`, off-map, between visits. `Caravan` is the shipped model and
it is designed to be TRANSIENT; we are using its shape for something PERMANENT,
and vanilla never stress-tests that across years.
🔑 **TWO of the three ways this could fail were found on disk and fixed before
you got here**, so do not spend the soak looking for them:
  1. `WorldObject.DoTick` ticks child `ThingOwner`s unless the owner `is Map` or
     `is Caravan`. Ours now implements `IThingHolderTickable` with
     `ShouldTickContents => false`.
  2. `Caravan.pawns` is `LookMode.Reference` and survives only because
     `WorldPawnGC.GetCriticalPawnReason` has an explicit `IsCaravanMember()`
     test. Ours is `LookMode.Deep` and stays out of `WorldPawns` entirely.
⇒ **What is left to prove is the interesting part:** that a deep-held,
deliberately un-ticked pawn comes back whole after a real save/load and a long
absence.
⚠️ **`mandrake.inhabited` is NOT in `ModsConfig.xml`.** Enable it first or none
of this exists. It is deployed and in sync.
THE RUN, and it is a soak, not a glance:
  1. Dev mode on. Debug actions, category `Inhabited`:
       `Create place at current tile`   -> makes a `WorldObject_Inhabited`
       `Stuff roster (3 pawns)`         -> 3 pawns; #1 gets a `Sibling` relation
                                           to a free colonist, #2 a missing eye
                                           and the `Abrasive` trait
       `Report roster`                  -> KEEP THIS OUTPUT. It is the baseline.
  2. Save. **Quit to desktop.** Reload. `Report roster` again.
  3. Let **100+ in-game days** pass WITHOUT visiting that tile.
  4. `Report roster` a third time.

## verify
diff the three reports.

## criteria
PASS = identical `ThingID`s, names, relation counts, hediff counts and trait
counts across all three.
🔑 **AND REPORT THE AGE LINE EXPLICITLY, because it answers a design question
nobody can answer from disk.** Each entry prints `age=Ny (T ticks)`. Either
  FROZEN — the tick count is unchanged across 100 days, which is what §3.4 of
           `design/Jawa/bridge/INHABITED_DESIGN.md` promises; or
  TICKED — it advanced by exactly the elapsed time, which is ACCEPTABLE but
           changes the design and DECIDE must be told.
FAIL = any pawn missing · any relation or hediff dropped · any
`Could not load reference to` in `Player.log` naming a pawn.
⛔ **If this fails, do not patch around it.** The container choice is wrong and
DECIDE re-specs before anything more is built on it.

## notes
**from:** BUILD, 2026-08-20, `f0a9f6c`. Harness only; BUILD cannot run this.

**Imported from `queue/CHECK.md`. Its `state:` read, verbatim:**

ready
