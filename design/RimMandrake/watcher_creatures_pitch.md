# Watcher creatures — the full pitch (WATCHER_CREATURES_MOD_1)

Status: the shape is RULED (owner, question cards 2026-10-08). One question remains open: how
the Rust Cathedral's camera-stalk head turns (§4, feasibility in §5). The kit carries the full
optional cue set (§1.3).
No roster is edited by this item: each member is admitted or cut at its own biome's sitting.

## 0. What this doc is

This is the pitch the item's second criterion asks for: the kit mechanism, the Q9 terrain-look
answer, and a per-biome member list in which every member names **one medium**. It brings
together two earlier docs, which stay as provenance:

- `design/RimMandrake/watchers_mod_pitch_2026-09-30.md`: the first pitch (29 rows). Its Q1–Q3
  were ruled 2026-09-30 and its Q9 was answered by the owner typing.
- `design/RimMandrake/watcher_creatures_kit_design_2026-10-02.md`: the kit design and the piinnok.
  Its Q1–Q4 were ruled 2026-10-03.

**The owner's 2026-10-08 rulings (question card, typed):**

- **Scope:** *"All biomes. It's a new fixture."* Every shipping biome gets a watcher, the Rust
  Cathedral included (its member is a machine, §3.2 and §5).
- **Media:** *"Ground and water for now. And we can bake in their little holes and things as part
  of their art."* A medium is always a terrain, ground or water. There is no Thing-medium: the
  knot-hole, leaf-roll, cocoon, casing or plate a creature peeks from is drawn into its peek pose.
- **Cues:** *"Full set."* The optional non-body flinch cues are built once on the extension, per
  member, each behind its own Mod Settings toggle (§1.3).

**The owner's second 2026-10-08 card (typed):**

- **Rust Cathedral:** *"Making a watcher here that looked like a little stalk that rose up like a
  camera and just watched and rotated to watch, then always pulled away when approached would be
  hilarious and very Star Wars."* The Watcher is a camera stalk. Design: §5.
- **Grey Sea:** *"That is not a watcher, that's its own creepy thing. Add an independent watcher
  that hides in place."* The fessk is not a member. The Grey Sea's member is the drossik (§3.2).
- **Contagion:** *"Of course it can get another creature. Just make one."* The Contagion's member
  is a new creature, the illuvek (§3.2). The sheet's ban 3 does not bar it.

**Other facts every row below rests on:**

1. **The kit is built** (`src/RimMandrake/Watchers`; first build `0d480998d`). It has not been run
   in game. A member's medium is a **list of `TerrainDef`s** (`RM_WatcherExtension.mediumTerrains`).
2. **The one-home law** (owner, 2026-09-21) rules out a shared Shiro in the Miasma. Shiro is canon,
   lives in two of our biomes, and needs no kit at all (§3, note S).
3. **Four biomes ship under different names:** Arid Shrubland → `RM_LeaningScrub`,
   Desert → `RM_LongShade`, Poison Forest → `RM_Cauldron`, Scarlands → `RM_Warscar`. Propane
   Lakes is `RM_TheChill` and the Nightside Ice is "the Sleeping Ice". Every row is keyed to the
   `RM_` BiomeDef that ships.
4. **The census was run on descriptions**, not defNames (method in §3.1). It found three existing
   alternatives the first pitch missed: the durrgak, the grellik and the ivvol.

## 1. The shared behaviour kit

### 1.1 The cycle (as ruled)

**Hidden → peeks out → watches** (it turns to face the nearest pawn that is not its own kind)
**→ flinches back and hides** when such a pawn comes inside `flinchRadius`, or when one of its own
optional cues holds **→ comes back up** after `hideTicks` once the radius is clear and every cue
is quiet. The rulings set the rest:

- **Hiding** means it vanishes in place and a **sign Thing** marks the cell.
- **The flinch cue** is anything not of its own kind, plus the member's optional cues (§1.3).
- **Packaging:** a standalone mod.
- **Medium:** one terrain per creature, ground or water (Q9; 2026-10-08).
- **Every biome** has one member.
- **The piinnok** lives on deep sand only and has two pictures.
- **A tamed member stays on its medium.**
- **Hunting is flush-only.**

### 1.2 What is built, and the prior art each piece reuses

`mandrake.rm.watchers` (`src/RimMandrake/Watchers`). No species is named in C#. A member opts in
with **one `DefModExtension` in XML**, and the comp is injected for it.

