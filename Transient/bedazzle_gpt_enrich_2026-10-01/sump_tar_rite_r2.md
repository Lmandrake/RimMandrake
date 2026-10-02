**Offerings check:** the best dining table; a bonded animal’s last-used bed; the fullest barrel from the busiest pump; a wick-garden’s dried harvest; a ground-penetrating scanner.  
**Systems touched check:** colonist grudges and social AI; bonded-animal rescue and pens; pump networks and industrial terrain; agriculture and fire; the dormant tar beast and structural evacuation.

## 1. The Table Names the Grudge (Rite B)

- **What goes in the tar (from this colony):** The colony’s highest-quality dining table as the good price, beside an effigy of a present colonist whom another colonist genuinely hates.
- **What the player sees on this map, and when:** At the next communal meal, tar-black handprints appear around the largest remaining gathering place and the Narrator announces an account due. The effigied pawn and up to four colonists holding real negative memories of them gather there. A visible lottery produces accusations, an interruptible social fight, or one claimant attempting to smash furniture assigned to the target. All resulting injuries, mood memories and opinion changes come from ordinary interactions—not a ritual-applied status.
- **Why a player on this map cares:** It puts the colony’s actual doctor, builder, spouse or troublemaker—and the relationships holding the settlement together—at risk.
- **How it works in RimWorld 1.6:** A `RitualOutcomeEffectDef` snapshots the target and eligible memories; an `IncidentDef` creates a short `LordJob`, while `JobDriver_AirGrievance` dispatches vanilla social interactions or property damage. Settings expose participant count and escalation odds.
- **Readable signs:** Named target and grievance, handprint decals, gathering countdown, argument motes, and freely draftable participants.
- **Drawn from:** [RimWorld: Ideology](https://rimworldgame.com/ideology/) and [Dwarf Fortress taverns](https://dwarffortresswiki.org/index.php/Tavern). Those produce ritual gatherings or ambient social trouble; this spends beloved communal furniture to force one saved, local grudge into the open.
- **Size:** M.

## 2. The Empty Stall Remembers (Rite A)

- **What goes in the tar (from this colony):** The highest-quality animal bed most recently used by one of the colony’s bonded animals; the animal itself never enters the tar.
- **What the player sees on this map, and when:** During the next sleep period, sump-mice flee the animal’s pen and a thin ring of tar begins closing around it. Over six hours the ring cuts toward the pen gate and feed access, giving time to rope out the herd, dismantle fencing, or lay duckboards across it. The offered bed’s former occupant is always named and visible; if caught inside, it remains selectable and can be rescued. The ring slumps back after a day, leaving fouled ground but nothing harvestable.
- **Why a player on this map cares:** It turns a cherished bonded animal and the colony’s carefully built winter feed arrangement into an immediate rescue problem.
- **How it works in RimWorld 1.6:** A usage `ThingComp` identifies the bed’s last bonded sleeper; a `MapConditionDef` lays concentric `TerrainDef` cells around its current pen and invalidates the path and pen grids after each step. Settings control warning, radius and persistence.
- **Readable signs:** Named-animal letter, fleeing mouse-lines, highlighted next ring, tar sounds, and uninterrupted pawn/animal markers.
- **Drawn from:** [RimWorld’s animal pens](https://rimworldwiki.com/wiki/Pen) and [Dwarf Fortress pastures](https://dwarffortresswiki.org/index.php/Pasture). Both make enclosure logistics important; neither turns surrendered shelter into a slow, telegraphed extraction emergency.
- **Size:** M.

## 3. The Pump Pays Backward (Rite A)

- **What goes in the tar (from this colony):** A sealed barrel containing one full day’s output from the colony’s highest-throughput active pump.
- **What the player sees on this map, and when:** Within 24 hours, that pump network’s gauges reverse and mouse-lines abandon its pipe route. Residual pressure then drives existing tar backward into its snapshotted barrel yard or pump shed, flooding cells from the output end rather than belching randomly from a pit. Depowering machinery slows the advance but cannot erase stored pressure; doors, conduits and access lanes may still be buried. The tar comes from the intake pond, cannot be collected during the incident, and creates no additional product.
- **Why a player on this map cares:** The industry keeping a Sump colony solvent becomes a layout-dependent threat to its own storage, power and escape routes.
- **How it works in RimWorld 1.6:** A `RitualOutcomeEffectDef` records the busiest `CompTarPump` network and its output footprint; an `IncidentDef` starts a `MapConditionDef` whose main hook reverses that network’s placement flow. Settings tune warning, affected cells and infrastructure damage.
- **Readable signs:** Reversing gauges, pipe overlays, named network, marked flood front and sequential pump-stall sounds.
- **Drawn from:** [Oxygen Not Included](https://www.klei.com/games/oxygen-not-included) and [Factorio](https://factorio.com/game). Their fluid failures are reusable engineering puzzles; this makes one colony’s actual production history return as a non-recoverable ritual incident.
- **Size:** M.

## 4. The Field Keeps One Candle (Rite A)

- **What goes in the tar (from this colony):** Dried wick-stems equal to one complete harvest of the colony’s oldest surviving wick-garden—never living plants.
- **What the player sees on this map, and when:** Six to eighteen hours later, the Narrator names that growing zone and a natural seep flame appears at its tarward edge. A slow line of ordinary fire follows adjacent wick-plants across the exact stored footprint, stopping at harvested cells, bare soil or a player-cut firebreak. It can escape into nearby buildings if neglected, using only vanilla fire and temperature. It teaches no technology and leaves no special resource behind.
- **Why a player on this map cares:** The colony must choose between an emergency early harvest and risking its slow-grown lighting crop, stores and neighboring rooms.
- **How it works in RimWorld 1.6:** The ritual worker stores a `Zone_Growing` load ID and cell set; a small `MapConditionDef` performs a breadth-first front through qualifying plants and calls vanilla fire-start logic. Settings govern delay, spread interval and maximum ignitions.
- **Readable signs:** Named garden, edge sparks, previewed next cells, ordinary fire warnings and the already-ruled seep-flame art.
- **Drawn from:** [Don’t Starve’s wildfires](https://dontstarve.wiki.gg/wiki/Wildfire) and [RimWorld fire](https://rimworldwiki.com/wiki/Fire). Those spread through general flammability; this fire keeps the shape of a particular surrendered harvest and is never gated by heat or darkness.
- **Size:** S.

## 5. When the Beast Turns Over (Rite A)

- **What goes in the tar (from this colony):** The colony’s complete ground-penetrating scanner, still carrying its most recent survey.
- **What the player sees on this map, and when:** Within 36 hours, every mouse-line runs outward from the dormant tar-beast bulge and the Narrator marks an evacuation radius. The beast does not wake, spawn or travel: it rolls once beneath the sheet-tar, sending two or three visibly telegraphed pressure rings across the ground. Each ring can crack glasswalk, collapse dig shafts and damage structures; caught pawns and animals take ordinary impact damage or stun but remain visible in place. The bulge then settles, leaving damaged terrain and no carcass, resource or loot.
- **Why a player on this map cares:** The colony must temporarily abandon whichever bedrooms, shafts, pumps or animal pens it knowingly built inside the old bulge’s reach.
- **How it works in RimWorld 1.6:** Available only with an existing dormant-beast `MapComponent`; the outcome schedules `MapConditionDef RM_BeastTurning`, which advances static radial `ThingDef` overlays and applies `DamageInfo` to occupied cells. Settings control rings, warning time and structural damage.
- **Readable signs:** Outrunning mice, named bulge, radius overlay, deep knocks, screen shake and cell-by-cell impact markers.
- **Drawn from:** [RimWorld: Anomaly](https://rimworldgame.com/anomaly/) and [Dwarf Fortress cave-ins](https://dwarffortresswiki.org/index.php/Cave-in). Those introduce map-scale horrors or collapses; this neither spawns nor redirects a monster—it makes the established, unfightable beast briefly turn in its sleep.
- **Size:** L.

1. **Build first:** *The Field Keeps One Candle*—small, immediately legible and rooted in a resource unique to this map.  
2. **Build second:** *The Empty Stall Remembers*—it puts a beloved animal at stake without sacrificing or secretly removing it.  
3. **Why this order:** Together they validate stored map footprints, advancing terrain fronts and readable evacuation play before touching pump networks or the tar beast.