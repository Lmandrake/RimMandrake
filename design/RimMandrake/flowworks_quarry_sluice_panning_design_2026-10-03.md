# FlowWorks quarry digging, sluice mining, gold panning — design pass (2026-10-03)

Item: `FLOWWORKS_QUARRY_DIGGING_1` (caused by `MINERALS_WHERE_THEY_BELONG_1`). Status: DESIGN, nothing
built. Cards: `Transient/flowworks_quarry_cards_2026-10-03.json`.

## 0. Owner request and the rulings it sits under

Typed 2026-10-03: *"Ticket out a design pass to consider extending FlowWorks to include the Quarry
concept: digging a canal can discover materials like the Quarry does. Would only work in the local
biome availability (by default, configuration changeable). But that now allows interesting options.
Could you make a sluice mining that slowly produces ore out of a stream/river? Also panning for gold in
a river..."*

Rulings it must obey (all 2026-10-03, on `MINERALS_WHERE_THEY_BELONG_1`):

- Quarries yield **only local materials**, like the deep drill/scanner.
- The **mineral abundance registry** (`design/RimMandrake/mineral_abundance_registry_design_2026-10-03.md`,
  draft CSV `design/RimMandrake/mineral_abundance_registry_2026-10-03.csv`) is the one source of what a
  biome holds. Settings unit is **deposits per map**. Per-biome numbers are still agent GUESSES; a
  review sheet is owed before they ship.
- An ore the registry has never heard of **behaves as its mod intended**.
- A bare biome quarry (no quarryable row) yields **local rock chunks only**.
- River Works (`design/RimMandrake/river_works_mod_design_2026-10-03.md`, fully ruled, reassigned to
  FOUNDRY) owns river currents, weirs, fords, the ferry, and the weir's fish/drift catch.

## 1. Inventory

Instruments: live `ModsConfig.xml` parsed with ElementTree (**634** active mods, all five DLCs active);
every installed `About.xml` across both roots (**1,416** files) searched by `<name>` + `<description>`;
FlowWorks source read directly. Sanity probe on the About sweep: "gravship" matched **42** mods
(23 active), so the sweep can see.

### 1a. How FlowWorks digs a canal today

- `Designator_DigCanal` places designation `RM_DigCanal`; `WorkGiver_DigCanal` hands out
  `JobDriver_DigCanal` (`src/RimMandrake/FlowWorks/Source/JobDriver_DigCanal.cs`, 61 lines).
- The driver subclasses vanilla `JobDriver_AffectFloor` (the smooth-floor engine), speed stat
  `MiningSpeed`, work `RM_ExcavationDepth.WorkToDeepen(current)` = 3200 × level being cut.
- **The completion hook is `JobDriver_DigCanal.DoEffect(IntVec3 c)`**, which calls
  `RM_MapComponent_Excavation.Deepen(c)` (`RM_MapComponent_Excavation.cs:385`). `Deepen` returns the new
  depth byte, records the original terrain on the first cut, and lays the depth's dry terrain.
- Four depths (`RM_ExcavationDepth.cs`): Shallow 1, Mid 2, Deep 3, Superdeep 4. LAW 1: we dig down,
  never build up. Fill-in (`JobDriver_FillInCanal`) restores the recorded terrain, so **a cell can be
  dug, filled and re-dug** — any per-cut roll needs an exploit guard (§2a).
- ⚠️ **Name collision:** FlowWorks already ships `RM_Sluice` — a **sluice gate** door
  (`Defs/Canals/ThingDefs/FlowWorks_Doors.xml`, in `RimMandrakeFlowWorks_DefOf`), and About.xml lists
  "sluice gates" as named-but-unbuilt. The mining building must be called **sluice box**
  (`RM_SluiceBox`), never `RM_Sluice`.

### 1b. Quarry buildings in the active set

- **Quarry** (`ogliss.thewhitecrayon.quarry`, CC0) is active: `QRY_Quarry`, `QRY_MediQuarry`,
  `QRY_MiniQuarry`. Its ore draw is the planet-wide `OreDictionary.TakeOne()`; the registry design §6.4
  replaces that one call by transpiler with `MineralRegistry.QuarryDraw(map)` and names it the public
  API for this item. **This design consumes that API; it builds no draw of its own.**