| kit piece (built) | what it does | prior art it copies (path) |
|---|---|---|
| `RM_WatcherExtension` | all per-member numbers: `mediumTerrains`, `flinchRadius` 6, `watchRadius` 14, `hideTicks` 2500~7500, `hiddenHediff`, `signDef`, `geophoneMinBodySize`, `boltTicks`, `emergeWhenFoodBelow`, and the optional `cues` block | `RM_BurrowOnFireExtension` (`src/RimMandrake/Pyrelands/Source/`) |
| `RM_JobGiver_Watch` + `RM_JobDriver_Watch` | one toil holds watch / flinch / hidden. `handlingFacing` + `FaceTarget` give the tracking. **One finish action removes the hediff and the sign on every exit** | `RM_JobDriver_Burrow` + `RM_JobGiver_BurrowOnFire` (Pyrelands): the same finish-action guarantee |
| `RM_WatcherHidden` hediff | `HediffComp_Invisibility` (`visibleToPlayer false`): nothing draws, and it is not valid prey | `RM_MurrekDrift` / `RM_JobDriver_MurrekBurrow` (`src/RimMandrake/BlueDesert/Source/RM_MurrekDrift.cs`); `RM_SandSwim_Hediffs.xml` |
| `RM_WatcherSign` + `RM_WatcherSign_SandDimple` | the readable sign: "no animal vanishes without a sign". Ethereal, so it spawns on ground and water alike | the first pitch named Anomaly's `PitBurrow` as the vanilla shape |
| `RM_JobGiver_WanderInMedium` | a `JobGiver_Wander` whose `wanderDestValidator` offers only medium cells; inserted at `Animal_PreWander` after the watch | `RM_JobGiver_WanderInShadeGrid` (`src/RimMandrake/CreatureBehaviors/Source/`) |
| `RM_CompWatcher` + startup injection | the medium backstop (found off its medium → walk back; nothing reachable → live as a plain animal that never hides), the orphan guard (a hidden hediff with no job holding it is removed), and the startup **water audit** (§1.4) | `RM_CompWaterLocked` (`src/RimMandrake/EnvironmentalHazards/Source/`); `RM_SandSwimStartup` |
| geophone | a submerged sand-swimmer at or above a body size, within `watchRadius`, sends it under. Bound by reflection, so the kit runs without CreatureBehaviors | `RM_SandSwimUtility.SubmergedSwimmersNear` ("§8, the piinnok hook", `RM_CompSandSwim.cs`) |
| `RM_WatcherCues` + `RM_WatcherCueUtility` | the seven optional non-body cues (§1.3) | see §1.3 |
| `RM_Designator_Flush` / `RM_WorkGiver_Flush` / `RM_JobDriver_Flush` | the only hunting route: the flusher reaches the sign, and the watcher comes up and bolts (huntable for `boltTicks`) | the murrek's dig-the-drift |
| `RM_WatchersSettings` | the master toggle, plus hide, face, medium lock, geophone, one toggle per cue kind, radius, delay and a per-map cap | the 2026-09-12 Mod Settings rule |

**The Brine Crown** (`RM_BrineCrown`, `src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Plants/RM_GreySeaFlora.xml`,
ruled 2026-09-26) is the fourth piece of prior art the item names. Its two-state retraction is
**still unbuilt**, and it is a *plant*. Plants get only `TickLong` (CLAUDE.md engine facts) and
never have a pawn job, so the watcher job can't drive it. It shares the **sign idea** (the
retracted crown is its own readable state) and the **cue model** (a chemical cue, never the
clock), which the kit's gas cue now implements for pawns. **Nothing in the kit is bent to drive a
plant.** If the Crown is built, it is a `ThingComp` on the plant with its own two graphics.

### 1.3 The optional cues (built 2026-10-08)

A member lists only the cues it has, under `<cues>` in its `RM_WatcherExtension`; an absent node
means it ignores that cue. While any of its cues holds, it goes under and stays under (the
geophone rule). Each kind has its own Mod Settings toggle. The decision is the Verse-free
`RM_WatcherKernel.Cues`, fuzzed in `Source/SelfTest/WatcherFuzz.cs` (family `cues`).

| cue | fires when | reading reused | first members |
|---|---|---|---|
| `gas` | a listed `GasType` at or above `minPercent` on its cell | vanilla `GasGrid.DensityPercentAt` | ulvoss (Cauldron, tox gas) |
| `heat` | its cell at or above `aboveC` | vanilla `GridsUtility.GetTemperature` | pralq (the Chill) |
| `fire` | a `Fire` within `radius` | vanilla Fire lister | ttekku (Pyrelands): up after the fire passes |
| `steam` | a listed Thing (a steam devil) within `radius` | `listerThings`; `RM_SteamDevil` (TerminalBiomes) as data | hveshk (Scald) |
| `shade` | shade on its cell below `minShade` (a shade-dweller stays under in the sun) | CreatureBehaviors' `RM_MapComponent_ShadeGrid.ShadeAt` by reflection while that grid is active; the roof and the sky otherwise (night = shade) | ennuk (Long Shade) |
| `buried` | a pawn carrying a listed hediff within `radius` | the murrek's own `RM_MurrekBuried` hediff, named as data | kuvvel (Blue Desert) |
| `light` | its cell's ground glow at or above `minGlow` | vanilla `GlowGrid.GroundGlowAt` | skeyr (Abyss); illuvek (Contagion) |

