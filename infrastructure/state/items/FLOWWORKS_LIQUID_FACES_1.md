# FLOWWORKS_LIQUID_FACES_1 — every liquid, every face

Owner ticket, 2026-09-24, typed at the Sump flow round, verbatim:

> "Add a ticket item for Flowworks to consider floods, rain, rivers, lakes, and
> oceans of every supported kind of fuel and liquid in the mod."

## what this is

The generalization of the Sump's tar hydrology (`SUMP_TAR_HYDROLOGY_1`) to the
whole LiquidDef registry: for EVERY supported liquid and fuel row
(`liquids_framework_design.md` §2's roster — water grades, tar, the slime trio,
chemfuel, propane, blood, brine, the ManyWaters adoptions, …), consider each of
the five faces:

| face | engine slot today |
|---|---|
| floods | FlowWorks pulsed spread (the engine's home turf) |
| rain | weather form slot (reserved in the framework; tar rain is the pilot) |
| rivers | terrain suite + flow seams (⚠️ map edges are SINKS, never sources — the edge law, `SUMP_TAR_HYDROLOGY_1` ruling 6) |
| lakes | terrain bodies + landmark meres (the Deep Black is the pilot) |
| oceans | terrain/worldmap body slot (⚠️ the frozen world map is NOT touched — map-scale and lore faces only until the paint pass; an on-map ocean canal-connected = infinite source, per the edge law) |
| **ground pump** | buildable on-site producer filling canals — owner, typed, 2026-09-24, verbatim: *"for flow works for some liquids it will make sense to be able to add a ground pump to produce the liquid on site to fill canals these should be switchable options in the mod because it is scenario dependent on whether it makes sense clearly"* ⇒ per-liquid YES/NO in the matrix, and every YES ships as a **Mod Settings toggle** (scenario-dependent by ruling — same mod-vs-scenario split as tar rain). The Sump's Junker pumping derricks are the fiction precedent |

## spec

A design pass over the registry: one matrix, liquids × five faces, each cell
YES (with the biome/mod that hosts it) / NO (with why — hazard, absurdity,
scope) / LATER. Safety and flavor per liquid matter (a chemfuel lake and a
propane rain are weapons, not scenery — the Propane Lakes sheet already owns
one such body). Card the matrix to the owner in one review; the Sump pilots
(tar) are the worked examples. Build items then spawn per YES cell that some
mod actually wants — this ticket itself builds nothing.

## verify

The matrix exists, every registry row has all five cells answered, the owner has
ruled the review, and each YES names its hosting mod/biome.

## criteria

Any liquid FlowWorks knows can appear anywhere a liquid appears — deliberately,
per ruling, never by accident.
