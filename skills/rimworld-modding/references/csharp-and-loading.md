# C#, Harmony, and how RimWorld loads a mod

Read this before writing any C#, and whenever a mod "does nothing" despite
appearing to load. Most of that category is a constructor signature, a load-order
problem, or a `LoadFolders.xml` that quietly excluded the folder you're editing.

**Contents**
1. Mod folder anatomy
2. About.xml — and why `modDependencies` does not order anything
3. LoadFolders.xml
4. Entry points and their required constructors
5. Harmony
6. Building
7. Failure shapes and what they actually mean
8. `EnableDefaultCompileItems false` csproj — a new file needs listing twice
9. Job drivers and think nodes that silently swallow a custom job or state

---

## 1. Mod folder anatomy

```
MyMod/
├── About/
│   ├── About.xml
│   ├── Preview.png          (optional, 640×360-ish)
│   └── PublishedFileId.txt  (Steam only; do not create by hand)
├── 1.6/
│   ├── Assemblies/MyMod.dll
│   ├── Defs/
│   └── Patches/
├── Languages/
├── Textures/
└── LoadFolders.xml          (optional)
```

Without `LoadFolders.xml`, RimWorld loads the folder matching the running
version (`1.6/`) plus the mod root. `Defs/`, `Patches/`, `Assemblies/`,
`Textures/`, `Sounds/`, `Languages/` and `Patches/` are all discovered by name —
subfolder structure beneath them is free, so organise by content, not by rule.

A pure-XML patch mod needs only `About/About.xml` and `Patches/*.xml`.

---

## 2. About.xml — and the ordering trap

```xml
<ModMetaData>
  <packageId>yourname.modname</packageId>   <!-- lowercase, unique, immutable -->
  <name>My Mod</name>
  <author>You</author>
  <supportedVersions><li>1.6</li></supportedVersions>
  <description>What it does.</description>

  <modDependencies>
    <li>
      <packageId>brrainz.harmony</packageId>
      <displayName>Harmony</displayName>
      <steamWorkshopUrl>steam://url/CommunityFilePage/2009463077</steamWorkshopUrl>
    </li>
  </modDependencies>

  <loadAfter><li>brrainz.harmony</li></loadAfter>
  <loadBefore>...</loadBefore>
  <incompatibleWith>...</incompatibleWith>
</ModMetaData>
```

**`modDependencies` asserts presence. `loadAfter` asserts order. They are
independent, and this catches experienced authors.** A mod can declare another as
a hard dependency, be sorted anywhere relative to it, and blow up at startup
with a `ReflectionTypeLoadException` naming types from its own dependency —
because the dependency's assembly hadn't been loaded when the CLR tried to
resolve them.

Two things follow. When you author: always add `loadAfter` alongside every
`modDependency` whose *types* you reference. When you diagnose: a
`TypeLoadException` or `ReflectionTypeLoadException` pointing at a mod that is
demonstrably installed is a load-order report, not a corruption report. Fix it in
the sorter (RimSort user rules, or `loadAfter` in a local copy) rather than
editing anyone's assembly.

`packageId` is the identity used by `MayRequire`, `FindMod`, dependencies and
save files. Changing it after release orphans every reference to the mod.

---

## 3. LoadFolders.xml

```xml
<loadFolders>
  <v1.6>
    <li>/</li>
    <li IfModActive="ludeon.rimworld.odyssey">Odyssey</li>
    <li IfModNotActive="someone.othermod">NoCompat</li>
  </v1.6>
</loadFolders>
```

The rule that surprises people: **once this file exists, it fully replaces the
default resolution.** If you don't list `<li>/</li>`, the mod root is not loaded,
and content you can plainly see in the folder is simply never read. When a def
you *know* exists doesn't resolve, check this file before checking anything else.

Paths are relative to the mod root and load in the listed order, so later entries
patch over earlier ones.

---

## 4. Entry points and their required constructors

Every one of these has a signature RimWorld reflects for. Get it wrong and the
object is never constructed — usually with no crash, just absence.

```csharp
// Settings / lifecycle. Needed only if you have mod settings or a settings UI.
public class MyMod : Mod {
    public MyMod(ModContentPack content) : base(content) { }
}

// Runs once at startup, after all defs are loaded.
[StaticConstructorOnStartup]
public static class Startup {
    static Startup() { /* ... */ }
}

// Persists with the save, ticks globally.
public class MyGameComp : GameComponent {
    public MyGameComp(Game game) { }        // <-- public, takes Game. Mandatory.
    public override void GameComponentTick() { }
    public override void ExposeData() { }
}

public class MyWorldComp : WorldComponent {
    public MyWorldComp(World world) : base(world) { }
}

public class MyMapComp : MapComponent {
    public MyMapComp(Map map) : base(map) { }
}
```

**Why the `GameComponent(Game game)` rule deserves special care:**
`Game.FillComponents` instantiates by reflection and throws
`MissingMethodException: Constructor on type '...' not found`. The exception is
logged and swallowed — the game proceeds, the component doesn't exist, and its
`GameComponentTick` never runs. If that component was enforcing a consequence
(a delayed check, a decay, a detection roll), the *feature* still appears to
work while quietly having no downside. That is worse than a crash, and it is
worth a deliberate look whenever a mod's costs seem suspiciously absent.

Components are also the safest place for anything that must be per-save: they
serialise through `ExposeData` and travel with the save file. Static fields do
not, and a static that survives a save/load boundary is a bug waiting for a
second colony.

### Two more silent-absence traps, this time on `Building`

