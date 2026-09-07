# NINEFOLD_LAUNCH_POSTFIX_FALSE_FIRE_1 — Ta'Baa is fed by FAILED gravship launches

Found by code review 2026-09-06 (DIRTY_CODE_REVIEW_STANDING_LOOP_1), `src/RimMandrake/Ninefold/Source/Patch_GravshipLaunched.cs` line ~29.

`CompLaunchable.TryLaunch(PlanetTile, TransportersArrivalAction)` is `void` with early returns before the launch: not spawned, no transporter group, `!CanLaunch()`, destination beyond fuel range (Log.Error or silent). The Postfix runs unconditionally, so a failed attempt still calls `GameComponent_Ninefold.Notify_Launched`, spiking Ta'Baa's satiation and resetting his erosion clock for a launch that never happened.

## spec
Prefix captures `__state` = (parent.Spawned && comp.CanLaunch() && destination within range) using the same checks TryLaunch makes; Postfix fires only when `__state` is true. Better: postfix a method that runs only on a real launch if one exists (`CompLaunchable` → the skyfaller/`TransportPodsArrivalAction` creation) — verify in the decompiled source before choosing.

## verify
```
PROVE   quicktest: a launch attempt with CanLaunch()==false (no fuel) leaves Ta'Baa's satiation unchanged; a real launch changes it once
EXPECT  two readings via the Ninefold debug/read surface, before/after each attempt
LIES    a postfix that fires twice on a real launch (if the chosen hook is also called on retry) — count, don't just check non-zero
```

## FOUNDRY, 2026-09-07: fixed source-side, exactly the "Better:" route this item names — live PROVE/EXPECT still owed

Found independently via an adversarial fresh-context code review of an EARLIER same-day self-fix (which itself only gated on `CanLaunch()` and missed the distance-vs-`MinFuelLevelInGroup` guard this item's own first paragraph names) — same root defect, same line, this item just got there first.

**Fixed, matching this item's own "Better:" suggestion**: rather than replicating TryLaunch's guard chain in the Prefix (drift-prone, and I'd already gotten it wrong once), `Patch_GravshipLaunched.cs` now gates on `CompLaunchable.lastLaunchTick` (public field), which vanilla itself sets unconditionally immediately after EVERY guard clause passes and before any pod is processed — verified via RimSage against the decompiled source, not assumed. Prefix captures it, Postfix credits Ta'Baa only if it changed. This is immune to any future guard-chain change, unlike a replicated check list. Commit `572413c0`, adversarially re-reviewed and marked CLEAN (`64e09460`).

**Not done**: the live PROVE/EXPECT this item's own verify section wants (a real quicktest: a no-fuel launch attempt leaves Ta'Baa unchanged, a real launch changes it once) — needs a game-up session with a gravship set up to fail-then-succeed a launch, not attempted this pass. `needs game-up` stands. Left `doing`, blocked rather than closed — the fix is source-complete and independently reviewed, but per this project's own doctrine a live check on a mechanism never observed running still counts as owed.