- No other quarry building active (the About sweep's other "quarr" hits are signage, wall stuff and a
  rumour mod; the registry inventory already confirmed no Odyssey/VE quarry).

### 1c. River terrain and fishing hooks (vanilla/Odyssey, from River Works §1c/§1e)

- Moving water: `WaterMovingShallow` (milder) and `WaterMovingChestDeep` (pathCost 42, extra
  non-drafted perceived cost 180, avoid-wander), plus toxic twins.
- Flow: `map.waterInfo.riverFlowMap`, read by `WaterInfo.GetWaterMovement`, written by
  `TileMutatorWorker_River`, used by the vanilla watermill (the only vanilla in-river building).
  River Works quantises it into its current field with lanes **Centre** (chest-deep, inescapable,
  ~45 ticks/cell) and **Margin** (shallow, ~90 ticks/cell, wadeable), scaled by river size.
- Fish stock: Odyssey `WaterBody.Population/MaxPopulation`, `WaterBodyTracker.FishPopulationAt`,
  `Notify_Fished`. The weir draws on it; this is the **precedent** for a per-water-body stock that
  several consumers compete for (§2b).

### 1d. Existing sluice / panning / placer mods installed

| search (name + description) | hits | real matches |
|---|---|---|
| sluice | 1 | FlowWorks itself (the gate) |
| panning / gold pan | 1 | Camera+ (camera panning) — false hit |
| placer / alluvial | 2 | both false hits ("placer" as in placement) |
| dredg | 1 | Aqued Dredge Aberrations — creatures, not mining |
| prospect | 1 | VFE Settlers (inactive) — not a river mechanic |

**No installed mod does sluice mining or panning.** Nothing to absorb or collide with.

### 1e. Salvaging skill (asked about)

`RM_Salvaging` is **proposed, not ruled** (`design/RimMandrake/jawa_scavenge_system_design_2026-10-03.md`
§4; its item `JAWA_SCAVENGE_SYSTEM_1` has not even been filed). Its identity there is *taking apart
made things* — wrecks, machines. Panning and sluicing are taking minerals out of the ground, which is
what Mining already means, and the canal dig already reads `MiningSpeed`.

## 2. Design

### 2a. Canal-dig discovery (FlowWorks)

*Each cut of a canal cell has a small chance to turn up a lump of something the local land holds.*

- **Hook:** after `excavation.Deepen(c)` in `JobDriver_DigCanal.DoEffect`, if the depth rose, call
  `RM_DigDiscovery.Roll(map, c, newDepth, pawn)`. One call site; nothing else in the dig changes.
- **What can come out:** `MineralRegistry.QuarryDraw(map)` — rows with `quarry=local` and a non-zero
  cell for this map's biome, weighted by the biome's EPM. Components and salvage-only rows can never
  appear. **Depth matters:** Shallow and Mid draw the surface pool only; Deep and Superdeep also admit
  the biome's `deep-only` rows (weighted by `deep_weight`), so digging deeper is how you meet what the
  scanner would find. A biome with no quarryable row yields nothing but the normal dig (or, optionally,
  a chunk of local rock — card).
- **Chance and size (defaults, to tune):** 1.5% per cell-level cut, find = 10–25 units (a "lump"), so
  100 cells dug one level ≈ 1–2 finds ≈ 25 units. Compare one vanilla 30-cell steel vein ≈ 1,200 units:
  digging is a side-benefit, never a replacement for mining.
- **Budget against deposits-per-map:** each map carries a **loose-find budget** = 5% of the biome's
  total registry EPM (setting). Every find spends it; at zero, finds stop. So the registry's "deposits
  per map" stays the true ceiling and a player who digs the whole map cannot out-mine the land.
- **Exploit guard:** a per-cell `rolledDepth` byte grid (Scribed beside `depthGrid`): a cut rolls only
  when the new depth exceeds what that cell has already rolled. Dig → fill → re-dig pays nothing twice.
