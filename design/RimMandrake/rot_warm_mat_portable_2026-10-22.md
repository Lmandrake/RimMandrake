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

### The second card (owner, 2026-10-22: "Rot mat cards 2026-10-22 → quest reward, raw food, buds, keep floor-tile art")

1. **How it is won: a quest reward.** The root is never found wild; it is earned (the literal reading of *"it not
   naturally occurs in the rot"*). Built as the dead ship's log's last camp, below.
2. **Diet: raw food only**, as built.
3. **Budding: "A well-fed root buds a second one now and then."** This changes the build. **The cost he accepted:
   free heat multiplies.** It stays bounded: a hard cap of roots per map, and every root heats only through the
   same mat-room rule at the same 21 °C cap, with one heat push per room per sweep. More roots grow more mat, on
   more rooms; no room gets hotter than one root makes it. The 2026-09-17 *"helps a lot, not trivialises"* number
   is unchanged.
4. **Art: "It is a floor tile. A living floor tile."** The mat-texture square is the art. No sprite is queued
   (the art ledger has no job for it: `artpipe_state.py find RM_LivingMatRoot`, 2026-10-22).

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
- **Art**: the existing `RotSporeKit/Terrains/MycelialMatting` texture, drawn at 1×1: a living floor tile (owner,
  2026-10-22). `validation.py`'s `mat_root_checks` goes red if the def ever names another texPath.

### How it is won: the crew's last camp (quest reward)

- The dead ship's log (`RM_NavigatorLog`, ROT_NAVIGATOR_LOG_SITES_1) reveals a salvage site at entries 2, 4, 6 and 8.
  Its **last** site entry (`lastCampEntry` 8) now reveals **`RM_NavigatorLastCamp`** instead: the camp past the third
  ridge where the crew stopped walking. The warm mat took them in, gently and completely, and where they lay a root
  of it knotted itself. *Generous and hungry; the Rot shares everything, including you.*
- The quest is the salvage site's own shape (an item stash, defended whenever violent quests are allowed, no
  timeout), plus one node, `RM_QuestNode_AddMinifiedToStash`, which puts a minified `RM_LivingMatRoot` in the stash.
  The player walks or flies there, carries the root home and installs it. Quest text is a DRAFT (FOUNDRY, free tier).
- **Firing route**: C# only. `RM_NavigatorLog.ReadEntry` → `SiteScriptFor` → `TryRevealSite`, when the swallowed
  core's pings reach entry 8 (8 × `navigatorPingsPerEntry` pings; at the defaults, 32 pings × 12 h with a grav
  engine on the giant's map). `validate_quest.py` reports `never-fires` for it, as it does for the salvage site,
  because it cannot see a C# route. With the root switched off in Mod Settings, entry 8 reveals a plain salvage site.
- **Site tiles**: free tier, the vanilla tile finder near the colony. The campaign's tiles for the log are
  `campaignSiteTiles`, which wait for the world remake. This build picks no tile.
- **The cost of this route**: the root goes only to a player who keeps the giant alive long enough to hear the
  whole log. Cutting the drive core out early ends the log, and the root with it. That is the trade the log's last
  line already asks for (*"Cut the beast open gently. It never meant us harm."*).

### Food: what it eats, who feeds it, what starving does (outside the Rot)

- It **eats raw food**: the `FoodRaw` category (raw meat, raw plant food, animal products such as eggs and milk).
  Food is loaded through vanilla `CompRefuelable`. The gauge reads "Food". Colonists keep it topped up with the
  ordinary refuel work (haulers), with an auto-refuel toggle, exactly like a campfire. No new job. Raw food only is the
  owner's ruling (2026-10-22 card).
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

### Budding: a well-fed root buds a second one now and then

- **Well fed** (measurable): the gauge is at least 80% full (`budWellFedPercent`) after the sweep's meal. In the Rot
  the network feeds it, so it is always well fed. The bud clock runs only while the root is well fed and restarts
  the moment it is not.
- After `portableWarmMatBudDays` (15, PROVISIONAL) well fed, the root rolls `portableWarmMatBudChance` (50%,
  PROVISIONAL). On a hit, a new root sprouts on a cell of mat in its own room and radius, at least 2 cells from every
  root, farthest first. A message names it. Hit or miss, the clock restarts.
