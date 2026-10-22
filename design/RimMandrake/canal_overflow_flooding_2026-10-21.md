# Canal overflow: spilling out onto the world — design pass, 2026-10-21

Owner request (2026-10-21): *"Do a design pass on what we could do when a canal is overfilled. Is it
possible to have it actually spill out onto the world? I know there is some kind of thin water you can
add everywhere on the map intended to simulate flooding. Could we engage that? Do a deep design pass on
this then send it to GPT for review and improvement."*

Status: **owner decisions D1–D7 answered 2026-10-21 (§5); Stage 0 offline kernel built** (`Source/RM_SheetMath.cs`).
FOUNDRY design helper, 2026-10-21. Section 6 holds GPT's review
and what we took from it. Every vanilla claim below was read from the 1.6 decompiled source or defs
through RimSage, and the file and line are cited. Every FlowWorks claim was read from `src/RimMandrake/FlowWorks/`.

**Short answer: yes.** And the "thin water" exists: it is Odyssey's `ShallowFloodwater` temporary
terrain (§2). FlowWorks already writes that same temporary layer through `Flood_FlowWorks`. What is
missing is a **volume-carrying sheet of water on undug ground** that the depth engine owns. Today the
engine refuses every litre above the brim.

---

## 1. What FlowWorks does today, and what "overfilled" means

### 1.1 The model
- **The depth engine** is `RM_MapComponent_Excavation` (`Source/RM_MapComponent_Excavation.cs`). Per cell it
  holds D (`depthGrid`, 0 = surface, 1..4 notches of 0.5 m, 4 = SUPERDEEP) and F (`fillGrid`, whole
  notches, 0 ≤ F ≤ D). It also holds `partGrid` (the decilitres below the next notch, so water is exact
  to the dL), `fluidGrid` (the liquid's identity per cell) and `originalTerrain` (which stops the map
  being laundered).
- **Units** (`RM_Volume`): one notch over one square = 1,000 L = `U` = 10,000 dL. So **1 cm of water over
  one square is 200 dL (20 L)**.
- **Motion** is `RM_LevelSolve`, a fill-and-spill solve. Each connected body gets ONE level surface, and
  nothing is created or lost (a solve that would not conserve is refused). It runs on the engine
  **pulse**, every 250 ticks by default (`pulseIntervalTicks`). That is pillar 2 of the liquids
  framework, an owner ruling (`liquids_framework_design.md` §1): *"Pulsed spread only … No per-tick fluid
  sim, ever."*
- **A source is terrain.** A natural body reads through as D = F = SUPERDEEP (ruling 24). Limited bodies
  hold stock, recede and refill (`RM_LiquidStock`).
- **The surface is capped at the brim.** `RM_LevelSolve` measures the pond surface "0 = brim, negative
  below ground". `RM_ExcavationSanityMath` repairs any cell whose water stands above the brim: *"water
  never stands above the brim"*.

### 1.2 Where water meets a full canal today, and what happens

| inflow | today, at the brim | source |
|---|---|---|
| pump pouring (`Building_LiquidPump`) | **refused**. The driver never writes into a brimming cell. The tank keeps its stock and the outlet is marked "backed up" (`RM_PumpMath.NoteBackedUp`) | `RM_PumpMath.cs:103-130` |
| rain (`ApplyRain`) | **skipped**: `RoomNotches(i) <= 0`, so the cell takes nothing | `RM_MapComponent_Excavation.cs:~3013` |
| natural source / river | **no head**. A limitless body sits at its own brim and never pushes above it | `RM_LiquidStock` |
| fill-in displacement | **destroyed and disclosed** (`ReportOverflow`, `overflowDestroyedTotal`). This is the owner's 2026-09-16 rule: *"if it would 'overflow' it is destroyed"* | `flowworks_mod_definition.md` §5 |
| `Flood_FlowWorks` release (hot kits, `RM_HotLiquid.Release`) | spends volume only on dug cells. **Dry ground is never a candidate** (`CanLiquidEnter` = excavated or natural liquid). Undug natural water is refused too, one gate earlier (`:295`), so the P14 "spill over open natural water" temp-terrain branch is effectively unreachable. GPT caught this and we confirmed it by reading the code; the in-file comment is wrong | `Flood_FlowWorks.cs:274-315` |
| CrackedLands canyon flood (driver) | raises F on dug cells through `TryFloodDriverCell`. On undug ground it writes its own **permanent** `WaterMovingShallow` wall, timed by its own clock | `CrackedLands/Source/RM_MapComponent_CanyonFlood.cs` header |