All cue numbers on members are PROVISIONAL and are set at each biome's sitting.

### 1.4 Water media

A water medium needs no new code. The kit was checked for it on 2026-10-08:

- **Every water medium on the list is shallow and passable** (`RM_DeepSand` Standable;
  `RM_SolidPropane`, `RM_TarShallow` and `RUT_ScaldMargin` inherit `WaterShallowBase`), so
  relocation and wander, which only need Standable cells, reach them.
- **The sign is Ethereal**, so it spawns on water as on ground.
- **The startup audit** (`RM_WatcherStartup.AuditMedium`, decision `RM_WatcherKernel.MediumAudit`)
  logs an error for an impassable medium and a warning for the two traps:
  - an `avoidWander` medium without race `waterSeeker true`: vanilla wander refuses it (give the
    race `waterSeeker` and a low `waterCellCost`, as the piinnok does);
  - an `IsWater` medium with a `swimmingGraphicData`: the swimming sprite outranks the peek pose
    in every state, so the peek never shows.

### 1.5 What each member costs

The kit needs no new code for any member. Each costs:

- one race + PawnKind def, with `RM_WatcherExtension` (and `<cues>` where §3.2 names one);
- one sign ThingDef (sand dimple exists; the others are new: hole, ripple ring, crust pock);
- art: a still peek pose (`stationaryGraphicData`) with its hole, knot or casing drawn in, the
  whole creature moving (`bodyGraphicData`), a desiccated corpse, and the sign;
- one roster row, added at that biome's own sitting, never by this item.

## 2. Q9 — can a pawn's look vary with the terrain under it?

**Answer: yes, for exactly one terrain class, and only by data. A sprite per *specific* terrain
needs new C#, and nothing in vanilla or our source does it.** I re-read this on RimSage
(decompiled 1.6) on 2026-10-08. The reads below are the evidence; each was made this session.

| symbol read (RimSage path) | what it says |
|---|---|
| `Verse.Pawn.DrawNonHumanlikeSwimmingGraphic` (`Source/Verse/Pawn.cs` l.1680) | It is true only when the pawn is spawned, not humanlike, `WaterCellCost.HasValue`, the current kind life stage has `swimmingGraphicData`, **and `Position.GetTerrain(Map).IsWater`**. This is the only terrain read anywhere in the animal-graphic path. |
| `Verse.TerrainDef.IsWater` (`TerrainDef.cs` l.324) | `HasTag("Water")`: a tag test. Any terrain tagged `Water` counts. Ours that are tagged include `RM_DeepSand`, the tar and slime liquids, `RM_SolidPropane`, `RM_TheChillDeep` and the `RUT_Scald*` waters. |
| `Verse.Pawn.DrawNonHumanlikeStationaryGraphic` (`Pawn.cs` l.1696) | It is true when the pawn is spawned, not humanlike, **`!pather.Moving`**, and the life stage has `stationaryGraphicData`. It is about motion, not terrain (the hermit crab precedent). |
| `Verse.PawnRenderNodeWorker_AnimalBody.GetGraphicState` | It returns `GraphicStateDefOf.Swimming` first, then `.Stationary`, and otherwise falls back to `base`. **Swimming outranks stationary.** |
| `Verse.PawnRenderNode_AnimalPart_Body.StateGraphicsFor` | It yields exactly those two extra states, from `swimmingGraphicData` / `stationaryGraphicData`, with female, alternate-graphic, mutant and skin-tint variants. Nothing else. |
| `Verse.PawnRenderNodeWorker.GetGraphicState` (`protected virtual`, l.98) and `PawnRenderNode.StateGraphicsFor` (`protected virtual`, l.396, read into `graphicStateLookup` at l.251) | Both hooks are overridable. A subclassed node plus worker *could* yield a custom `GraphicStateDef` keyed on any terrain. **Buildable, not proven**: no vanilla or `src/` example exists. |
| `Verse.PawnRenderer` l.189 | When `DrawNonHumanlikeSwimmingGraphic` is true, no shadow is drawn. That matters for a peek pose that should look half-buried. |
| (pitch 2026-09-30, verified) `PawnRenderer.ParallelGetPreRenderResults` with `IsHiddenFromPlayer` | A hidden pawn draws **nothing**, overlays included. So the sign has to be a separate Thing. |

**What this means for design:**

- A creature can look different **standing still vs moving** with no code. That is all the peek
  needs: the still sprite *is* the peek pose. This holds on **any** terrain.
- A creature can look different **on `IsWater` terrain vs everywhere else** with no code.
  For a watcher that is a trap rather than a feature (§1.4).
- A creature **cannot** look different on sand vs gravel vs ice without new C# (a custom render
  node + worker).
- ⇒ **The owner's binding of one medium per creature is the right call.** Every member below names
  exactly one terrain and ships one peek pose and one moving pose. **No per-terrain art is owed
  for any member.**

This answer is also owed to the item's own prose (its first criterion). It should be recorded
there by a note pointing to this section.

