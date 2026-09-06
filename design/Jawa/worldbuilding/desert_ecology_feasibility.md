# Desert ecology — engine feasibility

**Status: RESEARCH ONLY. Nothing here is built, filed or committed as work.**
Capability investigation for a desert biome where shade is scattered patches and open
ground is lethal. Answers what RimWorld 1.6 + Odyssey can express natively, what needs
C#, and what the engine will not do at all.

Researched 2026-09-05 against the decompiled 1.6 source via RimSage. Every conclusion
below cites the class or def it came from — where a citation is absent, treat the claim
as unverified.

---

## 1. Verdict table

| # | Behaviour | Verdict | The load-bearing fact |
|---|---|---|---|
| 1 | Creatures prefer/seek shade | **C# NEEDED** (small) | Vanilla ships `JobGiver_WanderInRoofedCellsInPen` and an `insertTag` splice point — the pattern exists, the shade grid does not |
| 2 | Predator burst out of shadow, then retreat | **C# NEEDED** (small) | `GhoulFrenzy` is vanilla's own burst-speed hediff; the burst *trigger* is a JobDriver calling `AddHediff`, the standard idiom |
| 3 | Herbivore poor sprint / good endurance | **NATIVE** | Pure stat + hediff authoring — asymmetry is just different numbers on the same machinery as #2 |
| 4 | Movement/heat budget hediff | **NATIVE** for the hediff shape; **C# NEEDED** for a movement trigger | `HediffComp_SeverityPerDay` takes a negative rate; no vanilla hook fires on traversal |
| 5 | Megafauna absorb heat crossing, radiate in shade | **C# NEEDED**, and *not* via real temperature | Outdoor temperature is **one float for the whole map**. Per-cell temperature variation is structurally impossible |
| 6 | Filter-feeding through sand | **C# NEEDED** | `FoodTypeFlags` has no terrain member and every food path resolves to a `Thing` with an `ingestible` comp |
| 7 | Sand burrowing | **C# NEEDED** | No creature tunnels in vanilla, but `PawnFlyer` already fakes exactly this shape and Anomaly already reuses it |

**Nothing on this list is impossible.** One thing is impossible *the way you'd expect it
to work* — see §2 and §6.

---

## 2. The one hard wall: there is no spatial variation outdoors

Two separate systems, same answer, and both matter to this design.

### Light does not vary spatially outdoors

`Verse/GlowGrid.cs`, `GroundGlowAt`:

```csharp
if (!ignoreSky && !map.roofGrid.Roofed(c)) {
    num = map.skyManager.CurSkyGlow;   // whole-map scalar, identical in every unroofed cell
    if (num >= 1f) return num;
}
Color32 accumulatedGlowAt = GetAccumulatedGlowAt(c, ignoreCavePlants);  // ARTIFICIAL light only
```

- `SkyManager.CurSkyGlow` is a single float per map, recomputed once per tick from
  weather/time-of-day. No spatial parameter anywhere in its computation.
- The only per-cell term, `accumulatedGlow`, is fed **exclusively** by `CompGlower`
  (lamps, torches) and glow-emitting terrain (`TerrainDef.glowRadius`/`glowColor`).
  That is emission, not occlusion.
- `PsychGlowAt` just wraps `GroundGlowAt`.
- **Trees and walls cast no shadow.** Searched `Plant.cs` and `Building.cs` for
  occlusion logic affecting glow: no hits. A tree does not darken the cell beside it.
- `TerrainDef` can *emit* light. It has no field to reduce or shade it.

The only per-cell light distinction that exists is the **binary** `RoofGrid.Roofed(c)`
(`Verse/RoofGrid.cs:70`) — and it does not distinguish constructed roof from overhead
mountain, both just set the bit.

> 🔴 **Consequence for the design:** "shade" cannot be read off `glowGrid`. Querying
> `GameGlowAt` in an open desert returns the same number in the shadow of a rock as in
> the middle of the flats. Shade must be a **thing we compute and store ourselves**.

### Temperature does not vary spatially outdoors either