- **How it surfaces (recommended):** the lump drops on the cell's lip (nearest standable non-canal cell)
  as items, with a small blue message ("Dug up 18 silver while cutting the canal"). The **first** find
  of each material on a map sends a letter naming it and saying the land holds more. Alternatives for
  the card: a seam reveal (a small mineable lump placed in adjacent rock — richer, but it adds
  mineables outside the registry's placement pass and needs a rock cell beside the canal), or
  message-only.
- **Local-only toggle:** on by default per the ruling; off = draw from every registry row the planet
  allows (still never `quarry=no` rows).

### 2b. Sluice box (River Works recommended — see §2e)

*A building set in shallow moving water that slowly washes ore out of the river.*

- `RM_SluiceBox`, **1×2 across the bank edge** like the weir and watermill: one cell on moving water,
  one on the bank where output drops. Wood/stuff, no power, no fuel, no pawn needed — passive, like
  the weir.
- **Placement:** water cell must be `WaterMovingShallow` (Margin lane). Chest-deep is too fierce (and
  inescapable in River Works). Still water (lakes, marsh, FlowWorks canals without flow) produces nothing.
- **Output:** one roll per day; yield drawn from the river's **placer stock** (below) using the
  **placer pool**: registry rows flagged `placer=yes` (heavy, durable minerals that collect in gravel:
  gold, silver, gems, tin-like ores; never salts, never soft rock) with a non-zero biome cell.
- **Flow strength:** River Works' current field gives Margin/Centre lane and river size; yield scales
  with river size (creek ×0.5, river ×1, great river ×1.5) and a spring flood **refills** the stock.
  Without River Works, the sluice could read vanilla `riverFlowMap` magnitude directly — but every
  ruled river behaviour is in River Works, so depending on it is the honest shape.
- **Placer stock (the balance knob):** each river water body carries a stock = 2% of the biome's
  placer-row EPM, regrowing to full once a year (EPM/yr unit) and topped up by spring floods. Sluices
  and panners **share** it, exactly as weirs and fishing zones share the fish stock. Ten sluices on one
  river earn about what three do; the river runs out, then recovers.
- Weir interaction: a weir upstream calms the current (~8 cells); a sluice in calmed water yields at
  the reduced lane rate. A player chooses: calm water to cross/fish, or fast water to wash gravel.

### 2c. Panning (same home as the sluice)

*A colonist squats on the bank and pans the shallows by hand.*

- **Where:** a **panning spot** (1×1, free, like a meditation spot) placed on a bank cell adjacent to
  `WaterMovingShallow`. The pawn **stands on the bank**, never in the water — River Works shoves pawns in
  moving water, and a job that wades would be fought by the current every minute. Alternative (card):
  a panning zone painted over shallow water like Odyssey's fishing zone.
- **Work:** WorkType **Mining**, skill **Mining**, speed `MiningSpeed`. Sessions of ~2 in-game hours;
  each session rolls against the river's placer stock, yield scaled by Mining skill (skill 0 ≈ 40%,
  skill 20 ≈ 160%). Grants a little Mining XP. Recommended over Salvaging (§1e): panning is not taking
  apart a made thing, and Salvaging is not yet ruled.
- **Yield:** small — a session gives 0–3 units of a placer row, mostly nothing. Per year a dedicated
  panner earns perhaps 40–80 units, less than a sluice, but it works on any shallow river with no build.

### 2d. "Gold panning" vs what the registry says — the honest problem

The draft registry puts **gold** at 0 in every biome except the Blue Desert (600 EPM, meteoritic) and
the Scald sea floor (1,500, nodules). So "panning for gold" under strict local-only rules would find
gold almost nowhere; most rivers would yield silver or nothing. Three ways out (card):

1. **Placer column in the registry** (recommended): a `placer` value per row and biome, separate from
   vein EPM, so a biome can carry river gold without carrying gold veins. This is how real placer gold
   works (gold eroded out of distant rock), stays inside "the registry decides, period", and gives the
   owner one more column to set at the registry's review sheet.
2. **Pan whatever the land holds**: no new column; the placer pool is the biome's dense vein rows. Gold
   only where gold veins already are.
