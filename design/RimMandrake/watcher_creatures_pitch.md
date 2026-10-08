# Watcher creatures — the full pitch (WATCHER_CREATURES_MOD_1)

Status: DESIGN for the owner to rule on. FOUNDRY helper, 2026-10-08. Offline; no roster edited.

## 0. What this doc is, and what came before it

This is the pitch the item's second criterion asks for: the kit mechanism, the Q9 terrain-look
answer, and a per-biome candidate list in which every member names **one medium**. The owner
asked for it by question card. It replaces nothing. It brings together and corrects two earlier
docs, which stay as provenance:

- `design/RimMandrake/watchers_mod_pitch_2026-09-30.md`: the first pitch (29 rows). Its Q1–Q3
  were ruled 2026-09-30 and its Q9 was answered by the owner typing.
- `design/RimMandrake/watcher_creatures_kit_design_2026-10-02.md`: the kit design and the piinnok.
  Its Q1–Q4 were ruled 2026-10-03.

**What changed since the first pitch, and why its member table can't be used as it stands:**

1. **The kit is built** (`src/RimMandrake/Watchers`, `0d480998d`, review fixes `c992f1cb2`,
   kernel fuzz `d00874002`). It has not been run in game. In the built kit a member's medium is a
   **list of `TerrainDef`s** (`RM_WatcherExtension.mediumTerrains`). Seven of the first pitch's
   22 new members had a medium that is a *Thing*, not a terrain: a knot-hole, a leaf-roll, a
   cocoon, an ordnance casing, its own cap, a glass plate, a mangrove root. The kit cannot lock
   those as written. §3 gives each a real terrain from its own biome, and Q2 asks whether a
   Thing-medium is worth new code.
2. **The one-home law** (owner, 2026-09-21) rules out the first pitch's "Shiro (shared)" in the
   Miasma. Shiro is canon, lives in two of our biomes, and needs no kit at all (§3, note S).
   The Miasma's hole is filled by a new creature.
3. **Four biomes have different names on the shipping tier:** Arid Shrubland → `RM_LeaningScrub`,
   Desert → `RM_LongShade`, Poison Forest → `RM_Cauldron`, Scarlands → `RM_Warscar`. Also,
   Propane Lakes is `RM_TheChill` and the Nightside Ice is "the Sleeping Ice". Every row is keyed
   to the `RM_` BiomeDef that ships.
4. **The census was re-run on descriptions**, not defNames (method in §3). It found four
   existing creatures the first pitch missed: the durrgak, the ikee, the grellik and the ivvol.

## 1. The shared behaviour kit

### 1.1 The cycle (as ruled)

**Hidden → peeks out → watches** (it turns to face the nearest pawn that is not its own kind)
**→ flinches back and hides** when such a pawn comes inside `flinchRadius` **→ comes back up**
after `hideTicks` once the radius is clear. The owner's rulings set the rest:

- **Hiding** means it vanishes in place and a **sign Thing** marks the cell.
- **The flinch cue** is anything not of its own kind.
- **Packaging:** a standalone mod.
- **Medium:** one per creature (Q9).
- **The piinnok** lives on deep sand only and has two pictures.
- **A tamed member stays on its medium.**
- **Hunting is flush-only.**

### 1.2 What is built, and the prior art each piece reuses