**`BuildingBase` never sets `tickerType`, so it defaults to `TickerType.Never`.**
Any custom `Building` whose mechanic lives in `Tick()` or `CompTick()` is
**silently dead** — no error, comps present, fields correct, nothing ever runs.
Measured: a pit trap's mass-sum trigger did not fire across 200 ticks with an
immobilised pawn standing on it. Add `<tickerType>Normal</tickerType>` (or
`Rare`/`Long` if the mechanic can tolerate it) to the def, and prove the fix by
testing the real tick path over real ticks — not by a forced debug call, which
proves only that the method itself is reachable.

**To make a `Thing` re-run its own `Print()`, dirty `MapMeshFlagDefOf.Things`**
(what `Verse/Thing.cs DirtyMapMesh` uses). `MapMeshFlagDefOf.Buildings` dirties
the linked/buildings mesh layers instead, so the old print stays on screen
**forever, with no error** — a terrain-mimic cover looked completely
unimplemented because of one wrong flag. The two `MapMeshFlagDef`s are not
interchangeable even though both sound like "redraw this building."

---
**A generator ThingDef (`CompPowerPlant` or a subclass) needs `<tickerType>Normal</tickerType>`** for the same reason: `CompPowerPlant` writes `PowerOutput` only from `CompTick` -> `UpdateDesiredPowerOutput`, so without a ticker it spawns, connects, reads as a generator and outputs 0 W forever, with no log line. Consumers (`CompPowerTrader` alone) do not need one. Likewise a tickerType `Never`->`Normal`/`Rare` repair wakes base-class behaviour that never ran: review the woken comps' CompTick paths (`CompProjectileInterceptor` recharges with no power check; per-tick state that was never reachable can be unsaved), not just the def line.

## 5. Harmony

```csharp
[StaticConstructorOnStartup]
public static class HarmonyInit {
    static HarmonyInit() {
        new Harmony("yourname.modname").PatchAll();
    }
}

[HarmonyPatch(typeof(Pawn), nameof(Pawn.Tick))]
public static class Pawn_Tick_Patch {
    static void Postfix(Pawn __instance) { }
}
```

Patch types, in order of how much you should want to use them:

- **Postfix** — runs after; can read/modify `__result`. Composes with other mods'
  postfixes. Reach for this first, essentially always.
- **Prefix** — runs before; returning `false` skips the original method entirely.
  Powerful and antisocial: any other mod's patch on that method is skipped too.
  Use only when you must prevent the original, and say so in a comment.
- **Transpiler** — rewrites IL. Precise, and the most fragile thing in the
  ecosystem: it breaks on any game update that shifts the instructions it
  matches. Last resort, and pin your matching to distinctive operands rather
  than offsets.
- **Finalizer** — runs even when the original throws. Use to contain exceptions
  from someone else's code.

Useful injected parameters: `__instance`, `__result`, `___privateField` (three
underscores), `__state` (Prefix→Postfix handoff).

Prefer depending on the Harmony mod (`brrainz.harmony`) over shipping
`0Harmony.dll`, so every mod shares one instance and version conflicts don't
arise. Declare it in both `modDependencies` and `loadAfter` (see §2).

---
- **`Mineable.TrySpawnYield` has two overloads in 1.6**, `(Map, bool, Pawn)` and an `[Obsolete]` `(Map, float, bool, Pawn)`: a name-only `[HarmonyPatch(typeof(Mineable), "TrySpawnYield")]` is ambiguous. Pass `new[]{typeof(Map), typeof(bool), typeof(Pawn)}` (verified by reflection on Assembly-CSharp.dll).
- **A Harmony adapter that reads a donor mod's state by reflection must return null (and warn once) when a member is missing, never an empty collection.** An empty list read as 'the donor has no entries' (a Quarry dictionary returning `[]` on reflection drift gave unregistered ores a share of 0 and silently broke a card). Let the caller see 'unknown' and keep the donor's own path.

## 6. Building

- Target **.NET Framework 4.7.2** for RimWorld 1.4–1.6.
- Reference `Assembly-CSharp.dll` and the `UnityEngine.*` DLLs from
  `RimWorld/RimWorldWin64_Data/Managed/`.
- Set **Copy Local = false** on every game/Unity reference. Shipping
  `Assembly-CSharp.dll` inside your mod loads a second, stale copy of the entire
  game's types and produces failures that look like anything but their cause.
- Output the DLL to `<ModName>/1.6/Assemblies/`.
- Bump the assembly name when the mod is renamed; two loaded assemblies with the
  same name is its own confusing class of failure.

Decompile with dnSpy or ILSpy against that same `Assembly-CSharp.dll` when you
need to know what a method actually does. Reading the real IL is the C# analogue
of reading the real def, and it is equally non-optional.

---

## 7. Failure shapes and what they actually mean

| Log shape | Usual meaning |
|---|---|
| `Error in static constructor of X` | The mod is **dead** — nothing in it ran. Highest-priority finding in any log. |
| `ReflectionTypeLoadException` naming another mod's types | Load order (§2), not corruption. |
| `MissingMethodException: Constructor on type ... not found` | Entry-point signature (§4). Feature silently absent. |
| `Could not execute post-long-event action` + exception inside `LongEventHandler.ExecuteToExecuteWhenFinished` | **One queued action failed; the queue continues.** Verified from IL 2026-08-10 — per-action try/catch, the handler's `leave` targets the loop increment. Cost is that one action (usually one def's `ResolveIcon`). The *only* abort path is an NRE in the DeepProfiler block outside the try, which also bricks the queue behind "Already executing." |
| `AmbiguousMatchException` in a Harmony patch | The target method gained an overload in a game/mod update. The patcher is version-drifted. |
| Harmony patch applies but has no effect | Another mod's Prefix is returning `false` on the same method. |
| `Could not find type named X` in a def | The assembly didn't load, or the def references a class from a mod that isn't present. |

