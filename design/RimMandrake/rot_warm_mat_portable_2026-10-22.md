# The Rot's warm mat, portable — design spec (2026-10-22)

Item: `ROT_WARM_MAT_BUILD_WORKS_FOR_FOOD`. Source: Rot open questions Q2
(`design/RimMandrake/rot_open_questions_2026-10-22.md`), answered by card with a write-in.

## The ruling

Owner, 2026-10-22, by question card (verbatim write-in):

> *"Make it work anywhere but it not naturally occurs in the rot. Can be installed on the gravship to help with
> heating in cold places as a reward. Needs food. Would grow in other biomes if tended with food. Rot doesn't
> require feeding due to sharing lore."*

Standing calibration it keeps (2026-09-17, card 3): *"It doesn't make enough to trivialize the deep deep dark. It
just helps a lot."* The 21 °C absolute cap and the ramp (`RM_MapComponent_WarmGround`'s `ThermalPowerDivisor`)
are unchanged.

What it changes: the 2026-09-17 ruling also said the mat has *"no fuel, no upkeep, no starvation clock"*. That still
holds **inside the Rot**. **Outside the Rot** the 2026-10-22 ruling replaces it: the mat needs food there. The
header of `src/RimMandrake/EnvironmentalHazards/Source/RM_MapComponent_WarmGround.cs` now says this.

**This breaks the cross-biome promise rule, and the owner ordered it.** Biome mechanics are promised inside OUR
biomes only (owner, 2026-10-15). The portable mat is an explicit exception the owner ordered: it is promised
on every map a gravship can carry it to, because that is the point of the reward. No other Rot mechanic becomes
cross-biome because of this.

Reading of *"but it not naturally occurs in the rot"*: the most likely meaning is *"but it only naturally occurs
in the Rot"* (the mat grows wild only there; anywhere else it is grown by hand). The literal reading, *"the
portable form never occurs naturally in the Rot"*, is also possible. The build below works under both readings.
Only the way you get it depends on which one is right (open question 1).

## What exists already (measured from source, 2026-10-22)

- **Warm ground** (`ROT_WARM_MAT_1`): `RM_MapComponent_WarmGround` in EnvironmentalHazards. It runs on a map
  whose BiomeDef carries `RM_WarmGroundExtension`, and that is only `RM_TheRot`, unless the owner turns on the
  Rot's cross-biome option. A proper indoor room is "on the mat" when ≥60% of its cells are one of
  `RM_TheRotGrass`, `RM_TheRotSoilRich`, `RM_MycelialSoil` or `RM_MycelialMatting`. Such a room gets
  `min(offset/36, target − current) × cellCount` of heat every 250 ticks, toward
  `min(outdoor + offset, 21 °C)`. The offset is 18 °C × the Rot's warmth slider. It has no state and needs no fuel.
- **Living produce heat** (`ROT_DECAY_HARVEST_1`): `RM_MapComponent_LivingProduce`. It is **already carried by the
  thing**, not the biome: any ThingDef with `RM_LivingProduceExtension` warms its room on any map. The ruling
  needs no change for produce. It "works anywhere" today. The Rot's own screen scales it only on Rot and
  cross-biome maps.
- **Gravship reward precedent**: `RM_SwallowedDriveCore` is a minified building cut out of a hwelgrue. It is
  installed on substructure and links to the grav engine as a facility. In Odyssey, everything standing on
  substructure flies with the ship. The mat root follows the same idea: a minifiable building that is not built
  but earned, and that travels because it stands on the ship.

## The design

### The object: `RM_LivingMatRoot` ("living mat root")

- A 1×1 minifiable building that cannot be built (no designator, no cost). Market value is high. It can be
  uninstalled and reinstalled like any furniture. It works on ordinary ground, on built floors and on gravship
  substructure. It does **not** require substructure: *"make it work anywhere"*.
