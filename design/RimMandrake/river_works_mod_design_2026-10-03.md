# River Works — whole-mod design (SURFACE_RIVER_WEIRS_1), 2026-10-03

Design only — nothing built, filed or claimed. Supersedes nothing: the 2026-10-02 port study
(`design/RimMandrake/surface_river_weirs_design_2026-10-02.md`) stays the engine-fact record and is cited,
not repeated. This doc defines the WHOLE mod the owner asked to see before it is built.
Engine facts are RimSage reads of decompiled 1.6 (2026-10-02/03); anything unchecked says UNMEASURED.

## 0. Rulings this builds on

Owner, 2026-10-03, by question card (two answers typed as free text; recorded on the item, `tsn=1791041731991523332`):

1. **Surface rivers shove pawns aggressively, like the undersea flows.** The weir therefore still matters:
   it tames or blocks the current. Weirs also **catch fish from the river's own stock**, competing with
   fishing zones.
2. **A continuous stake-line holds back vanilla spring floods like a levee**; only a breach lets the flood in.
3. **Home: almost certainly a new River Works mod**, which the sea-floor biome then also uses — but he wants
   the entire mod defined first, with question cards, *"so we might expand it appropriately"*.
4. **A breach washes the weir's held catch a few cells downstream.**

Standing rules that shape it: breach on by default (owner on `TWILIGHT_CHANNEL_CURRENT_1`, *"breach at
default, and this should be ported to normal river tiles too!"*); superb Mod Settings (2026-09-12); all
DLCs assumed present (Odyssey's floods and fish are fair to depend on); three-tier naming; every new mod
ships with its first script (`design/RimMandrake/debug_process.md`).

⚠️ **Ruling 1 reverses one line of the 2026-10-02 doc**: its §4 said *"nothing carries pawns or items along
a surface river (the carry stays sea-floor)"*. That was the earlier position recorded on the item note of
2026-09-27; the owner's 2026-10-03 answer replaces it. This doc is built on the new ruling.
## 1. What already exists (reuse census)

Measured 2026-10-03 on the bench clone (`5558448b6`) by reading the files named. The project keeps
having already built things; here is what it has.

### 1a. The sea-floor current — the engine River Works should become

`src/RimMandrake/TerminalBiomes/Source/RM_MapComponent_ChannelCurrent.cs` (848 lines) is a complete,
working **carry**: it is exactly "the undersea flow" the owner is pointing at.

| piece | what it does today | fate |
|---|---|---|
| `flowDir[]` byte grid (8 compass dirs) + `lane[]` (None / Margin / Centre) + `bankBand[]` | authored once by `RM_GenStep_TwilightChannels`, Scribed with `LookByteArray`, zero-filled on a bad load | **move to River Works** as the generic "current field" |
| Two-tier occupant scan (register every 250 ticks, step every 15) | MudSwallow's shape; cheap | **move** |
| `StepOne` / `Move` — pawn: `pather.StopDead()` + `Position = next` + `Notify_Teleported(false)`; item: plain `Position` | the shove | **move**, unchanged |
| Cadence: Centre 45 ticks/cell (inescapable), Margin 90 (pawn may still path across), items ×2 slower, × `channelCurrentStrength` | the "aggressive" feel | **move**; the strength slider becomes River Works' |
| Surge: Margin promotes to Centre cadence, Centre cadence halves; `GrabPawnsOnWidenedBand` | the undersurge | **move the surge STATE as generic** ("a flood is on"); the undersurge *condition* stays sea |
| Exemptions: buildings; races with `RM_ChannelNativeExtension`; cells on/next to `RM_FordStones`; cells a `CompChannelArrester` claims | weir arrest, natives, fords | **move**; `RM_FordStones` has no TerrainDef anywhere — it is a name only (see §3.7) |
| `RM_Apparel_FloatHarness` (caps a pawn at Margin cadence), `RM_Thing_CargoFloat`, sink cells, first-entry warning | sea kit | harness + warning **move** (they are generic river gear); cargo float and sink **stay** sea |
| `RM_GameCondition_Undersurge` + MTB roll on channel maps | sea weather | **stays** in TerminalBiomes, registers itself as a flood source |

### 1b. The bank works (all in TerminalBiomes; detail in the 2026-10-02 doc §1)

`RM_BankWorks.xml` (`RM_BankStake`, `RM_BankWeir`, `RM_SiltTrap`), `RM_Building_BankWeir.cs` (HP wear, breach
below 50 % during a surge, stake cascade within r=15, clogs traps), `RM_Building_SiltTrap.cs` (richens
`RM_BankSilt → RM_BankSilt_Rich`, **neither terrain exists**, so it does nothing today). Placeholder art.
No PlaceWorker — today all three can only stand on dry Light ground, never in the water they are about.
**All move to River Works** with the reworks listed in the 2026-10-02 doc §2 (breach trigger becomes a
flood-source list, downstream cascade order, river PlaceWorker, silt swap table as data).

### 1c. Fish

- Vanilla (Odyssey) per-water-body stock: `WaterBody.Population`, `MaxPopulation`, `CommonFish` /
  `UncommonFish`; `WaterBodyTracker.FishPopulationAt(c)` and **`Notify_Fished(IntVec3 c, float amount)`**,
  which is how a catch draws the stock down (RimSage, `Verse/WaterBody.cs`, `RimWorld/WaterBodyTracker.cs:105`).
  The vanilla catch roll `FishingUtility.GetCatchesFor` needs a Pawn, so the weir needs its own small roll.
- **Reuse precedent:** `RustCathedral/Source/Hum/RM_CathedralFishing.cs` already Harmony-postfixes
  `Notify_Fished` — so a weir that calls `Notify_Fished` is automatically seen by every mod that watches
  catches (the Cathedral's per-catch price included). That is the competition with fishing zones, for free:
  one stock, two drains.
- `SeaShores` (`RM_SeaShoresHarmony.cs`) already makes a sea's water body serve that sea's `fishTypes`,
  so a weir on a sea shore would catch sea fish without any River Works code.

### 1d. Floods

- Vanilla Odyssey: `SeasonalFlooding` incident → `SeasonalFlood` thing (spring, river maps, 10–12 cells,
  4–6 days); `TorrentialRain` weather → `TorrentialRainFlood`. 🔑 `Flood.CanFloodSpreadInto` refuses any cell
  holding an edifice and re-walks when a building despawns — **this is the levee, already in the engine.**
- FlowWorks' `Flood_FlowWorks` (canal release) re-implements the same walk for canals; River Works does not
  touch it, but a FlowWorks flood is a natural third registered flood source (§6).

### 1e. Rivers themselves

- Per-cell flow vector `map.waterInfo.riverFlowMap`, read by `WaterInfo.GetWaterMovement(Vector3)`, written by
  `TileMutatorWorker_River`, used by the watermill. **This is the surface's free `flowDir` grid** — River Works
  quantises it to the 8 compass directions instead of authoring one.
- `WaterMovingChestDeep`: pathCost 42, `extraNonDraftedPerceivedPathCost` 180, `avoidWander` — vanilla AI
  already avoids it hard. `WaterMovingShallow` is milder (UNMEASURED exact numbers; read the def at build).
- FlowWorks **does** touch vanilla rivers in one place, and the 2026-10-02 doc missed it: `FlowWorks/Source/
  ManyWaters/RiverSteamHook.cs` (`MapComponent_RiverSteam`) puts ambient steam on river cells of biomes that
  opt in. Visual only; no overlap with currents or works.

### 1f. Other code that moves pawns (checked, not reused)

`FlowWorks/Source/Superdeep/RM_SuperdeepTrap.cs` and `EnvironmentalHazards/.../RM_MapComponent_LivingRegrowth.cs`
use the same StopDead/Position/Notify_Teleported idiom — corroboration that the idiom is safe, nothing more.
`RM_CompWaterLocked` (EnvironmentalHazards) keeps a creature IN water — a possible future river-native.

### 1g. What does NOT exist anywhere in `src/`

Fords, ferries, river mills of our own, any surface-river current, any fish trap. (Grep for
ferry / FordStones / watermill / millwheel: only the ChannelCurrent comments and unrelated OasisMaker /
Research hits.) The vanilla watermill is the only in-river building.
## 2. Scope and boundaries

**River Works is the moving-water mod: the current, and the works people build against it.** Two halves:

- **The engine** — a generic *current field* on any map (flow direction + lane strength per cell), the
  carry that shoves pawns and items along it, the flood-source registry, and the surge. Fed on surface maps
  from vanilla's `riverFlowMap`; fed on the sea floor by TerminalBiomes' own channel genstep.
- **The works** — stake, weir, silt-trap (plus whatever expansions §4 he picks), their wear, the breach,
  the levee behaviour, the weir's fish.

**In:** every map with moving river water (`TerrainDef.IsRiver`), any biome, any mod list; the sea floor
through TerminalBiomes.
**Out:** canals, digging, liquids and fluid releases (FlowWorks); lakes and still water (no flow vector —
`riverFlowMap` is null/zero there); the sea-floor-only kit (undersurge, sink, cargo float, channel genstep,
which stay in TerminalBiomes); any new flood system (the floods are vanilla's); any worldgen (none, ever).

**Dependency direction:** TerminalBiomes depends on River Works, never the reverse. River Works names no
biome and no sea; it exposes three seams (§6) and the sea plugs into them.
## 3. Features

### 3.1 The surface current (ruling 1)

*Every moving-water river cell gets a current; pawns and loose items in it are shoved downstream.*

- **Direction:** `GetWaterMovement` at the cell, quantised to 8 compass directions, computed once per map
  (on generation, and on first load of a map that predates the mod — `riverFlowMap` is saved by vanilla, so
  this is deterministic, never a re-roll). Cells with a near-zero vector get no current.
- **Lanes:** `WaterMovingChestDeep` (and its toxic twin) = **Centre** — inescapable, one cell per ~45 ticks,
  the sea's number. `WaterMovingShallow` (and twin) = **Margin** — one cell per ~90 ticks, and a pawn there
  can still wade across or out. That is "aggressive like the undersea flows" literally: the same cadences.
- **River size:** the flow vector's magnitude differs between a creek and a huge river (UNMEASURED: its
  actual range — read `TileMutatorWorker_River` before tuning). Option: scale cadence by it so a big river
  shoves harder (§4, and a card).
- **Who is carried:** pawns (colonists, animals, raiders, visitors), corpses, and loose items. **Not:**
  buildings; flying pawns (1.6 `Pawn.Flying`); races carrying the native extension (fish-like or river
  creatures we author); anything in a cell a weir arrests; anything on a ford (§4).
- **Where carrying ends:** the next step must be in bounds and standable. So a carried thing stops at a weir,
  a bank bend, a bridge cell (UNMEASURED: whether a bridged cell still reports `IsRiver` — 1.6 bridges are
  foundation terrain; read `TerrainGrid` at build), or the **map edge**. What happens at the map edge is a
  real choice (Q card "Map edge").
- **AI awareness:** the carry is a teleport; the pathfinder does not know about it, so a colonist told to
  cross will be dragged and re-path, repeatedly. Vanilla already scares the AI off chest-deep moving water
  (perceived cost 180 undrafted). River Works raises the perceived cost of current cells further by an XML
  patch (no Harmony), so ordinary jobs route to bridges and fords, and drafted orders still go where told.
- **The surge:** while any registered flood source is live (vanilla seasonal flood, torrential-rain flood,
  sea undersurge), Margin behaves as Centre and Centre doubles — the sea rule, now meaning *"spring flood
  makes the river deadly"*.
- **Gear:** the float harness moves here (caps a wearer at Margin speed). It is RM_-tier and invented.
- **Tell:** first time a colonist is grabbed on a map, one message (the sea's `MaybeWarnFirstEntry`).
  "No pawn ever vanishes without a readable sign" (owner, heat ruling) — so a pawn carried off-map, if that
  option is chosen, gets a letter naming them.

### 3.2 Stake (and the stake-line levee — ruling 2)

`RM_BankStake`: cheap wood post, 1×1, edifice, lamp-topped (existing CompGlower), bank ground only. Wears
slowly (repair = "re-drive"). **A continuous line is a levee by engine fact**: vanilla floodwater cannot
spread into an edifice cell, so the flood stops at the line; any gap — missing post, snapped post, a door
left in the line (UNMEASURED: whether a door counts as an edifice to `CanFloodSpreadInto`; it is a Building
with `IsEdifice`, so probably yes — guard it in the script) — leaks at once. Behind-the-line cells stay dry
for the flood's whole 4–6 days. Option (§4): a stake-line must be tied to a weir to count, or any line works.

### 3.3 Weir (rulings 1, 4)

`RM_BankWeir`, re-shaped **1×2 across the bank edge** like the watermill: one cell on moving water, one on
bank ground (`RM_PlaceWorker_RiverWeir`). Three jobs in one building:

1. **Tames the current.** Its water cell arrests (the existing `CompChannelArrester` idea, moved here):
   anything carried into it stops there. Plus a **slack-water pool**: N cells upstream along the flow
   (default 3) drop one lane (Centre → Margin, Margin → none). That is what lets a colony cross, fish, or
   work a dangerous river at one chosen place. (Pool size is a card.)
2. **Catches fish** from the river's own stock. Every catch interval (default: one roll per 6 hours) it
   rolls against `FishPopulationAt` its water cell, spawns one fish from that body's `CommonFish` (rarely
   `UncommonFish`) on its **bank** cell, and calls `Notify_Fished` — so the fishing zone on the same river
   now finds less. Stock low → catch rarer. Catch held on the bank cell stacks up to a cap (default 30)
   until hauled ("tend the weir").
3. **Catches drift.** Corpses and items the current carries end up in it too — a downstream weir is where
   a river returns what it took.

**Breach (ruling 4, existing state machine):** a flood source goes live while the weir is below 50 % HP →
big-threat letter, arrester and pool switch off, **held catch is released into the current for a few cells
(default 4) and then strands on the nearest bank** (rotting meanwhile in moving water at ×3 deterioration),
the downstream stake-line snaps post by post on a visible timer, and the flood pours through each gap.
Repair to ≥ 50 % re-arms. Walls are never touched — catastrophe of harvest and safety, never a base-delete.

### 3.4 Silt-trap

As the 2026-10-02 doc §2: bank-only, richens `Soil` / `GrasslandSoil` / `MarshyTerrain` → vanilla
`SoilRich` within r=3.5 while healthy (one cell per half-day); a breach reverts the cells it changed.
Swap table is a `DefModExtension` so the sea registers its own pair. This is the one piece that has never
worked anywhere (its sea terrains were never authored) — first real build.

### 3.5 Maintenance

No new work type: wear → vanilla Repair; catch → vanilla Haul. A weir left alone is a weir that breaches
next spring — that IS the loop.

### 3.6 Flood-source registry

`RM_RiverWorks.FloodActive(Map)` true when any registered source is live. Built in: vanilla
`SeasonalFlood`, `TorrentialRainFlood`. Registered by others: TerminalBiomes' undersurge; optionally
FlowWorks' canal release (§6). Drives both the surge (3.1) and the breach (3.3).

### 3.7 Ford stones (the one piece already named but never built)

The sea carry already *exempts* cells on or next to `RM_FordStones`, a terrain nobody authored. River Works
should author it: a buildable terrain laid in Margin water (shallow only), stone cost, pathCost low. Cells on
and beside a ford are not carried. This is the cheap, natural answer to *"how do my colonists cross?"* and
it makes the sea's existing exemption real. Listed as a feature, not an option, because the engine is
already wired for it — but whether it ships in v1 is on a card.
## 4. Expansion options (for the owner, not decisions)

Each is sized as extra work on top of the core (§8). None is decided; the cards ask which belong.

| option | what the player gets | buys | costs | size |
|---|---|---|---|---|
| **Fords** (§3.7) | lay stepping stones across shallow water; nothing is carried on or beside them | the obvious crossing answer; makes the sea's dead exemption real | shallow-only, so a deep river still needs a bridge | S — one TerrainDef, art |
| **Ferry / rope line** | a two-post rope across deep water; a pawn holding it is not carried, crosses at walking speed | crossing deep rivers without a bridge's cost | new building pair + a job driver; AI pathing must learn it (hardest piece here) | L |
| **River mill** (grinding / sawing) | a weir-adjacent mill that works crops or logs with no power, faster in strong current | a reason to build where the current is fiercest | overlaps the vanilla watermill; needs recipes and balance | M |
| **Size-scaled current** | creeks barely push, great rivers are lethal | rivers read differently by size | magnitude range UNMEASURED; one more tuning number | S |
| **Crossing hazards** | a pawn carried in Centre lane can take bruise damage and drop held items; animals can drown | carrying has teeth beyond lost time | more ways to lose colonists unexpectedly; must be readable | S–M |
| **Driftwood / flotsam** | the current occasionally brings wood or a lost item down from off-map into weirs | weirs pay even when fish are scarce | invents stuff from nothing; competes with the fish purpose | S |
| **Flooded fields bonus** | a field that took a flood (breach) gets a one-season fertility boost after it recedes, the Nile way | a breach is half curse, half gift | softens the breach the owner wants harsh | S |
| **River-native creatures** | creatures that ride the current (native extension) and nest at weirs | uses the surplus cast; gives rivers wildlife | roster work per biome (review sheets, never sweeps) | M per creature |
| **Floodwater current** | during a flood, the floodwater cells themselves push gently back toward the river | a flood is something you can be swept by | more pawns dragged into the river; pathing noise | S |
## 5. Mod Settings

Defaults = shipped behaviour. All-off degrades to inert buildings and still water, never an error.
Toggles that change map generation: none (the current is derived from vanilla's own flow data, so turning it
off and on is safe mid-game).

| group | setting | default | notes |
|---|---|---|---|
| master | River Works enabled | on | off: no current, buildings stand inert, no wear |
| current | Surface river current | on | off: rivers are vanilla; the sea's current is still on (its own toggle in TerminalBiomes) |
| current | Current strength | 1.0 (0.25–3.0) | divides both lane cadences |
| current | Fast-lane speed (ticks per cell) | 45 | Centre |
| current | Edge-lane speed (ticks per cell) | 90 | Margin |
| current | Items drift slower by | ×2 | |
| current | Scale with river size | per card | §4 option |
| current | Flood surge | on | Margin→Centre, Centre ×2 while any flood is live |
| current | Carry animals / carry raiders / carry items | on / on / on | three checkboxes; "colonists" has no checkbox — the master current toggle is it |
| current | At the map edge | per card | stop at edge / washed off map |
| current | Teach the pathfinder to avoid currents | on | the perceived-cost patch |
| works | Wear rate multiplier | 1.0 | scales all upkeep |
| works | Breach | **on** | owner: breach at default |
| works | Breach HP threshold | 50 % | |
| works | Stake snap speed (ticks per cell) | 150 | |
| works | Stake-line holds floods (levee) | on | off: stakes get a flood-passable flag (UNMEASURED: needs a Harmony prefix on `CanFloodSpreadInto`, since the engine test is edifice-only) |
| works | Weir slack-water pool length | 3 cells | 0 = arrest only |
| fish | Weir catches fish | on | |
| fish | Catch interval | 6 h | |
| fish | Held-catch cap | 30 | |
| fish | Breach washes catch | 4 cells | 0 = lost outright |
| silt | Silt richening | on | plus speed |
| floods | Which floods count | seasonal ✓, torrential-rain ✓, + registered (undersurge ✓, canal release ☐) | event-linked, not worldgen |
| expansions | one toggle per shipped expansion | on | per §4 picks |
## 6. How the sea floor consumes River Works

TerminalBiomes adds `mandrake.rm.riverworks` to `modDependencies` and loads after it. It keeps the Twilight
genstep, undersurge, sink, cargo float and its biome toggles. It talks to River Works through three seams:

1. **Current field writer** — `RM_CurrentField.SetFlow(cell, dir, lane)` / `SetBankBand` (today's methods,
   moved). The Twilight genstep writes the channel grid; on surface maps River Works writes it from
   `riverFlowMap`. One map component, two authors, never both on one map (a seabed map has no river mutator).
2. **Flood-source registry** — TerminalBiomes registers `undersurge active on map`; the weir breaches and
   the surge fires off it exactly as today.
3. **Sink / arrival hook** — River Works calls an optional `IRM_CurrentSink` when a thing reaches an
   edge-stop cell; TerminalBiomes implements it with its sink cells. Surface maps without it use the
   map-edge rule.

Its silt pair (`RM_BankSilt → RM_BankSilt_Rich`) is a TerminalBiomes patch onto the trap's swap table,
**still owed** (the terrains do not exist). Its Compact's pre-placed weir keeps `neverBreaches`.
**Sea behaviour must be byte-for-byte what it is today** — that is a script bar (§9), and the reason the
cadences above default to the sea's numbers.

The other three sea biomes (Scald, Grey Sea, Propane Lake) have no current today; this mod makes adding one
cheap (author a grid), but none is proposed here.
## 7. Naming, packaging, save-compat

- packageId `mandrake.rm.riverworks`, display name "RimMandrake: River Works", folder
  `src/RimMandrake/RiverWorks/`, namespace `RimMandrake.RiverWorks`, prefix `RM_`. No reason found to deviate:
  everything here is invented and franchise-free (Q11a). Free tier, any game.
- **Biome-mod unification:** River Works is NOT a biome, so it stays its own top-level mod rather than
  folding into `RimMandrake.Biomes` (Q17); it is a dependency of that and of TerminalBiomes.
- **Kept defNames:** `RM_BankStake`, `RM_BankWeir`, `RM_SiltTrap`, `RM_FloatHarness` keep their names, so
  defs in saves still resolve.
- **Class moves break saved instances:** `RimMandrake.TerminalBiomes.RM_Building_BankWeir` →
  `RimMandrake.RiverWorks.…`. A saved weir loses its class. Fix cheaply with vanilla's
  `BackCompatibilityConverter` type remap, or accept the loss — map state is disposable and the world remake
  is the last step. Recommend the remap (an hour) since TerminalBiomes saves exist for testing.
- **Current grid save:** the moved component keeps its Scribe keys, so a Twilight map saved today loads
  its channels unchanged. Surface grids are derived, not saved — nothing to lose.
- **Mid-game add/remove:** adding is safe (grid derived on load). Removing leaves buildings missing their
  class (vanilla drops them with a log line).
## 8. Build cost estimate

| piece | est. | notes |
|---|---|---|
| Scaffold (About, csproj with explicit Compile list, settings screen) | 0.5 session | |
| Move current engine + bank works out of TerminalBiomes, seams, back-compat remap | 1 | mechanical but touches a live mod; TerminalBiomes' script must stay green |
| Surface current: grid from `riverFlowMap`, lanes, exemptions, path-cost patch, map-edge rule | 1 | |
| Weir: PlaceWorker, 1×2 shape, pool, fish roll + `Notify_Fished`, catch cap, breach wash | 1 | |
| Levee + downstream cascade + flood registry | 0.5 | engine does the levee |
| Silt swap table | 0.25 | |
| First script + walk + mock selftest | 0.5 | |
| Art: stake, weir 1×2, trap, (ford) — artpipe search first | daemon time | three placeholders today |
| **Core total** | **≈ 4–5 sessions + one load round** | |
| Each §4 option | S ≈ 0.25, M ≈ 0.5–1, L ≈ 1.5–2 | ferry is the only L |
## 9. North star and first script

Per `design/RimMandrake/debug_process.md` §2. **North star:** BENCH seeds a provisional `## north star` section
in the walk below from §0's four rulings; only the owner validates it. **First script:** `src/RimMandrake/RiverWorks/validation.py`
(a modcheck `Suite`) with walk `design/validation_walks/RimMandrake/RiverWorks.md`.

`## must be true` (each line gets a cheap state-read component):

- Defs load; weir carries `RM_PlaceWorker_RiverWeir`; current component present on a river map → `defs.core`
- A river quicktest map has a non-empty current grid; chest-deep cells are fast lane, shallow are edge lane → `current.grid_from_river`
- A colonist placed in fast-lane water is moved ≥3 cells downstream within 200 ticks; one on a ford is not moved → `current.shoves` / `current.ford_exempt`
- A flying pawn and a building are never moved → `current.exemptions`
- Spawning `SeasonalFlood` turns on the surge (edge lane moves at fast-lane cadence) → `current.flood_surge`
- A weir cannot be placed on dry ground or wholly in water; can across a bank edge → `place.weir_bank_edge`
- A thing carried into a weir stops there; the pool cells upstream drop a lane → `weir.arrest_and_pool`
- A weir over a stocked river spawns a fish on its bank cell and `FishPopulationAt` drops → `weir.fish_draws_stock`
- A continuous stake-line keeps a spawned `SeasonalFlood` off every cell behind it; one removed post lets it in → `levee.holds` / `levee.gap_leaks`
- Below 50 % HP a weir breaches within 600 ticks of a flood; at full HP it does not → `breach.threshold`
- On breach, held catch ends within 4 cells downstream on a bank; downstream stakes fall in downstream order → `breach.wash` / `breach.cascade_order`
- Silt-trap richens `Soil` → `SoilRich`; breach reverts → `silt.richen_and_revert`
- Every settings toggle off removes its effect (`suite.toggles`) → `toggles.*`
- **TerminalBiomes regression:** Twilight channel carry, undersurge breach and weir arrest behave as before the move → `sea.unchanged` (reuses TerminalBiomes' own suite components)

`## anti-guessing notes` to seed:
- `RULED OUT: stakes must be Impassable to stop a flood — Flood.CanFloodSpreadInto tests GetEdifice only`
- `RULED OUT: rivers need an authored flow grid — vanilla saves riverFlowMap per cell (WaterInfo.GetWaterMovement)`
- `RULED OUT: the weir can use FishingUtility.GetCatchesFor — it requires a Pawn`
- `UNMEASURED (guard it): a door in a stake-line counts as an edifice to the flood`; `bridge cells still report IsRiver`

Offline `static_check()` under `--mock` first (defs parse, csproj lists every .cs, swap table names real
terrains, PlaceWorker named); live chain on a quicktest river map with the flood spawned directly.
## 10. Questions for the owner

Cards: `Transient/river_works_cards_2026-10-03.json` (3 cards, 10 questions). Same questions in prose:

**Card 1 — the current**
1. **Map edge** — when the river carries someone to the edge of the map: stop there and wade out
   (recommended; nobody vanishes) / washed off the map and return days later / washed off and lost, with a letter.
2. **River size** — every river shoves equally / bigger rivers shove harder, creeks barely (recommended) /
   only the deep channel shoves at all.
3. **Flood surge** — should a spring flood make the river itself fiercer (recommended) / leave the river's
   strength alone?
4. **Pathfinding** — teach colonists to avoid strong water and use bridges/fords (recommended) / let them
   blunder in and be dragged / avoid only while a flood is on.

**Card 2 — weir and harm**
5. **Weir calm** — arrest only its own cell / calm about 3 cells upstream into a crossing pool (recommended)
   / calm a long stretch (~8 cells).
6. **Weir catch** — fish only (recommended) / fish plus rare driftwood / fish plus anything carried from off-map.
7. **Harm** — being swept only moves you (recommended) / also bruises and may drop what you carry /
   also drowns downed pawns and small animals.

**Card 3 — what goes in the mod**
8. **First version** — core plus fords (recommended) / core only / core plus fords plus crossing hazards /
   core plus fords plus rope ferry.
9. **Mills** — leave grinding/sawing to the vanilla watermill (recommended) / add a powerless river mill
   later / add it in the first version.
10. **Old saves** — carry existing sea-floor weirs across the move (recommended) / accept they vanish.