`Verse/GenTemperature.cs` `TryGetDirectAirTemperatureForCell` resolves to
`c.GetRoom(map).Temperature`. `Verse/RoomTempTracker.cs:63,181` sets
`Temperature = map.mapTemperature.OutdoorTemp` for every room where
`Room.UsesOutdoorTemperature` is true — and `Verse/Room.cs:99` makes that true for any
room under 25% roof coverage (`UseOutdoorTemperatureUnroofedFraction = 0.25f`).

The entire open map is **one logical room reading one float**
(`MapTemperature.OutdoorTemp`, itself derived from a per-*world-tile* seasonal curve in
`RimWorld/Planet/TileTemperaturesComp.cs`). Even the game-condition offset
(`GameConditionManager.AggregateTemperatureOffset()`) is map-wide.

> 🔴 **Per-cell outdoor temperature variation is NOT POSSIBLE** through the existing
> systems. The engine's granularity floor is the Room, and outdoors is one Room. A
> "hot open ground / cool shade" *temperature* gradient cannot be built by setting
> temperatures. It has to be modelled on the **pawn**, not on the map.

That is the single most important line in this document. Design around it now rather
than discovering it three weeks in.

---

## 3. Shade preference — the cheapest credible route

**Verdict: C# NEEDED, but small — one JobGiver subclass plus one additive XML def. No
Harmony, no think-tree replacement, no patch into vanilla XML.**

Three facts make this cheap:

1. **Vanilla already has a shade-seeking JobGiver in all but name.**
   `Verse/AI/JobGiver_WanderInRoofedCellsInPen.cs` overrides `GetExactWanderDest` and
   sets `wanderDestValidator = (pawn, cell, root) => cell.Roofed(pawn.Map)`, then calls
   `RCellFinder.RandomWanderDestFor(...)`. It is wired into the vanilla `Animal` tree
   under `ThinkNode_ConditionalRoamer`, gated on
   `GameConditionDef.pennedAnimalsSeekShelter` (heat waves). The exact behaviour we want
   already ships — it is just conditional on a game condition and keyed to `Roofed`
   rather than a shade grid.

2. **`JobGiver_Wander` takes an arbitrary cell filter.** The base class
   (`Verse/AI/JobGiver_Wander.cs`) accepts `wanderDestValidator` as a
   `Func<Pawn,IntVec3,IntVec3,bool>`. Arbitrary cell scoring is a first-class extension
   point. It is not reachable from XML only because delegates cannot be set from XML.

3. **Insertion into the vanilla animal tree is additive, not a patch.**
   `Verse/AI/ThinkNode_SubtreesByTag.cs` scans `DefDatabase<ThinkTreeDef>.AllDefs` for
   any tree whose `insertTag` matches, ordered by `insertPriority`, and splices its
   `thinkRoot` in. The vanilla `Animal` tree already carries `Animal_PreMain` and
   `Animal_PreWander` hooks (`Insect.xml` uses `Insect_PreMain` this way). We add a
   **new** `ThinkTreeDef` with `insertTag = Animal_PreWander`. Vanilla `Animal.xml` is
   never touched, and the per-pawn `DeepCopy` semantics stay intact.

**Route:**
- A `MapComponent` precomputes a per-cell shade value on map load and on roof/plant/
  building dirty events, from `RoofGrid` plus adjacency to high-`fillPercent` buildings,
  rock, and large plants. Store as a `ByteGrid`/`float[]`; expose `ShadeAt(IntVec3)`.
  **Do not route it through `GlowGrid` — `GlowGrid` structurally cannot see it.**
- One `JobGiver_Wander` subclass, near-identical to `JobGiver_WanderInRoofedCellsInPen`,
  whose validator scores on `ShadeAt` instead of `Roofed`.
- One new `ThinkTreeDef` with `insertTag`, `MayRequire` our packageId.

Rejected: Harmony-patching `TryGiveJob` on an existing JobGiver (fights the cloned
per-pawn tree, duplicates logic the tag hook already serves); a full custom
`thinkTreeMain` (a replacement, not an overlay — it would have to reproduce all vanilla
animal behaviour).

