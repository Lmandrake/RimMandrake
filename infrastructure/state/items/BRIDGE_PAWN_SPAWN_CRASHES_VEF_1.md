# BRIDGE_PAWN_SPAWN_CRASHES_VEF_1 — `GenSpawn`-based bridge spawns NPE on pawns

# 🔴 RE-MEASURED 2026-09-20 (BENCH, live) — THE WORKFLOW IS NOT BLOCKED

**The title claim "universally" was WRONG, and it is the most expensive kind of
wrong: it says a standard workflow is dead when a working route was sitting next
to it the whole time.** Corrected rather than annotated.

`jawa/spawn_pawn` **WORKS**. MEASURED live on a VEF-loaded game (the 16-mod
`xenotypes` tier includes `oskarpotocki.vanillafactionsexpanded.core`), same map,
same session, same defName, back-to-back calls:

| tool | pawn (`Chicken`) | non-pawn |
|---|---|---|
| `rimworld/spawn_thing` | 🔴 **NPE** | ✅ |
| `jawa/spawn_batch` | 🔴 **NPE** | ✅ (`ChunkSlagSteel`) |
| `jawa/spawn_pawn` | ✅ **success**, pawn count 81 → 82 | n/a |

🔑 **65 pawns were spawned through `jawa/spawn_pawn` earlier in the same session**
(13 xenotypes × grids, for `XENOTYPE_CANON_CORRECTION_1`) with zero failures. The
"spawn many, screenshot, observe" method of `rimworld-debug-testing` is **usable
today** — it just has to call `jawa/spawn_pawn`.

⇒ **The common factor is `GenSpawn.Spawn` on a `ThingMaker`-made Thing.** Both
failing tools construct the Thing and hand it to `GenSpawn`; a Pawn built that way
never ran `PawnGenerator`, so its sub-trackers are null and VEF's `SpawnSetup`
postfixes dereference one. `jawa/spawn_pawn` generates a real pawn instead, which
is why it survives. (Construction detail confirmed from our own source — see below.)

## ✅ RESOLVED: `jawa/spawn_batch`'s parameter shape

The item recorded this as *"genuinely unknown, not a negative result"*. It is known
now. **`ops` is a STRING, not a list** — `'Def:x,z[,count]'` separated by `;` or
newlines, e.g. `'Chicken:124,100,1'`. The earlier `IConvertible` cast error came
from passing `[{x,z}]`. And with the right shape it **still NPEs on a pawn**, so it
is not an alternative route.

## ⚠️ UNMEASURABLE: VEF's own internals

RimSage indexes **core game assemblies only** — `RimWorld`, `Verse`, and the libs
bundled with the engine. There is no `VEF`/`OskarPotocki` namespace in its index, so
the bodies of `CompShieldField.SpawnSetup_Patch.Postfix` and
`PhasingPatches.CheckPhasing` **cannot be read from this machine** and the exact
member that is null is UNKNOWN. That does not block the fix: VEF's postfix is the
victim, not the cause — it is reading a pawn that our own call built wrong.
⛔ Do not write a guess at VEF's body into this item.



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