- It is a heart, not a heater. It does not warm anything by itself. It feeds the **mat floor around it**, and the
  mat floor is what warms the room, under the same rule as the Rot's own mat (≥60% of the room's cells are mat,
  heading toward `min(outdoor + offset, 21 °C)` with the same ramp). A room fully covered in mat around a fed
  root is exactly a Rot mat room: the same heat, the same cap. That is the 2026-09-17 "helps a lot, not
  trivialises" number, carried over unchanged.
- **Art**: it reuses the existing `RotSporeKit/Terrains/MycelialMatting` texture, drawn at 1×1, so it reads as a
  patch of the mat. No new art is queued, because the art status is not NONE. A dedicated sprite is a cosmetic
  change, a delegated art call (`delegation_policy.md`; open question 4).

### Food: what it eats, who feeds it, what starving does (outside the Rot)

- It **eats raw food**: the `FoodRaw` category (raw meat, raw plant food, animal products such as eggs and milk).
  Food is loaded through vanilla `CompRefuelable`. The gauge reads "Food". Colonists keep it topped up with the
  ordinary refuel work (haulers), with an auto-refuel toggle, exactly like a campfire. No new job. *What* it eats
  is open question 2.
- **Appetite** (PROVISIONAL): 3 units a day to stay alive, plus 1 unit for each cell of mat it grows. It holds
  30 units (10 days of upkeep). The Mod Settings appetite slider scales both numbers.
- **Starving**: when the gauge reaches 0, the mat stops warming at once, and the inspect pane says so. After a
  2-day grace period (PROVISIONAL), the mat **dies back**: about every 2 game hours, one cell of the mat the root
  grew turns back into the ground underneath it. The root never dies and never removes mat it did not grow.
  Feed it and it recovers. *No pawn or animal vanishes, and every change is visible on the floor* (the Direct Sun
  ruling's "no readable sign" rule, applied here).

### Growing in other biomes only when tended

- While the root is fed (gauge ≥ 50%) it **spreads mat**: about every game hour (PROVISIONAL), it lays one cell of
  `RM_MycelialMatting`. The cell is within 6 cells of the root, in the root's own room (or outdoors, when the root
  is outdoors), and next to the root or to existing mat. Each cell costs 1 unit of food.
- It spreads only onto bare ground or substructure. It never lays mat over a floor the player built, over water or
  under a wall. The mat is a floor layer, so dying back (or deconstructing it) uncovers the original ground.
- An unfed root never spreads, so outside the Rot the mat grows **only when tended**, as ruled.

### The Rot exemption: the shared lore

- On a Rot map, the root **eats nothing and still spreads**. The inspect pane gives the in-game reason:
  *"Joined to the Rot's network: the living ground feeds it."* This is the Rot's established lore. Its organisms
  share one body: wounds are shared through `RM_KinMendingNetwork` and the health-sharing comps, and the Rot is
  the one biome where the network runs. A root set down in the Rot plugs back into the network it was cut from.
- In the Rot, heating is left to the biome's own `RM_MapComponent_WarmGround`, which already warms mat rooms with
  no fuel. The root adds no heat of its own there, so a room is never heated twice. The same guard applies on a
  cross-biome map where that component is already running. Those maps are **not** the Rot, so the root still
  needs food there.
- The exemption is decided by the map's biome (`RM_TheRotFront.IsRotBiome`). A gravship in orbit, or on any other
  biome, is not the Rot.

### Heat stays at the ruled cap

The target, the ramp and the cap are the same numbers as the Rot's mat. The root adds no heat of its own beyond
what its mat gives. Calibration, from the existing component's arithmetic: a 10×10 room fully covered in mat on a
−19 °C night settles near −2 °C. A heater then has 22 °C to cover instead of 39. *"Helps a lot"*: yes.
*"Trivialises"*: no.

### Mod Settings (the Rot's screen, a new "Portable warm mat" group)

| field | default | does |
|---|---|---|
| `portableWarmMat` | on | Master for the root. Off: the root neither heats, eats, spreads nor dies back. It is inert furniture. |
| `portableWarmMatWarmth` | 1.0× | The warmth dial off the Rot (the same 18 °C offset × this). The 21 °C cap is not a setting. |
| `portableWarmMatAppetite` | 1.0× | Scales both upkeep and spread cost (0.25–3×). |
| `portableWarmMatSpread` | on | Off: the root keeps the mat it has, but never grows more. |
| `portableWarmMatDieBack` | on | Off: a starving root stops heating, but its mat never dies back. |