The pattern worth carrying between sessions: in a large stack, hard breaks
concentrate in **mods that reflect over other mods' types at startup** — patchers,
compatibility layers, indexers. They run early, they assume a shape, and the
shape changed. Grep for `static constructor` first, every time.

---
- **A subprocess-wrapping C# (`OracleClient.cs` style) must read both streams.** A real `claude -p` auth failure ('OAuth session expired') prints to STDOUT, so a wrapper that reads stderr only on a nonzero exit logs nothing useful; fall back to stdout when stderr is empty.
- **A native Burst-job crash with no managed exception is a native array freed too early, not the sounds logged just before it.** Seen on Stillsand 100x100 (4 of 4): a sun-cost path array in `RM_MapComponent_ShadeGrid` was freed one rebuild too early. Free retired native arrays only after 60 ticks (`RM_DeferredDisposal`); live-confirmed over 12,084 ticks, one run.
- **A float-times-int in a `Ceil` can overshoot:** `0.3f*100` ceils to 31, moving a 30% floor by one HP. Keep thresholds as whole percents and compare `hp*100 > max*pct`.

## 8. A csproj with `EnableDefaultCompileItems false` needs the new file listed twice

⚠️ **A project that sets `EnableDefaultCompileItems false` and lists every
`.cs` file explicitly** — `RM_CreatureBehaviors.csproj` lists all ~75 files
this way — **compiles a new file dropped into `Source/` into NOTHING, with no
error.** The class simply does not exist at runtime, and every def
referencing it then fails to resolve for a reason that points nowhere near the
missing `<Compile Include>` line. ⇒ Adding a `.cs` file to such an assembly is
always a two-file change: the source file, and the csproj's file list.
(2026-09-23)

## 9. Job drivers and think nodes that silently swallow a custom job or state

**A job that "starts then reverts to Wait after 60 ticks" is usually the
DRIVER killing it, not the target.** Read the job driver's `FailOn`/
`AddFailCondition` lines in source before blaming the thing the pawn was
aimed at — `JobDriver_Refuel.cs` kills any unforced job when its auto-refuel
gating says no. A companion mod fixed this class of bug by setting
`job.playerForced` on the jobs it hands out. (2026-09-09)

**`Pawn.CurrentlyUsableForBills()` requires `InBed()` for EVERY pawn
billGiver** (surgery, memory wipe, any whole-pawn `Recipe_Surgery`-style
bill). A droid-type pawn never satisfies this: `needsRest=false` gives it no
drive to seek a bed, and `WorkGiver_TakeToBedToOperate` explicitly refuses any
pawn with `RaceProps.IsFlesh==false`. This silently blocks **every**
whole-pawn recipe on a non-fleshy race, not just whichever one happens to be
under test. Fix: a Harmony prefix on `CurrentlyUsableForBills` that skips the
`InBed()` check for non-fleshy pawns specifically, keeping the
`InteractionCell` reachability check. (2026-09-12, `DROIDWORKS_WIPE_SEVERITY_1`)

**Two think nodes dispatch mental states and only one of them is
subclass-aware.** `ThinkNode_ConditionalMentalState` tests
`pawn.MentalStateDef == state` (def IDENTITY); `ThinkNode_ConditionalMentalStateClass`
tests `stateClass.IsInstanceOfType(...)`. Manhunting is routed by the CLASS
one, so a custom `MentalStateDef` whose `stateClass` subclasses
`MentalState_Manhunter` inherits `JobGiver_Manhunter` with **no** think-tree
patch and **no** Harmony needed — and conversely a state routed by the DEF one
would silently have no behaviour at all if authored the same way. Check which
of the two the vanilla think tree actually uses before assuming a custom
mental state needs its own JobGiver wiring. (2026-09-21)
- **`Pawn_JobTracker.TryTakeOrderedJob` sets `job.playerForced=true` for ANY pawn, and 1.6 never interrupts a playerForced job on damage** (`Notify_DamageTaken`: `!curJob.playerForced`). A comp steering a wild/AI animal with it makes the animal ignore being shot and cut through mental states, flees and sleep: use `pawn.jobs.StartJob(job, JobCondition.InterruptForced, ...)` and only from idle jobs (null/Wait/Wait_Wander/GotoWander); `JobDef.isIdle` is no filter (Flee and FleeAndCower are isIdle). A `Goto` (PathEndMode.OnCell) to an impassable cell fails CanReach silently every time: target a standable reachable cell beside the thing.

