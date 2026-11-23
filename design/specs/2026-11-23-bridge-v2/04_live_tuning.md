# BRIDGE v2.0, side pass: change the running game's values without a reload ("live tuning")

Item `RIMMANDRAKE_DESIGN_BRIDGE_LIVE_TUNING_POKE_DEF_AND_CODE_VALUES_NO_RELOAD`.
This file says WHAT is possible and needed. HOW to build it is the second designer's question.
No game and no code was touched for this file. Every engine claim is marked **[read: symbol]** (read in the RimWorld 1.6
source through RimSage, or in a file on this machine) or **[guess N%]**.

## The answer

**Yes, for most tuning numbers; partly, for behaviour; no, for anything that changes which defs or types exist.**
1. A value loaded from XML can be changed in the running game by one reflection write on the live def object. Most
   tuning values (comp properties, verb and projectile numbers, hediff stages, incident chances, stats, costs) then act
   at once or after one named cache clear. This is what RIMMSqol does, and its source is on this machine.
2. A C# number can be poked when it is a mutable field. A `const` cannot, ever. Two of our three example mods are
   already pokeable today with a tool we have (`jawa/mod_settings_field`); the Pyrelands fire carry rule is not,
   because its numbers are `const`.
3. Behaviour can change a little without a restart (a switch, a formula in a prepared slot, a Harmony patch taken off).
   A rebuilt mod DLL cannot replace the loaded one.
4. A value changed live is a **tuning result**, never a result of the shipped build. The game itself carries the stamp
   that says so, on every receipt, screenshot and save.
