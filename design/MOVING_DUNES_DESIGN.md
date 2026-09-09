# MOVING_DUNES_DESIGN — real aeolian transport for RimWorld maps

**Status: DRAFT v2 — owner rulings folded, build-ready pending final read** · item
`MOVING_DUNES_ENGINE_1` · 2026-09-09
Engine sources verified via RimSage against 1.6 decompiled source (file:line cited inline).
Owner rulings folded (2026-09-09): Odyssey soft-dep YES · pacing fully tunable ·
edge condition designed §2, source/sink chosen · wild-items-only burial · generic
release day one with per-map material skins · dig-vanishes and vanilla half-speed accepted.

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
### The edge condition: source/sink, not toroidal (RULED — designed here, committed)

The owner's fast-dune case (violent windstorms marching dunes clear across the map)
forces the choice. **Toroidal wrap** (leeward exit re-enters windward) conserves mass
perfectly and needs no tuning — but it loops the SAME sand forever: total mass is
frozen at map-start, so a violent storm can never bring MORE sand than the map began
with, a wind reversal replays the same banks backwards, and opposite map edges become
visibly correlated (a dune exiting south materializes north — the fiction of an
endless desert breaks exactly at the map edge where it matters). **Source/sink** treats
the map as a window onto an endless desert: slabs hopping off the leeward edge are
gone; a windward-edge influx budget deposits new sand at a tunable rate. **Committed:
source/sink** — it is the only model where influx is a knob (per-biome base ×
per-weather multiplier, which is precisely what "disturbingly fast dunes during
windstorms" needs), and the endless-desert fiction holds. Save implications are equal
(both are just the existing depth grid; source/sink adds one float of accumulated
influx debt to the MapComponent). Guard: a total-grid-mass cap per material def so a
mis-tuned influx cannot drown a map unboundedly — unless the def says it can (see
open question 3).

- **Supply**: influx ≪ loss ⇒ isolated migrating banks; influx ≈ loss ⇒ steady dune
  field; influx > loss ⇒ a map that is slowly burying (designer's choice, capped).

### The tunable surface (RULED: no constants — everything a designer might retune is data)

One new def type, **`RM_DuneMaterialDef`**, is the whole knob panel; the MapComponent
reads it, hardcodes nothing: `tint` (display color), `slabSize` (q), `hopRange`,
`erodeMinDepth`, `windSpeedThreshold`, `shadowRange`, `attemptsPerCellPerDay` (K,
normalized by map area), `stormTransportFactor` (default 4×; a violent-windstorm
WeatherDef can carry a modExtension overriding it higher), `ambientDecayFactor`
(0 = full suppression), `influxPerDay` + `weatherInfluxFactor`, `burialDepth`,
`revealDepth`, `plantChokeDepth`, `plantChokeDays`, `maxTotalMassFraction`, optional
`depositFilthDef`. "Particle mass" (owner's phrase): Odyssey has no mass concept —
mass IS the parameter cluster (heavier ⇒ higher `windSpeedThreshold`, shorter
`hopRange`, larger `slabSize`), and the def is where it lives. Biomes bind a material
via DefModExtension; the map resolves its one material at init.

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

### Rendering: subclassed layer with a per-map tinted material (delivers "any color, anywhere")

`SectionLayer_Sand` draws opacity-blended windswept sand at terrain altitude, but from
one STATIC shared material (`GetSubMesh(MatBases.Sand)`, `SectionLayer_Sand.cs:62`) —
no per-map color source exists. The route that ships: our own `SectionLayer` subclass
(MapDrawer auto-instantiates every SectionLayer type per map, so it is per-map by
construction) that clones the vanilla layer's vertex-opacity logic against the same
depth grid and same `MapMeshFlagDefOf.Sand` dirty flag, but builds its submesh from a
per-map `new Material(MatBases.Sand)` instance carrying the material def's `tint`
(the mesh's vertex colors carry opacity in alpha and the pollution mask in red;
material color multiplies on top). One tiny prefix on `SectionLayer_Sand.Regenerate`
disables the vanilla submesh on skinned maps so the two layers never double-draw.
⚠️ One honest unknown: whether the sand shader respects material `color` — if it
ignores it, the fallback is drawing with a vertex-color shader from `MatBases` and
folding the tint into our own vertex RGB (we own the layer, red is free on skinned
maps). Verify with one quicktest before building the rest. The same subclass adds the
downwind-gradient crest shading (darkened slip faces, lightened crests) that fixes
sand-on-sand contrast — the reason vanilla excluded sand terrain. Visual burial of
things is a vanilla FIELD:
`hideAtSnowOrSandDepth`, honored by `SectionLayer_Things.cs:66`,
`DynamicDrawManager.cs:69`, and `Plant.cs:193` — we set it by XML patch on the
categories we bury.

## 3. Gameplay systems, each on its vanilla anchor

- **Burial of items** (RULED: wild/unclaimed only — anything in a stockpile, home
  area, or player-forbidden-on-purpose is exempt) — depth > `burialDepth` sustained
  over a cell holding qualifying haulables ⇒ despawn
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
cell — there is no multi-material grid to fuse into, `snowGrid` is temperature-owned,
and ash is filth (Pyrelands' ladder), not a grid. Multi-material-PER-MAP therefore
stays refused. But the owner's "any color, anywhere, with particle mass" (ruled, v2)
is delivered one level up: **one material PER MAP** — the map's `RM_DuneMaterialDef`
skins the channel (tinted renderer §2, transport-mass parameters, optional deposit
filth) so an ash map drifts grey and a glacier-sand map drifts blue on the SAME grid
with all vanilla couplings intact. The engine+data-pack doctrine (R6) lands at the
right layer: **RM_MovingDunes is the machinery** (transport, burial, choke, wind
state, skin renderer) with a generic sand material as default content; **data packs
add materials and biome bindings** — RUT patches the campaign's deserts and any
Pyrelands ash-dune biome in. Per R6's guard: materials are real def-configured
machinery users, not empty shells.

## 5. v1 cut (YAGNI)

**Ships:** one grid channel (`map.sandGrid`; Odyssey soft-dep, inert without — RULED);
`RM_DuneMaterialDef` + the full tunable surface (§2 — RULED: no constants) with one
generic sand material as default; per-map material skin renderer (subclassed layer +
tinted material instance + vanilla-layer suppression prefix); MapComponent with saved
wind direction + Werner slab transport (erode/hop/shadow/prefer-low, weather-driven
transport factor); source/sink edge flow with tunable influx and mass cap (RULED §2);
patches: CanHaveSand-on-sand, ambient-decay suppression (per-map-flag, loud-failure);
burial caches — **wild/unclaimed items only (RULED)** — + reveal + `BuryThingsAt` API;
plant choke; biome opt-in via DefModExtension, **generic from day one (RULED)**:
vanilla Desert/ExtremeDesert bound to the default sand material in the RM mod itself,
campaign biomes via RUT pack.
**Out, explicitly:** multi-material per map / own grids; snow drifting; sand as a
haulable item (dig vanishes — RULED); deep-drift extra path tier (vanilla half-speed
accepted — RULED); burying pawns/corpses/turrets; any worldgen; non-Odyssey fallback.
**Size vs the yardstick:** Pyrelands' `FireEcologyHook.cs` is ~400 lines/one file.
v2 additions (material def + skin layer + suppression patch + formalized edge flow)
move the estimate: transport component ~400, material def + resolution ~100, skin/crest
layer ~180, cache thing ~150, patches ~180, choke ~50, plus XML — call it
**1,100–1,400 lines C#** in one small assembly. A real mod, not a hook; still bounded,
and nothing in it is speculative.

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

## 7. What remains genuinely open (post-rulings)

1. **Shader tint** (technical, pre-build gate): does the sand material's shader respect
   material `color`? One quicktest decides tinted-instance vs vertex-color fallback
   (§2 Rendering). This and decay-suppression fragility (§6.3) are the two build risks.
2. **Decay-suppression mechanism** (technical): exact-constant intercept vs transpiler
   on `DoCellSteadyEffects` — decided at build time by whichever survives a selftest
   asserting the vanilla constant.
3. **Owner-level, the one real question left:** may a material def legitimately set
   influx > loss so an unmanaged map PERMANENTLY buries (a slow-loss map as designed
   drama), or is the total-mass cap always binding? Default until ruled: cap binding.
