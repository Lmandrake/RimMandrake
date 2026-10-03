# Surface river weirs — design (SURFACE_RIVER_WEIRS_1), 2026-10-02

Design only, for the owner to rule on. Nothing here is built, filed or claimed. Engine facts are
RimSage reads of the decompiled 1.6 source/defs (2026-10-02); anything not checked says UNMEASURED.

## 1. What exists (measured 2026-10-02, bench clone at e47414eb1)

Item: `SURFACE_RIVER_WEIRS_1` (proposed, v1, no item prose file). Source ruling: owner-typed Q3 on
`TWILIGHT_CHANNEL_CURRENT_1` — *"breach at default, and this should be ported to normal river tiles
too!"* — recorded in `design/Jawa/worldbuilding/biomes/the_twilight_deep_river_pass_2026-09-27.md` §7.
The design being ported is that doc's §4 ("the bank works").

All the bank-works code lives in **TerminalBiomes** (`mandrake.rm.terminalbiomes`, `src/RimMandrake/TerminalBiomes/`):

| file | lines | what it is |
|---|---|---|
| `Defs/ThingDefs_Buildings/RM_BankWorks.xml` | 155 | three buildable defs: `RM_BankStake` (Building, tickerType Never, 60 HP, 10 wood, small CompGlower), `RM_BankWeir` (thingClass `RM_Building_BankWeir`, 150 HP, 60 wood + 20 cloth, `CompProperties_ChannelArrester`), `RM_SiltTrap` (thingClass `RM_Building_SiltTrap`, 140 HP, 50 wood). All `repairable`, designationCategory Structure, **placeholder art** (reused Scald vent / steam-catch / salt-chimney textures) |
| `Source/RM_Building_BankWeir.cs` | 215 | HP wear (1 HP / 2000 ticks); every 600 ticks: if HP < 50 % **and** `RM_MapComponent_ChannelCurrent.SurgeActive` → `Breach()`: arrester off, ThreatBig letter-message, stake cascade (every `RM_BankStake` within r=15 takes full-HP Deterioration damage, staggered 150 ticks per cell of distance), and `Clog()` on every silt-trap within r=15. Re-arms when repaired back to ≥ 50 %. `neverBreaches` flag for the Compact's pre-placed weir |
| `Source/RM_Building_SiltTrap.cs` | 117 | HP wear (1 HP / 3000 ticks); while HP ≥ 40 %, every 30000 ticks swaps `RM_BankSilt` → `RM_BankSilt_Rich` within r=3.5, remembering the cells; `Clog()` reverts only cells still carrying the rich terrain |
| `Source/RM_MapComponent_ChannelCurrent.cs` | 848 | the sea-floor carry: authored flow/lane/band byte grids, occupant drift, sink, undersurge roll (MTB 4 or 12 days, only on maps with channel cells). Also hosts `CompChannelArrester` (a bool `Active` comp) |
| `Source/RM_GenStep_TwilightChannels.cs` | 348 | paints the channels, places the stake-line and one Compact weir |
| `Languages/English/Keyed/RM_ChannelCurrent_Mechanics.xml` | 23 | `RM_ChannelWeirBreach` text names "the undersurge" |

**Findings that shape the port (all measured by reading the files above):**

1. **The "dredge / tend / re-drive" jobs do not exist as jobs.** All three are vanilla `WorkGiver_Repair`
   on HP that decays on a timer, plus vanilla hauling of whatever the weir caught. That idiom is fully
   generic and ports for free.
2. **The silt-trap currently paints nothing anywhere.** `RM_BankSilt`, `RM_BankSilt_Rich` and
   `RM_FordStones` are referenced only by C# `GetNamedSilentFail` lookups and comments — no TerrainDef
   with those names exists in `src/` (grep over every `*.xml` under `src/` hits only the
   `RM_BankWorks.xml` comment). The trap stands, wears and clogs, and silently does nothing. So the
   farm-bonus half of the works is unbuilt *even on the sea floor*; the port must build it, not copy it.