Vanilla's `JobGiver_SeekSafeTemperature` is worth reading as precedent for
condition-scored region search (`RegionTraverser.BreadthFirstTraverse` to the nearest
region whose `Room.Temperature` is in range) but is not directly reusable: it only fires
when `requiresInjury` and the pawn already carries a temperature hediff. It is an
emergency reaction, not a preference. And per §2, every outdoor region returns the same
temperature, so it would find nothing.

---

## 4. Burst-then-recover — the cheapest credible route

**Verdict: NATIVE hediff shape; the trigger is one JobDriver line, already the vanilla
idiom.**

Everything the burst/crash curve needs exists in XML:

- `Verse/HediffStage.cs` has `statOffsets` and `statFactors` (both
  `List<StatModifier>`), `minSeverity` to key a stage to a severity range,
  `statOffsetsBySeverity`/`statFactorsBySeverity` for continuous scaling, and `capMods`
  for the `Moving` capacity. `MoveSpeed` is a legal target.
- `HediffComp_SeverityPerDay.SeverityChangePerDay()` returns
  `severityPerDay * stage.severityGainFactor` and **`severityPerDay` may be negative** —
  vanilla's own drug highs do exactly this (`GoJuiceHigh` at `-0.75`/day, `WakeUpHigh`
  at `-1.5`/day). `Hediff.ShouldRemove => Severity <= 0f` (`Verse/Hediff.cs:177`), so a
  decaying hediff cleans itself up.
- **Vanilla ships the multi-stage severity-keyed MoveSpeed ramp**: Anomaly's
  `AwokenCorpse` (`Defs/Anomaly/HediffDefs/Hediffs_Global_Misc.xml`) has six stages
  keyed by `minSeverity` (0, 0.166, 0.333, 0.5, 0.666, 0.833), each with a different
  `statFactors/MoveSpeed` from 0.5× to 3×, driven by `HediffCompProperties_SeverityPerSecond`.
  That one ramps up; ours is the mirror — high-severity burst stage decaying down through
  a penalty stage.
- **Vanilla ships a burst-speed hediff outright**: Anomaly's `GhoulFrenzy` —
  `statOffsets/MoveSpeed = 4`, `statFactors/MeleeCooldownFactor = 0.7`, expiring via
  `HediffCompProperties_Disappears`. It has no crash stage (it simply expires), but
  adding one is either a second `minSeverity`-gated penalty stage on the same hediff
  decayed by `severityPerDay`, or `HediffComp_Disappears.CompPostPostRemoved()` applying
  a separate fatigue hediff.

**The trigger is the only C#, and it is one line.** There is no vanilla hook that adds a
hediff in response to a pawn *traversing cells* — nothing on `Pawn_PathFollower` or any
JobDriver does this. `GhoulFrenzy` is fired as an `AbilityDef`
(`CompAbilityEffect_GiveHediff.ApplyInner()` → `target.health.AddHediff(hediff)`,
`aiCanUse=true`, `cooldownTicksRange=1800`). The predator's burst-attack JobDriver
calling `pawn.health.AddHediff(...)` at job start is the same shape and is the natural
answer — **not** a generic on-move tick hook, which would be both expensive and
un-vanilla.