## 3. Per-biome members

### 3.1 Method

- I parsed every BiomeDef in `src/` with ElementTree: 65 defs, 571 race ThingDefs, 199
  TerrainDefs.
- `<wildAnimals>` was read **as XML elements**, both the `<DefName>n</DefName>` form and the
  `<li><animal>` form. Patch-added rows came from each PatchOperation's own `xpath`
  (`BiomeDef[defName="…"]/wildAnimals`) and its `<value>`.
- I joined each roster row to its race's **description**, keyword-flagged
  watch / peek / shy / hide / burrow / retract / gape / lurk / sink, and hand-read the 100
  flagged rows across the 27 shipping `RM_` biomes.
- Sanity probe: `korrum` 1 and `hawkbat` 1 among race descriptions, so the join sees text.
- Every new name below came back with **zero** hits in `src/`, `design/` or
  `infrastructure/state/items` today, the first pitch excepted. The first pitch's Wookieepedia
  check (zero hits for each) is carried over, not repeated.
- The bans for the 22 new names were checked against each biome sheet on 2026-09-30 (first
  pitch). Those sheets could have moved since, so each biome's sitting re-checks its own row.

**Every medium is a `TerrainDef` named in that biome's own def, or one its mod owns.** `[W]`
marks an `IsWater` terrain: the waterSeeker lever applies, and so does the swimming-sprite trap.
"Laid: UNMEASURED" means the terrain is defined, but whether that biome's map generator places
it was not checked offline.

### 3.2 The list: one member per biome, each bound to one terrain

**E** = existing creature (its own description is quoted). **NEW** = invented, franchise-free
`RM_` tier. **cue** = the optional cue(s) of §1.3 it carries besides bodies. No row here edits a
roster. Each member is added at its biome's own sitting.