- Off the Rot a bud costs 10 food × appetite (`budCost`), and the new root starts with that food.
- **Hard cap**: a map never holds more than `portableWarmMatBudCap` roots (3; slider 1–6). Installed and minified
  roots both count, so uninstalling roots and letting the rest bud again cannot get past it. A root carried to
  another map counts on that map; the cap is per map, as ruled.
- The clock and roll are `RM_TheRotKernel.MatBudStep`, fuzzed offline (`selftest_therot_fuzz.py --fuzz-only mat`,
  coverage `mat.bud`, `mat.budCapped`); `mutate_therot_fuzz.py bud` plants seven defects (cap gone, cap off by one,
  merely fed counts as well fed, roll ignored, clock never restarts, clock survives hunger, free off the Rot) and
  the fuzz catches all seven.

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
| `portableWarmMatBudding` | on | Off: roots never bud. |
| `portableWarmMatBudDays` | 15 | Days well fed between bud rolls (3–60). PROVISIONAL. |
| `portableWarmMatBudChance` | 50% | Chance a roll buds (5–100%). PROVISIONAL. |
| `portableWarmMatBudCap` | 3 | Most roots on one map, installed and minified (1–6). |

Every setting is off-safe: all of them off means an inert building. None of them affects worldgen.

## Built offline (this item)

- `src/RimMandrake/TheRot/Source/RM_LivingMatRoot.cs`: `CompProperties_RM_LivingMatRoot` and `RM_CompLivingMatRoot`
  (heat, appetite, spread, die-back, budding, Rot exemption, inspect string, saved state), plus `RM_LivingMatRootProof`
  (`ProofStage`, `ProofSweeps`, `ProofBud`) for `jawa/static_call`.
- `src/RimMandrake/TheRot/Source/RM_NavigatorLog.cs`: `lastCampEntry`/`lastCampQuest`, `SiteScriptFor`,
  `RM_QuestNode_AddMinifiedToStash`, `RM_NavigatorLogProof.ProofLastCamp`; the quest `RM_NavigatorLastCamp` in
  `Defs/Misc/RM_NavigatorLog.xml`.
- `src/RimMandrake/TheRot/Defs/ThingDefs_Buildings/RM_LivingMatRoot.xml`: the building and its `CompRefuelable`.
- Settings fields, UI and Scribe lines in `RM_TheRotMod.cs`. Functional-script rows in `TheRot/validation.py`
  (a `living_mat_root` chain plus static checks; `mat_root_checks` with six planted defects under `--planted`; the
  mock plants `nobudcap`, `nobud`, `noreward`), and must-be-true lines in
  `design/validation_walks/RimMandrake/TheRot.md`.

## Live criteria owed

- L2: on a non-Rot quicktest map, a dev-spawned root in a sealed room spreads mat while it is fed and stops when
  it is empty. On a room ≥60% covered in mat, the room temperature rises toward `min(outdoor+18, 21)` and never
  above 21 °C. A starved root's grown mat dies back after the grace period. (`RM_LivingMatRootProof.ProofSweeps`)
- L2: on an `RM_TheRot` map, the root's food gauge does not move over a day of ticks, and it still spreads.
- L2: minify it, reinstall it on gravship substructure, launch and land. The root and its mat floor arrive.
  (UNMEASURED: whether Odyssey carries a top-layer floor laid over substructure. The engine stores foundation
  and top terrain separately, `TerrainGrid.foundationGrid` and `topGrid`, but whether launch copies the top
  layer has not been observed.)
- L2: on a non-Rot quicktest map, `ProofBud 8` fills the map to the cap and never past it.
- L2: `RM_NavigatorLogProof.ProofLastCamp` generates `RM_NavigatorLastCamp`, and its site's stash holds a minified
  root. Visiting the site puts the root in the cache's stockpile (UNMEASURED: a minified building through
  `GenStep_ItemStash`'s stockpile has not been observed).
- L4: the owner plays a cold-biome stop with it: does it "help a lot"? With two or three budded roots, does it still
  not trivialise?