Herbivore asymmetry (#3) is then free: same machinery, inverted numbers — low
`statOffsets/MoveSpeed` on the burst, shallow or absent crash stage, longer duration.
That one is **NATIVE**, pure def authoring.

---

## 5. Heat carried across a crossing — the cheapest credible route

**Verdict: C# NEEDED, and it must be modelled on the pawn. Per §2, real per-cell
temperature is off the table.**

The good news is vanilla already ships the *accumulator with hysteresis* pattern, and it
is not the binary threshold you might assume. `Verse/HediffGiver_Heat.cs`
`OnIntervalPassed`: when `ambientTemperature > SafeTemperatureRange().max`, severity
added per interval is
`TemperatureOverageAdjustmentCurve.Evaluate(overage) * 6.45E-05f`, floored at
`0.000375f` (constants `HeatstrokeGrowthPerDegreeOver` and
`MinHeatstrokeProgressPerInterval`, `Verse/HealthTuning.cs:80,82`). Crucially it also
**decays** — `firstHediffOfDef.Severity -= value` — once ambient drops back under the
comfortable max.

That is precisely the megafauna curve: rises while exposed, falls while sheltered. What
it lacks is any memory of *where* the pawn has been, because it reads
`pawn.AmbientTemperature`, which per §2 is the same number everywhere outdoors.

Searched for an existing thermal-load-on-a-Thing accumulator: `CompTempControl`,
`Pawn_HealthTracker`, `ImmunityHandler` — **nothing** tracks accumulated heat on a pawn
independent of instantaneous ambient temperature. `CompTempControl` only pushes heat
into the room's air pool via `GenTemperature.PushHeat`; there is no pawn analogue.

**Route:** a custom `HediffComp` (or a `HediffGiver` subclass modelled directly on
`HediffGiver_Heat`) whose per-interval severity delta is driven **not** by
`pawn.AmbientTemperature` but by the same `MapComponent.ShadeAt(pawn.Position)` grid
built for §3. Severity rises while the pawn stands on unshaded cells, falls while it
stands in shade. Reuse the `SimpleCurve` shape and interval cadence from
`HediffGiver_Heat` — it is calibrated and shipped.

Note this makes §3 and §5 share one piece of infrastructure. **The shade grid is the
keystone of the whole design.** Build it once, well, and behaviours 1, 2, 4 and 5 all
hang off it.

---

## 6. Filter-feeding through sand

**Verdict: C# NEEDED. `FoodTypeFlags` cannot express it and no vanilla precedent exists.**

`RimWorld/FoodTypeFlags.cs` is a `[Flags]` enum with members `VegetableOrFruit, Meat,
Fluid, Corpse, Seed, AnimalProduct, Plant, Tree, Meal, Processed, Liquor, Kibble` plus
composite masks (`VegetarianAnimal`, `CarnivoreAnimal`, `OmnivoreAnimal`,
`DendrovoreAnimal`, `OvivoreAnimal`, …). **There is no terrain, mineral or sand member,
and the flags are a fixed enum — a mod cannot add one.**

Every match is Thing-vs-Thing. `FoodUtility.cs:443` builds a `ThingRequest` from
`ThingRequestGroup.FoodSource` gated by the eater's `foodType` mask; lines 1178 and 1500
compare `source.ingestible.foodType` bit-for-bit. Every consumer resolves to a scannable
`Thing` with an `ingestible` comp. Never a `TerrainDef`.

Two corrections to common assumptions, worth recording:

- **There is no `GrazeUtility` and no `JobDriver_Graze` in 1.6.** Both searches returned
  zero. On a real map, herbivores eat actual wild `Plant` Things through the ordinary
  `FoodUtility`/`JobGiver_GetFood`/`JobDriver_Ingest` pipeline, same as anything else.
- "Grazing" as a named system is the **virtual-plants** abstraction
  (`RimWorld/Planet/VirtualPlantsUtility.cs`, `BiomeDef.hasVirtualPlants`,
  `Caravan_NeedsTracker.cs:172` calling `EatVirtualPlants`) — a *world-tile* mechanic for
  caravans, with no map-level job behind it at all.

**Route:** a custom `JobDriver` that needs no target `Thing` — it checks
`pawn.Position.GetTerrain(map)` against an allowed `TerrainDef` set and ticks nutrition
straight into `pawn.needs.food.CurLevel` (or via a feeding hediff), bypassing
`FoodTypeFlags`/`FoodUtility` entirely. A `JobGiver` fires it when the pawn is hungry and
standing on qualifying terrain. The creature's declared `foodType` then becomes cosmetic
for this path — set it to something sane so unrelated systems do not misbehave, but the
sand feeding does not go through it.

---

## 7. Sand burrowing

**Verdict: the visual illusion is NATIVE today, already shipped in an installed mod.
True sub-terrain pathfinding is C# NEEDED, and the plumbing for it exists — Anomaly
already reuses the relevant pattern for exactly this visual.**

**Installed-mod precedent found: Alpha Animals' Sand Prowler (`AA_SandProwler`,
`Races_SandProwler.xml`) already does the "burrows in sand" illusion with zero C#.** It
uses the Vanilla Expanded Framework component `VEF.AnimalBehaviours.
CompProperties_GraphicByTerrain`: while the pawn stands on a listed terrain (`Sand`,
`SoftSand`, and several modded sand terrains), the comp swaps its graphic to a `_Hidden`
suffix variant and applies hediff `AA_BurrowingUnderSand` (a flat `+0.75`
`ArmorRating_Blunt`/`ArmorRating_Sharp` bonus while active). This is a **re-skin, not
real locomotion** — the pawn never leaves the surface pathing layer, it just looks and
fights as if submerged. For "the ambush predator looks buried until it strikes," this is
the cheapest possible route and it is pure XML riding an already-installed framework
component — no new DLL required for that variant of the behaviour.