### 1.3 What "overfilled" means in our model
**Overfilled = an inflow offered water at a brimming connected body and found no room.** The engine
already knows this moment exactly: it is the refusal or skip in each row above. Since the map has no
ground elevation (RimWorld maps are flat, and dug cells are the only relief), water *above* the brim has
exactly one physical place to go: **out over the lip, onto the undug ground around it, as a thin sheet**.
On flat ground that sheet spreads until it is thinner than the ground can hold, then soaks in or dries.

So the feature is: **turn "refused at the brim" into "spilled over the lip"**, with exact accounting, and
let the spill run back into any channel or pit with room.

---

## 2. The "thin water" — what it actually is (with evidence)

**It is Odyssey's temporary flood terrain**, laid over any cell by the Core temporary-terrain layer.

- **The layer (Core, no DLC gate).** Every cell has one optional *temporary* terrain over its base and
  floor. `TerrainGrid.SetTempTerrain` (`Verse/TerrainGrid.cs:396`) refuses only a non-`temporary` def, and
  `RemoveTempTerrain` (`:435`) gives the underlying terrain back untouched. `Map.tempTerrain` is a
  `TempTerrainManager` constructed on every map (`Verse/Map.cs:585`). Its `QueueRemoveTerrain(cell, tick)`
  is a priority queue that strips whatever temp terrain is on that cell when the tick comes
  (`RimWorld/TempTerrainManager.cs`).
- **The water defs (Odyssey, `Defs/Odyssey/TerrainDefs/Terrain_Temporary.xml`):** `ShallowFloodwater`
  (parent `WaterShallow`, label "shallow floodwater"), `MarshFlood`, `ToxicFlood` and `SpringFlood`. Each
  is `temporary`, tagged `Flood`, `canFreeze` false (*"Thin ice and floodwater are both temp terrain, this
  means we can't support frozen floodwater"*) and has an empty `driesTo`. Core's `WaterBase` names
  `floodTerrain` `ShallowFloodwater` (`Defs/Core/TerrainDefs/Terrain_Water.xml:20`), so each water
  terrain says which flood terrain it spawns.
- **What lays it.** The abstract `RimWorld.Flood : Thing` engine (`Flood.cs`, Odyssey-gated by
  `ModLister.CheckOdyssey("Flood")`) drives two subclasses:
  - `SeasonalFlood` (incident `SeasonalFlooding`): spreads from river-bank cells, 10–12 tiles deep,
    stands 4–6 days (`FloodedTicksRange` 240k–360k), and is cancelled below −7 °C.
  - `TorrentialRainFlood` (spawned by `WeatherWorker_TorrentialRain`): spreads from unroofed fresh
    water-body edges, and recedes 2,000 ticks after the rain ends.
  
  Spread is a weighted random walk that refuses water, foundations and **any edifice**. That is why our
  `RM_BankStake` levee holds a flood with no code (`Rivers/RM_FerryAndLevee.cs:133`).
- **What it does, read from code:**
  - **Pawns:** path cost 30, perceived +180 undrafted and +18 drafted, `traversedThought` SoakingWet, and
    `WaterInEyes` kicks.
  - **Fire:** `extinguishesFire`.
  - **Items:** `extraDeteriorationFactor` 3, added whether or not the cell is roofed
    (`StatPart_EnvironmentalEffects.cs:31`).
  - **Filth:** filth is washed away (`filthAcceptanceMask` None plus `DoTerrainChangedEffects`).
  - **Snow and sand:** cleared.
  - **Plants:** destroyed where fertility drops below the plant's `fertilityMin`, unless the terrain
    `IsFlood` and the plant has `destroyedByFlooding=false`. The default is true, so **a vanilla flood
    drowns crops at once** (`TerrainGrid.DoTerrainChangedEffects`, `Verse/TerrainGrid.cs:502`).
- **What it does NOT do:** it carries no volume or depth, it does not conserve anything, and it recedes
  on a timer. It is a picture with effects, not water.
- **FlowWorks already uses all of this.** `Flood_FlowWorks` reimplements the spread walk over Core
  members, so the mod stays DLC-free by construction. It lays each fluid's `floodTerrain`
  (`RM_Fill_Water_Trace`, a clone of `ShallowFloodwater`, and `RM_Fill_<Fluid>_Trace` for the rest)
  through `SetTempTerrain` plus `QueueRemoveTerrain`. Rivers counts seasonal and torrential floods and
  patches `Flood.CanFloodSpreadInto` for the levee-off setting.
- **Not it:** *Nature's Pretty Sweet* is installed in the workshop but **not active** (parsed
  `ModsConfig.xml`, 325 active, 2026-10-21). Its "puddles" are a **filth** (`TKKN_FilthPuddle`), not
  water, and it turns its own flooding off when Odyssey is present (its About.xml). No other installed mod
  matched a flood/puddle/water-flow About search across both mod roots (1,270 workshop + 106 local).