5. The gain is largest for short scenes: seconds for each point of a sweep against about 2 minutes (small mod list) or
   many minutes (the owner's full list) for each reload. The approach is cheap to confirm: the first experiment needs no
   new code.

## Words used here

| word | what the thing does |
|---|---|
| **live write** | One write of one value into an object of the running game: a field of a def, of a def's nested object, or of a C# class. |
| **follow-up** | The named engine call (or private cache field set to null) that makes the game notice a live write. |
| **write recipe** | What we know about one kind of field: when the engine reads it (the timing class below), its follow-ups, and how to check by behaviour that the write acted. |
| **timing class** | One of five: AT ONCE, AFTER A CLEAR, NEW THINGS ONLY, LOAD ONLY, NEVER LIVE. |
| **overlay** | A named, ordered list of live writes, each with the value that was there before. The game process holds it. |
| **overlay stamp** | The overlay's name and content hash. Every receipt, screenshot and save made while an overlay is on carries it. |
| **tuning point** | A C# number that a mod declares as pokeable: a mutable static field in the mod's one tuning class. |
| **formula slot** | A place where a mod calls a replaceable function (a delegate) for one formula, with the shipped formula as its default. |
| **load-time overlay** | The same overlay written as a real XML patch in a test-only mod that loads last. It needs one restart and is as faithful as a build. |
| **absorbed** | An overlay is absorbed when a fresh game, with no overlay on, already holds every value the overlay would write. |

## How this differs from the retired `jawa/hot_reload_defs`

The retired tool called vanilla `PlayDataLoader.HotReloadDefs()`. On 2026-09-03 it hung a 589-mod game for about 5
minutes and left every pawn spawn failing with `KeyNotFoundException: 'RimWorld.HairDef'`, while every read still
answered (`infrastructure/state/items/closed/HOT_RELOAD_DEFS_BREAKS_PAWNGEN_1.md`). The exact broken index was never
named; that stays unknown.

What `HotReloadDefs` does **[read: `PlayDataLoader.HotReloadDefs`, `LoadedModManager.ParseAndProcessXML`]**: it parses
the XML of every active mod again, copies each parsed def over the existing def object (`Gen.MemberwiseShallowCopy`),
generates the implied defs again, runs about 55 static resets, resolves every def type again, points every spawned
thing's comps at new property objects, rebuilds the map meshes and closes all windows.

| | `hot_reload_defs` (retired, stays retired) | a live write (this design) |
|---|---|---|
| unit of change | every def of every mod | one field of one object |
| source of the value | the XML files on disk | the caller's value |
| def database | rebuilt and re-resolved | never touched: no def is added, removed, replaced or re-resolved |
| type-keyed indexes, short hashes, implied defs | regenerated (the place the failure sat) | never touched |
| cost | most of a cold load's def phase (5 min on 589 mods) | one field write and at most a few cache clears **[guess 90%: milliseconds]** |
| a value written by reflection | **overwritten from disk** | kept |
| undo | none | the previous value is recorded and written back |

A live write must never call `HotReloadDefs`, `DefDatabase<T>.Clear`, `ResolveAllReferences` or any "reset all" step
as a follow-up. A field that would need one is LOAD ONLY and is refused. One more reason to keep the two apart:
`HotReloadDefs` would silently erase an overlay.

## What exists today (read in `src/RimMandrake/bridgetools/JawaBench.BridgeTools/`)

| tool | what it does for live tuning | gap |
|---|---|---|
| `jawa/get_defs` | reads def fields by reflection, many per call; `deep=true` for nested objects | reads only |
| `jawa/mod_settings_field` | **reads and writes** a public static or instance field of a mod's settings class; returns `valueBefore` and `valueAfter`; refused in the CAMPAIGN profile | settings classes only; no overlay, no stamp, no guard against the settings being saved to disk |
| `jawa/static_call` | calls a public static method (enough to call most follow-ups) | no field write; public only |
| `jawa/stat_cache_bust` | clears one stat's cache, whole or for one thing (uses `TryClearCache`, with the reason why not `DeleteStatCache`) | one follow-up of many |
| `jawa/harmony_patches` | lists Harmony patches | cannot remove or add one |
| vanilla dev mode "TweakValues" window | sliders for every `[TweakValue]` static field **[read: `EditWindow_TweakValues`]** | by hand only; none of our mods uses `[TweakValue]` (grep of `src`, 0 hits) |

So: **no tool writes a def field today**, and a C# poke exists only for settings classes.

## 1. Def values: what takes effect when

The five timing classes:
- **AT ONCE**: the engine reads the def field at each use. The write is enough.
- **AFTER A CLEAR**: the engine reads through a cache. The write needs the named follow-up.
- **NEW THINGS ONLY**: the value was copied into each thing (or into a map structure) when the thing was made. Things
  made after the write have the new value. Things that exist need the named refresh, or are replaced.
- **LOAD ONLY**: the value was used once at load to build something else. A live write does nothing, or leaves the built
  thing stale. Write the built thing instead where the table says so; otherwise use the load-time overlay.
- **NEVER LIVE**: the write breaks the game's own bookkeeping.

The one fact that makes this approach work: **a comp, a hediff comp and a verb each hold a reference to the def's own
properties object, not a copy** **[read: `ThingComp.Initialize` sets `this.props = props`; `HediffWithComps.InitializeComps`;
`VerbTracker.InitVerb` sets `verb.verbProps = properties`]**. A write to `comps[..].someNumber` on the def is seen by
every existing thing of that def on its next read.

| category | field (example) | class | follow-up, or what goes wrong | evidence |
|---|---|---|---|---|
| **stats** | `ThingDef.statBases`, `StatDef.defaultBaseValue` | AFTER A CLEAR | computed from the def on each call, behind `StatWorker.immutableStatCache` (kept for ever when `StatDef.immutable`) and `temporaryStatCache`. Follow-up: `StatWorker.TryClearCache()` or `ClearCacheForThing(thing)`. Never `DeleteStatCache`. | read: `StatWorker.GetValue`, `GetBaseValueFor` |
| | abstract values (`BaseMaxHitPoints`, `BaseMarketValue`) | AT ONCE | `GetValueAbstract` has no cache | read: `StatWorker.GetValueAbstract` |
| | `MaxHitPoints` of an existing thing | AFTER A CLEAR | up to 10 ticks stale by itself; `HitPoints` of each thing is its own number and is not rescaled | read: `Thing.MaxHitPoints` |
| | `StatDef.parts`, `statFactors` (the stat's structure) | AFTER A CLEAR | `StatDef.immutable` is worked out once at load. Follow-up: `StatDef.SetImmutability()` | read: `StatDef.SetImmutability` |
| | `equippedStatOffsets`, hediff stat offsets | AFTER A CLEAR | the stat caches above; pawn capacities are dirtied only on equip: `PawnCapacitiesHandler.Notify_CapacityLevelsDirty()` | read: `StatWorker`, `Pawn_ApparelTracker` |
| **comp properties** | any number the comp reads from `Props` at use | AT ONCE | by reference | read: `ThingComp.Initialize` |
| | `CompProperties_Explosive.wickTicks` | AT ONCE for the next wick | copied when the wick is lit | read: `CompExplosive` |
| | `CompProperties_Refuelable.fuelCapacity` | AT ONCE (refuel reads it live); the START fuel is NEW THINGS ONLY | | read: `CompRefuelable.Initialize` |
| | `CompProperties_Power` consumption | NEW THINGS ONLY | `CompPowerTrader.SetUpPowerVars()` on each live comp (RIMMSqol does this) | read: `CompPowerTrader.SetUpPowerVars` |
| | `CompProperties_Glower.glowRadius` | NEW THINGS ONLY | copied into the glow grid; `CompGlower.ForceRegister(map)` | read: `GlowGrid.RegisterGlower` |
| | add or remove a comp on a def | NEW THINGS ONLY, risky | existing things keep their comp list; a save then holds things of both shapes. Refused in the first version. | read: `ThingWithComps.InitializeComps` |
| | **our own comps** | by how we wrote them | a comp of ours that copies a `Props` number into a field at spawn is NEW THINGS ONLY | rule for our code, section 2 |
| **costs and recipes** | `costList`, `costStuffCount` | AFTER A CLEAR | `CostListCalculator.Reset()` | read: `CostListCalculator.CostListAdjusted` |
| | `RecipeDef` fields (work amount, products, skill) | AT ONCE for most **[guess 75%]**; a few private caches | RIMMSqol nulls `premultipliedSmallIngredients`, `workerInt`, `isSurgeryCached` and the users' `allRecipesCached` | read: RIMMSqol `SettingsInit.cs:2325-2347` |
| | `ThingDef.recipeMaker.*` | LOAD ONLY | copied into the generated `Make_X` RecipeDef at load. **Write the generated RecipeDef instead.** | read: `RecipeDefGenerator` |
| | which recipes a bench offers (`AllRecipes`) | AFTER A CLEAR | private `ThingDef.allRecipesCached`; no method clears it; set it to null by reflection | read: `ThingDef.AllRecipes` |
| | market value from cost | AT ONCE, behind the stat caches | | read: `StatWorker_MarketValue` |
| | frame and blueprint defs | LOAD ONLY | generated at load; the frame's hit points are baked | read: `ThingDefGenerator_Buildings` |
| **verbs and projectiles** | `VerbProperties` (range, warm-up, burst) | AT ONCE | by reference | read: `VerbTracker.InitVerb` |
| | `projectile.damageAmountBase`, `explosionRadius` | AT ONCE | read at impact | read: `Projectile.DamageAmount`, `Projectile_Explosive` |
| | `projectile.speed` | AT ONCE for the next shot | a projectile in flight keeps its `ticksToImpact` | read: `Projectile.Launch` |
| | add or remove a melee `Tool` | LOAD ONLY | tool ids are given in `ThingDef.PostLoad`; RIMMSqol asks for a restart here | read: `ThingDef.PostLoad`; RIMMSqol `SettingsInit.cs:2952` |
| **hediffs** | `HediffStage` numbers, `lethalSeverity`, `hediffGivers` | AT ONCE | `Hediff.CurStage` reads the def each time | read: `Hediff.CurStage` |
| | `capMods`, `painOffset` | AFTER A CLEAR | `HediffSet.DirtyCache()` and `PawnCapacitiesHandler.Notify_CapacityLevelsDirty()` for each pawn that has the hediff | read: `HediffSet.DirtyCache` |
| | hediff comp properties | AT ONCE | by reference | read: `HediffWithComps.InitializeComps` |
| **graphics and draw size** | `graphicData.texPath`, `drawSize`, `color`, `shaderType` | AFTER A CLEAR, then per thing | private `GraphicData.cachedGraphic` (rebuilt after `CopyFrom`, or set null); then `Thing.Notify_ColorChanged()` on each spawned thing (clears the thing's graphic and dirties its map mesh); pawns: `PawnRenderer.SetAllGraphicsDirty()` | read: `GraphicData`, `Thing.Notify_ColorChanged`, `PawnRenderer` |
| | `ThingDef.uiIconPath` | LOAD ONLY | resolved once; write the `uiIcon` texture itself | read: `BuildableDef.PostLoad` |
| | `ThingDef.size` | **NEVER LIVE** while a thing of the def is spawned | the thing grid registers and deregisters by `def.size`; a change strands grid entries | read: `ThingGrid.Register` |
| | `altitudeLayer`, `drawerType` | unknown | **[guess 60%: needs `MapDrawer.RegenerateEverythingNow()`]** | not read |
| **terrain** | `fertility` | AT ONCE | only the overlay drawing caches it | read: `FertilityGrid.FertilityAt` |
| | `pathCost`, `passability` | AFTER A CLEAR, heavy | stored per cell in `PathGrid`, and copied again into the 1.6 path finder's data. `Pathing.RecalculateAllPerceivedPathCosts()` does **not** refresh that second copy; the per-cell `Pathing.RecalculatePerceivedPathCostAt(c)` does. A passability flip also needs regions rebuilt (`RegionAndRoomUpdater.RebuildAllRegionsAndRooms()`, which resets room temperatures: RIMMSqol avoids it for that reason). | read: `PathGrid`, `Pathing`, `PathFinderMapData`; RIMMSqol `SettingsInit.cs:163` |
| | `affordances` | AT ONCE | **[guess 65%]** | not read |
| **biome and weather** | `animalDensity`, `plantDensity` | AT ONCE | read at each spawner pass; `WildPlantSpawner` keeps a whole-map count | read: `Tile.AnimalDensity`, `WildPlantSpawner` |
| | `wildAnimals`, `wildPlants` commonalities | AFTER A CLEAR | private lazy caches on `BiomeDef` (`cachedAnimalCommonalities`, `cachedPlantCommonalities`, `cachedWildPlants` and three more) and on `WildPlantSpawner`; nothing clears them; set them to null by reflection | read: `BiomeDef` |
| | `baseWeatherCommonalities`, `WeatherDef` numbers | AT ONCE | read at each weather choice | read: `WeatherDecider` |
| | temperature data | AFTER A CLEAR | `TileTemperaturesComp.ClearCaches()` | read: `TileTemperaturesComp` |
| **incidents** | `baseChance`, `minRefireDays`, `earliestDay` | AT ONCE | read at each fire attempt | read: `IncidentWorker`, `StorytellerComp` |
| | storyteller comp numbers | AT ONCE | by reference; the comp list itself: `Storyteller.Notify_DefChanged()` | read: `Storyteller` |
| | any `workerClass` (incident, weather, work giver, stat) | LOAD ONLY in effect | the worker object is made once and kept in a private `workerInt` | read: `IncidentDef`, `WeatherDef`, `WorkGiverDef` |
| **AI** | a number on a `JobGiver` or other think node | AT ONCE **[guess 75%]** | the nodes are live objects built at load; address the node by its place in the tree | read: `ThinkTreeDef.ResolveReferences` |
| | the shape of a think tree (add, remove, reorder nodes) | LOAD ONLY | keys are assigned once | read: `ThinkTreeDef` |
| | `JobDef` flags | AT ONCE | | read: `Pawn_JobTracker` |
| | `JobDef.driverClass` | new jobs only | a running job keeps its driver | read: `Job.MakeDriver` |
| | work giver priority | AFTER A CLEAR | `WorkTypeDef.workGiversByPriority` rebuilt, then `Pawn_WorkSettings.Notify_UseWorkPrioritiesChanged()` on each pawn (RIMMSqol does this) | read: `Pawn_WorkSettings`; RIMMSqol |
| | `PawnKindDef.combatPower`, `RaceProperties.baseBodySize` | AT ONCE | pawns already generated keep what generation gave them | read: `Pawn.BodySize` |
| **sounds** | `SubSoundDef` numbers (volume, pitch) | next play **[guess 60%]** | resolved grains are LOAD ONLY; a running sustainer is unread | read: `SubSoundDef.ResolveReferences` |
| **UI text** | `label` | AFTER A CLEAR | `Def.ClearCachedData()` and `GenLabel.ClearCache()` | read: `Def`, `GenLabel` |
| | `description` | AFTER A CLEAR | private `ThingDef.descriptionDetailedCached`, set null | read: `ThingDef` |
| | translated text | not read | | not read |
| **identity** | `defName`, `shortHash`, the def's class, `thingClass` of spawned things, `race`/`body` structure | **NEVER LIVE** | saves, the def database and every reference hold these | read: `DefDatabase<T>`, `ShortHashGiver` |

Three things the table teaches:
1. **A write that succeeds proves nothing.** The value reads back as written while the game still acts on a cache.
   `Def.ClearCachedData()` clears only the label **[read]**, in spite of its name. Vanilla's own def editor
   (`TreeNode_Editor`) writes the field and clears nothing **[read]**.
2. **The follow-ups are a hand-kept list.** RIMMSqol has no generic rule: each def type has a hand-written routine and
   about 25 fix-ups (its `SettingsInit.cs`, 12,000 lines). It also shows a restart dialog for the cases it cannot do
   live. We should take its list of fix-ups as a starting catalogue, not its structure.
3. **Other mods add caches of their own.** RIMMSqol's author warns that Performance Fish can drop its changes (GPT,
   round 1, from the mod's page). On the owner's full list, only a check by behaviour tells whether a write acted.

## 2. C# values: what can be poked

| kind of value | poke? | why |
|---|---|---|
| mutable static field (public or private) | yes | one reflection write; the next read sees it |
| `[TweakValue]` static field | yes | the same; vanilla accepts only static, non-const, non-readonly `float`, `int`, `ushort`, `bool`, and calls a method named `<field>_Changed` after a change **[read: `EditWindow_TweakValues`]** |
| instance field | yes, when the object can be named | a comp of a thing (thing id, comp class), a map or game component, a mod's settings object, a def's nested object |
| auto-property | yes | write its backing field, or call the setter (that runs code) |
| elements of a `static readonly` array or list | yes | the reference is fixed; the contents are not |
| `const` | **no, never** | the compiler copied the number into every caller, in every assembly that used it. No field is read at run time. The tool refuses it by name (`FieldInfo.IsLiteral`). |
| `static readonly` number, flag or enum | **refuse** | the reflection write succeeds, but Unity's Mono folds such a field into the compiled code of methods that already ran (integers, booleans, enums; not floats). Methods compiled before and after the poke would then disagree. **[GPT read `method-to-ir.c` of `unity-2022.3-mbe`; the exact Mono commit of RimWorld 1.6 is unverified]** |
| a field of a struct | only by writing the whole struct back to its holder | a struct read out of a field, list or dictionary is a copy |
| a value captured by a lambda, or copied into a local of a running job or toil | no | running jobs keep what they captured; new jobs read the new value |
| a value already pushed outside managed code (a material's colour, a shader property, an audio source) | needs its own push | the write changes our copy only |

**What our own mods should do** (for new code, and for a mod when it next advances; no bar moves):
- Put each number that someone may want to tune in **one tuning class per mod**: `public static class
  RimMandrake.<Mod>.Tuning`, mutable static fields, each with `[TweakValue]` and a sensible range. Player-facing numbers
  stay in Mod Settings, as today; those are pokeable already.
- **Read the field where it is used.** Do not copy it into an instance field at spawn, unless "the value when this
  thing was made" is the meaning. Say so in a comment when it is.
- A table worked out from tuning numbers gets a `<field>_Changed()` method that works it out again.
- **A tuning number is never `const` and never `static readonly`.** `const` stays right for what must be constant:
  array sizes, switch labels, save keys, protocol numbers.
- Where a formula (not a number) is the thing to tune, give it a **formula slot** (section 3).
- Bonus: the owner gets sliders for every tuning point in the vanilla dev-mode TweakValues window, with no work from
  us. That is the hands-on tuning he had with RIMMSqol.

Cost at run time **[guess 90%]**: one memory read where there was a compiled-in number, and the compiler can no longer
fold arithmetic on it. That is nothing outside the hottest loops; in a per-cell loop, copy the field to a local before
the loop. A real cost of another kind: a mutable static can be changed by anyone, so the receipt must say what its
value was (section 5).

**Measured state of the three example mods** (read in `src/RimMandrake`, 2026-11-23):

| mod | numbers | pokeable today? |
|---|---|---|
| FlowWorks pit fall | `fallDamageMultiplier`, `fallDamagePerMetrePast2`, `fallDamageCap`: public static fields of the settings class (`RimMandrakeFlowWorksMod.cs:291-296`) | **yes**, with `jawa/mod_settings_field` |
| Explosive Knockback | `force`, `maxThrowCells`, `impactFactor`: instance fields of the settings (`RM_KnockbackMod.cs:30-34`) | **yes**, the same tool. `GoodsThrowWild`, `MaxBounces`, `PitSpread`, `RimSpread` are `const`: **no** |
| Pyrelands fire carry | `WindCarryTicks`, `WindCarryExtraTicks`, `WindCarryReach`: `public const int` (`Kernel/RM_BurnKernel.cs:520-528`) | **no**, until they become tuning points. The Python model `pyre_burn_sim.py` holds the same numbers, tied by a checksum; an export must change both. |

## 3. Behaviour, not only numbers

From least risk to most. Each rung is tried before the next.

| way | what it changes | risk | verdict |
|---|---|---|---|
| **a switch** (Mod Settings on/off, a tuning flag) | turns a feature or a branch off | none beyond section 5 | have it already, by the Mod Settings rule |
| **a formula slot**: the mod calls `Tuning.SomeFormula(args)`, a static delegate whose default is the shipped method; the bridge replaces it with a function compiled in the game from a small expression (arithmetic, `min`, `max`, `clamp`, comparisons, the arguments, named tuning points) | one formula | the expression language must stay small and typed; compiling uses `System.Linq.Expressions`, which should work on desktop Mono **[guess 85%; experiment E8]** | **build**, for the few formulas worth it |
| **a Harmony patch taken off or put on live** | whether one of our patches (or another mod's) runs | Harmony supports it at run time (Dubs Performance Analyzer does this). Three traps: a method already on the stack is not rewritten; a small method already inlined into a compiled caller may keep running the old way, so a late patch can silently not act; taking a patch off does not undo what it already did to state. | **build, narrow**: off and on for patches that already exist, with a check by behaviour. Its best use is a hunt: "is this fault our patch, or theirs?" |
| **replace method bodies in place** (the approach of Zetrith's HotSwap: same types, same fields, new body for an existing method) | code inside existing methods | cannot add a field, a type, a method or change a signature; whether it runs on 1.6 with our mods is unverified; a body compiled from source that is not the committed source is the worst kind of overlay | **experiment only** (E9); not in the first build |
| **a script evaluated in the game** (the Mono C# evaluator, or Roslyn scripting) | anything | it can do everything a mod can, with no recipe and no revert; Roslyn under RimWorld's Mono is unproven and large | **not for tuning.** If pass 1's telemetry design wants an in-game script engine, one engine can serve both; that is the second designer's call. |
| **load the rebuilt mod DLL beside the old one** | nothing useful | Mono cannot unload an assembly. The new copy's classes are different classes with the same names. Every existing comp, map component and settings object stays an object of the OLD code; statics exist twice; the old Harmony patches stay and the new copy's apply a second time; `GenTypes` does not list the new assembly and caches failed lookups **[read: `GenTypes`, `ModAssemblyHandler.ReloadAll`]**; a save names a class by text and gets whichever copy is found first. | **refuse.** A rebuilt mod needs a restart. |

So the honest limit: **numbers and prepared formulas change live; new logic needs a build.** The tuning class and the
formula slots are how a mod moves its "new logic" questions into the first group ahead of time.

## 4. XML-shaped changes on live defs

After load the XML document is gone; only the def objects remain. A normal `PatchOperation` has nothing to act on. (The
mod XML Extensions has separate "DefDatabase operations" for live use, for the same reason; GPT round 1.)

A **live patch** therefore means: translate an XML-shaped request into live writes.
1. **Address.** Accept the common xpath shape `Defs/<DefType>[defName="X"]/a/b/c` (and `li` selectors by a child's
   value, or by the element name for the classes that load by name, such as stat entries and cost entries). Map it to
   a def and a field path by the same rule the loader uses: an element name is a field name.
2. **Value.** Parse the text with the engine's own parser for that field's type, so `3~5`, `(1,2)` and a def name mean
   what they mean in XML **[guess 85%: `ParseHelper.FromString` is the entry; not read]**. A def name resolves through
   `DefDatabase` at once; a missing def is a refusal, never a null.
3. **Write, follow up, check.** The write recipe of the field decides the follow-ups and the check.
4. **A whole edited def** is handled as a difference, never as a swap: build a scratch object from the edited XML,
   compare it leaf by leaf with the live def, and turn the differences into live writes. **The live def object is never
   replaced**, because every thing, comp and list in the game points at it.

Where a live patch refuses, each by name and with the route that works:

| request | answer |
|---|---|
| a field in class LOAD ONLY or NEVER LIVE | refuse; route: the load-time overlay |
| a new def, or removing a def | refuse; other defs, short hashes and saves refer to defs by identity |
| a change of `ParentName`, `Name`, `Abstract` | refuse; inheritance was flattened at load and no parent object exists. A patch aimed at an abstract parent lists the concrete defs it would have reached, and the caller addresses those. |
| a change of a def's class, `thingClass`, `compClass`, any `workerClass` | refuse; existing objects are of the old class |
| adding or removing a comp, a tool, a think node | refuse in the first version (NEW THINGS ONLY with mixed shapes, or LOAD ONLY) |
| a field with **no write recipe yet** | write it, and mark the write **UNVERIFIED**: the receipt says the effect is not known until a check by behaviour passes. An unknown field is never reported as changed-and-acting. |

**The load-time overlay** is the second route and the faithful one: the same overlay, written as ordinary
`PatchOperation`s into a test-only mod that loads last. It costs one restart, covers every XML-shaped change
(inheritance, new defs, LOAD ONLY fields), and is exactly what a build would do. This is the "loads after anything else
so it sticks" half of RIMMSqol.

## 5. Stickiness and truth: the overlay

### What the overlay is
A file an agent writes and the game holds while it is on:
- a name (by the naming rule) and a purpose line;
- the build it was made against: assembly hashes and the mod list fingerprint, from pass 1's receipt (capability 9);
- an ordered list of entries. Each entry: the target (a def field path, or a C# type and field, or a formula slot, or a
  patch switch), the new value, the timing class from its recipe, and, filled by the game when applied, the value
  that was there before.

### Rules
1. **The game process owns the truth.** The list of live writes lives in the companion, not in the calling script. A
   script that crashes cannot leave an unknown game: one call returns "no overlay", or the overlay with every entry.
2. **Every write goes through the overlay.** There is no bare "set field" beside it (the existing
   `jawa/mod_settings_field set` joins the overlay). One write is an overlay of one entry.
3. **Apply is all-or-nothing in order.** Each entry is written, followed up, read back. If one fails, the entries
   already written are reverted, and the answer names the failed entry.
4. **Revert is exact and is checked.** Entries are undone in reverse order with their follow-ups, and each target is
   read back. A fingerprint of every touched def (all scalar leaves, taken before the first write) must be equal after
   the revert. Revert reports honestly what it cannot undo: things made while the overlay was on keep what was copied
   into them, and everything that happened in the simulation happened. After a sweep, the scene is discarded, not
   "reverted".
5. **What survives what.** Defs and C# statics belong to the process, not to the save: an overlay **stays on through a
   save load inside the same process** and is gone after a restart **[guess 90%; defs are not rebuilt on a game load]**.
   Values that a save holds for each thing come back from the save. So "re-apply after load" has two cases:
   - after a game load in the same process: check and repair (pass 1's "reassert", capability 3, includes the overlay);
   - after a restart: only when the overlay file is marked armed for this game instance. The companion then applies it
     at startup, after defs are resolved, as RIMMSqol does **[read: RIMMSqol `HarmonyBootstrap.cs:23-72`]**, and stamps
     it. A restart without an armed file starts clean. ArchBig never arms.
6. **Mod settings must not reach the disk.** A poked settings field is written to the mod's config file if anything
   calls `WriteSettings` (closing the options window does). The overlay keeps a journal file of poked settings; revert
   restores them; the companion's handshake reports an unreverted journal; and a settings file whose hash changed while
   an overlay was on is restored from the copy taken at apply.

### How every record says which overlay was on
- **Receipts.** Every scene receipt carries `overlay: none`, or the overlay stamp and the entry list with before and
  after values and each entry's state (ACTING, UNVERIFIED). This sits beside the loaded build in pass 1's capability 9.
  The game fills the field; a scene script cannot leave it out.
- **Screenshots.** While an overlay is on, the companion draws a small fixed line in a corner of the game view:
  `OVERLAY <name> <hash>`. Any capture, by any tool, and the owner's own eyes, see it. The capture's sidecar repeats it.
- **Saves.** A save written while an overlay is on gets the stamp in its file name and a sidecar file with the overlay.
  The def values themselves are not in a save, so such a save loaded in a clean game shows the SHIPPED values with
  things whose copied state came from the overlay: a mixed state that proves nothing. Such a save is a scratch save.
  It is never promoted to a keeper, a fixture or a canonical save.

### How a tuning result is kept apart from a result of the build
Three rungs, in rising order of truth and cost:

| rung | what the game runs | what a result is worth |
|---|---|---|
| 1. live overlay | shipped build + live writes | a **tuning result**: it steers the choice of a value. It decides no bar. |
| 2. load-time overlay | shipped build + a last-loading patch mod, after one restart | a **rehearsal**: faithful for XML values; still not the build. Decides no bar. |
| 3. the build | values exported into the mod's XML or C#, built, deployed, loaded | a result of the build |

- **Export.** One call turns an overlay into the change for the build: def entries as XML edits to our own def files
  (or as `PatchOperation`s when the def is not ours), C# entries as a list of `file:line, field, old, new`, formula
  slots as the expression to write as code. Settings entries become new defaults.
- **Absorbed check.** After the build is loaded with no overlay, the overlay is run in dry mode: every entry's target
  must already hold the entry's value. The call answers ABSORBED, or names the entries that differ.
- **One confirming run.** The scene runs once on the build, overlay `none`. Only that run is evidence for a bar.
- **The program enforces it.** A row of a mod's test table, a proof, a visit result or a `modcheck` record with an
  overlay stamp other than `none` cannot be recorded as PASS. Its state is TUNED, with the stamp. This is the rule of
  `rule_draft3.md` section 8 ("the record names the build that the game had loaded") made mechanical. A tuning result
  is not one of the seven run outcomes of a scene: a scene under an overlay still ends in one of the seven, and the
  stamp says what it was a run OF.

## 6. Sweeps

### The design
A sweep is one request: named parameters, their values, a scene, the measures to return.
- **Parameters**: overlay targets, each with a list or a range. The first point and the last point are always the
  shipped values (the **baseline twice**): if the two baselines differ by more than the differences between points, the
  sweep says its noise is too large to rank the points.
- **Order of points**: a full grid for one or two parameters; one parameter at a time around the baseline for more;
  halving for "where is the threshold"; a simple search on a score for "best". All are a list of points made by the
  caller's side; the game side only needs "run this list".
- **For each point**: write the point's values → follow-ups → read back → build the scene fresh (new things, because
  of class NEW THINGS ONLY) → run to the scene's end → return the receipt and the measures → clear the scene.
- **Side by side, or one after another?** A parameter that is global (a static, a def field) has one value at a time
  in the game. So points run **one after another**, each on a fresh copy of the scene. Copies of the scene side by
  side help in two cases only: the axis is a property of each copy (pit depth, distance from the blast, the stuff of a
  wall), or several random repeats of the SAME point run at once. A sweep can use both: a row of copies along the
  per-copy axis, run once for each point.
- **Randomness**: a point with a random result runs N seeds (kind B thinking: the sweep reports the spread, never one
  sample as the answer). Pass 1's `Rand` capture and snapshot restore (capability 8) are used as they are; this design
  adds nothing there.
- **What a sweep returns**: a table, one row for each point (values, measures, the scene's outcome, ticks, seconds),
  the baseline pair, and the overlay file of the chosen point, ready to export.
- **Offline first, still.** A sweep that a model can run offline runs offline: it is free and exact
  (`infrastructure/state/lessons/20261108T222103Z-BENCH-gss-geometry-offline-sweep-first.md`). The in-game sweep is
  for what the model does not hold: vanilla's own systems, other mods, pathing, real damage and armour.

### Cost for each point, against a reload
| | cost |
|---|---|
| a reload on the 13-mod list | 22 s load (measured 2026-08-19, `skills/rimworld-load-round`) + about 90 s quicktest map (root `CLAUDE.md`) + staging: about 2 minutes. A C# value adds the build and the deploy. |
| a reload on the owner's full list | many minutes |
| a live point | the write and follow-ups **[guess 90%: under 50 ms; UNMEASURED]** + staging the scene (seconds) + the scene's own ticks |

The scene's own ticks are paid either way. So the gain is about 100 to 1 for a scene of a few hundred ticks, and falls
towards 2 to 1 for a scene that must run a game day. Short scenes are where live tuning pays.

### Three worked examples
**Explosive Knockback, throw distance** (the best case).
- Parameters: `force` 0.5 to 2.0 in 7 steps × `impactFactor` 0.5, 1, 2: 21 points + 2 baselines. Both are settings
  fields: pokeable today.
- Scene: a row of five standing pawns at 1, 2, 3, 4, 5 cells from one shell (the per-copy axis); the shell detonates.
- Measures for each pawn: landing cell and distance thrown, damage taken, whether it hit a wall, flight ticks (pass 1's
  telemetry of a thing in the air).
- Cost: about 300 ticks and a restage for each point; 23 points in a few minutes **[guess 70%]**, against about 45
  minutes of reloads on the small list. The `const` numbers (`GoodsThrowWild`, `MaxBounces`) wait for tuning points.

**FlowWorks, pit fall damage.**
- Parameters: `fallDamagePerMetrePast2` × `fallDamageCap`, 4 × 4 = 16 points + 2 baselines. Static settings fields:
  pokeable today.
- Scene: pits of depth 1 to 6 side by side; one healthy pawn of fixed kind is dropped into each.
- Measures: total injury, parts hit, downed or dead, for each depth. The result for each point is a damage-by-depth
  curve.
- The bar stays a sentence ("a short fall bruises; a deep fall can kill"). The sweep picks the numbers that make the
  sentence true; the numbers are never the bar.
- Random by design (which part is hit): 5 seeds for each point.

**Pyrelands, fire carry rule** (the hard case, told honestly).
- Parameters: `WindCarryTicks`, `WindCarryExtraTicks`, `WindCarryReach`. Not pokeable today (`const`). First they
  become tuning points, and the export must also change `pyre_burn_sim.py`.
- The offline model stays the first tool for the rule's own geometry. The live sweep answers what the model takes on
  trust: vanilla fire growth on real plants, rain, the real flammability of a real map.
- Scene: a strip of ember grass 9 cells wide and 20 long, wind held on one bearing (pass 1's weather control), a fire
  lit at the upwind end. Twelve strips are built on one map; each point burns a fresh strip.
- Measures: the tick at which the front passes each fifth cell, fires seen outside the strip's lanes, whether the line
  went out.
- Cost: about 1,400 ticks for each cell, so about 28,000 ticks for each point. Here the scene's ticks dominate, and the
  gain against a reload is small for each point. The real gain is a different one: twelve points in one game with no
  rebuild and no restart between them, unattended.

## 7. Dangers and guards

| danger | what it does | guard |
|---|---|---|
| **A tuning result counted as a result of the build** (the worst one) | a mod passes on values that are not in it | the stamp is filled by the game; a stamped row cannot be PASS; export, the absorbed check and one confirming run (section 5) |
| **The write "took" but the game acts on a cache** | the test lies: a sweep shows no effect, or the old effect | write recipes; a field without one is UNVERIFIED; a check by behaviour for each recipe; the baseline twice |
| **An overlay left on** | every later scene in that process runs on wrong values | the game owns the overlay; every receipt shows it; the on-screen line; pass 1's reassert includes "overlay is what the scene declares"; a scene that declares no overlay refuses to start while one is on |
| **Poked settings saved to the config file** | the values survive a restart silently, on that game | the journal, the hash check and the restore (section 5, rule 6) |
| **A save written under an overlay** | a mixed state that looks like a normal save | stamped file name and sidecar; never promoted; autosave is off in the calm test environment (pass 1) |
| **A write to identity or structure** (`size`, `defName`, classes, comps added) | stranded grid entries, broken references, a save that will not load | class NEVER LIVE is refused by name; structural changes are refused in the first version |
| **A full rebuild used as a follow-up** | the 2026-09-03 failure again | no follow-up may call `HotReloadDefs`, a database clear or a resolve-all; `DeleteStatCache` is banned by name |
| **A value out of range** (a zero divisor, a negative radius, a huge loop count) | exceptions each tick, or a hang | the recipe or the `[TweakValue]` range bounds the value; pass 1's first-exception capture ends the point and reverts |
| **A late Harmony patch that does not act** (inlined caller) | the test lies | a call counter proves the patch runs, or that it stopped |
| **A poke of `const` or `static readonly`** | no effect, or two answers in one game | refused by name |
| **Two agents, one game** | one changes values under the other's scene | the overlay belongs to the bridge holder of that game (the driver lock); a second holder cannot apply |
| **Another mod's cache** (Performance Fish and the like) | writes dropped on the full list | results from the small list are confirmed on the list they are claimed for; check by behaviour |
| **Drift of the sweep's own environment** | points are not comparable | the baseline twice; fresh scene for each point; pass 1's calm environment |

**The owner's game (ArchBig) and his saves. This tool must never:**
- apply an overlay on ArchBig by any agent's own decision. Live writes are denied in the CAMPAIGN profile, as
  `jawa/mod_settings_field set` is today. His OWNER hold and `./pipe off game:ArchBig` bind as for all work;
- arm an overlay to be applied again at startup on ArchBig;
- write a mod settings file, `ModsConfig.xml` or any file in his Config folder;
- save over, or write a stamped save beside, a canonical save, or run while a canonical save is loaded;
- leave an overlay on when the holder releases the game: release reverts, checks, and reports.

When **he** wants to tune by hand on his game, as he did with RIMMSqol, that is his act: the tuning points show as
sliders in the dev-mode TweakValues window, and an overlay applied on his word shows its line on his screen.

## 8. Experiments (designed, not run)

All on ArchSmall or a SteveDesktop game, small mod list, test profile, a scratch map. Each ends with the game reverted
or closed. E1 and E2 need no new code.

| # | the poke | expected | a failure would mean |
|---|---|---|---|
| **E1** | `jawa/mod_settings_field set` FlowWorks `fallDamageMultiplier` 1 → 2; drop the same pawn kind into the same pit before and after; set it back | injury about doubles; back to the first value after the reset; the mod's config file hash is unchanged throughout | the settings are copied somewhere at load (then our own mods need the tuning-class rule first); or the config file changed (then rule 6 is needed before anything else) |
| **E2** | the same tool, Knockback `force` at 5 values, one blast each on a fresh pawn at 3 cells; time the whole loop | thrown distance rises with `force`; seconds for each point | no change: the value is copied into the plan at load. The timing: the real cost of a point, to put beside the 2 minutes of a reload |
| **E3** | (needs a first def-field write tool, test profile only) write `comps[CompProperties_Explosive].explosiveRadius` of a vanilla shell def; detonate a shell that was spawned BEFORE the write | the blast has the new radius | comps do not read by reference as read in the source: the central claim of section 1 is wrong, and most writes become NEW THINGS ONLY |
| **E4** | write `statBases[MaxHitPoints]` of a wall def; read `MaxHitPoints` of an existing wall at once, after 15 ticks, and after `stat_cache_bust` | old or new at once; new within 10 ticks or after the clear | the stat is cached for ever (immutable): the recipe needs the clear always. Either answer fixes the recipe. |
| **E5** | after E3 and E4 (about ten writes): spawn a colonist and a muffalo; revert all; compare the touched defs' fingerprints with the ones taken before; spawn again | both spawns succeed; fingerprints equal | a spawn failure is the 2026-09-03 symptom: stop, the approach is unsafe as designed. A fingerprint difference: revert is not exact. |
| **E6** | negative controls in a test class in the companion: poke a `static readonly int` after the method that reads it has run; ask the tool to poke a `const` | the `const` is refused by name; the readonly poke reads back new while the method still returns the old value | if the method returns the new value, Mono 1.6 does not fold it, and the refusal can soften to a warning |
| **E7** | write a `BiomeDef` wild animal commonality on a map of that biome; read the spawner's choice weights before and after setting the private caches to null | no change before the clear; the new weights after | a change with no clear: the cache table is wrong for 1.6; trust the table less and check by behaviour more |
| **E8** | in the companion, compile `(depth, cap) => min(cap, 0.5 * (depth - 2))` with `System.Linq.Expressions` and call it 1,000 times | right answers; time for each call near a normal delegate | no formula slots by this route; fall back to tuning numbers only, or a hand-written interpreter |
| **E9** | take one of our own Harmony prefixes off with `Harmony.Unpatch`, count its calls over 600 ticks, put it back, count again | zero calls while off; calls return | calls continue while "off": an inlined or cached caller; live patch switching cannot be trusted for that method |
| **E10** | repeat E3 and E4 on a game with a large mod list (SteveDesktop, or ArchBig on his word) | the same results | another mod caches the value: name the mod; results from the small list do not carry to the full list for that field |
| **E11** | export the E1/E2 overlay as a load-time patch mod and as new defaults; restart; run the absorbed check | ABSORBED | the export does not write what the live write wrote: the path from tuning to build is broken |

The first three (E1, E2, E3) answer the owner's question for our own mods, for the cost of a point, and for defs.

## Three shapes, and the pick

| shape | what it is | buys | costs |
|---|---|---|---|
| **A. A reflection read/write tool with a follow-up list** | two generic calls (read, write) on any def path or C# field, plus a catalogue of write recipes; the calling script keeps track of what it changed | smallest build; reaches everything on day one | the truth lives in the script: a crashed script leaves an unknown game; nothing forces the stamp; every caller must remember the follow-ups |
| **B. A declarative overlay that the game holds** | the caller sends a named overlay file; the companion applies it entry by entry with recipes, keeps the before values, stamps receipts, screenshots and saves, reverts exactly, exports | the truth rules of section 5 hold by construction; sweeps are lists of overlays; the owner can read an overlay file | more to build; a field with no recipe needs the UNVERIFIED route; structural changes are out |
| **C. A script engine in the game** | the caller sends C# (or another language) that runs in the game | reaches everything, including behaviour and telemetry | no recipe, no revert, no stamp of WHAT changed; the largest ways to corrupt a game; Roslyn on RimWorld's Mono is unproven |

**The pick: B, built on A's two primitives, with our own mods made pokeable by design; C is left out of tuning.**
- A's write primitive exists only inside B (every write is an overlay entry). That keeps A's reach and removes its
  flaw.
- The write recipes start from the table in section 1 and RIMMSqol's fix-ups, and grow by experiment. A field without
  a recipe is usable at once, as UNVERIFIED.
- For C# values, the tuning class and the formula slots do most of the work at almost no build cost, and give the
  owner his sliders.
- The load-time overlay covers what a live write cannot, at the price of one restart.
- Order of building, by value for effort: (1) join `jawa/mod_settings_field` to an overlay with stamp, journal and
  revert (our settings are pokeable today); (2) def-field writes with the first recipes; (3) the sweep runner on pass
  1's atomic scene; (4) export and the absorbed check; (5) tuning classes in the mods as each advances; (6) formula
  slots and patch switching; (7) the load-time overlay.

## What GPT changed

Round 1 (web facts, `gpt_consult.py`, 2026-11-23; the answer is in agent scratch, not in the repo):
- **Taken**: Unity's Mono folds initialized `static readonly` integers, booleans and enums into compiled code, and not
  floats (it cited the JIT source). This made "refuse `static readonly`" a rule and E6 an experiment.
- **Taken**: HotSwap-style method replacement keeps types and layout and cannot add fields, methods or types; loading
  a second copy of an assembly doubles statics and patches. This set the last two rows of section 3.
- **Taken**: Performance Fish can drop RIMMSqol's changes. This made E10 and the "another mod's cache" danger.
- **Taken**: its ranked risks; "a successful reflection write does not prove the simulation uses the new value" is
  the centre of section 1.
- **Rejected**: RuntimeUnityEditor and UnityExplorer as a base. They are hand tools with no recipe, stamp or revert,
  and their fit with RimWorld 1.6 is unverified.
- **Not relied on**: its account of RIMMSqol's internals (it could not verify them). The RIMMSqol facts here come from
  the mod's source on this machine.

Round 2 (skeptical review of this file): see the end of this section once it has run.

## What is guessed, not read

- Every row marked **[guess]** in the tables: `RecipeDef` field timing, think-node fields, `affordances`,
  `altitudeLayer`/`drawerType`, sound numbers, the name of the engine's value parser.
- That defs and statics stay as written across a game load in one process.
- All costs in time for a live point (UNMEASURED; E2 measures the first).
- That `System.Linq.Expressions` compiles under RimWorld's Mono (E8).
- The Mono facts about `static readonly` come from GPT's reading of Unity's Mono source, not from RimWorld's shipped
  runtime (E6).
- Not read at all: translated text and def injection, running sound sustainers, `ResearchProjectDef`, `DamageDef`, the
  melee `Tool` damage path, `injuryProps`, `DebugSettings`.
- The cause of the 2026-09-03 hot-reload failure is still unknown; this design avoids the whole act and does not
  explain the failure.
- RIMMSqol's line numbers were read by a Sonnet helper from the mod's source; the engine symbols by two Opus helpers
  through RimSage. I did not re-read each symbol myself.