**True "moves under terrain, pathfinds, and surfaces elsewhere" locomotion has no
vanilla or installed-mod precedent.** Checked and ruled out: `Mech_Tunneler` (Biotech) is
a normal surface-walking pawn with the `Mining` worktype — it digs through rock via
mining jobs, not by moving beneath open terrain. `PitBurrow` (Anomaly) and VFE
Insectoids 2's `Buildings_Burrows.xml` are static spawner buildings, not mobile-creature
locomotion. For that, the closest existing plumbing is `RimWorld/PawnFlyer.cs`:
`MakeFlyer()` **DeSpawns** the pawn into an inner
`ThingOwner<Thing>` (untargetable, invisible, off the map surface), ticks a transit
timer, then `RespawnPawn()` puts it back at `destCell` with `LandingEffects()`.

**Anomaly already uses this to fake erupting from the ground.** `RimWorld/PitBurrow.cs`
`FlushSpawnQueue` spawns Fingerspike fleshbeasts via
`PawnFlyer.MakeFlyer(ThingDefOf.PawnFlyer_Stun, ...)` starting from a point below and
behind the pit (`randomCell.ToVector3() + Vector3(0,0,-1)`). That is the burrow-surface
motion, built out of DeSpawn → invisible transit → land, with no terrain traversal at
all.

Checked and ruled out as precedent: `GenStep_UndercaveInterest`/`PitGate`/
`UndercaveMapComponent` build a separate pocket map (`BiomeDefOf.Undercave`) reached by a
map transition — not sub-terrain movement. Insectoid hives are static spawns with no
tunnel-in. Chimeras, Sightstealers and Metalhorrors move on the surface (Sightstealer
invisibility is `HediffDefOf.HoraxianInvisibility`, not burrowing). Odyssey added no
underground mechanic — its new content is orbital/vacuum.

**Route:** copy the `PawnFlyer` DeSpawn/hold/respawn pattern into a small custom Thing:
dig-in DeSpawns the pawn and drops a dust effecter and optionally a marker, hold N ticks
(optionally moving the destination during transit, which is the actual "burrowing"),
then `GenSpawn.Spawn` at the resurface cell with landing dust. Gate on
`TerrainDef` being sand.

---

## 8. What the engine will simply not do

Design around these. Do not go looking for a flag.

1. **Outdoor light does not vary by position.** `SkyManager.CurSkyGlow` is one float for
   the map; the per-cell glow term is artificial light sources only. Nothing casts a
   shadow. A shade grid must be ours.
2. **Outdoor temperature does not vary by position.** The whole open map is one Room
   reading `MapTemperature.OutdoorTemp`. There is no hook to give individual outdoor
   cells distinct ambient temperatures — `TryGetDirectAirTemperatureForCell` structurally
   returns `cell.GetRoom(map).Temperature`. "Hot sun, cool shade" must be modelled as
   pawn state, never as map temperature.
3. **`FoodTypeFlags` is a closed enum with no terrain member.** Terrain feeding cannot be
   expressed as a food type; it must bypass `FoodUtility`.
4. **No hediff fires on movement.** There is no traversal hook. Bursts are triggered by
   the job that performs them.