**Can we engage it?** Its *engine* (the timer flood) is the wrong tool. A canal spill must know how much
water it has, stop when it runs out, and flow back. Its *layer and look* are exactly right: the
temp-terrain slot, a `Flood`-tagged shallow-water def, vanilla's own effects on pawns, fire, filth and
crops. **Recommendation: borrow the layer and the look; own the volume.**

---

## 3. Design options

### Option A — Reuse vanilla's timer flood (spawn a `Flood` subclass at the lip)
Spawn a `Flood` subclass seeded at the brimming lip cells. It lays `ShallowFloodwater` for N days and
recedes.
- *For:* almost no code, and the look and effects are pure vanilla.
- *Against:* no volume and no conservation, because the engine's litres would simply vanish. That breaks
  the conservation contract (overflow is today the ONLY sanctioned destroy). It is random-walk shaped,
  with no return to the canal, and it is Odyssey-gated (which is acceptable, since DLC is assumed, but
  `Flood_FlowWorks` dropped that edge on purpose). The width is 10–12 tiles whatever the volume.
- **Rejected as the main mechanism.** It stays acceptable only as a cosmetic stand-in, and we would not
  ship it.

### Option B — Extend `Flood_FlowWorks` onto dry ground
Let a release whose seed is a brimming lip treat undug, open ground as a candidate. Each tile debits
`volumePerTile` (the sheet depth) and lays `floodTerrain`, then recedes after `floodedTicks`.
- *For:* it is small, it already debits volume, it already respects grates, sluices and flow doors, it
  already cools tar to glass at its front, and it already has a hot-release kit.
- *Against:* it is still a one-shot walk with a random shape and **one fixed depth**. The water leaves
  by timer, not by soak or evaporation, so receding is an undisclosed destroy. It has no return to the
  channel and does not merge with a second spill. It is one Thing per release, so a pump that keeps
  overflowing spawns a stream of them.
- **Not the model, and not scaffolding either.** It carries its own accounting faults (§6 item 15). It
  stays the hot-kit burst path until the sheet replaces it.

### Option C — A sheet-water layer in the depth engine (RECOMMENDED)
Add one more grid to `RM_MapComponent_Excavation`: **`sheetGrid`** (`ushort` dL per cell of water
standing *above ground* on an undug cell, 0..`SheetCapDl`). Run it as a **pulsed, integer, double-buffered
cellular automaton** over an **active set** only, on the engine's own pulse.

Water is identified by the existing `fluidGrid` (an undug cell has no other use for it). The temp-terrain
slot shows a *picture* of the grid. **The grid is the truth and the terrain is the picture**, which is the
same principle the depth engine already lives by.

**Per pulse, in this order** (all of it inside the existing pulse, after the level solve):
1. **Spill.** Each inflow that today is refused at a brimming body offers its surplus to the overflow.
   It is credited to that body's **lip cells**: undug, open, non-edifice cardinal neighbours of
   brim-full dug cells, split evenly in cell-index order (the remainder 1 dL each in order).
   - **Pumps:** the backed-up outlet pours its cycle's levels onto the lip.
   - **Rain:** a brim-full cell's share runs over its lip.
   - **Drivers, floods and kits:** a brim-full driver or kit release offers its surplus the same way (D2).
   - **Fill-in:** the homeless remainder of a fill-in displacement spills (D1).
   - **Gravity feed:** a source whose head stands above the receiving body's brim keeps pushing, and its
     surplus spills at the lip like a pump's (D2).
2. **Relax** (K sweeps, default 3). Each active cell i with h_i above its **retention depth** r_i offers
   a flux to each open cardinal neighbour j, where H = h + z and z is micro-relief:
   - f_ij = max(0, (H_i − H_j) − ε) / 5
   - The outflows are scaled so Σf ≤ h_i − r_i. This is the "virtual pipes" outflow limit, in integers.
   - Fluxes are computed from a snapshot and applied after, so the result does not depend on order and
     conserves exactly.
   - **Micro-relief z** is a deterministic hash of (map seed, cell index), within ±1 cm. It breaks the
     flat-map diamond into organic puddles and costs nothing to save, because it is recomputed.
3. **Return.** A sheet cell beside a dug cell, pit or SUPERDEEP cell with room drains into it, credited
   through the engine (`TryCredit`). Water finds the canal again, a pit's lip becomes a waterfall, and
   when the pump stops and the canal is drawn down, the sheet runs back. *Pit = superdeep cell* holds
   without special cases.
4. **Losses** (rates per terrain *property*, never per biome):
   - **Infiltration** `k_inf` by the base terrain's class: sand/soil/gravel high→low. Rock, constructed
     floor, ice, mud, marsh and water take 0.
   - **Evaporation** `k_evap(T, roofed)`, ×0 at or below 0 °C.
   - **Per-fluid multipliers on FluidDef:** propane evaporates fast, tar and slimes never soak.
   - Losses are integer dL with the remainder carried, and they are **disclosed** as running totals
     (`sheetSoakedTotal`, `sheetEvaporatedTotal`) beside `overflowDestroyedTotal` and `BurnedLevelsTotal`.
   - Water that soaks in also calls `ExplosiveGrowthAPI.Soak` (found by name, no hard reference), so a
     shallow spill **irrigates**.