| `RM_` biome | member | E/NEW | the one medium | cue | why it is a watcher | notes |
|---|---|---|---|---|---|---|
| Stillsand | **piinnok** `RM_Piinnok` | E (built) | `RM_DeepSand` [W] | geophone | "the watching glass"; its lenses sink when a buried giant moves | Built in the kit. Its roster row is owed by `STILLSAND_BEDAZZLE_CONTENT_1`, not here. Placeholder art. |
| Long Shade (desert) | **ennuk** | NEW | `Sand` | shade | a palm-sized sitter under shade-plant root plates; its dimples mark damp sand | `Sand`, not deep sand: that keeps it off the piinnok's medium and off hardpan (desert ban 6). Out only in shade. |
| Leaning Scrub (arid shrubland) | **vellisk** | NEW | `Soil` | — | a crust-lizard under venomvine roots that leans out toward you | food (small); can be tamed |
| Abyss | **skeyr** | NEW | `RM_EtchHollow` | light | a fog-crevice sitter whose pale throat-pouch is all that shows; it ducks from carried light | `RM_EtchHollow` is the Abyss's own terrain (the Etchcap grows only there). Existing alternative: **`RM_Durrgak`**, "works the black glass … with a patient, shy care". But it is a mobile sorter, and a watcher would lose that behaviour. |
| Cauldron (poison forest) | **ulvoss** | NEW | `RM_CauldronSoil` | gas (tox) | a vent-crust sitter peering from chemical-vent holes, its vent hole drawn into its peek art | chem-resistant hide |
| Blue Desert | **kuvvel** | NEW | `Ice` | buried (`RM_MurrekBuried`) | a drift-sitter with one eyestalk above the ice-sand | Goes under for a buried murrek nearby: the murrek hides with its own hediff, which the sand-swim geophone cannot see, so this is the `buried` cue. |
| Contagion | **illuvek** | NEW | `GU_AlienSandFine` (donor terrain, `MayRequire`) | light | an eye the goo budded and never finished: a lidded globe on a stub of red tissue in the wet sand, which sinks into the goo when light comes | The owner lifted ban 3 for it (2026-10-08). The light cue keeps it inside ban 2 (no UV-immune native): it goes under before a Burn, as the ocular jellies sink. It dissolves to goo on death and is not food (ban 4). |
| Cracked Lands (`RM_FloodedCanyon`) | **tarruq** `RM_Tarruq` | E | `Soil` (the clay pan) | — | "goes silent and climbs when the cracks begin to fill", the biome's second warning | "Crack" is not a terrain, so the clay is the binding. The kit adds the visible half of its hush. Its flood behaviour is unchanged. |
| Fever Wood | **phennu** | NEW | `SoilRich` | — | a soft six-eyed thing; only the eye-ring shows | Lives on the root floor; the knot-hole it peeks from is drawn into its peek art. |
| Forge | **zhaskel** | NEW | `CooledLava` | — | an ember-dark plated sitter in cooled-crust fissures | never in lava (ban 1). `CooledLava` is in the biome's own def. |
| Greentide | **wennoq** | NEW | `SoilRich` | — | a small leaf-sitter that unrolls to look | Lives on the floor; its leaf-roll is drawn into its peek art. Shiro is not this member (note S). Can be tamed. |
| Grey Sea | **drossik** | NEW | `RM_SeaFloorGround` | — | a grey eye-cup on a short stem in the sediment that turns to follow a diver, then folds flat and is a pebble | Hides in place: it never leaves its cell. `RM_SeaFloorGround` is the one shared floor terrain, and `RM_SeabedFloorLife` copies the Grey Sea cast onto it. **Sea rule:** fish-sized, so it owes a floor def **and** a `fishTypes` catch. `RM_Thollim` is not taken: its own text says it notices nothing and moves "only downward", so making it watch would rewrite a creature. |
| Lantern Deeps | **thrennick** | NEW | `RM_LanternstoneFloor` | — | a wall-foot sitter that sinks for anything big in the dark | No glow (ban 6). The Lantern Deeps sheet has a host-and-injection rule (§0), and this row is subject to it. |
| Miasma | **lussaq** | NEW | `Mud` | — | a six-legged root-sitter whose eye-fan is banded like the rainbow flora | The Miasma's own member (Shiro is not one, note S). `RM_Bozzuga` ("half-sunk … only its eyes showing") is an ambush predator, not shy, so it is not taken. |
| the Chill (propane lakes) | **pralq** | NEW | `RM_SolidPropane` [W] | heat | a frost-crust sitter at the lake margin that flinches from warmth | Can never be transported (R-H10). `animalDensity` is 0.08 (`RM_TheChill.xml`). |
| Pyrelands | **ttekku** | NEW | `RM_FE_Ash_Heavy` | fire | an ash-hole sitter that pops up after a fire passes | "ttekku up" means the ground is safe to walk. `RM_Ashwallow` is the sibling burrow-on-fire grazer and stays separate. |
| Rot | **mollugh** | NEW | `RM_TheRotSoilRich` | — | a fungus/animal that pulls itself under its own cap | Lives on the rot soil; its cap is drawn into its peek art. Ban 2 fits. Existing alternative: **`RM_Grellik`**, "the growth hides it among the caps". But it is vermin that breeds back, so a hide-and-flush pest is a design risk. |
| Rust Cathedral | **Watcher** (`RM_Watcher`) | NEW (machine) | `RM_RustCathedral_CrackedMetalSoil` | — | a little camera stalk that rises out of a deck seam, turns its head to follow you, and pulls back down into the seam when you come near. **Very shy:** see 5.7 | **Mechanical wildlife on the living-bolt shape** (not organic, not tameable, not butcherable into meat), so ban 7 does not bar it. Its text never says why it watches (ban 1). The stalk animation and head tracking are §5. The rise/track behaviour belongs to this biome's Watcher only; no other member uses it. |
| Scald | **hveshk** | NEW | `RUT_ScaldMargin` [W] | steam (`RM_SteamDevil`) | a sinter-rim sitter on the shore, never in the boil (ban 4) | The margin is named in `RM_TheScald.xml`. Not fish-sized and not on the floor, so it owes no catch def. |
| Sump | **thossa** | NEW | `RM_TarShallow` [W] | — | only its eye-blister breaks the tar surface | "thossa gone" means the tar is unsafe to cross. Laid: UNMEASURED (the Sump's own fauna cite `RM_TarShallow`). |
| Twilight Sea | **yennith** | NEW | `RM_SeaFloorGround` | — | a fan of three eyestalks from a silt tube | **Sea rule:** fish-sized, so it owes a floor def **and** a `fishTypes` catch. `RM_Kellu` ("hiding in the fronds by day") is a mobile hunter, so it is not taken. |
| Warscar (Scarlands) | **okkash** | NEW | `AncientMegastructure` | — | peeks from under the edge of a fused-glass plate | That is the only terrain `RM_Warscar` names; the plate edge is drawn into its peek art. It goes down when a Sentinel patrol passes (a body cue). |
| Wastes | **haddoq** | NEW | `VolcanoSoil` | — | peeks from the mouth of a spent ordnance casing | Lives on the volcanic soil; the casing is drawn into its peek art. Never the headline threat (ban 3). |
| Webwork | **qellith** | NEW | `SoilRich` | — | a thread-hermit that peers out of an old cocoon | Lives on the floor; the cocoon is drawn into its peek art. Goes down for a Wyyyschokk: an early spider warning. |
| Weeping Stones | **ommeth** | NEW | `SoftSand` | — | a pool-rim sitter whose comb is the sign it leaves | Never ambushes at water (ban 5). The comb is the **sign Thing**, because a hidden pawn draws nothing (§2). Existing alternative: **`RM_Ivvol`**, "the ridge surfaces, the eyes count", a stocked-pool floor-thing; a pool is a water terrain, so it fits the ruled media if chosen at the sitting. |
| Slime | **uuloq** | NEW | `RM_Slime_Liquid` | — | a nodule in the slime body; a bubble-eye breaks the surface | jelly food; no sentience read (ban 1). The slime liquid is Standable and not Water-tagged. |
| Sleeping Ice | **hessarn** | NEW | `Ice` | — | a seam-grazer that turns a heat-pit face toward warm bodies and draws down | Thermal sensing reads as its body cue. It retracts in place and never flees (bans 7/8). |

`[W]` = an `IsWater` terrain: §1.4 applies.

**Count:**

- 27 shipping biomes, one member each.
- **2 existing primaries:** the piinnok (built) and the tarruq.
- **25 new**: the 22 names of the first pitch, the Watcher (Rust Cathedral), the illuvek
  (Contagion) and the drossik (Grey Sea). The illuvek and the drossik had zero hits in `src/`,
  `design/` and `infrastructure/state/items` and zero Wookieepedia search results on 2026-10-08
  (probes: `korrum` 62 files; `dewback` 10 results).
- **8 members carry an optional cue** (§1.3): ennuk, skeyr, ulvoss, kuvvel, illuvek, pralq,
  ttekku, hveshk. The piinnok carries the geophone.
- **3 existing alternatives** for the owner to weigh at their sittings: the durrgak, the grellik
  and the ivvol.
- Not counted:
  - The Fall Line: a region with no roster.
  - Fuel Snows and Umbra: `RUT_`-only, with no shipping `RM_` biome.

**Note S: Shiro** (`RSW_Shiro`, canon, rostered in **both** `RM_Greentide` and `RM_Miasma`). It is
not a member. Three reasons:

- An extension goes on the race, so a watcher Shiro would be a watcher in both homes. Its medium
  lock would then have to span both biomes' terrains, which breaks one-creature-one-medium.
- The evictions ruling (2026-09-22) means this pitch must not pick its home.
- **It does not need the kit.** Its canon behaviour is "retract its head, legs and tail into its
  spiny shell". That is exactly vanilla's hermit-crab `stationaryGraphicData` (§2): data only,
  through the Utinni patch layer (Q11), and it never vanishes, so no sign is needed.

### 3.3 Wave plan

Members go in **biome by biome at each sitting**, never as a sweep. That follows the first
pitch's Q10(a), and it is how the owner wants rosters handled. Each sitting admits or cuts its
row, re-checks its bans, sets its cue numbers, and names the sign family:

- **dimple:** sand
- **hole:** soil, ash, crust
- **ripple ring:** tar, propane, margin water, slime
- **pock:** ice, floor
- **seam glint:** deck plate (the Watcher's hatch)

The item's third criterion ("one member per biome proven on a quicktest map") is therefore a
27-sitting target, not one build.

## 4. Questions for the owner

Ruled, so not asked again: hide in place + sign; the flinch cue; standalone mod; one medium each,
ground or water; the piinnok's ground, pictures, taming and hunting; all biomes; the full cue set;
the Rust Cathedral's member is a machine camera stalk named literally "Watcher", with an eight-step head pan and very shy behaviour (this biome only); the fessk is not a watcher; the Contagion
gets a new creature.

## 5. The Rust Cathedral camera stalk: feasibility (2026-10-08)

Offline design and feasibility only. Nothing in this section is built.

### 5.1 What the owner asked

Owner, 2026-10-08, typed on a question card: *"Making a watcher here that looked like a little
stalk that rose up like a camera and just watched and rotated to watch, then always pulled away
when approached would be hilarious and very Star Wars. How possible is it to make an animation
like that of an extending camera stalk, retracting stalk, and player tracking behavior?"*

That is three things: **(1)** a stalk that extends and retracts, **(2)** a head that turns to
follow a pawn, **(3)** pulling away when approached. **(3) is already the kit's flinch-and-hide
cycle** (§1.1). (1) and (2) are new rendering work.

**Short answer: possible in RimWorld 1.6 without new art tricks. The extend and retract use the
engine's own keyframe animation system. The head turns in eight 45-degree steps, eased toward its
target, using a small amount of code. Owner ruling 2026-10-08: eight span, named literally "Watcher",
Rust Cathedral only, very shy.**

### 5.2 What the engine can do (RimSage, decompiled 1.6, read 2026-10-08)

| symbol read | what it says | what it gives the Watcher |
|---|---|---|
| `Verse.AnimationDef` | an animation has `durationTicks`, a `loopMode`, and `keyframeParts` keyed by a render-node tag | one animation per motion: *rise*, *retract*, *idle sway* |
| `Verse.Keyframe` | each keyframe holds `tick`, `offset` (Vector3), `angle`, `scale` (Vector3) and an optional `graphicState` | the stalk can move up, grow, tilt and swap pictures per keyframe |
| `Verse.AnimationWorker_Keyframes.GetKeyframeData` | offset, angle and scale are **linearly interpolated** between keyframes (`Vector3.Lerp`, `Mathf.Lerp`); `graphicState` steps (no blend) | the rise is smooth motion, not a flip-book, unless we want frames |
| `Verse.AnimationPart.pivot` (default 0.5, 0.5), read by `PawnRenderNodeWorker.PivotFor` | each animated part sets its own pivot | a pivot at the stalk's **foot** (0.5, 0) makes it grow upward from the seam instead of from its middle |
| `Verse.PawnRenderTree` l.73–97 | `LoopMode.Clamp` holds the last frame; `LoopMode.End` reports the animation finished | *rise* holds at full height; *retract* tells the job when it is down |
| `Verse.PawnRenderer.SetAnimation(AnimationDef)` | starts an animation on a pawn now (or clears it with null), and dirties the tree | the watch job calls it on emerge and on flinch |
| Anomaly's `DevourerDigesting` (`Defs/Anomaly/AnimationDefs/Devourer.xml`) | a shipped keyframe animation: the Root node rocks ±5–7° over 120 ticks | vanilla precedent that keyframe animation runs on a wild creature's body |
| `Verse.PawnRenderNodeWorker.RotationFor` / `ScaleFor` (both `public virtual`) | rotation and scale are computed per draw from props + animation, and a subclass may add to them | a custom worker can add *any* angle to the head node |
| `Verse.PawnRenderNodeWorker_TurretGun.RotationFor` + `RimWorld.CompTurretGun.CompTick` | the worker multiplies in `turretComp.curRotation`; the comp sets that float every tick from `(target − DrawPos).AngleFlat()`. Used on **pawns**: `Mech_Centurion`, `Mech_Warqueen`, `Mech_Diabolus` (`Races_Mechanoids_SuperHeavy.xml`) | **vanilla already turns one part of a moving pawn freely to track a target.** That is our tracking head, minus the gun |
| `RimWorld.TurretTop.TurretTopTick` | with no target, a turret sweeps idly at 0.26°/tick for 140 ticks, then pauses 150–350 ticks | a ready-made "looking around" idle for when nobody is near |
| `Pawn_RotationTracker.FaceCell` (what the kit calls now, `RM_JobDriver_Watch.cs` l.154) | sets the pawn's `Rot4`: north, east, south, west only | today's piinnok "tracking" is four-step; the Watcher replaces it with the eight-step pan (5.6) |

**Two engine limits to design around:**

- **A hidden pawn draws nothing** (§2). So the *retract* animation must finish **before** the
  hidden hediff goes on. Otherwise the stalk blinks out instead of pulling down. That is one
  small change to the watch job's flinch step: retract first, then hide.
- **Turning a sprite in the picture plane is not the same as panning a camera.** RimWorld draws
  from above at an angle. Spinning a side-view camera head by 180° turns it upside-down. The
  free-spin route only looks right for a head drawn **from above** (a round lens dome), which
  reads like a turret. For a camera that pans to look left and right, we use **direction
  frames**: the head picture is chosen by which way it is looking. That is the trade-off in §5.6.

### 5.3 Prior art we can reuse (our source)

| piece | path | what it lends |
|---|---|---|
| The whole kit: watch, flinch, hide, sign, flush, medium lock, cues | `src/RimMandrake/Watchers` | the behaviour. The owner's "always pulled away when approached" is the kit's flinch, unchanged |
| A custom animal body worker that picks a graphic state per draw | `src/RimMandrake/TheForge/Source/RM_PawnRenderNodeWorker_DormantBody.cs` + `TheForge/Defs/PawnRenderTreeDefs/RM_DormantAnimalBody.xml` | the pattern for choosing a head picture by look direction (the eight-step pan), and a working custom `PawnRenderTreeDef` in our tree |
| A Harmony postfix that swaps an animal into its alternate graphic slot | `src/RimMandrake/CreatureBehaviors/Source/RM_SandBuriedGraphic.cs` | not needed here; listed so nobody rebuilds it |
| The living bolt: a mechanoid-fleshed wild creature with its **own whole think tree** | `src/RimMandrake/RustCathedral/Defs/ThingDefs_Races/RM_LivingBolt.xml`, `RustCathedral/Defs/ThinkTreeDefs/RM_ThinkTree_LivingBolt.xml` | the def shape for a machine creature. **Important:** a mechanoid-fleshed race is never an Animal, so the kit's `Animal_PreWander` splice never reaches it. The Watcher needs its own small tree listing `RM_JobGiver_Watch` and `RM_JobGiver_WanderInMedium`, as the bolt has its own. No kit C# changes for that |
| The bolts' attitude freeze | `RM_ThinkNode_ConditionalAttitudeBand` (same tree) | optional: the Watchers could freeze with the bolts when the place's mood drops. Data only. Not proposed unless the owner wants it |
| The piinnok's tracking | `RM_JobDriver_Watch.cs` l.152–154 | four-step `FaceCell`. The Watcher does not use it; its head is driven by the tracked angle (5.6) |

**What does not exist anywhere in `src/`:** a keyframe `AnimationDef`, and a render node turned
by a comp angle. Both are new to this repo, though both are vanilla mechanisms.

**Do not reuse:** the `PawnRenderNodeProperties_Spastic` wing tree. It was reversed on the fire
hawk (CLAUDE.md flyer section) because it wiggles one fixed texture and cannot express poses.

### 5.4 The bans

Frozen sheet: `design/Jawa/worldbuilding/biomes/the_rust_cathedral.md` §6.

- **Ban 7, no ordinary wildlife** ("nothing organic spawns here that isn't §4's short list"). The
  Watcher is not organic. It follows the living bolts' precedent exactly: mechanical "wildlife",
  mechanoid flesh, not tameable, not butchered into meat. Its only yield is a component or steel,
  as the bolt's `butcherProducts`.
- **Ban 1, no §GM truth in player text.** Its description says what it **does** and never **why**.
  It must not say it is the place's eye, belongs to the mind, reports to anything, or shares the
  bolts' origin (the bolts' origin is named in ban 1). That is the obvious joke to reach for, and
  it is banned. Allowed: "it rises, it turns to follow you, it drops into the seam. Nobody has
  found the other end of the stalk."
- **Bans 2–6** don't touch it: no droid-mercy text, no hunting Sentinels, no settlement, no acid,
  no drill explanation.
- Every other kit rule stands: hide in place, a readable sign in the seam, flush-only hunting.

### 5.5 Art owed

| sprite | count | notes |
|---|---|---|
| seam hatch (the base, flush with the deck) | 1 | doubles as the still pose when the stalk is down |
| stalk segment | 2–3 | telescoping segments, each slid up by an offset keyframe. That beats stretching one texture, which smears it |
| head, by look direction | 5 | 8 directions from 5 drawn (the three west-side ones mirror) |
| moving body (a small crawler base for relocating along the seams) | 3 | north / east / south |
| sign (seam glint) | 1 | the readable mark while it is down |
| corpse | 0 | a mechanoid-fleshed race has none, as with the living bolt |

Total: about **11–12 sprites.** All are small (the bolt draws at 0.1),
which suits the artpipe. **No flight is involved, so the no-unattended-flyer-test rule doesn't
apply.** A live quicktest proof with screenshots is allowed.

### 5.6 Design and effort

Rise and retract: a keyframe `AnimationDef` (*rise*, held with `LoopMode.Clamp`; *retract*, ending
with `LoopMode.End`), with the stalk's pivot at its foot. Two Mod Settings toggles (stalk
animation; smooth tracking); the plain still pose is the all-off state.