## 9. What already exists in the installed mod set

Searched Alpha Animals, Alpha Biomes, VFE Insectoids 2, Anomaly, Odyssey, and the full
601-mod active list for existing implementations of the four headline behaviours, before
assuming any of this needs to be built from scratch.

- **Shade-seeking AI: nothing beyond vanilla.** Targeted search for
  `SeekShade`/`PreferDark`/`prefersDark`/`seeksShade`/`avoidsSun`/`SeekRoof` across every
  active mod's `Defs/` returned zero hits. Alpha Animals rides Vanilla Expanded
  Framework's `VEF.AnimalBehaviours` almost entirely (32 distinct `CompProperties_*`
  classes catalogued: `DigWhenHungry`, `GraphicByTerrain`, `MakeOtherPawnsFlee`,
  `AutoNutrition`, `TerrainChanger`, etc.) — none is a shade/cell-preference JobGiver.
  Vanilla's heat-wave-only `JobGiver_WanderInRoofedCellsInPen` (§3) remains the closest
  thing installed.
- **Heat-budget / stamina movement system: none installed, and the obvious candidate
  isn't in the mod list.** Combat Extended is **not active** — zero matches for
  "combatextended"/"Combat Extended" in the live `ModsConfig.xml`'s 601 mods (mods that
  mention it in their About.xml, e.g. Pick Up And Haul, are unrelated compat flavor
  text). A broad `stamina`/`sprint`/`fatigue` sweep across all installed `Defs/` found
  exactly one incidental hit — flavor text in an RPG-perk mod's tooltip, not a mechanic.
- **Burst-speed-with-recovery outside Anomaly: none found.** Targeted search for
  `chargespeed`/`rushattack`/`burstspeed`/`adrenalinerush`/`ambushspeed`/`pouncespeed`/
  `HuntingRush` across all installed `Defs/` returned zero hits. Anomaly's `GhoulFrenzy`
  and `AwokenCorpse` (§4) are the only shipped precedent in the whole install.
- **Sand burrowing: real precedent exists, see §7.** Alpha Animals' Sand Prowler
  (`AA_SandProwler`) already fakes burrowing via VEF's `CompProperties_GraphicByTerrain`
  + a hediff, pure XML, no DLL. A related-but-different VEF comp,
  `CompProperties_DigWhenHungry` (used on Alpha Animals' Frostmite/Dark Vandal, fields
  `isFrostmite`/`spawnForbidden`/`digAnywayEveryXTicks`), looks like a dig-to-forage/
  spawn-resource trigger rather than locomotion-burrowing — worth a second look if the
  burrow behaviour wants a foraging analogue, but not verified further here.

**Bottom line: of the seven behaviours, only sand burrowing has a reusable installed-mod
shortcut (Sand Prowler's re-skin illusion).** The other three headline mechanics
(shade-seeking, heat-budget movement, burst-speed-recovery) would be original C# work —
small, and built on vanilla-native patterns (§3, §4, §5), but original. Nobody has
already solved this in the current mod stack.

## 10. Where the cost actually is

The three behaviours that matter reduce to a small amount of C#, and two of them share
their infrastructure:

| Piece | Serves | Size |
|---|---|---|
| `MapComponent` shade grid + `ShadeAt(IntVec3)` | #1, #2, #4, #5 | The real work. Dirty-event handling is the fiddly part |
| `JobGiver_Wander` subclass + additive `ThinkTreeDef` (`insertTag`) | #1 | Small — a near-copy of a vanilla class |
| Burst/crash `HediffDef` (staged, negative `severityPerDay`) | #2, #3, #4 | Pure XML |
| Burst-attack `JobDriver` calling `AddHediff` | #2 | One line inside an otherwise ordinary JobDriver |
| `HediffComp` heat-load driven by `ShadeAt`, modelled on `HediffGiver_Heat` | #5 | Small once the grid exists |
| Terrain-feeding `JobDriver` + `JobGiver` | #6 | Self-contained |
| `PawnFlyer`-pattern burrow Thing | #7 | Self-contained; copy `PitBurrow`'s usage |