5. **Picture.** Tier from h with hysteresis (up at 3 cm, down at 2 cm). Only a **tier change** writes
   terrain. That bounds mesh regeneration and `RecalculatePerceivedPathCostAt` to the cells that actually
   changed.
   - *Film* (< 2 cm): no terrain write, drawn as a translucent `SectionLayer` overlay. No vanilla flood
     effects, so no crop kill and no thought.
   - *Sheet* (2–15 cm): `RM_Sheet_<Fluid>`, a clone of `ShallowFloodwater`: `temporary`, tag `Flood`,
     `waterBodyType` None (so `WaterBodyTracker.Notify_TerrainChanged` early-outs), `canFreeze` false.
     Path cost and SoakingWet come from vanilla.
   - *Pool* (> 15 cm, only possible where walls hold it): the fluid's existing `fillTerrainVeryShallow`
     look.
6. **Sleep.** A cell with no significant incident flux and no pending boundary work for 4 pulses stops
   *flowing* (§6 item 3). Its losses still run every pulse, never lazily on wake. A neighbour change, a new spill or a terrain or
   edifice change wakes it (`map.events.TerrainChanged` and `BuildingSpawned`/`BuildingDespawned`, the
   same hooks vanilla `Flood` uses).

**Blocking rules (vanilla parity):**
- Walls, any edifice, foundations, map edge and natural water block.
- Doors **leak slowly under them** (D4): an edge touching a door passes a small fraction of the normal flux,
  so a door holds a pool for a while and drains it slowly.