`mandrake.rm.watchers` (`src/RimMandrake/Watchers`, about 1,140 lines of C#). No species is
named in C#. A member opts in with **one `DefModExtension` in XML**, and the comp is injected
for it.

| kit piece (built) | what it does | prior art it copies (path) |
|---|---|---|
| `RM_WatcherExtension` | all per-member numbers: `mediumTerrains`, `flinchRadius` 6, `watchRadius` 14, `hideTicks` 2500~7500, `hiddenHediff`, `signDef`, `geophoneMinBodySize`, `boltTicks`, `emergeWhenFoodBelow` | `RM_BurrowOnFireExtension` (`src/RimMandrake/Pyrelands/Source/`) |
| `RM_JobGiver_Watch` + `RM_JobDriver_Watch` | one toil holds watch / flinch / hidden. `handlingFacing` + `FaceTarget` give the tracking. **One finish action removes the hediff and the sign on every exit** | `RM_JobDriver_Burrow` + `RM_JobGiver_BurrowOnFire` (Pyrelands): the same finish-action guarantee |
| `RM_WatcherHidden` hediff | `HediffComp_Invisibility` (`visibleToPlayer false`): nothing draws, and it is not valid prey | `RM_MurrekDrift` / `RM_JobDriver_MurrekBurrow` (`src/RimMandrake/BlueDesert/Source/RM_MurrekDrift.cs`); `RM_SandSwim_Hediffs.xml` |
| `RM_WatcherSign` + `RM_WatcherSign_SandDimple` | the readable sign: "no animal vanishes without a sign" | (new; the first pitch named Anomaly's `PitBurrow` as the vanilla shape) |
| `RM_JobGiver_WanderInMedium` | a `JobGiver_Wander` whose `wanderDestValidator` offers only medium cells; inserted at `Animal_PreWander` after the watch | `RM_JobGiver_WanderInShadeGrid` (`src/RimMandrake/CreatureBehaviors/Source/`) |
| `RM_CompWatcher` + startup injection | the medium backstop (found off its medium → walk back; nothing reachable → live as a plain animal that never hides). Also the orphan guard: a hidden hediff with no job holding it is removed | `RM_CompWaterLocked` (`src/RimMandrake/EnvironmentalHazards/Source/`); `RM_SandSwimStartup` |
| geophone | a submerged sand-swimmer at or above a body size, within `watchRadius`, sends it under. Bound by reflection, so the kit runs without CreatureBehaviors | `RM_SandSwimUtility.SubmergedSwimmersNear` ("§8, the piinnok hook", `RM_CompSandSwim.cs`) |
| `RM_Designator_Flush` / `RM_WorkGiver_Flush` / `RM_JobDriver_Flush` | the only hunting route: the flusher reaches the sign, and the watcher comes up and bolts (huntable for `boltTicks`) | the murrek's dig-the-drift |
| `RM_WatchersSettings` | the master toggle, plus hide, face, medium lock, geophone, radius, delay and a per-map cap | the 2026-09-12 Mod Settings rule |

**The Brine Crown** (`RM_BrineCrown`, `src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Plants/RM_GreySeaFlora.xml`,
ruled 2026-09-26) is the fourth piece of prior art the item names. Its two-state retraction is
**still unbuilt**, and it is a *plant*. Plants get only `TickLong` (CLAUDE.md engine facts) and
never have a pawn job, so the watcher job can't drive it. What it can share is the **sign idea**
(the retracted crown is its own readable state) and the **cue model**: it retracts on a
**chemical** cue (salt snow, a venting chimney), never on light or the clock. That is a precedent
for members whose flinch cue is something other than "a body came near" (Q3). **Nothing in the
kit should be bent to drive a plant.** If the Crown is built, it is a `ThingComp` on the plant
with its own two graphics.

### 1.3 What wave 2 costs per member

The kit needs no new code for any member whose medium is a terrain. Each member costs:

- one race + PawnKind def, with `RM_WatcherExtension`;
- one sign ThingDef (sand dimple exists; the others are new: hole, ripple ring, crust pock);
- art: a still peek pose (`stationaryGraphicData`), the whole creature moving (`bodyGraphicData`),
  a dessicated corpse, and the sign;
- one roster row, added at that biome's own sitting, never by this item.

⚠️ **An `IsWater` medium has two levers, one free and one a trap.** Those media are deep sand,
tar, solid propane and the Scald margin (§2).
- **The free lever:** race `waterSeeker true` plus a low `waterCellCost` makes vanilla wander and
  pathing *prefer* the medium.
- **The trap:** if that member also ships a `swimmingGraphicData`, the swimming sprite wins in
  every state and the peek pose never shows. The piinnok header already records this.

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
  For a watcher that is a trap rather than a feature (§1.3).
- A creature **cannot** look different on sand vs gravel vs ice without new C# (a custom render
  node + worker).
- ⇒ **The owner's binding of one medium per creature is the right call.** Every member below names
  exactly one terrain and ships one peek pose and one moving pose. **No per-terrain art is owed
  for any member.**

This answer is also owed to the item's own prose (its first criterion). It should be recorded
there by a note pointing to this section.

## 3. Per-biome candidate members

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
`RM_` tier. No row here edits a roster. Each member is added at its biome's own sitting.

| `RM_` biome | member | E/NEW | the one medium | why it is a watcher | notes |
|---|---|---|---|---|---|
| Stillsand | **piinnok** `RM_Piinnok` | E (built) | `RM_DeepSand` [W] | "the watching glass"; its lenses sink when a buried giant moves | Built in the kit. Its roster row is owed by `STILLSAND_BEDAZZLE_CONTENT_1`, not here. Placeholder art. |
| Long Shade (desert) | **ennuk** | NEW | `Sand` | a palm-sized sitter under shade-plant root plates; its dimples mark damp sand | `Sand`, not deep sand: that keeps it off the piinnok's medium and off hardpan (desert ban 6). "Out only in shade" is a cue the kit lacks (Q3). |
| Leaning Scrub (arid shrubland) | **vellisk** | NEW | `Soil` | a crust-lizard under venomvine roots that leans out toward you | food (small); can be tamed |
| Abyss | **skeyr** | NEW | `RM_EtchHollow` | a fog-crevice sitter whose pale throat-pouch is all that shows; it ducks from carried light | `RM_EtchHollow` is the Abyss's own terrain (the Etchcap grows only there). Existing alternative: **`RM_Durrgak`**, "works the black glass … with a patient, shy care". But it is a mobile sorter, and a watcher would lose that behaviour. |
| Cauldron (poison forest) | **ulvoss** | NEW | `RM_CauldronSoil` | a vent-crust sitter peering from chemical-vent holes | also flinches from tox gas (Q3); chem-resistant hide |
| Blue Desert | **kuvvel** | NEW | `Ice` | a drift-sitter with one eyestalk above the ice-sand | The geophone it wants is **buried murrek**. Murrek hide with their own hediff, not the sand-swim kit, so `SubmergedSwimmersNear` will not see them. That is a second geophone source, and it is code (Q3). |
| Contagion | **ikee** `RM_ContagionIkee` *or* **peeper** `RM_Peeper` | E | `GU_AlienSandFine` (donor terrain, `MayRequire`) | ikee: "follows bigger things and watches … **dives into the pockets when the light comes**"; peeper: "watching replaced hunting" | Ban 3 (no new natives), so it must be one of these two. The ikee's own text already hides. The peeper is mid-sized for a peeker. Pick one at the sitting. |
| Cracked Lands (`RM_FloodedCanyon`) | **tarruq** `RM_Tarruq` | E | `Soil` (the clay pan) | "goes silent and climbs when the cracks begin to fill", the biome's second warning | "Crack" is not a terrain, so the clay is the honest binding. The kit adds the visible half of its hush. Its flood behaviour is unchanged. |
| Fever Wood | **phennu** | NEW | `SoilRich` | a soft six-eyed thing; only the eye-ring shows | **Rebound** from "knot-hole" (a tree, not a terrain) to a root-floor hole. Q2 asks whether a tree is worth the code. |
| Forge | **zhaskel** | NEW | `CooledLava` | an ember-dark plated sitter in cooled-crust fissures | never in lava (ban 1). `CooledLava` is in the biome's own def. |
| Greentide | **wennoq** | NEW | `SoilRich` | a small leaf-sitter that unrolls to look | **Rebound** from "leaf-roll" (a plant) to the floor. Shiro is not this member (note S). Can be tamed. |
| Grey Sea | **thollim** `RM_Thollim` | E | `RM_SeaFloorGround` | "valves sitting half down in the sediment with a finger's width of gape" | Sessile on the floor layer. `RM_SeaFloorGround` is the one shared floor terrain, and `RM_SeabedFloorLife` copies the Grey Sea cast onto it. **`RM_Fessk` is held, not taken:** it is man-sized and mobile, and "the moment it is noticed, it is already leaving" describes fleeing, not hiding in place (Q4). |
| Lantern Deeps | **thrennick** | NEW | `RM_LanternstoneFloor` | a wall-foot sitter that sinks for anything big in the dark | No glow (ban 6). The Lantern Deeps sheet has a host-and-injection rule (§0), and this row is subject to it. |
| Miasma | **lussaq** | NEW | `Mud` | a six-legged root-sitter whose eye-fan is banded like the rainbow flora | **Fills the hole the first pitch filled with a shared Shiro.** `RM_Bozzuga` ("half-sunk … only its eyes showing") is an ambush predator, not shy, so it is not taken. |
| the Chill (propane lakes) | **pralq** | NEW | `RM_SolidPropane` [W] | a frost-crust sitter at the lake margin that flinches from **heat** | Can never be transported (R-H10). Its cue is heat (Q3). The first pitch's "spawns nowhere" warning is **stale**: `animalDensity` is 0.08 (`RM_TheChill.xml` l.90). |
| Pyrelands | **ttekku** | NEW | `RM_FE_Ash_Heavy` | an ash-hole sitter that pops up after a fire passes | "ttekku up" means the ground is safe to walk. `RM_Ashwallow` is the sibling burrow-on-fire grazer and stays separate. |
| Rot | **mollugh** | NEW | `RM_TheRotSoilRich` | a fungus/animal that pulls itself under its own cap | Ban 2 fits. Existing alternative: **`RM_Grellik`**, "the growth hides it among the caps". But it is vermin that breeds back, so a hide-and-flush pest is a design risk. |
| Rust Cathedral | **none** | — | — | ban 7: no ordinary wildlife | Q5 |
| Scald | **hveshk** | NEW | `RUT_ScaldMargin` [W] | a sinter-rim sitter on the shore, never in the boil (ban 4) | It also flinches from steam bursts (Q3). The margin is named in `RM_TheScald.xml`. Not fish-sized and not on the floor, so it owes no catch def. |
| Sump | **thossa** | NEW | `RM_TarShallow` [W] | only its eye-blister breaks the tar surface | "thossa gone" means the tar is unsafe to cross. Laid: UNMEASURED (the Sump's own fauna cite `RM_TarShallow`). |
| Twilight Sea | **yennith** | NEW | `RM_SeaFloorGround` | a fan of three eyestalks from a silt tube | **Sea rule:** fish-sized, so it owes a floor def **and** a `fishTypes` catch. `RM_Kellu` ("hiding in the fronds by day") is a mobile hunter, so it is not taken. |
| Warscar (Scarlands) | **okkash** | NEW | `AncientMegastructure` | lives under fused-glass plates and peeks from the edge | That is the only terrain `RM_Warscar` names, and it is a weak fit: the glass plate was a Thing. It goes down when a Sentinel patrol passes. Q2. |
| Wastes | **haddoq** | NEW | `VolcanoSoil` | peeks from the mouth of a spent ordnance casing | **Rebound** from the casing (a Thing). Never the headline threat (ban 3). |
| Webwork | **qellith** | NEW | `SoilRich` | a thread-hermit that peers out of an old cocoon | **Rebound** from the cocoon (a Thing). Goes down for a Wyyyschokk: an early spider warning. |
| Weeping Stones | **ommeth** | NEW | `SoftSand` | a pool-rim sitter whose comb is the sign it leaves | Never ambushes at water (ban 5). The comb has to be the **sign Thing**, because a hidden pawn draws nothing (§2). Existing alternative: **`RM_Ivvol`**, "the ridge surfaces, the eyes count". But it is a stocked-pool floor-thing, so a pool medium is Q2 again. |
| Slime | **uuloq** | NEW | `RM_Slime_Liquid` | a nodule in the slime body; a bubble-eye breaks the surface | jelly food; no sentience read (ban 1) |
| Sleeping Ice | **hessarn** | NEW | `Ice` | a seam-grazer that turns a heat-pit face toward warm bodies and draws down | Thermal sensing only. It retracts in place and never flees (bans 7/8). |

**Count:**

- 27 shipping biomes. 26 have one member each; the Rust Cathedral has none.
- **4 existing primaries:** the piinnok (built), ikee/peeper, thollim and tarruq.
- **22 new**, the same 22 names as the first pitch. Seven are rebound from a Thing to a terrain:
  the phennu, wennoq, lussaq, mollugh, okkash, haddoq and qellith. The lussaq also replaces the
  shared Shiro.
- **3 existing alternatives** for the owner to weigh: the durrgak, the grellik and the ivvol.
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

Wave 2 goes **biome by biome at each sitting**, never as a sweep. That follows the first
pitch's Q10(a), and it is how the owner wants rosters handled. Each sitting admits or cuts its
row, re-checks its bans, and names the sign family:

- **dimple:** sand
- **hole:** soil, ash, crust
- **ripple ring:** tar, propane, margin water
- **pock:** ice, floor

The item's third criterion ("one member per biome proven on a quicktest map") is therefore a
26-sitting target, not one build.

## 4. Questions for the owner

Already ruled, so not asked again:

- hide: in place + sign
- flinch cue
- standalone mod
- one medium each
- the piinnok's ground, its pictures, taming and hunting

**Q1. Is this list the right shape to take to the sittings?**
- **(a) Yes:** one member per biome as listed, each admitted or cut at its own biome sitting
  (recommended).
- **(b) Fewer biomes:** only biomes where an existing creature already fits (Stillsand,
  Contagion, Grey Sea, Cracked Lands), with no new creatures. Cheapest, but most biomes get no
  watcher.
- **(c) A different set**, written in by you.

**Q2. Some members want to live in a *thing*, not on ground** (a tree hole, a leaf, a cocoon, a
shell casing, a glass plate, a stocked pool). Do we build that?
- **(a) No.** Every member lives on its biome's ground, as rebound in §3 (recommended). No new
  code, and the art is honest about it.
- **(b) Yes:** the kit gets a second medium kind, "beside or inside this kind of thing". Truer to
  the first pitch, but it is new code, and the creature is stranded whenever its thing is cut,
  burned or hauled off.

**Q3. Should some members flinch from something other than a body?** (The Brine Crown is the
precedent: a chemical cue, never light or the clock.) The first pitch's
offers are tox gas (Cauldron), heat (the Chill), steam bursts (Scald), shade (Long Shade) and
buried murrek (Blue Desert).
- **(a) Not yet.** Every member flinches only from bodies; extra cues wait until a sitting asks
  for one (recommended: they are each new code, and the base kit has never run in game).
- **(b) Yes, as a small set of optional cues** on the extension, built once for all members.
- **(c) Only the ones that make the creature a warning sign** (gas, heat, steam, murrek), which
  is where the player gets real information.

**Q4. The fessk (Grey Sea): a "lean out from cover" watcher, or left as it is?** Its own text has
it leaving the moment it is noticed, and the kit's hide is vanishing in place.
- **(a) Leave it as it is** (recommended). It already reads eerie, and the thollim is the Grey
  Sea's member.
- **(b) A cover variant:** it steps back behind a pillar and never vanishes. That is a second
  behaviour mode in the kit.

**Q5. The Rust Cathedral: no member, or a machine watcher?**
- **(a) None.** Ban 7 (no ordinary wildlife) stands (recommended).
- **(b) A machine that turns to follow you** from the cables. It needs care with the mind-truth
  ban.

**Q6. Contagion: the ikee or the peeper?** (Ban 3 means no new creature.)
- **(a) The ikee** (recommended). Its own text already "dives into the pockets when the light
  comes", so hiding is its nature. Trade: it also "follows bigger things", which the sitting
  must reconcile with flinching from them.
- **(b) The peeper.** "Watching replaced hunting". Trade: it is a mid-sized browser, big for
  something that pops in and out of the ground.
