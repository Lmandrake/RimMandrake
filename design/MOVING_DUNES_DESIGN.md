# MOVING_DUNES_DESIGN — real aeolian transport for RimWorld maps

**Status: DRAFT — pending owner ruling** · item `MOVING_DUNES_ENGINE_1` · 2026-09-09
Engine sources verified via RimSage against 1.6 decompiled source (file:line cited inline).

## 1. Verdict

**Worth building — in the cut form below, and the cut is most of the fun.** The
fun-per-effort ratio is unusually good for one reason: Odyssey already shipped ~80% of
the substrate as a live, save-integrated sand channel — `Map.sandGrid` (a per-cell float
depth grid, `Verse/SandGrid.cs`), a renderer (`SectionLayer_Sand`), pathing penalties
(`PathGrid.cs:169`), a clear-sand designator/area/WorkGiver
(`Area_SnowOrSandClear`, `JobDriver_ClearSnowAndSand`), per-def visual burial
(`ThingDef.hideAtSnowOrSandDepth`, honored by both static and dynamic drawers), plant
gating (`PlantUtility.SandAllowsPlanting`, depth ≥ 0.2 blocks sowing and wild spawns),
and a Sandstorm weather that already deposits into the grid (`sandRate 1.6`,
`Defs/Odyssey/WeatherDefs/Weathers.xml`). What vanilla lacks is exactly the interesting
part: the sand never MOVES after landing, and it evaporates within days. The mod is
therefore one bounded cellular automaton plus a burial container plus ~4 small Harmony
patches — not a physics engine. The full vision as spoken ("any particle type", 1.5m
drifts, fused multi-material physics) fails fun-per-effort and partly fails the engine
(depth is hard-capped at 1.0, the grid is single-channel); the cut — **sand only, riding
Odyssey's grid, Werner-style slab transport, burial caches, plant choke** — keeps every
gameplay beat the owner named (creeping dunes, buried reveals, refilling pits, slow
crossings, windbreak engineering) and is the campaign's own fantasy: Jawas sweeping
erosion faces after a wind shift. Not a terrible idea. The terrible version is the
generic multi-material own-grid engine; this design refuses it.

## 2. The mechanism, for real

### Grid: ride `map.sandGrid`, do not build one