- FlowWorks grates, sluices and flow doors pass by `RM_FlowDoorRules.LetsLiquidThrough`.
- Undug natural water (lakes, rivers, CanyonFlood's permanent wall) **absorbs** the sheet: the water joins
  that body's stock if limited, or is lost to a limitless one (disclosed as "joined the lake").
- A cell holding a **different fluid** refuses (`RM_StockMath.FluidsCompatible`, no mixing).

**Saturation / back-pressure.** The sheet has hard caps: `maxActiveCells` (default 4,000) and `SheetCapDl`
(default 0.5 m, which only a walled yard reaches). When a spill cannot place its surplus under these caps,
the remainder is **refused back to the inflow exactly as today**: the pump stays backed up and rain is
skipped. Nothing is destroyed to make room. The overflow never makes the system less conservative than
it is now.

**Effects, mostly vanilla for free:**
- **Pawns:** path cost and SoakingWet at the sheet tier. Slime sheets slip (`RM_SlimeSlip`). Poison
  fluids add toxin through `RM_FillEffectMath.ToxinPerCheck`, with fill = h/notch. Hot spills scald
  through `RM_HotLiquid` (it already works on releases).
- **Items:** deteriorate ×3 in standing sheet (vanilla `extraDeteriorationFactor`).
- **Crops (D3):** standing overflow kills a crop only if it is left for **1 week**; until then, and at
  film depth, the water irrigates. The kernel keeps the per-cell standing timer as data.
- **Fire:**
  - Water sheets `extinguishesFire`.
  - **Burnable spills (chemfuel, astrofuel, oil, propane) join `RM_LiquidFire`'s front.** A sheet cell is
    a liquid cell with depth in dL, and *"a thin sheet burns away in a fraction of a day"* is already the
    rule.
  - **A chemfuel overflow becomes a spreading fire carpet.** That is the most dramatic consequence and
    decision D5.
  - Propane evaporates fast and its sheet is short-lived, so a lit propane spill is a flash, not a pool.

**Cost (estimated, to be measured by the stage-0 bench):**
- **CPU:** 4,000 active × 4 neighbours × 3 sweeps ≈ 48k integer ops per 250-tick pulse, about 200 ops a
  tick amortised, against vanilla `TempTerrainManager`'s own 0.06 %-of-map sweep every tick.
- **Memory:** a 250×250 map adds 125 KB of `ushort` live, and a few hundred bytes deflated when empty
  (the `partGrid` precedent).
- **Ticking:** Plant ticking does not matter, because nothing here ticks per thing. The sheet is not a
  Thing and spawns none (the "200 ticking Things" trap the engine header warns about).

**Determinism / savegame:**
- Integer dL, snapshot fluxes, cell-index order, and no `Rand`: relief is a hash.
- The `sheetGrid` is scribed deflated and the active set is rebuilt on load from `h > 0`.
- The pictures live in vanilla's temp grid, which is saved anyway. On load we **reconcile**, and the grid
  wins.
- A one-shot debug/Mod-Settings action **"Dry all spilled liquid now"** clears grid and pictures before
  the mod is removed, because a removed mod's temp terrain is an unresolvable def in the save.

**Temp-slot contention** (the one-slot problem, `flowworks_natural_water_engine_2026-10-17.md` §2.2):
- Odyssey ice (`ThinIce`), vanilla floods and our sheet all want the single temp slot.
- **Rule:** if a vanilla `Flood`-tagged or ice temp terrain is on a cell, the sheet keeps its volume but
  **does not draw**, because vanilla's water is visible anyway and ours carries the accounting.
- Vanilla's queued removal may strip our picture at its tick. The next pulse redraws it from the grid.
- We never `QueueRemoveTerrain` our own sheet. Pictures are removed by the grid, not by a timer.

**Map-gen:** nothing. Every map starts with an empty sheet, and there is no mapgen or worldgen hook (CLAUDE.md
worldgen ruling). A natural body at its own brim has no head, so it overflows only when fed from a higher
source (D2). Rain-swollen lakes stay vanilla `TorrentialRainFlood`.

### Option D — Full shallow-water equations (velocity, momentum) on the map
- *For:* real waves, a dam break that surges.
- *Against:* it needs a per-cell velocity, many sub-steps per pulse for stability (CFL) and float
  arithmetic, so it is not deterministic across machines. It is a fluid sim in spirit, which pillar 2
  forbids. On a flat map without elevation, momentum buys nothing a player can read.
- **Rejected.**

### Comparison

| | A vanilla flood | B extend release | **C sheet layer** | D SWE |
|---|---|---|---|---|
| conserves litres | no | partly (recede = silent destroy) | **yes, exact dL** | yes (float) |
| returns to canal | no | no | **yes** | yes |
| shape follows volume | no (10–12 wide) | random walk | **yes, finite: V/r cells** | yes |
| fire on fuel spill | no | front-only | **yes, the existing front** | yes |
| pillar 2 (pulsed) | yes | yes | **yes** | no |
| code size | tiny | small | medium (≈1.2k C# + twin) | large |
| perf risk | low | low | low, bounded by caps | high |

---

## 4. Recommendation and staged plan

**Recommendation:** Option C, a sheet-water layer owned by the depth engine.
- An overflowing canal spills its exact surplus over the lip as a thin sheet. The sheet spreads to a
  finite, volume-determined puddle and runs back into any channel or pit with room.
- It soaks in, which irrigates through the Explosive Growth soak, or it dries, and both are disclosed.
  Fuel spills carry the existing fire front.
- It draws with vanilla Odyssey's `ShallowFloodwater` look and effects (cloned per fluid). With the
  setting OFF, behaviour is today's, byte for byte.

### Stage 0 — offline kernel (no game)
- `Source/RM_SheetMath.cs` (Verse-free): relax, spill split, return, losses, tiers, relief hash, sleep.
- Python twin `northstar/sheet_water.py`, plus the differential selftest
  `selftest_flowworks_sheet_oracle.py`, exact to the dL like the `RM_LevelSolve` twin.
- **Offline tests:**
  1. Conservation over 10k pulses: in = sheet + returned + soaked + evaporated + absorbed + burned.
  2. Finite extent: growth stops once every frontier cell is at or below retention, and the final wet
     count is at most ⌈V/q_min⌉, where q_min is the minimum receive quantum (§6 item 6).
  3. Order independence: shuffled input order gives the same output.
  4. Walls and doors block, grates pass.
  5. Return-to-channel drains fully.
  6. Back-pressure: under a full cap, the surplus is refused, never destroyed.
  7. Tier hysteresis: no flapping at the threshold.
  8. Bench: 250×250, 4,000 active, 3 sweeps, under 1 ms per pulse on the dev box.
  9. Save round-trip of `sheetGrid` gives an identical hash.

### Stage 1 — engine layer
- `RM_MapComponent_Excavation`: add `sheetGrid` (scribed `RM_sheetGrid`), the active set, the spill hook,
  return, losses and disclosure totals. Build it inside the pulse as an **additive region**, like the
  driver API.
- **Spill hooks at the three refusal points:**
  - `Building_LiquidPump` backed-up pour
  - `ApplyRain`'s `RoomNotches ≤ 0`
  - `Flood_FlowWorks` / driver API (`TrySetDriverFillOutcome` at a brim)
  - `Displace`'s homeless remainder (D1)
  - a gravity feed from a higher source (D2)
- **Defs:** `RM_Sheet_<Fluid>` tiers, generated by `Tools/generate_liquid_suite.py` from each `FluidDef`.
  New `FluidDef` fields: `sheetInfiltration`, `sheetEvaporation`, `sheetRetentionCm`.
- **Film overlay:** `RM_SectionLayer_SheetFilm`.
- **Readout:** extend `RM_MouseoverDepth` (shows "standing water 4 cm").

### Stage 2 — effects
- **Crops:** killed after 1 week of standing overflow, irrigated before that (D3).
- **Soak:** call `ExplosiveGrowthAPI.Soak` by reflection-free name lookup, following the GSS
  `RegisterLiveWireSource` precedent.
- **Fire:** `RM_LiquidFire` treats sheet cells as liquid cells (burn in dL, front speed per `fireKind`).
- **Pit effects:** `RM_PitFillEffects` (poison, slip, hot) reads the sheet.
- **Message:** the first spill on a map sends a one-time "The canal at X is overflowing" message (a
  readable sign).

### Stage 3 — Mod Settings (every mod ships superb settings)
- **Master:** "Overfilled channels spill onto the ground". Default **ON** once validated (D7); OFF stops new
  spills, and existing sheets keep draining.
- **Per inflow:** pumps / rain / floods-and-kits / fill-in / gravity feed (D1, D2).
- **Per family:** "Fuel spills can spread and burn" (D5).
- **Tuning (defaults = shipped):** retention depth (1 cm), sweeps (3), max active cells (4,000),
  infiltration ×1, evaporation ×1, crop-drowning delay (1 week, D3), door leak rate (D4), sheet cap (0.5 m).
- **Debug actions:** spill N litres here, dry all spill, show sheet grid.
- **Northstar functional script:** `northstar/sheet_overflow_proof.py` (debug process ruling: every
  mechanism gets its script, and every live session writes into it).

### Stage 4 — live acceptance (joint, or once the bridge is free; never on the owner's game without the bridge)
1. A pump into a full canal on flat soil puts a sheet at the lip within one pulse. The extent stays
   finite (§6 item 6), and the litre ledger closes to the dL.
2. The pump stops and the canal is drawn down, and the sheet runs back.
3. A wall ring holds a pool, and a door in the ring leaks it out slowly (D4).
4. A lit chemfuel spill carries the front across the sheet and burns it away. A water spill puts out a
   grass fire.
5. Crops under the sheet tier follow D3. A film spill soaks, and the Explosive Growth soak shows.
6. Save/load mid-spill gives an identical `sheetGrid` hash and the same pictures.
7. Perf row: the pulse costs under 1 ms at 4,000 active cells (measured on the minimal list).
8. With the setting OFF, the behaviour is identical to today (a regression row on the existing proofs).
9. A vanilla seasonal flood over sheet cells logs no errors, and the picture is restored after its
   recede.

### Risks
- **Temp-slot fights** (ice, vanilla floods, the vanilla removal queue). Mitigated by "grid is truth,
  redraw each pulse". **UNMEASURED live**, and a row in acceptance item 9.
- **Mesh churn** on a big spill. Bounded by hysteresis and tier-change-only writes. Bench it.
- **Conservation contract widens:** soak, evaporation and lake-absorption become disclosed exits (accepted,
  D6).
- **Two owners of a cell:** CanyonFlood's permanent wall and the sheet. The rule is that undug natural
  water absorbs the sheet and the sheet never writes there.
- **Mod removal** leaves temp terrain behind. Mitigated by the "Dry all" action and a note in About.
- **Fire balance:** a chemfuel overflow carpet can burn a base. The owner wants it (D5), behind its own
  setting.

---

## 5. Owner decisions — answered 2026-10-21 (question cards)
- **D1 — Fill-in's homeless water: it spills as a sheet.** This supersedes the 2026-09-16 rule (*"if it
  would 'overflow' it is destroyed"*) for fill-in displacement.
- **D2 — Which inflows overflow: pumps, rain and floods, plus a gravity feed from a higher source.** Owner:
  *"1 for sure plus even gravity from an even higher source of course"*.
- **D3 — Crops: standing overflow kills only if left for 1 week; otherwise it irrigates.** Owner:
  *"Overflow kills if left for 1 week. Otherwise it irrigates"*.
- **D4 — Doors: water leaks slowly under them.** Owner: *"Leak slowly under them"*. They do not block.
- **D5 — Fuel spills spread and burn**, with their own setting.
- **D6 — Soak-in, evaporation and "joined the lake" are accepted** as recorded exits, beside overflow and
  burn.
- **D7 — Overflow ships in FlowWorks 1.0, default ON** once validated.
- **Pillar 2:** engine-pulse movement is inside *"no per-tick fluid sim, ever"*.
- **D8 — Sheets lie level** (card 2026-10-22): the level-surface ruling extends to sheets; basins level
  by priority-flood, not the diffusion kernel alone.
- **D9 — Retention (1 cm) and micro-relief (±1 cm) are physical rules** (card 2026-10-22): they decide
  where puddles linger and where a spill stops.
- **D10 — Cold: a sheet below 0 °C freezes into its own ice tier**, keeping its volume, and thaws back
  (card 2026-10-22). **Lowering the sheet cap** stops further filling; water already deeper stays and
  drains by its normal exits (card 2026-10-22). Temp-slot priority stays the §3 rule (sheet yields the
  picture to vanilla flood/ice, keeps its volume).

---

## 6. GPT review and what we took/rejected

Consulted 2026-10-21. The run used `gpt_consult.py` (gpt-6.1-sol, high effort), with this doc,
`Flood_FlowWorks.cs`, `FluidDef.cs` and `RM_LevelSolve.cs` inlined. The answer is a Transient record and
is not kept. Its verdict: *"Keep the engine-owned volume layer, but do not approve Option C as
written."* The direction stands. **Where this section and §3–§4 disagree, this section wins.** The build
item carries these amendments.

### Taken (they amend §3–§5)
1. **Atomic integer-dL transfers and one hydraulic interface (GPT's #1).** Every inflow does
   offer → accepted dL → debit exactly that amount. The existing boolean / whole-notch
   `DriverFillOutcome` is not enough for partial sheet acceptance, so the driver API grows an
   `accepted dL` return. Sheets, dug cells and natural bodies expose one *head + room* interface. The sheet
   is positive head above 0, and dug water is at or below 0. Sheet→canal and sheet→limited-lake are
   **internal transfers** inside the ledger, not exits. A full limited lake **refuses**, and never
   swallows past its capacity. Only a limitless body is a sink, and that sink is disclosed.
2. **Overlay-first renderer, and temp-terrain writes only behind a proven ownership gate (GPT's #2).**
   We confirmed the removal queue has no ownership: `TempTerrainManager.Tick` dequeues and calls
   `RemoveTempTerrain(cell)` on whatever is there. So "redraw next pulse" fixes the picture but not the
   side effects: crops already destroyed, filth already washed, fires already put out. Stage 1 therefore
   draws **every** sheet tier as a `SectionLayer` overlay and applies effects from the grid in our own
   code. These effects cover path cost through a pathing hook or vanilla-parity numbers, the SoakingWet
   thought, deterioration, extinguishing and crops per D3.
   - Temp-terrain pictures become a later, optional stage, after the integration spike shows they are
     safe.
   - Pool tiers need dedicated **temporary** clones. `FluidDef.ConfigErrors` requires most existing fill
     tiers to be non-temporary, so they can never be written over undug ground.
   - Fuel sheets must not inherit water's `extinguishesFire`.
3. **Losses on the pulse, never lazily on wake (GPT's #3).** Reconstructing evaporation on wake from
   *current* temperature and roof is wrong. Sleep now only skips *flow*: a cell is asleep when it has no
   significant incident flux and no pending boundary work, not merely zero Δh. Losses still run on every
   occupied cell each pulse, which costs O(occupied) at one multiply-add per cell.
4. **Persist everything a continuation needs (GPT's #3).** The scribed state is:
   - `sheetGrid`, fluid identity, loss remainders and hysteresis state
   - the relief salt and kernel version, and the pulse phase
   
   The acceptance test is *continue-uninterrupted vs. save/load-then-continue gives identical future
   trajectories*, not just an equal hash.
5. **Receiver caps, fluid arbitration, occupied-cell cap (GPT's #4).**
   - Destination room is resolved before commit, and rejected flux stays with its sender. Nothing is
     ever clamped after the fact.
   - Two fluids reaching an empty cell in one pulse are settled by a stable rule (lower fluid-palette
     index, then lower donor cell index), and the loser stays upstream.
   - The cap counts **occupied** cells (`maxWetCells`), with new cells reserved deterministically. A
     separate cap bounds work per pulse.
   - Lowering either cap in settings never deletes water. Already-wet cells keep draining, and only new
     wetting is refused.
6. **Retention is moisture, not trapped mobile water.** Water below retention depth is *held moisture*.
   It does not flow, it only soaks or evaporates, and it is drawn as the faintest film. The §4 claim
   "the sheet runs back" is restated: mobile water returns, and held moisture dries where it is. The
   §4-stage-0 extent test "≤ ⌈V/r⌉ cells" was **false**: 401 dL at r = 200 can wet five cells. It is
   replaced by *"the extent stops growing once every frontier cell is at or below retention, and the
   final wet count is bounded by ⌈V/r_min_receive⌉"*, with a minimum receive quantum so a donor cannot
   make dust-thin new cells.
7. **Underlying ground is read from authoritative state, never from the exposed picture.** Eligibility,
   permeability and `originalTerrain` capture read the base and foundation layers and the engine's
   `IsNaturalLiquid`, never `TerrainAt`. That way our own water picture cannot make a cell look like a
   lake.
8. **Local, not teleporting, spill.** The surplus enters at the lip cells nearest the inflow (the pump
   outlet, or the rained-on cell), walking the connected body outward. It is not split evenly over every
   lip of a long canal. The lip set is cached per body and invalidated on dig/fill.
9. **More topology wake-ups.** Door, sluice or grate state changes, dig/fill under a wet cell,
   floor/foundation changes and roof changes all wake cells. Subscriptions are re-made after load, and
   reconciliation writes never schedule more work.
10. **Stages reordered:**
    - Stage 0 is a **build-pinned integration spike**. It writes and removes temp terrain over crops,
      floors, filth, fire, ice, vanilla floods and fishing zones on the 1.6 assembly, and records the
      mutation, mesh and path cost.
    - Stage 1 is the **water-only kernel and transfer ledger** (no losses, fire or irrigation). Then come
      persistence and settings transitions, then losses and effects, then other fluids, fire and
      defaults.
    - Explosion and fire-effect budgets are counted separately. A bounded kernel does not bound a burning
      carpet.
11. **Precedent we missed: *Dynamic Flooding* (TrueBlueSwablu, Steam 3144491125).** GPT reports it as a
    separate flood layer with building blockers, recession, plant effects and cleanup-before-removal. It
    targets 1.4/1.5. **UNVERIFIED by us**: it is not installed (our About search over both mod roots
    found it nowhere), and exact conservation and 1.6 support are unknown. Stage 0 reads its listing and
    source for terrain-ownership lessons before we write ours.
12. **Perf claims made honest.** "48k integer ops" becomes *48k neighbour evaluations plus all
    integration work*. The acceptance runs cover 250² and 325² maps, concentrated and scattered spills,
    and the full modpack. Kernel time, total pulse time, frame spikes, allocations, dirty sections and
    terrain writes are recorded separately. The 1 ms target stays provisional.
13. **Pin the rounding.** The rules are: fixed integer hash with a persisted salt, checked 64-bit
    intermediates, flux remainders allocated in stable order, and no dead zone from `/5` plus ε that
    strands water. Anisotropy and convergence time are measured, and spread and drain *times* get
    targets, because K × pulse sets gameplay speed.
14. **New owner decisions:**
    - **D8:** does the exact level-surface ruling (*"VERY smooth water"*) extend to sheets? Yes means
      basin levelling by priority-flood. No means the diffusion kernel.
    - **D9:** are retention and micro-relief physical rules or cosmetic? They decide where puddles stay.
    - **D10:** temp-slot priority, cold weather (a sheet stays liquid below 0 °C, or freezes into its own
      ice tier), and what lowering a cap does.
    - **D7:** turning OFF never makes standing water vanish silently. OFF stops new spills, and existing
      sheets keep draining. The "Dry all" action is a disclosed purge.
15. **Existing `Flood_FlowWorks` accounting faults, filed with the build so they do not migrate into the
    sheet:**
    - Expiry, an empty frontier or a missing def can destroy a release with `remainingVolume > 0`, which
      is an undisclosed exit.
    - The float-notch `remainingVolume` does not match the dL engine.
    - Refused/HandsOff cells are not saved, so eligibility changes on reload (the in-file comment already
      admits this).
    - Global `Rand` makes the walk nondeterministic.
    
    `Flood_FlowWorks` is therefore **not** stage-0 scaffolding (this reverses §3 Option B's "good as
    scaffolding").

### Checked by us, against GPT's open questions
- **FreezeManager does not touch our sheet.** It tests `c.GetTerrain(map).canFreeze`, the top terrain
  with temp winning (`Verse/FreezeManager.cs:108`). Melting removes temp terrain only where the terrain
  *is* `ThinIce` (`CanEverMelt`). So a `canFreeze=false` sheet picture is never frozen or melted away.
  Under the overlay-first renderer it is moot anyway.
- **The `WaterBodyTracker` early-out is conditional, as GPT says.** It compares old and new
  `waterBodyType`. A None sheet over None ground skips the body branch, but replacing a water-typed
  terrain does not. It is moot under the overlay renderer and stays a row in the integration spike.

### Rejected
- **GPT's "floating point does not automatically mean nondeterminism; reject SWE on value, not on
  that".** The correction is accepted, and so is its conclusion. Option D stays rejected on complexity
  and value: no elevation on the map means momentum gives the player nothing to read.
- **Persistent virtual pipes (saved edge discharges).** Rejected for v1: more saved state and damping
  calibration, for a dynamic effect that a flat map cannot show. Revisit only if D8 asks for surge
  behaviour.
- **Factorio-style unrestricted reservoir merging for sheets.** Rejected, because it spreads sheets
  implausibly far. GPT also says this. We keep only its boundary-transfer lesson, which item 1 already
  takes.
