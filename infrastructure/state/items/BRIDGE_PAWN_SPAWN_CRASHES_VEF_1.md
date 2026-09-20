# BRIDGE_PAWN_SPAWN_CRASHES_VEF_1 — bridge-triggered pawn spawns NPE, universally

## what is wrong

**MEASURED 2026-09-20, this session.** `rimworld/spawn_thing` and the
`Actions\Spawn Pawn...\<Kind>` debug action both throw the same
`NullReferenceException` for **any pawn defName**, on the owner's real,
live full modlist (618 mods) — not just a reduced test tier. Confirmed against
`Muffalo`, `Thrumbo`, vanilla `Chicken`, and our own `RSW_Sketto`; all four
fail identically. Non-pawn Things (`Steel`, `Gun_Revolver`) spawn fine via the
same call, same map, same session — this is pawn-specific, not a general
bridge outage.

Full trace (captured once, before the server's own dedup collapsed later
occurrences to `[Ref D3D588D] Duplicate stacktrace, see ref for original` —
same ref ID recurred across a 14-mod test tier AND the full 618-mod list, so
it is one root cause, not a modlist-size artifact):

```
System.NullReferenceException: Object reference not set to an instance of an object
  at Verse.Pawn.SpawnSetup (Verse.Map map, System.Boolean respawningAfterLoad)
    - POSTFIX OskarPotocki.VEF: Void VEF.Apparels.CompShieldField+SpawnSetup_Patch:Postfix(Pawn __instance)
    - POSTFIX OskarPotocki.VEF: Void VEF.Hediffs.PhasingPatches:CheckPhasing(Pawn __instance)
  at Verse.GenSpawn.Spawn (Verse.Thing newThing, Verse.IntVec3 loc, Verse.Map map, Verse.Rot4 rot, Verse.WipeMode wipeMode, System.Boolean respawningAfterLoad, System.Boolean forbidLeavings)
  at Verse.GenSpawn.Spawn (Verse.Thing newThing, Verse.IntVec3 loc, Verse.Map map, Verse.WipeMode wipeMode)
  at RimBridgeServer.LifecycleCapabilityModule.SpawnThing (System.String defName, System.Int32 x, System.Int32 z, System.Int32 stackCount)
```

## why it matters

Colonists and wildlife spawned as part of normal map/scenario generation are
unaffected (31-38 pawns present on a fresh quicktest map, every time) — the
crash is specific to a pawn spawned via `GenSpawn.Spawn` **after** the map is
already active, whether triggered by the bridge or (untested, ask the owner)
a manual dev-mode click. If it also fires from the dev-mode UI directly, this
is a live-game regression, not just a bridge-testing gap. Either way, it
currently blocks a large fraction of this project's standard workflow: the
`rimworld-debug-testing` skill's whole "spawn many, screenshot, observe"
method depends on exactly the call that is broken.

## Watch out

- Two other things were RULED OUT this session, not just suspected:
  removing `sarg.alphaanimals` (VEF's own pull-in dependency) from the
  modlist to route around this does NOT fix it cleanly — it breaks
  `RimWorld.ScenPart_StartingAnimal.PossibleAnimals` instead (a different
  NullReferenceException), implying some of our own SWBestiary defs lean on
  an Alpha-Animals-sourced parent/field that goes null without it. Do not
  re-attempt that removal as a "fix" without first fixing that dependency.
- The failure is **pawn-specific**, confirmed by a same-session A/B
  (`Steel`/`Gun_Revolver` spawn clean, `Muffalo`/`Chicken`/`RSW_Sketto` all
  NPE) — do not reopen "is it the bridge at all" as a question.
- `jawa/spawn_batch` was tried as a possible different code path but its
  `ops` parameter shape was not resolved this session (an `IConvertible`
  cast error on a naive `[{x,z}]` list) — untested whether it hits the same
  crash, genuinely unknown, not a negative result.

## verify

`rimworld/spawn_thing` with `defName: "Chicken"` on any live map returns
`success: true` and the pawn appears (`jawa/list_pawns` count increases),
with no `NullReferenceException` in the response.

## criteria

Any wild animal or humanlike PawnKindDef can be spawned via the bridge on the
owner's real modlist without crashing — the standard debug-testing method is
usable again.