3. **Gold everywhere a river runs**: a flat river-gold rate ignoring the registry — simplest, and it
   contradicts the local-only ruling.

### 2e. Mod home — decided honestly

| feature | home | why |
|---|---|---|
| canal-dig discovery | **FlowWorks** | its only hook is FlowWorks' own dig job; nothing about it involves rivers |
| sluice box | **FlowWorks (Rivers)** | it sits on moving water and its rate *is* the current field River Works owns; the 1×2 bank-edge pattern, the per-water-body stock and the flood refill are all River Works machinery (weir) |
| panning | **FlowWorks (Rivers)** | a bank job on moving water, sharing the sluice's stock; splitting the two across mods would split one stock |
| the draw (`QuarryDraw`, placer pool) | **the minerals registry mod** | already designed as the public API; FlowWorks and River Works both depend on it, neither owns it |

Since 2026-10-05 River Works is part of FlowWorks (owner: *"I think river works needs to be part of flow
works."*), so all three live in FlowWorks: digging in the canal engine, sluice + panning in `Source/Rivers/`
beside the current field and the weir's stock.

### 2f. Settings

FlowWorks (dig): enable dig discovery (on); finds follow local minerals (on; off = any planet-allowed
row); discovery chance multiplier (1.0); loose-find budget % of biome EPM (5%); first-find letter (on).
FlowWorks Rivers section (sluice/panning): enable sluice box (on); enable panning (on); placer stock % (2%);
sluice/panning yield multipliers (1.0); flood refill (on). All-off = vanilla behaviour. Labels say
these are live (no map-gen effect).

### 2g. Balance against deposits-per-map

Ceilings, not rates, keep it honest: dig finds are capped by the per-map loose budget (≤5% of the
biome's registry total), and sluice + panning by the river's yearly placer stock (≈2%/yr). A colony
that does all three gets perhaps a tenth of what mining the biome's veins gives — a reason to dig and
to settle by rivers, not a new economy. Every number above is a GUESS to be set on the registry review
sheet.

### 2h. Build size

| piece | size | notes |
|---|---|---|
| dig discovery (hook, roll, budget, `rolledDepth` grid, message/letter, settings) | S | blocked on registry R4 (`QuarryDraw`) |
| registry `placer` column + generator + `PlacerDraw` | S | registry mod |
| sluice box (def, art 1×2, comp, stock per water body, flood hook) | M | blocked on River Works core |
| panning (spot def, WorkGiver, JobDriver, art) | S–M | shares the stock |

Order: registry R4 → dig discovery (FlowWorks) → River Works core → sluice + panning.

### 2i. First-script plan (`design/RimMandrake/debug_process.md` §2)

FlowWorks walk `## must be true` gains (each a chain component in `src/RimMandrake/FlowWorks/validation.py`):
1. A canal cut in a biome with quarryable rows can drop a registry-local material → spawn a test map in
   a known biome, force the roll (debug action sets chance 100%), read the spawned thing's def against
   the biome's pool.
2. A cut never drops a `quarry=no` row (components) → same, 200 forced rolls, count zero.
3. Fill-in then re-dig pays nothing → read `rolledDepth`, re-dig, assert no new thing.
4. Budget exhaustion stops finds → set budget tiny, assert finds stop.
5. Toggle off → no finds (`suite.toggles`).
River Works walk gains: sluice on shallow moving water produces only placer-pool rows; on still water
produces nothing; stock falls with use and refills on a forced flood; panning pawn stays on the bank.
Selftest under `--mock` before any bridge minute.

## 3. Open questions (cards)

`Transient/flowworks_quarry_cards_2026-10-03.json` — 2 cards, 7 questions:

1. How a dig find shows up (lump + first-find letter / seam reveal / message only).
2. Should dig finds draw deeper rows at deeper cuts?
3. Bare biome: rock chunks or nothing from the dig?
4. Gold in rivers: placer column / pan what the land holds / gold everywhere.
5. Where the sluice and panning live (River Works / FlowWorks / both in FlowWorks needing River Works).
6. Panning skill: Mining / Salvaging.
7. Panning spot vs panning zone.
