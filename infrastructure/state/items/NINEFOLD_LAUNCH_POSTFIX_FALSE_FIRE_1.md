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