## Vanilla 1.6 engine behaviours that bite mod code (decompiled-verified)
- **Changing a spawned pawn's `BodySize` (life-stage lock, growth) under Large Pawns** must deregister/re-register it from `thingGrid` + the region listers around the change: Large Pawns registers the square by BodySize at registration and deregisters by current BodySize, and `Thing.SpawnSetup` registers BEFORE comps' `PostSpawnSetup`. A shrink leaves a ghost ring in the grid.
- **A spawned random `Colonist` pawnkind is sometimes a `HumanlikeTeenager` (BodySize 0.8, Biotech).** Any bar that depends on body size (mass gained, capacity, prey fraction, trench cover, pit width, fall damage) must read the victim's own `BodySize`, never assume an adult. One probe of 20 adults nearly 'disproved' it; one probe of a minority outcome proves nothing.
- **Vanilla 1.6: a `WaterBody` made at runtime counts 0 freezable cells,** so FreezeManager's chance is 0/0 NaN and dug water never freezes, silently. `RM_WaterBodyFreezeCountFix.cs` patches it (fish size is counted correctly); expect it to be needed again for any runtime-made water body.
- **XML that LOOKS like a dictionary is not proof the C# field is an `IDictionary`:** 1.6 `GenStep_Asteroid.mineableCounts` is `List<MineableCountConfig>` read by `LoadDataFromXmlCustom`, so reflection doing `f.GetValue(x) as IDictionary` silently no-ops (a doonium toggle shipped dead). Read the field type in the decompile (`D:\ClaudeWork\rimmandrake\decomp\rw16`), prefer typed access when Assembly-CSharp is referenced, and check every list a def is added to (e.g. `GeneratedLocationDef.preciousResources`) when writing a remover.
- **Meteorite and mineable draws roll a bucket first.** `ThingSetMaker_Meteorite.FindRandomMineableDef` picks a bucket (0.4 non-resource rock, 0.35 ore <5 silver, 0.25 ore >=5) then `RandomElement()`s inside it, so filtering `nonSmoothedMineables` to remove every stone type makes 40% of meteorites pick null and `ThingMaker.MakeThing(null)` throws. Replace the draw (prefix renormalising over non-empty buckets) and filter only while that prefix is installed. A `Reset` postfix must not touch a `[StaticConstructorOnStartup]` class: Reset runs from `PlayDataLoader.ResetStaticDataPost` BEFORE static constructors.
- **A building whose printed Graphic depends on fuel (or any state another actor changes) must compare against the state it last PRINTED**, not a before/after inside its own tick: `CompRefuelable.Refuel` calls no `MapMeshDirty`, so a refill between rare ticks is invisible to a before/after test and the mesh keeps the stale graphic.
- **`CompGlower.GlowColor`'s setter de-registers and re-registers a lit glower on EVERY write, even with the same value,** re-flooding the glow grid. A periodic sweep that re-assigns colour dirties the grid around every light it touches: compare against `glower.GlowColor` before writing.
- **1.6 GenStep subclass traps.** `GenStep_ScatterLumpsMineable.ScatterAt` clears `recentLumpCells` only AFTER its early returns (tutorial storyteller, null def), so a subclass counting lumps by it must clear it itself before each call. `GenStep_ScatterThings` with `minify=true` lists the result under `MinifiedThing`, so a `ListerThings.ThingsOfDef(thingDef)` delta cannot see it; override `GenerateThing` (once per ScatterAt) to hold the reference. A render-node worker probing `PawnRenderNodeWorker_Apparel_Head.HeadgearVisible` sees every mod's postfix on it (ReGrowthCore vetoes while `curJob.swimming`): mirror any re-ask context flag your own patch uses or the probe and the real draw disagree.
- **`GameCondition.TicksLeft` on a Permanent condition logs 'Trying to get ticks left of a permanent condition' (ErrorOnce) and returns 360000000.** Check `.Permanent` first when mirroring another condition's remaining time (vanilla Aurora and others can be permanent via scenario). Also: destroying `holdsRoof` buildings under a constructed roof marks the unsupported roof to collapse (`Building.DeSpawn` -> `RoofCollapseCellsFinder.Notify_RoofHolderDespawned`); clear `roofGrid` first if the structure should vanish whole.
- **`map.gameConditionManager.ActiveConditions` holds MAP conditions only;** a world-scope condition lives on `Find.World.gameConditionManager`, the map manager's `Parent`. Vanilla's `Aggregate*` reads walk it: `for (var mgr = map.gameConditionManager; mgr != null; mgr = mgr.Parent)`. Each condition must still pass `cond.CanApplyOnMap(map)` (underground maps without `allowUnderground`, layer white/blacklists, orbit layers). Vanilla `AggregatePlantDensityFactor` passes `ownerMap`, which is null for the world manager, so a WORLD condition's `PlantDensityFactor` never applies in vanilla: pass the asking map yourself if a world condition must reach maps.
- **`TerrainGrid` temporary and layered terrain are lossy to paint-and-restore.** `TerrainAt(c)` returns the TEMPORARY layer first (lava, floodwater, thin ice), then foundation, then top: record `TopTerrainAt`/`UnderTerrainAt`, or skip cells where `TempTerrainAt(c) != null`, or the temp def is saved as the 'original' and the replacement stays permanent. Setting a non-layerable terrain (water) over a built floor nulls `underGrid` (the soil is gone) and setting the floor back puts the water into `underGrid`: skip layerable/`isFoundation`/`FoundationAt` cells or remember and restore `underGrid` too, restoring into the layer that holds your terrain (`SetTerrain` vs `SetUnderTerrain`).
- **`ReservationManager.CanReserve` returns false outright when ANY existing reservation on the target (same layer, respected claimant) has a different `maxPawns`.** A job giver's `CanReserve` must use the exact maxPawns and stackCount its driver's `Reserve` uses, or a shared target is silently never shared. Also: a bare `thing.stackCount` write skips `DirtyMapMesh` and `listerMergeables`; shrink a spawned stack with `SplitOff(n).Destroy()`.
- **A hediff's `tickAdded` does not identify the killing wound:** `Hediff_Injury.TryMergeWith` folds a new Burn/Crush/Shredded/Frostbite (`injuryProps.canMerge`) into the existing wound of its def on the same part, which keeps its OLD `tickAdded`. To know what killed a pawn, record `DamageInfo` in `ThingComp.Notify_Killed` (called by `ThingWithComps.Kill` inside `Pawn.Kill`, before `DeathActionWorker.PawnDied`, which gets no dinfo). Also: vanilla `Building_Heater` has no `CompHeatPusher` (it heats in its own TickRare via `CompTempControl`), so code finding 'heaters' by `CompHeatPusher` misses the main colony heater.
- **A static collection of Things (`Dictionary<Thing,...>`, `HashSet<Pawn>`, a leak/alert registry) outlives the game.** Loading a save or quitting to menu drops the old Game and Maps WITHOUT despawning anything, so no `PostDeSpawn`/Release cleanup runs, the static keeps the old Map graph alive, and stale entries still read `Spawned=true` (`mapIndexOrState` is never reset), so `RemoveWhere(Destroyed || !Spawned)` never prunes them and `t.Map` can index `Find.Maps` out of range. Tag the collection with the `Current.Game` it was filled in and `Clear()` it on access when that differs, or keep the state on a MapComponent/GameComponent.
- **A PAWN does get `CompTickRare` in 1.6:** `Pawn.Tick` runs `base.Tick()` then `if (IsHashIntervalTick(250)) TickRare();`, and `ThingWithComps.TickRare` calls every comp's `CompTickRare`. Only NON-pawn Normal-ticker things (buildings) miss it. Never add a CompTick that calls `CompTickRare` at `IsHashIntervalTick(250)` on a pawn comp (it runs the rare logic twice on one tick). A vanilla comp that works in BOTH `CompTick` and `CompTickRare` (`CompHeatPusher`: PushHeat every 60 and x4.1666 in rare) assumes one ticker, so on a pawn it does its work twice (a heat pusher on an animal heats ~2x): grep it for both overrides first and override `CompTickRare` to return when `parent is Pawn`. Read `Pawn.Tick`, not `ThingWithComps` alone; `lint_ticker_compat.py` already knows this.
- **A pawn's death DOES reach `Destroy(KillFinalize)`:** `Pawn.Kill` despawns the pawn into its corpse, then calls `base.Kill` unless already destroyed, so a comp's `PostDestroy(KillFinalize)` fires. The catch: its map is `base.MapHeld` at that moment, which resolves through the corpse and is null when no corpse was placed (no corpseDef, placement failed, died in a container). For death logic prefer `ThingComp.Notify_Killed(prevMap, dinfo)` with `pawn.prevMap`. Separately, `Thing.Destroy` never drops or destroys an `IThingHolder`'s contents: a holder Thing must spill or `ClearAndDestroyContents` in its own Destroy override.
- **`Corpse.Destroy` (any DestroyMode) runs `PostCorpseDestroy`, which DESTROYS the inner pawn's equipment, inventory and apparel,** so relics, persona weapons, quest items, carried meds and silver vanish silently. Code that makes a body vanish (dissolve, eat, absorb, cremate-in-place) must first call `corpse.Strip(false)` or drop apparel, equipment AND inventory (`inventory.DropAllNearPawn` works while the corpse is spawned, via `MapHeld`).
- **A pre-aged corpse needs `Corpse.Age` set as well as `CompRottable.RotProgress`.** `PawnGenerationRequest(forceDead: true)` kills the pawn now, so `timeOfDeath = now`; setting only the rot gives a dried corpse whose inspect text says it died 0 days ago. Vanilla `GenStep_ScatterCaveDebris` sets Age, then adds it to RotProgress, before `GenSpawn`.
- **A new ThingDef with `thingClass` Hive (or `CompProperties_SpawnerHives`) escapes vanilla's 30-hive cap:** `HiveUtility.TotalSpawnedHivesCount` counts `ListerThings.ThingsOfDef(ThingDefOf.Hive)`, an exact def match, so `CanSpawnChildHive` reads 0 and a re-skinned hive breeds forever. Re-derive the cap against your own def (subclass `CompSpawnerHives` via `<compClass>`).
- **`HediffWithComps` runs two separate severity passes:** `PostTick` sums `CompPostTick(ref adj)` every tick, `PostTickInterval` sums `CompPostTickInterval(ref adj, delta)`. Vanilla `SeverityPerDay`/`SeverityModifierBase` adjust only on the interval path (every 200 ticks), so a comp that clamps or floors severity in `CompPostTick` lags that fade by a tick: override both and list the clamp comp after the one it clamps. A hediff that a MapComponent adds and removes must also remove itself off that map (a pawn leaving by caravan, gravship or pods is no longer reached by the component): use a `HediffComp` with `CompShouldRemove` checking `pawn.MapHeld`, ticked in `CompPostTickInterval` (world pawns tick with delta>1 and can skip `IsHashIntervalTick`).
- **`WildAnimalSpawner.CommonalityOfAnimalNow(kind, loc)` gets the map-edge ENTRY cell for ongoing wild spawns** (`SpawnRandomWildAnimalAt`) and random interior cells only during map generation. A postfix gating a kind on what is near `loc` (plants, terrain, buildings) gates arrivals at the edge, not the map.
- **`SetFaction` after `GenSpawn.Spawn` is too late for anything acting in `PostSpawnSetup`:** `CompSpawnerPawn` spawns its `initialPawnsCount` (and their lord) inside Spawn using `parent.Faction`, so they come out wild. Call `thing.SetFaction` BEFORE `GenSpawn.Spawn`. Also, a GenStep placing a multi-cell building with `WipeMode.Vanish` must test every cell of `GenAdj.OccupiedRect`, not the root cell.
- **A vanilla SoundDef with `sustain=True` (e.g. GeyserSpray) cannot be played with `PlayOneShot`/`PlayOneShotOnCamera`:** it logs 'Tried to play sustainer SoundDef ... as a one-shot sound' plus 'no on-camera subSounds' and plays nothing. Read the vanilla def's `sustain`/`onCamera` before reusing it; for a one-shot define a new SoundDef on the same `clipPath`.
- **A Sustainer spawned with `SoundInfo.OnCamera` has no source map,** and `SoundDefHelper.CorrectContextNow` checks map-vs-world only when `sourceMap` is null, so a MapComponent's MapOnly ambient sustainer plays while the player looks at ANY map. Gate on `Find.CurrentMap == map` (end on look-away, resync on look-back), and end it in `MapComponentUpdate` (called every frame for every map, paused or not), not in `MapComponentTick`: when the player switches map while PAUSED, ticks stop and a PerTick sustainer only expires when `TicksGame` passes `lastMaintainTick+1`, so it keeps playing until unpause.
- **`GenPlace.TryPlaceThing(thing, cell, map, ThingPlaceMode.Near)` can merge PART of the stack into neighbouring stacks before returning false;** the remainder stays on the unspawned Thing (`thing.stackCount`). Treating false as 'nothing landed' and re-storing the full count duplicates the merged part: count what landed as `n - thing.stackCount`.
- **Prefixing `CompProjectileInterceptor.CheckIntercept` does NOT switch an interceptor off:** `CheckBombardmentIntercept`, `BombardmentCanStartFireAt`, `PostDraw` (the bubble), the `activeSound` sustainer and BroadshieldPack all read the non-virtual `Active` getter. To disable a subclass drive the base private `shutDown` field (`AccessTools.FieldRefAccess`) and track that YOU set it.
- **`Scribe_Values.Look<char>` compiles and saves but never loads:** `ParseHelper` registers no char parser, so load logs 'Trying to parse to unknown data type Char' and returns NUL. Only non-default values are written, so a fresh save looks fine. Scribe a char through a string under the same key (old saves stay loadable).
- **`GenGrid.Standable(c)` is false on every cell of a building whose passability is not Standable** (PassThroughOnly heaters, lamps, chargers, masts, as well as Impassable). A 'deposit filth / mark under this machine' loop gated on Standable silently does nothing for most powered devices; `FilthMaker` itself needs only `WalkableByAny`. Gate on the ring around the footprint (`OccupiedRect().ExpandedBy(1)`) or on `WalkableByAny`.
- **`FilthMaker.TryMakeFilth` thickens an existing same-def filth (to 5) instead of spawning a second,** so a check counting filth things under-reads a spill: sum thickness. It also defaults `shouldPropagate=true`: when the cell already holds that filth at the cap (`!CanBeThickened`) or is not `WalkableByAny`, the deposit spills onto a random 8-way neighbour checked only for `WalkableByAny`, ignoring your Roofed/Standable gate, so a repeated 'saturate this cell' creeps outward and under roofs and every call on a saturated cell pays 8 neighbour searches. For a deliberate per-cell mark pass `shouldPropagate:false` and early-out on `!CanBeThickened`.
- **`Verse.Messages.Message` does NOT silently drop a duplicate:** `AcceptsMessage` finds the live one with the same text+targets, resets its timer, Flash()es it and replays `def.sound`. A Message fired from a poll (every 250 ticks) while a condition holds is a sound nag: gate it per subject with a quiet window.
- **C# allocates a lambda's closure (display class) at the ENTRY of the scope owning the captured variable, on every call, even if the lambda never runs.** A ThreadPool lambda in a cache `Get` cost 32 B per pair per frame on pure cache hits. Move the lambda into its own helper method. Measure with `GC.GetAllocatedBytesForCurrentThread` after a warm-up call. Also `foreach` over an `IList<T>` boxes the enumerator: use an indexed loop on hot paths.
- **Vanilla `CompExplosive.Detonate` does NOT use `instigator ?? parent`:** it names the explosion `(stored == null || stored.HostileTo(parent.Faction) && parent.Faction != OfPlayer) ? parent : stored`, where `stored` is the `dinfo.Instigator` of the damage that lit the wick, and a factionless thing (plant, chemfuel stack) is never hostile-to. A gate keyed on an explosion's instigator def must read the exploding thing, not `explosion.instigator`. Likewise a Fire's instigator escapes any scope around `Fire.TickInterval`: one spread in five launches a Spark with the Fire as launcher and `Spark.Impact` swaps in `fire.instigator` on a later tick, and `Pawn.Kill` relights an attached fire on the corpse with `fire.instigator` outside the Fire's tick. A gate keyed on 'inside a fire's tick' must also cover `Spark.Impact` (Launcher is Fire) and the corpse relight.
- **`ThingComp.PostPostApplyDamage` runs AFTER `DamageWorker.Apply`, which kills (Destroy KillFinalize) a thing whose HP reaches 0,** so on the killing blow `parent.Map` is already null and an 'about to die' branch reading `parent.Map` or a map component through it silently does nothing (no drop, no notify). Snapshot the map in `PostPreApplyDamage` and use `parent.Map ?? snapshot`.
- **Wall-mounted storage.** An item on a wall cell is listed in the regions on BOTH sides (`RegionListersUpdater.CanRegisterInAdjacentRegions`), so an OnCell->Touch reach patch lets pawns take it from the back of the wall too (vanilla and RimFridge behave the same: accepted). `def.blockLight` is read live by the lighting layers but `GlowGrid.lightBlockers` is written only at `Building.SpawnSetup`/`DeSpawn`: a setting that flips `blockLight` in play must call `map.glowGrid.LightBlockerAdded/Removed` on built things, or a phantom blocker outlives the building.
- **Hiding a recipe through `RecipeDef.AvailableNow` only filters the add-bill list.** `WorkGiver_DoBill` asks `Bill.ShouldDoNow`, so bills made before a settings switch went off keep running: a mod setting that turns a recipe off must also postfix `Bill_Production.ShouldDoNow`.
- **Converting a held stack into another def as ONE stack silently destroys the units above the target def's `stackLimit`** when the source stack is bigger (stack-size mods; `made.stackCount = Min(n, into.stackLimit)`). Cap the converted count at the target stackLimit or emit several stacks.
- **Vanilla temperature is not save-exact.** Outdoor `GenTemperature.GetTemperatureForCell` returns `TileTemperaturesComp`'s 60-tick cache, phased from its FIRST query (the phase restarts after a load); outdoor rooms copy it at `TicksGame%120==7`; room temperatures are saved truncated to 1/16 C (`(int)(t*16)+32768`). A deterministic sim that must continue identically across save/load reads `TileTemperaturesComp.OutdoorTemperatureAt(tile, TicksAbs)` + `GameConditionManager.AggregateTemperatureOffset` (internal in 1.6: `AccessTools.MethodDelegate`) outdoors and quantises indoor reads to 1/16 C.
- **`GenSpawn.Spawn` defaults to `WipeMode.Vanish`, and `GenSpawn.SpawningWipes` returns true for an Item under a new Impassable building,** so a mid-game spawn of a wall/plug/blocker silently DELETES loot, weapons and corpses on its cells. Use `WipeMode.VanishOrMoveAside`; grep other mid-game impassable spawns for the default.
- **RelativeVeto-style region/depth gating.** Vanilla regions (walls, no depth) ANDed with a depth-only pocket grid (depth, no walls) is not reachability on the joint graph: walls plus a trench that cut a route only together make `CanReach` true while A* finds nothing. Gate any job you hand out with `FindPathNow` where walls and pits meet.
- **Every per-cell depth read on the DRAW side (sink, sink clamp, lip occluder) must ask the deck/lid layer, not `HollowDepthAt`,** or a covered cell renders as the hole (a pit-lid walker drew sunk because `DrawDepth` handled only suspension decks). A 'hidden' proof bar must read Harmony's patch table + the prefix, not the predicate the prefix guards.
- **Shrinking or reloading a capped pool by replaying old records oldest-first through its own evicting `Write()` does not apply the eviction rule to the whole set:** each Write sees only what is already in, so later low-priority records evict earlier protected ones. Pick the survivors over the whole list first, then replay only them. Same family: post-filtering `GenClosest`'s single hit instead of passing the filter as its validator makes a pawn give up when the nearest candidate fails.
- **The engine already says who started a fight: every hit carries `DamageInfo.Instigator` AND `InstigatorGuilty`**, and vanilla sets guilt by drafted-ness (`Bullet.cs:22`, `Verb_MeleeAttackDamage.cs:50`); undrafted self-defence is NOT guilty. Any aggressor-detection or retribution mechanic (a truce that punishes the first attacker) keys on the first guilty hit, with no "don't fight back" rule needed.
- **A sea biome's `wildAnimals` cannot ambient-spawn its cast on its own generated map.** The spawn chooser reads `BiomeAt(cell)` PER CELL (`MixedBiomeMapComponent`), so every standable cell belongs to the blend/secondary biome while the sea's own cells are unstandable water (gen seeded 5 donor Gorg, 0 of 6 Scald entries). The tick spawner is `Rand.Chance(0.027 x density)` per 1213 ticks (about 0.4% per roll at density 0.15), so a zero over a few thousand ticks proves nothing. Dive/floor maps must seed their own cast; sea `wildAnimals` rows only feed tile-level consumers (herd migration, animal ambush).
- **`BeautyUtility.CellBeauty` keeps only Fillage.Full things when a cell holds one,** so anything else on a wall tile (a filth-class mark, say) adds zero beauty, and filth under a roof is multiplied by .3. `Thing.GetBeauty` is virtual, so a Thing subclass can set its beauty per instance with no Harmony. Moving a beauty-bearing thing's Position onto a wall tile silently zeroes it.
- **A custom InteractionDef's `socialFightBaseChance` is judged on the RECIPIENT's traits and opinion** (`Pawn_InteractionsTracker.TryInteractWith` calls `recipient.CheckSocialFightStart`); only gene factors read the initiator. So a 'confront' interaction scales with the person confronted, not the angry one. To scale with the initiator's temper, set the base to 0 and roll after TryInteractWith, using SocialFightChance(Insult, initiator)/Insult base as the shared factor.
- **A building's 'lost' hook on `Destroy()` misses a gravship launch:** `GenerateGravship` DeSpawns every ship thing with `DestroyMode.WillReplace` and never destroys it. Put loss hooks on `DeSpawn` (Destroy reaches it too) and check `generatingGravship` for the fly-together case.
- **`Building_Door.OpenPct` is protected in 1.6:** a static helper cannot read it. Pass the open state in from the door subclass (`DoorPreDraw`/`Comps_PostDraw` are callable from the subclass).
- **`GenRecipe.MakeRecipeProducts` registers EVERY ingredient def in the product's `CompIngredients`,** so a sealing agent (resin, salt, brine, bitumen) shows in a sealed food's ingredients line. Cosmetic; a postfix removing agents (non-ingestibles / `NeverForNutrition`) fixes it if wanted.
- **A hostile raider walking off the map never calls `CaravanExitMapUtility.ExitMapAndCreateCaravan`:** `Pawn.ExitMap` routes there only for colonists or pawns with a player caravan to join, and `FindCaravanToJoinFor` returns null for other factions. Hook raid departure at `Lord.GotoToil` to an exit toil instead.
- **`MatLoader.LoadMat` can never load a mod asset:** it reads only Unity `Resources/`, returns null, and `MaterialAllocator.Create(null)` throws, which in a static field is a `TypeInitializationException` on every `Update()` and a black map. Build overlay materials from a texture, or use a vanilla material.
- **`FleckCreationData.exactScale` stretches a spawned fleck non-uniformly,** the lever for turning a round stock puff texture into a thin ribbon or sliver with no new art.
- **`UnityEngine.GUI.DrawTexture`'s 12-parameter leaf (the only overload holding the 'null texture passed to GUI.DrawTexture' warning) is INTERNAL in 1.6's IMGUIModule,** as are the 9- and 11-param forwarders. A Harmony target lookup with `BindingFlags.Public` silently lands on a forwarder the JIT may inline. Use `Public|NonPublic` and check method flags with dnfile.
- **Tame animals CAN open the player's doors** (`PawnKindDef.canOpenDoors` defaults true). What shuts wild animals, hostiles and prisoners out is the faction rule `GenAI.MachinesLike` inside `Building_Door.PawnCanOpen`, and a FACTIONLESS door (`jawa/spawn_batch` leaves doors factionless) lets a wild animal through. Model 'animal vs door' as 'cannot open the player's doors', not `!CanOpenDoors`.
- **`Verse.Mod.GetSettings<T>()` tracks ONE `ModSettings` per `Mod` object** (a private field, not keyed by type): a second call for a different `T` logs a `Log.Error` and returns null, with no exception. A constructor calling it for several types silently breaks the others (NRE in `DoSettingsWindowContents`, fields never persist). Make extra settings classes plain `new` and scribe them from the one real `ModSettings.ExposeData()`.
- **A refusal added to a BUILT hook needs its mirror in the LOST hook,** and a settings toggle gating one path into a side effect must gate every other caller of it. A tower refused on a drawbridge by `Notify_TowerBuilt` was re-added by `Notify_SupportLost` and swung the bridge down on deconstruction: lose only what `r.towers.Remove(i)` says was held. `Notify_StageChanged` synced hum sustainers with the hum switched off: grep every caller of the effect for the same gate. In a live gate script, an early raise/return for an UNMEASURED case skips the gate's clean-up and leaks state (manhunter slimes) into later gates' log budgets.
- **C# `NextChange` predictions built from float fields lose ~1e-7 per unit** (`l.lit * l.period / len`): over a long dark gap (lit 0.02 = ~150 units) the predicted change landed microseconds EARLY and a +-1e-6 exactness check caught it. Promote def floats to double before multiplying them into a time. A NextChange test with only lit 1 / short gaps cannot see this.
- **A static (session-wide) table or cache keyed by thing/pawn ID breaks across fixture and save reloads:** a reload restarts BOTH the thing-ID counter and the tick, so the next session's first-spawned pawn inherits an old 'already handled' entry at a fresh-looking tick, and a 'too far ahead = stale' guard does not catch it. Key such tables per map (`MapComponent`) or clear them when `Current.Game` changes.
- **Scribing a field is not saving it: check that nothing resets it after the load.** `FinalizeInit` called `ResetDetector()` on every map init, including loads, wiping scribed `lastCell`/`walkedInto`; only a save->load->tick live row caught it. Grep `FinalizeInit`/`PostLoadInit`/`SpawnSetup(respawningAfterLoad)` for resets of any field you scribe.
- **A periodic pass that acts on a pawn 'once it has arrived' misses it:** a vanilla Goto ends ON the cell and the think tree hands the pawn a new job that same tick (on sun-heat biomes `RM_JobGiver_SunEscape` dashes it away). Put the arrival action in the job's own last toil.
- **When you make a work method incremental, keep the public no-arg entry point's old complete contract;** slice only in the per-frame caller. A budgeted `Rebuild()` left scripted callers reading half-laid pieces; the fix was `Rebuild()` => `Rebuild(true)` with only frame paths calling `Rebuild(false)` (pinned by `selftest_gimmesomeslack.py sliced_rebuild_callers`).
- **A versioned snapshot accessor called with `maxAge 0` on a hot path rebuilds the whole artifact every tick** even when its version proves nothing changed (per-lay `World()` did ~100 whole-map `CordWorld` rebuilds, ~0.85 MB each, in a 300-tick wave and forced full GCs). Readers should pass the largest age their correctness allows (`World(60)`), and the census should count rebuilds (`worldBuilds`).
- **A `MapParent` that must outlive gravship visits needs `CanBeSettled=false` and an `Abandon` override:** MapGenerator hands a settleable parent to `GravshipUtility.SettleTile`, which destroys it on landing, and a launch with no grav anchor calls `Abandon`, which destroys it. A proof that generates the map via `GetOrGenerateMap` cannot see either. Landing on an EXISTING map leaves the marker unspawned until `Designator_MoveGravship` picks a spot, so `jawa/gravship_land` reports no marker; `step_game_ticks` may advance fewer ticks than asked, so poll state, never a tick total.
- **RimWorld 1.6 `GenPlace` puts one item per cell,** so a `ThingPlaceMode.Near` drop lands OUTSIDE a small radius once items such as stripped gear fill it. Code that later finds its own drop by 'within radius r of the spot' loses it: remember the Thing you dropped (`Scribe_References`) instead of searching.