3. **The weir's catch is the carry's exemption, nothing more.** `CompChannelArrester` is read only by
   `RM_MapComponent_ChannelCurrent.IsArrestedCell`; there is no hopper inventory ("the hopper's stock IS
   whatever is physically sitting there"). On a surface river, where nothing drifts, the weir as written
   catches nothing at all.
4. **The breach trigger is sea-only.** It needs `SurgeActive`, which is set only by
   `RM_GameCondition_Undersurge`, which only rolls on maps with authored channel cells. On a surface
   river map a weir would wear to 1 HP and never breach.
5. **Every tick is gated on the Twilight Sea's toggle.** Both buildings early-return unless
   `RM_TerminalBiomesSettings.ChannelCurrentActive` (= master && `twilightSeaEnabled` &&
   `channelCurrentEnabled`). A player who switches the Twilight Sea off would silently disable every
   surface weir too.
6. **No placement restriction.** None of the three defs carries a PlaceWorker or terrain affordance
   gate; a weir can today be built in the middle of a desert.
7. **Nothing outside TerminalBiomes references the three defs** (grep over `src/` `*.cs`/`*.xml`: only
   `RM_GenStep_TwilightChannels.cs` and `RM_TerminalBiomesDefOf.cs`).
8. **The weir cannot stand in a river today.** `BuildingBase` sets `terrainAffordanceNeeded Light`
   (RimSage, `Defs/Core/ThingDefs_Buildings/Buildings_Base.xml:11`), and `WaterMovingShallow`'s
   affordances are ShallowWater / WaterproofConduitable / Bridgeable / Walkable / MovingFluid — no
   Light. So the three defs can go on any dry Light ground (a desert, a hilltop), and never on the
   water they are about.

**FlowWorks overlap — re-verified.** The 2026-09-28 note on the item stands: FlowWorks
(`src/RimMandrake/FlowWorks/`) owns canals, fluid movement and excavation depth; a fresh grep for
weir / silt / stake / breach over `Source/` and `Defs/` hits only prose: "breach" in comments of
`RM_MapComponent_Excavation.cs` (lines 863, 1081) and `SelfTest/Program.cs:604` about moats draining,
and the word "staked" in `RM_LiquidDrill.xml`'s description. **No overlap.** FlowWorks does not touch
vanilla rivers at all beyond its own `Flood_FlowWorks` (a canal release that re-implements Odyssey's
flood walk over Core temp terrain).

### 1a. Engine facts about vanilla rivers (RimSage, measured)

| fact | source |
|---|---|
| River water is `WaterMovingShallow` / `WaterMovingChestDeep` (plus `ToxicWater…` twins). Both carry the `River` tag; `TerrainDef.IsRiver => HasTag("River")` | `Verse/TerrainDef.cs:320`; defs |
| `WaterMovingShallow` affordances: ShallowWater, WaterproofConduitable, Bridgeable, Walkable, **MovingFluid**; `extraDeteriorationFactor 3`; `floodTerrain ShallowFloodwater` (Odyssey) | def |
| **Rivers have a real per-cell flow vector.** `map.waterInfo.riverFlowMap` (two floats per cell), read by `WaterInfo.GetWaterMovement(Vector3)`, written by `TileMutatorWorker_River` (rivers are tile mutators in 1.6), saved compressed. The watermill uses it for spin direction | `Verse/WaterInfo.cs:95`, `RimWorld/TileMutatorWorker_River.cs:333`, `CompPowerPlantWater.RebuildCache` |
| The watermill is the in-river building precedent: `terrainAffordanceNeeded` emptied, plus `PlaceWorker_WatermillGenerator` demanding Heavy on its ground cells and MovingFluid on its water cells | def + `PlaceWorker_WatermillGenerator.cs` |
| **Vanilla HAS river floods (Odyssey).** `IncidentDef SeasonalFlooding` (baseChance 3, minRefireDays 40, Map_PlayerHome) fires only on a surface tile with rivers, outdoor temp ≥ −7 °C, in Spring/PermanentSummer; it spawns `ThingDefOf.SeasonalFlood` at map centre, which seeds from every river cell touching non-river ground, lays `ShallowFloodwater` temp terrain 10–12 cells out, holds it 4–6 days, then recedes. It is destroyed early if the temperature drops below −7 °C | `IncidentWorker_SeasonalFlooding.cs`, `SeasonalFlood.cs` |
| A second flood: `TorrentialRain` weather (Odyssey; 0.5 commonality in several Core biomes) spawns `ThingDefOf.TorrentialRainFlood`, seeded from every unroofed fresh water body's edge, and removes it when the weather ends | `WeatherWorker_TorrentialRain.cs:16,22`, `TorrentialRainFlood.cs` |
| 🔑 **A vanilla flood cannot spread into a cell holding an edifice or a foundation** (`CanFloodSpreadInto`: `cell.GetEdifice(map) != null → false`), and it subscribes to `BuildingSpawned`/`BuildingDespawned` so a building that disappears re-opens the walk at once | `RimWorld/Flood.cs` `CanFloodSpreadInto`, `SpawnSetup`, `Notify_BuildingChanged` |
| Floodwater is TEMP terrain over the base terrain; when it recedes the base terrain (e.g. rich soil) comes back untouched | `SeasonalFlood.SpreadFlood` → `SetTempTerrain` + `QueueRemoveTerrain` |
| Odyssey fish live per water body: `WaterBody.Population`, `waterBodyTracker.FishPopulationAt(c)`; the catch roll `FishingUtility.GetCatchesFor(Pawn, IntVec3, bool, out bool)` **requires a Pawn** | `Verse/WaterBody.cs`, `RimWorld/FishingUtility.cs:129` |
| Vanilla rich soil exists: `SoilRich` (alongside `Soil`, `GrasslandSoil`, `MarshyTerrain`, `Gravel`…) | defs |

UNMEASURED: what a crop does while its cell is under temp floodwater (fertility 0) — whether it dies,
pauses or is untouched. Read `Plant` growth / `PlantUtility` before tuning the farm side.
## 2. What ports as-is, what needs rework

The headline: **the surface port is easier and better than the sea version in one respect and empty
in another.** Easier, because vanilla already ships the two things the sea had to invent — a
real flood (Odyssey's seasonal and torrential-rain floods) and a real flow direction (`riverFlowMap`).
Empty, because the weir's whole yield on the sea floor is *what the current carries*, and on a
surface river nothing drifts.

| piece | sea-floor version | surface river | verdict |
|---|---|---|---|
| Maintenance = HP wear + vanilla `WorkGiver_Repair` ("tend / dredge / re-drive") | yes | identical | **ports as-is** |
| Breach cascade structure (letter, stakes snap on a timer, silt reverts, re-arm on repair) | yes | identical | **ports as-is**, data-driven trigger |
| Breach TRIGGER | `RM_MapComponent_ChannelCurrent.SurgeActive` (undersurge) | a vanilla `SeasonalFlood` or `TorrentialRainFlood` Thing spawned on the map (`listerThings.ThingsOfDef`) | **rework**: trigger becomes a list of "flood sources"; the undersurge stays one of them |
| Stake cascade order | everything within r=15, staggered by straight distance | follow `GetWaterMovement` **downstream** from the weir, nearest-first along the flow | **rework** (and the sea version's own comment calls radius a simplification) |
| Stake as boundary | lamp post, ~8 cells apart, a visual tell | 🔑 a vanilla flood cannot enter an edifice cell — **a continuous stake-line IS a levee**; a snapped stake is a gap the flood pours through at once | **rework, and the strongest idea in this port** |
| Weir catch | `CompChannelArrester` stops drift; the hopper is what sits on the cell | nothing drifts; arrester has nothing to arrest | **must be redesigned** — see Q1 |
| Weir placement | Light ground anywhere (finding 8) | straddle the bank like the watermill: ≥1 cell on MovingFluid water, ≥1 on bankside ground | **new PlaceWorker** (`RM_PlaceWorker_RiverWeir`) |
| Silt-trap richening | `RM_BankSilt → RM_BankSilt_Rich`, both terrains **unbuilt** (finding 2) | `Soil`/`GrasslandSoil`/`MarshyTerrain → SoilRich` (vanilla), within r=3.5 of a trap that stands on the bank | **rework**: the swap table becomes data (a `DefModExtension` of from→to pairs), so the sea's pair and the surface's pair share one class |
| Flood after a breach | (b) loose things become drift-eligible | the flood enters through snapped stakes; floodwater covers the farm for the rest of the flood | falls out of vanilla `Flood` for free once stakes are edifices |
| Hopper spill | stock rides the carry to the sink | stock is washed downstream along the flow vector N cells into moving water (deterioration ×3 there) — recoverable, decaying | **rework** (small) |
| Settings gate | `ChannelCurrentActive` (needs Twilight Sea ON) — finding 5 | own toggle, independent of any biome | **rework** |
| Compact pre-placed weir, `neverBreaches` | Twilight genstep | no surface equivalent; keep the flag | ports, unused on the surface |

**Generic vs sea-specific, cleanly:** generic = the three buildings' HP/maintenance, the breach
state machine, the cascade, the silt swap, the letter. Sea-specific = the carry, the arrester, the
undersurge, the sink, the cargo float, the harness, the channel genstep. The port line runs exactly
between `RM_BankWorks.xml` + the two building classes and `RM_MapComponent_ChannelCurrent.cs`.

## 3. Which mod it belongs in

| option | for | against |
|---|---|---|
| **A. Extend TerminalBiomes** | zero moves; defs already there | TerminalBiomes is the terminal-biome kit (Scald, Chill, Twilight, Grey Sea); a player who wants river weirs on a temperate map must load four sea biomes. Its settings tree is per-biome, and the code is gated on the Twilight toggle |
| **B. New free-tier mod `mandrake.rm.riverworks` ("RimMandrake: River Works"), recommended** | one small generic mod: the three buildings, the breach state machine, the flood-source list, the silt table, the river PlaceWorker. TerminalBiomes then **depends on it** and registers the undersurge as one more flood source plus its own `RM_BankSilt` pair. Matches the standing rule that biome-kit mechanics are feature-gated so they work without the biome | a move: the thingClass namespace changes from `RimMandrake.TerminalBiomes` to `RimMandrake.RiverWorks`, so any weir already in a save loses its class. Acceptable: map state is disposable and the world remake is the last step. One more mod in the list |
| **C. FlowWorks** | it is "the water mod" | measured no overlap: FlowWorks owns canals, excavation depth and fluid releases, never vanilla rivers; it carries a VALIDATED north star whose scope would grow; FlowWorks is the engine other mods call, not a building set. Wrong home |

**Recommendation: B.** Keep defNames `RM_BankWeir`, `RM_SiltTrap`, `RM_BankStake` (they are
RM_-tier invented names already, Q11a), move them and the two classes into River Works, and leave
the carry, arrester and undersurge in TerminalBiomes. The arrester comp stays a TerminalBiomes comp
that TerminalBiomes patches onto the weir def, so River Works never knows a sea exists.

## 4. Player experience on a river map

*Spring on a temperate river tile, year one.* The **seasonal flooding** letter arrives (vanilla,
Odyssey): the river widens 10–12 cells over a day and the low fields go under for four to six days.
Year two the colony fights back:

1. **Drive a stake-line** along the bank at the flood's reach — cheap wood posts, lamp-topped. A
   continuous line holds the flood off the fields, because vanilla floodwater cannot enter a cell
   that holds a building. Gaps leak; the line is only as good as its weakest post.
2. **Build a weir** straddling the bank and the moving water, like a watermill's footprint. It
   pays its upkeep with a steady trickle (Q1 decides what — fish from the river's own stock,
   driftwood, the odd lost item), dropped on its own cell for haulers.
3. **Set silt-traps** on the bank behind the weir. Over days they turn ordinary soil around them
   into **rich soil** — the best farm on the map, one step from the water.
4. **Three standing jobs** — tend (haul the catch), dredge (repair the trap), re-drive (repair
   stakes and weir) — ride vanilla repair and hauling. No new work type; the colony just has to
   keep pawns on it.

**The breach.** If a flood arrives while the weir is below half its hit points, it breaches: a
big-threat message, the weir's held catch washes downstream into the water, the stake-line
downstream snaps post by post on a visible timer (a colonist who reaches a post first can stop the
run by repairing it), the flood pours through every gap onto the fields, and the silt-traps' rich
soil reverts to plain soil. Walls and other buildings are untouched — **a catastrophe of harvest and
safety, never a base-delete**, exactly the sea version's ruled shape. A tended weir never breaches.

What is NOT in it: no new flood system (the floods are vanilla's). Surface rivers DO carry pawns
(owner, 2026-10-03): the whole mod is defined in `river_works_mod_design_2026-10-03.md`.

## 5. Mod Settings (River Works)

Defaults = shipped behaviour. All-off degrades to three inert buildings, never an error.

| setting | default | notes |
|---|---|---|
| River works enabled (master) | on | off: the buildings stand, wear stops, no breach, no silt |
| Breach | **on** (owner Q3: *"breach at default"*) | off: weirs wear and need repair but never fail catastrophically |
| Breach HP threshold | 50 % | the "untended" line |
| Stake cascade speed | 150 ticks per cell | slower = more time to save the line |
| Weir catch | on | Q1 decides the content; a rate slider beside it |
| Silt richening | on | plus a speed slider (default: one richening per half-day, as on the sea) |
| Wear rate multiplier | 1.0 | scales all three jobs' upkeep at once |
| Flood sources that can breach | seasonal flood ✓, torrential-rain flood ✓, (TerminalBiomes adds) undersurge ✓ | per-source checkboxes; labelled as event-linked, not worldgen |

TerminalBiomes' own `channelCurrentEnabled` / `undersurgeFrequency` stay where they are and only
govern the sea.

## 6. Build plan for FOUNDRY

Sized as **one item, ~1 working session of C# plus one load round**, in this order:

1. **Scaffold `src/RimMandrake/RiverWorks/`** — About.xml (`mandrake.rm.riverworks`, depends on
   Core; Odyssey assumed per the all-DLC ruling), csproj (remember explicit `<Compile Include>` if
   it follows the `EnableDefaultCompileItems false` pattern), Settings class.
2. **Move** `RM_BankWorks.xml`, `RM_Building_BankWeir.cs`, `RM_Building_SiltTrap.cs` and the breach
   key into River Works; namespace `RimMandrake.RiverWorks`. TerminalBiomes: add the dependency,
   keep `CompChannelArrester` and patch it onto `RM_BankWeir`; keep its DefOf entries pointing at
   the same defNames.
3. **Flood-source abstraction**: a static registry `RM_RiverWorks.FloodActive(Map)` answering true
   when any registered source is live. Built-in sources: `ThingDefOf.SeasonalFlood` /
   `TorrentialRainFlood` spawned on the map. TerminalBiomes registers `SurgeActive`.
4. **`RM_PlaceWorker_RiverWeir`** — watermill-shaped: empty `terrainAffordanceNeeded`, ≥1 MovingFluid
   cell + ≥1 Light cell; weir becomes 1×2 (bank cell + water cell). Stakes and traps keep Light
   (bank only).
5. **Downstream cascade** — order stakes by projection onto `GetWaterMovement` at the weir, nearest
   downstream first; fall back to radius when `riverFlowMap` is null (sea floor, lakes).
6. **Silt table** — `RM_SiltSwapExtension { List<(TerrainDef from, TerrainDef to)> }` on the trap
   def; River Works ships Soil/GrasslandSoil/MarshyTerrain → SoilRich; TerminalBiomes patches in
   its `RM_BankSilt` pair once those terrains exist.
7. **Weir catch** per Q1's answer.
8. Real art (three placeholders today) — artpipe search first, per the art rule.

**First script sketch** (`src/RimMandrake/RiverWorks/validation.py`, walk
`design/validation_walks/RimMandrake/RiverWorks.md`):

`## must be true`
- The three defs load and `RM_BankWeir` carries the river PlaceWorker → `defs.weir_placeworker`
- A weir cannot be placed on dry ground away from water, and can across a bank edge → `place.weir_bank_only`
- A continuous stake-line stops a spawned `SeasonalFlood` from entering the cells behind it → `flood.stakes_hold`
- A weir below 50 % HP breaches within 600 ticks of a flood spawning; a full-HP weir does not → `breach.threshold`
- On breach the downstream stakes reach 0 HP in downstream order, upstream ones are untouched → `breach.cascade_order`
- A silt-trap at working HP turns adjacent `Soil` into `SoilRich`; a breach turns it back → `silt.richen_and_revert`
- Master off / breach off: a damaged weir sees a flood and nothing happens → `toggles.breach_off` (in `suite.toggles`)
- TerminalBiomes still breaches on undersurge → `sea.undersurge_source`

Offline `static_check()` first (defs parse, PlaceWorker named, swap table names real terrains,
csproj lists every .cs) under `--mock`; the live chain on a quicktest river map with
`SeasonalFlood` spawned directly (no wait for spring). `## anti-guessing notes` to seed:
`RULED OUT: buildings block the flood only if Impassable — Flood.CanFloodSpreadInto tests GetEdifice, not passability`
(keep a guard component on it).

## 7. Questions for the owner

**Q1. What does a weir catch on an ordinary river, where nothing drifts?**
- (a) **Fish**, drawn from the river's own fish stock — trade-off: real food every day, but it competes
  with your fishing zones on the same water, and needs its own small catch roll (the vanilla one
  needs a pawn).
- (b) **Driftwood and flotsam** — wood, the odd lost item — trade-off: no food, never depletes the
  fish, but weaker as a reason to build one.
- (c) **Nothing** — the weir is only the flood-guard and the breach risk — trade-off: simplest, but
  the "tend the weir" job has nothing to haul.

**Q2. Should a continuous stake-line hold back vanilla floods completely?**
- (a) **Yes** — a solid line is a levee; the only way the flood gets in is a breach — trade-off: clear
  and satisfying, but a careful player turns spring flooding off for good.
- (b) **Mostly** — stakes slow the flood but every flood has a small chance to topple one regardless —
  trade-off: floods always matter a little, but the rule is harder to read.
- (c) **No** — stakes are only a boundary and warning; the flood ignores them — trade-off: matches the
  sea version, but the stake-line does no work on the surface.

**Q3. Where should this live?**
- (a) **A new small "River Works" mod** that the sea-floor biome then uses too (recommended) —
  trade-off: one extra mod; any weir in an existing save is lost.
- (b) **Stay inside Terminal Biomes** — trade-off: no move, but a river weir needs four sea biomes
  loaded and is switched by the Twilight Sea's settings.

**Q4. What should a breach do to the weir's held catch?**
- (a) **Wash it a few cells downstream into the water** — trade-off: recoverable if you hurry, rotting
  meanwhile.
- (b) **Lose it outright** — trade-off: harsher and simpler, no rescue play.