Every setting is off-safe: all of them off means an inert building. None of them affects worldgen.

## Built offline (this item)

- `src/RimMandrake/TheRot/Source/RM_LivingMatRoot.cs`: `CompProperties_RM_LivingMatRoot` and `RM_CompLivingMatRoot`
  (heat, appetite, spread, die-back, Rot exemption, inspect string, saved state), plus `RM_LivingMatRootProof` for
  `jawa/static_call`.
- `src/RimMandrake/TheRot/Defs/ThingDefs_Buildings/RM_LivingMatRoot.xml`: the building and its `CompRefuelable`.
- Settings fields, UI and Scribe lines in `RM_TheRotMod.cs`. Functional-script rows in `TheRot/validation.py`
  (a `living_mat_root` chain plus static checks), and must-be-true lines in
  `design/validation_walks/RimMandrake/TheRot.md`.

**Not built: any way to obtain it.** Open question 1 decides that. Until then it exists only through dev spawn,
which is enough for the live criteria.

## Live criteria owed

- L2: on a non-Rot quicktest map, a dev-spawned root in a sealed room spreads mat while it is fed and stops when
  it is empty. On a room ≥60% covered in mat, the room temperature rises toward `min(outdoor+18, 21)` and never
  above 21 °C. A starved root's grown mat dies back after the grace period. (`RM_LivingMatRootProof.ProofSweeps`)
- L2: on an `RM_TheRot` map, the root's food gauge does not move over a day of ticks, and it still spreads.
- L2: minify it, reinstall it on gravship substructure, launch and land. The root and its mat floor arrive.
  (UNMEASURED: whether Odyssey carries a top-layer floor laid over substructure. The engine stores foundation
  and top terrain separately, `TerrainGrid.foundationGrid` and `topGrid`, but whether launch copies the top
  layer has not been observed.)
- L4: the owner plays a cold-biome stop with it: does it "help a lot"?

## Open questions for the owner

1. **How is it won?**
   1. **Found growing in the Rot**: a few roots stand wild on every Rot map, and you dig one up and fly it home.
      Buys: the simplest route; it fits "naturally occurs in the Rot". Costs: wrong if your "not" was literal.
   2. **A quest reward**: a faction (or the navigator-log salvage site) gives a root once a quest is done.
      Buys: it is a real reward, and it fits the literal "not naturally". Costs: a quest has to be written.
   3. **Cut from the hwelgrue's gut**, like the drive core. Buys: it reuses a reward route that already exists.
      Costs: it piles a second prize on the one giant.

   **Recommended: 1**, if your sentence meant "only naturally occurs in the Rot". **Otherwise 2.**
2. **What does it eat?**
   1. **Raw food only** (meat, vegetables, eggs, milk). Buys: a simple rule, and a real food cost. Costs: it
      competes with the kitchen.
   2. **Raw food and corpses**. Buys: it fits a fungus, and it gives corpses a use. Costs: the refuel work hauls
      corpses into a bedroom.
   3. **Rot produce only** (glimmerslime, dulcis). Buys: it ties the root to the Rot. Costs: off the Rot it
      starves once the hold runs dry.

   **Recommended: 1**, which is built.
3. **Can players cultivate more roots?**
   1. **No: one root per prize.** Buys: it stays a reward. Costs: none.
   2. **A well-fed root buds a second one now and then.** Buys: a long-term goal. Costs: free heat multiplies.

   **Recommended: 1**, which is built.
4. **Dedicated art?** The root is currently drawn as a square of the mat texture.
   1. **Keep the mat square.** Buys: no cost. Costs: it reads as a floor tile, not as an object.
   2. **Queue a sprite** (a knotted, pulsing root in the mat). Buys: it reads as a prize. Costs: an art run.
      This is a cosmetic change, so it needs your permission.

   **Recommended: 2.**