**Head turn: eight-step pan** (owner ruling 2026-10-08, "Eight span is good"). A head picture per
45 degrees, picked from a tracked angle. The angle eases toward its target a few degrees per tick,
with the turret's idle sweep when nobody is near. New code: the retract-before-hide change, an
`AnimationDef` hook on `RM_WatcherExtension`, a head worker (the Forge `DormantBody` pattern) and a
tracked angle on `RM_CompWatcher`, with the easing as a Verse-free kernel function fuzzed in
`WatcherFuzz.cs`. Art: about 11-12 drawings. Effort: about a day (agent build plus one live
quicktest). It reads as a camera panning to follow you.

**Scope: the Rust Cathedral only.** The rise/track behaviour is this biome's Watcher alone, not a
kit-wide mode; no other biome's member rises on a stalk or pans its head. Build it as data and
hooks on this creature, not as a kit option other members can switch on.

**Risks, said plainly:**

- No keyframe `AnimationDef` has been built in this repo. The engine reads are clear, but the
  first one may need a tuning pass on the live game (the pivot and the offsets).
- The render tree for a mechanoid-fleshed creature with custom nodes is new. The bolt uses a plain
  body graphic.
- Ordering: the hide must wait for *retract* to end. If the hidden hediff goes on early, the stalk
  vanishes instead of pulling down. This is a kernel decision and gets a fuzz family.

**What ships it:** one race and kind def; a `PawnRenderTreeDef` (base, segments, head); two or
three `AnimationDef`s; its own think tree; a seam-glint sign; the kit changes for the chosen
option; the art; one live quicktest showing rise, track, retract and the sign. It goes in at the
Rust Cathedral's own sitting, like every member.

### 5.7 Shyness (owed design parameter; numbers PROVISIONAL)

Owner, 2026-10-08, typed: *"it should be very shy when approached."* The Watcher is the shyest
member of the kit: it hides from a small distance, drops fast, and stays down a long time.

| parameter | direction | provisional value |
|---|---|---|
| flinch radius | small: it notices and pulls back before anything gets close | PROVISIONAL, tune in the quicktest |
| retract speed | fast: a short *retract* animation | PROVISIONAL |
| re-emerge delay | long: it stays down well after the pawn has left | PROVISIONAL |

These are `RM_WatcherExtension` fields on this creature's def, not kit defaults. The retract must
finish before the hidden hediff goes on (see Risks above).
