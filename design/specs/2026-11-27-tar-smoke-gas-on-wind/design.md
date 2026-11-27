# Tar smoke and gas on the wind (FlowWorks 0.2.0 design)

Item: `RIMMANDRAKE_DESIGN_TAR_SMOKE_AND_GAS_ON_THE_WIND`. Status: a design for his look. Divergent. It moves no 0.1.0 bar.
Written 2026-11-26 by the Designer, offline. Nothing here is built.

## 1. His words

Walk of 2026-11-25, station 75 (`D:\ClaudeWork\rimmandrake\showings\FLOWWORKS_WALK3_20261125\his_words.md`):
*"It should also make horrible smoke (burning tar produces choking smoke that should blow with the wind). That's a big
area likely for the next version of FlowWorks: gas flows in the air with and without wind, sealed in rooms, and the
effects they have. What a beast of a mod."*

The same walk says that tar catches and burns too fast. That is a separate item
(`RIMMANDRAKE_SLOW_TAR_FIRE_IT_WENT_UP_IN_A_WHOOSH`). This design does not change how tar catches or burns.

## 2. What the game has today (read 2026-11-26)

RimWorld 1.6, from the decompile at `D:\ClaudeWork\rimmandrake\decomp\rw16\all\Verse\` (RimSage was not reachable from
this session; the decompile is the same source):
- `GasGrid` packs four gases into one `uint` per cell, one byte each: BlindSmoke, ToxGas, RotStink, DeadlifeDust. There
  is no free byte for a fifth gas.
- Each tick it visits area/64 cells to dissipate and area/32 cells to diffuse, in a fixed random order. Diffusion moves
  half the difference to a cardinal neighbour when that half is 17 or more. Dissipation per visit: smoke 4, tox 3, rot
  stink 4, deadlife 3. A roof halves it. Vacuum (Odyssey) multiplies it by 25 more.
- `GasCanMoveTo`: a full-fillage edifice blocks gas. A door passes gas only when it is open.
- `Building_Vent` equalizes tox, rot stink and deadlife (not BlindSmoke) through itself on `TickRare`.
- Nothing in `GasGrid` reads wind, rain or weather. `WindManager` has a speed only (0.04 to 2, scaled by weather and
  conditions). **RimWorld 1.6 has no wind direction. Wind moves no gas today.**
- Effects: shots through BlindSmoke have 0.7 accuracy (`ShotReport.factorFromCoveringGas`). ToxGas gives
  `ToxGasExposure` and toxic buildup (Biotech). RotStink gives lung rot exposure. Apparel or a gene with
  `immuneToToxGasExposure` protects: `Apparel_GasMask`, `Apparel_VacsuitHelmet`, `ToxicEnvironmentResistance_Total`.
- Vanilla `Fire` throws smoke flecks only. A fire makes no gas.

Our files:
- FlowWorks tar fire: `RM_LiquidFire` (channels) and `RM_SheetFire` (spills). Each burning cell runs an effects step
  every 60 ticks (`EffectEvery`, `ApplyEffects`, `ApplyInfernoEffects`, the sheet's effects). That step is the place to
  emit smoke. Tar and oil are `CreepingFuse`, chemfuel `Inferno`, astrofuel `Detonation` (`FlowWorks_Fluids.xml`,
  `FlowWorks_PitFluids.xml`). FlowWorks already vents vanilla ToxGas from a failed reaction (`RM_LiquidReaction`).
- Cauldron already has a drifting gas (`src/RimMandrake/Cauldron/Source/RM_VentGas.cs`,
  `Kernel/RM_VentGasKernel.cs`). It keeps its own byte grid, ports vanilla's diffusion and dissipation, asks
  `GasGrid.GasCanMoveTo` for walls and doors, draws through a `SectionLayer_Gas` subclass, and adds a wind drift: a
  quarter of a thick cell moves one cell along one of eight headings, which jumps once a day. Its kernel is Verse-free and
  runs offline in `Cauldron/Source/SelfTest/CauldronFuzz.cs`. It is the proof that this design can be built.
- Six mods each invent their own wind direction: Cauldron (daily heading), The Forge and Scarlands (one fixed seeded
  bearing), Pyrelands (from yesterday's scar edge), Leaning Scrub (the lean), Moving Dunes (from the sun bearing).
- Pyrelands smoke weather (`RIMMANDRAKE_BUILD_PYRE_SMOKE_WEATHER_ONLY_LONGSHADE_HAS_ONE`, Pyrelands 0.2.0) is a
  map-wide weather. This design is a local plume. They share one lung effect (section 4); neither owns the other.

## 3. The range of situations

What the game can vary for this mechanic:
- the source: one burning tar cell, a 200-cell moat, a spill, oil, chemfuel; inside a pit, under a deck or cover, in a
  room;
- the air: wind from calm to gale (weather and conditions set it); the wind direction; rain, snow, none; vacuum on a
  gravship in space;
- the surroundings: open ground, walls, open or closed doors, vents open or shut, a roofed room open to the outside, a
  sealed room, a covered pit, the map edge;
- who breathes it: colonists with and without a gas mask, animals, raiders, mechanoids, babies, pawns held in a pit,
  drafted pawns;
- other gas in the same cells: vanilla smoke, tox gas, rot stink, Cauldron vent gas;
- map size, time, save and load.

Regimes that these make: **open air in wind** (a plume); **open air in calm** (a pall); **under a roof, open to outside**
(slow seep out of doors); **sealed room** (it fills and stays); **rain** (it washes out); **vacuum** (it is gone at once).

Left out, and why:
- Gas heavier than air that sinks into pits. No gas of 0.2.0 is heavier than air: tar smoke is hot and rises. A propane
  leak would be; that is a later idea.
- Smoke from vanilla fires (wood, grass, buildings). That changes every fire in the game. It is not his ask.
- Soot that harms plants or stains floors, and smoke that moves heat. Not asked; extra load (Principle 5).
- Raider AI that walks round smoke. Raid tests are paused, and raider will moved to 0.2.0's raid proof.
- Map-wide smoke weather. That is the Pyrelands item.

## 4. What the player sees and suffers

**The look.** Burning tar sends up a thick, black-brown smoke. Near the fire it is opaque. Downwind it thins to a
grey-brown haze. It must read as tar smoke at a glance: never the pale grey of vanilla smoke, never the yellow-green of
tox gas. The fire also throws dark smoke flecks for a rising column (the flame on a tar cell is a non-ticking look
only, so today no fleck rises from it).

**The shape.** In wind the smoke streams away in a long tail, and the tail turns when the wind turns. In calm air it
spreads slowly round the fire into a round pall and thins at its edge. A big burning moat makes a wall of smoke on its
downwind side.

**What it does to pawns.** One condition, "smoke in the lungs", for every pawn that breathes:
- It grows while the pawn stands in tar smoke, faster where the smoke is thicker. It fades in clean air.
- First stage, coughing: the pawn coughs (a fleck and a sound), sees worse and breathes worse.
- Second stage, choking: it also moves and works worse, and it has a bad mood thought.
- Third stage, suffocating: consciousness falls and the pawn collapses. A pawn left down in thick smoke dies. This is
  the sealed-room danger he named. (Question 4.)
- Readable signs, always before harm: the smoke is visible, the pawn coughs, the condition shows in the health tab, and
  an alert lists every pawn in choking smoke.

**Sight.** A shot through thick tar smoke has vanilla's covering-gas accuracy, the same as BlindSmoke. Smoke hides a
defence the way vanilla smoke does. A player can burn a moat upwind of raiders to blind and choke them.

**Animals.** They suffer the same condition and leave the smoke when they can. Colonists who are not drafted also leave
thick smoke for clean air. Drafted pawns stay where the player put them.

**Who is safe.** The condition reads physical conditions, not item names:
- a pawn with no breathing (mechanoids) is not affected;
- a pawn with apparel or a gene that sets `immuneToToxGasExposure` (the gas mask, the vacsuit helmet, total toxic
  resistance) breathes freely and does not lose sight;
- a pawn behind a wall, a closed door or a shut vent is in clean air.

**What blocks and moves it.** A wall stops it. A closed door stops it. An open door lets it seep through. An open vent
lets it through (unlike vanilla smoke). Rain thins outdoor smoke fast; snow less. Space vacuum takes it at once.

## 5. How gas moves

All four rules run in one kernel, the same for every gas kind of ours.

1. **Diffusion (always).** Vanilla's rule, ported as Cauldron did: half the difference to a cardinal neighbour, not
   through walls or closed doors (`GasGrid.GasCanMoveTo`).
2. **Drift (wind, outdoors only).** Only an unroofed cell drifts. On each visit, with a chance that grows with
   `WindManager.WindSpeed`, a thick cell pushes a share of its gas to the downwind side. The wind bearing is a free
   angle, not eight fixed headings: the share splits between the two neighbours that bracket the bearing, by weight. So
   the tail points where the wind points. Under a roof the air is still: smoke seeps out of an open door by diffusion,
   and the drift carries it off once it is outside. Gas that drifts off the map edge is gone.
3. **Dissipation (depends on the room).** Three cases:
   - outdoors: vanilla's open-air rate, faster in rain by the map's rain rate;
   - roofed, in a room that is open to the outside (an open door, an open vent, an open roof cell): vanilla's roofed
     rate;
   - **sealed room** (no open way out): settling only, much slower than vanilla. A sealed room fills and stays thick
     until someone opens a door or a vent. Then the room clears through it.
   Vacuum multiplies every case, as vanilla does. The room state is read once per room per sweep (`Room`), never per
   cell per tick.
4. **Vents.** On `TickRare` each open `Building_Vent` equalizes our gas through itself, as vanilla does for tox gas.

**The wind direction.** 1.6 has none, so we add one law. The bearing wanders slowly: it holds for hours, swings over an
hour or two, and sometimes backs round. It is a pure function of the map's seed and the absolute tick, so it needs no
save data and every mod that calls it gets the same answer. The player reads it: the weather readout (top right) gets a
wind line with a direction and a strength word; plants and smoke agree with it.

**Vanilla gases.** The same drift can move vanilla smoke, tox gas, rot stink and deadlife dust. It reads and writes them
only through `GasGrid`'s public `GetDirect` / `SetDirect`, with no Harmony patch on `GasGrid`. Vanilla dissipation does
not change. (Question 1.)

## 6. Vanilla GasGrid or our own field

**Recommendation: our own field for our gases, vanilla's grid untouched in storage.** Reasons:
- There is no free byte in vanilla's cell. A fifth gas means patching every reader of that `uint` and can break other
  mods' gases. Cauldron's ruling already chose a separate grid for this reason.
- Tar smoke must look like tar smoke. Vanilla's colours are fixed per gas type.
- Sealed-room pooling and rain washout need a dissipation that vanilla does not have. Changing vanilla's dissipation
  changes every gas in the game.
- Our field keeps vanilla's look of gas (a `SectionLayer_Gas` subclass), vanilla's walls and doors, and vanilla's
  diffusion law. A player sees one kind of physics.

Rejected: tar smoke as vanilla BlindSmoke plus ToxGas. It is cheap, but it looks pale and green, it never pools, and a
smoke grenade would choke. Rejected: Thing-based gas (`Verse.Gas`, as Environmental Hazards uses). One Thing per cell
cannot carry a 200-cell moat's plume at a sane cost.

## 7. Which mod owns the general gas mechanic

**Recommendation: FlowWorks owns the air field. The wind law is shared source.**
- FlowWorks moves liquids; gas is the same kind of physics. He named it FlowWorks' next version.
- FlowWorks is already under most of our biome mods: Cauldron, Cracked Lands and Environmental Hazards depend on it,
  and Blue Desert, Contagion and Fever Wood depend on Environmental Hazards. A new mod would add one more entry to every
  list and one more pipeline item.
- The field must be one MapComponent per map, so one mod must own it. Other mods add gas kinds by XML (a gas kind def)
  and emit through one public call.
- The wind law is a pure function in `src/RimMandrake/_Shared/Wind/` (the `AirHeatSetting` pattern: compiled into each
  mod that needs it). Pyrelands, The Forge and the others can read the same wind without a FlowWorks dependency. A
  biome may give a prevailing bearing as biome data (Pyrelands' scar edge, Moving Dunes' sun). Each of those mods
  converts at its own next version; this design moves none of their bars. (Question 3.)
- Cauldron's vent gas moves onto the FlowWorks field at Cauldron's next version. Not in this version.

The other way: a new RimMandrake-level "Air" mod. It is cleaner in name, but costs one more mod, one more settings
page, and a dependency for FlowWorks itself, because FlowWorks makes the smoke. (Question 2.)

## 8. What changes in code (FlowWorks 0.2.0)

- New `Source/Air/RM_AirKernel.cs`: Verse-free. Diffusion (vanilla port), drift by bearing and speed, dissipation by
  room state, rain and vacuum, emission with overflow. Copied from `RM_VentGasKernel` and widened; Cauldron's file does
  not change.
- New `RM_MapComponent_Air`: one byte grid per gas kind, a sweep budget, an active window (the box round all non-zero
  cells), save and load, a dev readout (total, cells, centroid, bearing, wind) in Cauldron's format for validation.
- New `RM_SectionLayer_AirGas`: draws each kind in its own colour.
- New `RM_GasKindDef` and `RM_Gas_TarSmoke`: colour, settling rate, rain washout, lung effect, sight effect.
- New hediff "smoke in the lungs", one thought, one alert, and a flee-from-smoke job for non-drafted colonists and
  animals.
- `FluidDef`: two new fields, the smoke kind and the smoke a burning cell makes. Set for tar and oil (heavy), chemfuel
  (light). Astrofuel and propane make none.
- `RM_LiquidFire.ApplyEffects`, `ApplyInfernoEffects` and the sheet fire's effects step: one emit call per burning cell.
  No change to ignition, front, burn rate or reach.
- One Harmony postfix on `ShotReport.HitReportFor`: thick tar smoke counts as covering gas.
- `_Shared/Wind/RM_WindLaw.cs` and a selftest that keeps the copies equal.
- Mod Settings: "Burning liquids make smoke" (on), "Wind moves gas" (on), "Wind also moves vanilla gases" (by
  question 1), "Smoke in the lungs can kill" (by question 4). Each row's tooltip says what on and off do.

## 9. Proposed 0.2.0 bars, each with its cheapest test

| # | Bar (experience) | Cheapest test |
|---|---|---|
| 1 | Burning tar sends up thick black-brown smoke that a player can tell from vanilla smoke and tox gas at a glance. | One live screenshot of a lit tar channel beside a smoke grenade and a tox cloud; the art judge, then his walk. |
| 2 | In wind the smoke streams away downwind in a tail; the player can read which way the wind blows; the tail turns when the wind turns. | Offline kernel: the cloud's centroid moves along the bearing and follows a turned bearing. Live: the dev readout's centroid moves along the readout's bearing. |
| 3 | In calm air the smoke spreads round the fire into a pall and thins away when the fire is out. | Offline kernel: calm air leaves the centroid on the source and the total falls to zero after the source stops. |
| 4 | A wall or a closed door stops the smoke; an open door or an open vent lets it through. | Offline kernel on a fake room: no gas crosses a wall or a shut door; gas crosses an open door and an open vent. |
| 5 | A sealed room with tar burning inside fills with smoke and stays thick; once opened, it clears. | Offline kernel: a sealed room keeps most of its gas over a day; the same room with a door open clears. |
| 6 | Rain thins outdoor smoke clearly faster than dry air. | Offline kernel: the same plume clears sooner under rain. |
| 7 | A pawn who breathes thick tar smoke coughs, then chokes, then collapses, with a visible sign at each step, and recovers in clean air; a gas mask keeps a pawn well. | Offline: the severity rule rises with density and falls in clean air. Live: one scene, two colonists in smoke, one masked; read the hediff and the alert. |
| 8 | Animals and non-drafted colonists leave thick smoke when they can. | Live: the same scene; the unmasked, undrafted pawn walks out. |
| 9 | Shots through thick tar smoke are less accurate, as through vanilla smoke. | Live: the shot report's covering-gas line reads the same factor for tar smoke as for vanilla smoke. |
| 10 | How tar catches, creeps and burns is the same as in 0.1.0, and every 0.1.0 fire scene still passes with smoke on. | The existing 0.1.0 fire tests (`canal_fire_burns_back`, `moat_drains_and_burns`, `toss_flame_from_rim`) re-run with smoke on. |
| 11 | A map with no burning liquid and no gas pays nothing for this. | Offline: the sweep does no cell work when the field is empty. Live: tick time with the setting on and off on the dev start, no fire. |

Bar 10 has one real risk: the toss-flame colonist stands on the rim of a burning chemfuel moat. Chemfuel makes light
smoke, and the colonist steps back from fire today. The re-run decides it.

## 10. Offline simulation: yes

Offline simulation: **yes**. Gas movement is physics with many cases (wind, calm, rooms, doors, rain, vacuum), and each
live check costs a staged scene. The form is the real kernel against a fake grid, not a second copy of the logic:
`RM_AirKernel.cs` is Verse-free and compiles alone into the FlowWorks selftest, as Cauldron's kernel does in
`CauldronFuzz.cs`. The fake world gives walls, doors, vents, roofs, rooms, rain, vacuum and a fake clock for the wind.
It covers bars 2 to 6, the severity rule of bar 7, and the empty-field cost of bar 11. It does not cover the look, pawn
AI, the shot report or the tick cost on a real map; those are live. One live check ties the two: the dev readout's
centroid on a staged plume against the kernel's prediction for the same wind.

## 11. Performance risks

- **Sweep cost.** Vanilla visits area/64 + area/32 cells each tick. Our field must not double that on every map. Skip
  all work when the field is empty (Cauldron's `NonZero == 0`), and sweep only the active window. Cost then scales with
  the smoke, not the map.
- **Big moats.** A 200-cell moat alight emits 200 cells each 60 ticks. Cap at 255 per cell; overflow spreads to
  neighbours with a small radius, never vanilla's 40-cell flood fill per cell.
- **Mesh rebuilds.** Marking a section dirty for each changed cell each tick can rebuild many meshes. Collect dirty
  sections and rebuild at a lower rate.
- **Room reads.** Read the sealed state once per room per sweep, cached; never a room lookup per cell per tick.
- **Vanilla drift.** It adds a sweep over vanilla's grid when that grid has gas. It uses the same window rule and runs
  only when vanilla's `CalculateGasEffects` is true.
- **Pawns.** One byte read per pawn each 50 ticks, as vanilla. No path cost patch (pathfinder patches are the expensive
  kind); the flee job only.
- **Memory and save.** One byte per cell per kind (a 250 x 250 map is about 62 KB per kind), saved compressed.

Load on every map (Principle 5): nothing on a map without burning liquid or gas; one wind line in the weather readout;
on a fire map, one more danger to read, which is the point.

In-world brake (Principle 3): the smoke ends when its fire ends; it thins in open air, wind and rain; walls and closed
doors hold it; masks protect. Nothing holds it back by a hidden limit.

## 12. Questions for him

1. **Does wind also move vanilla gases?** Smoke grenades, tox gas and rot stink would drift downwind; a smoke screen
   blows away in a gale. Recommendation: yes, default on, with a setting. Principle 1: wind is a condition, and a tox
   cloud that stands still beside a drifting tar plume reads false.
2. **Who owns the air field?** Recommendation: FlowWorks (section 7). The other way is a new "Air" mod.
3. **One wind for every mod?** Six mods have their own wind today. Recommendation: yes, one shared law; each mod
   converts at its next version, and a biome may still give a prevailing bearing as its data.
4. **Can tar smoke kill a pawn left in it?** Recommendation: yes, after the coughing and choking signs and a collapse,
   with a setting to stop at collapse. A sealed room that fills with smoke is only a danger if it can kill.
