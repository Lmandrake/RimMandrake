# GIZKA_HOLD_HOOK_SPIKE_1 — gravship-landing hook, research phase

Spike for Card 4 (`design/RimStarWars/gizka_ship_pest_draft.md` §1, owner
sitting 2026-09-12): *"the flagship found-in-your-hold moment ships WITH the
feature or the feature does not ship — confirming the engine hook is the
gating spike."* This item answers **what the real hook is**; live
confirmation is a separate, still-owed step (see Status).

## What was read (RimSage, decompiled Odyssey/Verse source, no load)

- `Source/RimWorld/Scenario.cs:358-364`

  ```csharp
  public void PostGravshipLanded(Map map)
  {
      foreach (ScenPart allPart in AllParts)
      {
          allPart.PostGravshipLanded(map);
      }
  }
  ```

  `Scenario.PostGravshipLanded(Map map)` is a **public instance method** on
  the live `Scenario` object (`Find.Scenario`). It fans out to every
  `ScenPart.PostGravshipLanded(Map map)` (`Source/RimWorld/ScenPart.cs:124`,
  virtual, default no-op — overridden today only by
  `ScenPart_PursuingMechanoids.PostGravshipLanded`, `Source/RimWorld/ScenPart_PursuingMechanoids.cs:127`).

- `Source/Verse/WorldComponent_GravshipController.cs:526` — `LandingEnded()`
  (private) calls `Find.Scenario.PostGravshipLanded(map)` as its last act,
  after the gravship+cargo+colonists have already been placed on `map`
  (`PlaceGravship(...)` runs earlier in the same landing sequence) and after
  clearing the cutscene state.
- `LandingEnded()` is called from `WorldComponentUpdate()`
  (same file, ~line 408) once the landing timer (`timeLeft`) reaches zero.
  Read the branch at lines ~388-408: the countdown only animates the
  cutscene visuals — when `Prefs.GravshipCutscenes` is off, `timeLeft` never
  counts down from its initial value in the animated branch, so the `else`
  branch (`LandingEnded()`) still runs on the very next update once capture
  is complete. **The hook fires regardless of the player's cutscene-visuals
  setting.** `ResetCutscene()` (called inside `LandingEnded`) clears
  `cutsceneInProgress`, so this fires **exactly once per landing**.
- Both landing routes converge here: `GravshipUtility.ArriveNewMap(Gravship)`
  (brand-new map/site, read in full — generates or fetches the map, places
  the gravship's substructure/cargo/pawns via `GetOrGenerateMapUtility` +
  `PlaceGravship`) and the existing-map arrival path
  (`Gravship.cs:784-789`, `GravshipUtility.ArriveExistingMap` /
  `ArriveNewMap`) both end up inside the same
  `WorldComponent_GravshipController` cutscene/landing state machine, so
  `PostGravshipLanded` fires for **every** gravship landing, not just the
  first.

## The "hold first walked" half of the draft's speculative row is not real

Searched the decompiled source (`Source/**/*.cs`) for any cargo-hold /
ship-hold concept distinct from the ordinary map: nothing exists. A
gravship's "hold" is just player-built substructure sitting inside the
landed footprint on the ordinary `Map` — there is no `CargoHold` class, no
`Notify_*` for a pawn first pathing into the substructure, no first-entry
event of any kind. The two-part trigger in the draft's table ("Gravship
lands / hold first walked") collapses to **one real event**: the landing
itself. There is nothing further to hook for "first walked into the hold" —
the landing moment already puts colonists on the map with the cargo, which
is the moment the draft's flavor text ("something has been living in the
hold") wants anyway. Building a separate first-entry watcher is unnecessary
scope, not a missing hook.

## The hook (confirmed by source read)

**`RimWorld.Scenario.PostGravshipLanded(Map map)`** — public, fires once per
gravship landing (new map or existing map alike), called with the landed
`Map`, after cargo/colonists/substructure are already placed on it.

### How a mod attaches

Two routes exist; recommend the first:

1. **Harmony postfix on `RimWorld.Scenario.PostGravshipLanded(Map map)`.**
   Public method, no scenario/save cooperation needed, fires with the target
   `Map` as a parameter — exactly what `RSW_GizkaStowawayManager` needs to
   pick a spawn cell and drop the letter. This is the recommended route:
   ```csharp
   [HarmonyPatch(typeof(Scenario), nameof(Scenario.PostGravshipLanded))]
   static class Patch_Scenario_PostGravshipLanded
   {
       static void Postfix(Map map) => RSW_GizkaStowawayManager.Instance.Notify_GravshipLanded(map);
   }
   ```
2. **A custom `ScenPart` subclass overriding `PostGravshipLanded(Map map)`.**
   Matches the vanilla pattern (`ScenPart_PursuingMechanoids` does exactly
   this) but requires the part to be present in the active `Scenario`'s
   `AllParts` list — not retrofittable onto an already-started save/scenario
   without extra plumbing. Not recommended for this feature.

The manager itself (GameComponent, per the draft) does not need to subscribe
to anything else at load — Harmony patches the static method table once at
mod init, independent of save state.

## Status: hook IDENTIFIED, live confirmation OWED

Research/read half is complete and the hook is concrete (real method,
signature, call site, and firing guarantee all read directly from decompiled
source — no guessing). **Not yet live-confirmed**: no quicktest was run to
prove the postfix actually fires on an in-game gravship landing.

Reason: the bridge was held by another FOUNDRY window for the whole of this
session (`vermin spawn debug + tibanna source cut`, session-start check via
`rimflow bridge who` showed `idle 0 min` — actively driving, not stale) so
`rimbridge` doctrine (never drive in parallel; take only a stale/idle lock)
ruled out taking it. Per CHARTER.md's "You are already the dedicated agent
for this task" instruction and the task's own routing, live proof is left
explicitly for whoever runs it next:

**Owed**: build a minimal Harmony postfix on `Scenario.PostGravshipLanded`
that logs/letters when hit, deploy it, quicktest-land a gravship (or trigger
`WorldComponent_GravshipController`'s landing path via the bridge/dev tools),
and confirm the postfix fires with a valid `Map`. Only then does Card 4's
gate close — per the owner's ruling this item wants **confirmation**, not a
candidate, so it is left BLOCKED rather than closed.

## Not in scope here (future work, gated on this spike closing)

The stowaway manager, the fecundity hediff, mod settings, letters, or any
other build content from `design/RimStarWars/gizka_ship_pest_draft.md` —
this item's scope is the hook question only.