An own `DepthGrid` forfeits everything vanilla already couples — renderer, path cost,
clear job, hide-at-depth, plant gating, sandstorm input, ushort-compressed save — and
would need all of it rebuilt (snow's and sand's mesh layers are engine `SectionLayer`s;
reimplementable, but that's the whole budget gone on parity). `snowGrid` is out: melt is
temperature-driven (`SteadyEnvironmentEffects.MeltAmountAt` — anything above 0 °C melts
it), useless on a desert. `sandGrid` is Odyssey-gated at construction
(`SandGrid.cs`: `ModLister.CheckOdyssey("sand")`; without Odyssey the NativeArray is
never created and every call no-ops safely). **The campaign runs Odyssey; the mod
declares it a soft dependency and is inert without it — that is the honest price of
riding the channel.** Facts that shape everything: depth ∈ [0,1] (1.0 ≈ "thick", the
cap — there is no 1.5m), saved as ushort/cell (125 KB on 250×250, already in every
Odyssey save; we add zero save data for the grid itself).

Three vanilla behaviors fight persistence, each needing one patch (all patched with the
FireEcology loud-failure pattern — target missing ⇒ `Log.Error`, rule off, not silent):

1. **Sand refuses sand terrain.** `SandGrid.CanHaveSand` returns false on
   `Sand`/`SoftSand` and any `!holdSnowOrSand` terrain — on a desert map most cells
   can't hold depth. One prefix on the private method, gated on a per-map "dune field
   active" flag.
2. **Ambient decay.** `SteadyEnvironmentEffects.DoCellSteadyEffects` removes 1/180
   depth per cell-visit whenever `sandRate ≈ 0` (and always indoors). Visit cadence is
   ~every 1,667 ticks per cell ⇒ a full-depth drift evaporates in ~5 clear-weather
   days. For persistent dunes this must be suppressed on dune-field maps (prefix on
   `SandGrid.AddDepth` intercepting the exact ambient constant when our flag is set;
   fragile to game updates — hence the loud-failure logging).
3. **Zeroing writers.** Building spawn (full-fillage), floor construction, terrain
   changes, gravship placement all `SetDepth(0)` — correct behavior, keep it; it means
   walls can never be buried and are natural dune fences for free.

### Transport rule: Werner slab model, amortized like the ashfall batches

Vanilla has wind SPEED only — `WindManager` is one Perlin-driven float, **no direction
exists anywhere in the engine** (verified: `Verse/WindManager.cs` whole class). The
MapComponent owns a persistent wind direction (8-way), random-walking on a multi-day
timescale, saved in `ExposeData`. Wind shifts are the reveal-mechanic driver.

Per batch (every 250 ticks, the Pyrelands ashfall cadence), K random unroofed cells:

- **Erode** if depth ≥ 0.1, wind speed above threshold, and the cell is not in a wind
  shadow (a full-fillage edifice or a meaningfully deeper cell within ~4 cells upwind).
- **Hop** a slab (q = 0.05 depth) 2–6 cells downwind; **deposit** at the first
  candidate that is shadowed or lower-depth than its neighbors — deposition prefers low
  cells, so **pits and cleared lanes refill from the rule itself, free** (the owner's
  pit mechanic is not a feature, it's a corollary).
- **Supply**: eroding cells at the leeward map edge lose mass off-map; a per-biome
  influx budget deposits at the windward edge. Influx ≪ field ⇒ isolated migrating
  banks; influx ≈ loss ⇒ steady dune field. This is the one big tuning knob.

**Budget arithmetic, 250×250 (62,500 cells):** K = 2,000 attempts/batch is index math
plus a short upwind scan — sub-millisecond, and only every 250 ticks (the ashfall
component's not-my-weather path stays nearly free). One full-map sweep = ~31 batches ≈
7,800 ticks ≈ 3 in-game hours. A crest advances one cell per ~depth/q = 20 slab
arrivals ≈ 20 sweeps ≈ **2.5 game days per cell** — a 10-cell creep toward the base is
a season. That is the owner's "extremely slow" pacing, tunable via K and q, with a
storm multiplier (during Sandstorm weather, 4× K) so storms visibly reshape the field.
Mesh cost: `SandGrid.CheckVisualOrPathCostChange` already rate-limits dirtying (only
changes > 0.15, else 1.25% chance) — q = 0.05 slabs ride that limiter by design.

**Emergent shapes, honestly:** Werner's model (the 1995 CA this rule is) genuinely
produces transverse ridges under one wind and barchans under limited supply — but at
depth cap 1.0, 8-way quantized wind, and this cell count, you get **readable creeping
drift banks with crisp windward erosion faces, leeward lobes, and classic
snowdrift-behind-fence tails around every building** — emergent and visibly
wind-driven, not textbook crescent barchans. "Dune-like", not "dune simulation". That
is enough for every gameplay beat below.

### Rendering: vanilla layer + one additive crest layer

`SectionLayer_Sand` draws opacity-blended windswept sand at terrain altitude — free.
Its one weakness is the reason vanilla excluded sand-on-sand: low contrast against Sand
terrain. Fix: one additional `SectionLayer` subclass (MapDrawer auto-instantiates all
of them) reading the same depth grid and shading by local downwind gradient — darkened
slip faces, lightened crests — keyed on the same `MapMeshFlagDefOf.Sand` dirty flag.
~120 lines, no shader work. Visual burial of things is a vanilla FIELD:
`hideAtSnowOrSandDepth`, honored by `SectionLayer_Things.cs:66`,
`DynamicDrawManager.cs:69`, and `Plant.cs:193` — we set it by XML patch on the
categories we bury.

## 3. Gameplay systems, each on its vanilla anchor

- **Burial of items** — depth > 0.75 sustained over a cell holding haulables ⇒ despawn
  the stack into a `RM_Dunes_BuriedCache` thing (ThingOwner container, low-bump
  graphic; anchor: grave/crashed-part inner containers). Present-but-hidden via
  `hideAtSnowOrSandDepth` alone is worse: the item stays selectable, haulable, and
  deteriorating — confusing, not buried. Caches pause deterioration, merge per cell,
  and **respawn contents when erosion drops the cell below 0.25** — the wind-shift
  reveal IS the scavenger-campaign hook. WreckedMachines wrecks and Antiquities digs
  seed caches at mapgen for free (one API call: `BuryThingsAt(cell, things, depth)`).
- **Plant choking** — vanilla already blocks sowing/wild-spawn at depth ≥ 0.2; we add
  the kill: batch visits apply damage above depth 0.5 scaled to die over 2–4 days
  (anchor: toxic-fallout-style chance damage on plants). An advancing front leaves a
  dead strip — legible, slow, fair.
- **Movement** — vanilla already charges +4/+8/+12 ticks per cell by buildup category
  (`WeatherBuildupUtility.MovementTicksAddOn` via `PathGrid.cs:169`): thick sand ≈ half
  speed. "Extremely slow" (quarter speed on deep drift) is one small postfix on the
  path-cost add — offered as a knob, not assumed.
- **Digging** — the whole loop ships in vanilla: `Area_SnowOrSandClear` designator +
  `WorkGiver_ClearSnowOrSand`. Dug sand vanishes (vanilla). A maintained clear pit
  upwind becomes a sand moat that the transport rule preferentially refills — dig,
  drift, re-dig: exactly the owner's "pits that fill in", emergent, zero extra code.
- **Windbreaks** — full-fillage buildings zero sand on their cells and cast deposition
  shadows: wall lines and cheap "sand fence" builds shape the field. Base orientation
  vs prevailing wind becomes a real layout decision.
- **Emergent plays defended:** (1) *dune-fence engineering* — sacrificial fence rows
  upwind that bank the drift where you want it; (2) *siege terrain* — approach lanes
  drift thick while your leeward killzone stays clear, so raiders wade at half speed;
  honest limit: you cannot "bury" live enemies or turrets — dune warfare here is
  terrain shaping, not entombment; (3) *prospecting after the storm* — wind shifts +
  storm-multiplied transport expose erosion faces studded with caches; a periodic
  beachcombing loop that is pure Jawa. Sandcastle synergy is flavor only (recreation
  building already needs sand terrain; deep-drift cells could gate it — one line, v2).

## 4. The Odyssey fusion question, plainly

"Fusion into the existing particle physics" can only honestly mean: **ride Odyssey's
single sand channel and inherit everything coupled to it.** `sandGrid` is one float per
cell with one material — there is no multi-material grid to fuse into, `snowGrid` is
temperature-owned, and ash is filth (Pyrelands' existing ladder), not a grid. A generic
per-material engine-owned DepthGrid is buildable but forfeits every vanilla coupling
and is the 5× budget version of the same fun. The engine+data-pack doctrine (R6) is
satisfied at the right layer: **RM_MovingDunes is the machinery** (transport, burial,
choke, wind state) with generic defaults; **data packs configure it** (biome opt-ins,
influx budgets, thresholds, cache loot tables) — RUT patches the campaign's deserts in.
Materials-as-skins is deferred until a second real material exists with real machinery
behind it; per R6's guard, no empty shells.

## 5. v1 cut (YAGNI)

**Ships:** sand only, riding `map.sandGrid` (Odyssey soft-dep, inert without);
MapComponent with saved wind direction + Werner slab transport (erode/hop/shadow/
prefer-low, storm multiplier, edge influx); patches: CanHaveSand-on-sand, ambient-decay
suppression (both per-map-flag, loud-failure); burial caches + reveal + `BuryThingsAt`
API; plant choke; crest-shading section layer; biome opt-in via DefModExtension
(vanilla Desert/ExtremeDesert patched in as the generic default, campaign biomes via
RUT pack).
**Out, explicitly:** multi-material/own grids; snow or ash drifting; sand as a haulable
item; deep-drift extra path tier (knob, ruled separately); burying pawns/corpses/
turrets; any worldgen; non-Odyssey fallback; sandcastle coupling.
**Size vs the yardstick:** Pyrelands' `FireEcologyHook.cs` is ~400 lines/one file. This
is 4–6 hooks' worth of real machinery: transport component ~350, cache thing ~150,
patches ~150, section layer ~120, choke ~50, plus XML — call it **800–1,100 lines C#**
in one small assembly. A real mod, not a hook; still bounded, and nothing in it is
speculative.

## 6. Perf and failure risks — top 3

1. **Section-regen churn** (the real cost, not the automaton): every meaningful depth
   change dirties Sand AND Things mesh sections. Mitigation: q = 0.05 slabs sit under
   SandGrid's built-in 0.15/1.25% dirty limiter; cap K; batch slab moves spatially so
   one section regens once per batch, not twenty times.
2. **Path-cost recalc storms / hauling AI thrash**: category-boundary crossings call
   `RecalculatePerceivedPathCostAt` per cell; a dune front crawling across the main
   hauling artery re-paths the colony forever. Mitigation: hysteresis — transport
   avoids depositing a cell to rest exactly at a category boundary; fronts move cells
   per days, not per hour.
3. **Cache proliferation as save bloat** (the grid itself adds zero — already ushort in
   every Odyssey save): thousands of one-pebble caches. Mitigation: merge per cell,
   bury only stacks above a value/age floor, hard per-map cap with oldest-merge.
   Honorable mention: the two Harmony patches ride exact vanilla constants — a game
   update silently changes dune behavior; the loud-failure pattern plus one selftest
   asserting the constants is the guard.

## 7. Open questions for the owner

1. Odyssey as a hard soft-dependency — acceptable that the mod is inert without it?
2. Pacing ruling: ~1 cell of crest creep per 2–3 days baseline, 4× during sandstorms —
   right feel, or should calm-weather creep be near-zero and storms do all the work?
3. Burial scope: everything unroofed (your stockpiles too — harsh, forces roofs/walls)
   or wild/unclaimed items only in v1?
4. Deep-drift movement: keep vanilla's ~half speed, or ship the quarter-speed deep
   tier (one extra patch)?
5. Should digging yield a haulable sand item (sandbag/sandcastle economy), or vanish
   like vanilla clear-sand? (v1 default: vanish.)
6. Generic release posture: RM_MovingDunes with vanilla deserts opted in from day one,
   or campaign-gated until it has soaked on Ash'karr?
