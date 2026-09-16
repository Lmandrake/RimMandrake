# Fluid Canals — mod definition

Status: DRAFT — agent-drafted 2026-09-16 from the owner's bench session; his four rulings of that date are marked; nothing else here is ruled.

Position in the family: FluidCanals is the **flow-engine client** of the liquids framework
(`design/RimMandrake/liquids_framework_design.md` §5 client map). Liquid *types* are rows in the core
registry (`LiquidDef`); pumps, tanks and hoses belong to `RimMandrake: Liquid Logistics` and are
**not** this mod's to build — it only publishes the interface they debit against (§8). Framework
pillar 2 — *pulsed spread only, no per-tick fluid sim, ever* — is an owner ruling, and everything
below stays inside it.

## 1. What the mod is

The player digs channels into soil and a nearby liquid body flows into them, so a canal is an
extension of that body rather than a new thing: what fills it, how fast, and how far it reaches are
properties of the liquid and of the source's remaining volume. Every source carries a real stock, so
filling a canal, pumping into a tank, or letting a canal burn all take the same liquid out of the
same body, and the body visibly recedes. The spine is **defense** — a channel is a barrier when dry,
a wade when wet, a fire trap when flammable, and an inescapable pit when it holds slime — with
irrigation, industry and terraforming riding the same engine.

## 2. The four rulings (owner, 2026-09-16)

1. **Motivation ranking.** Defense first, then irrigation, then industry, then terraforming.
   Defense is the spine: viscosity, ignition and escape times are the numbers tuned until they
   feel right. Terraforming is allowed to be rough.
2. **Refill.** A limited source refills slowly from rain, season, and ground liquids oozing in.
   His words: *"Less punishing but it can take quite a while to fill up from a very small natural
   source."*
3. **Acquisition — all four routes are real.** You can produce a liquid; you can drill it, on the
   right maps, with custom buildings — *"but that's part of Many Waters please add"*; you can pump
   it in from tanks or other areas; and you can find lakes, ponds, seeps, rivers and oceans.
4. **Scarcity is stock, not rate.** A full reversal of the 2026-09-13 line: every source carries a
   real volume, "limitless" means a stock large enough that it never matters, and conservation of
   mass is true everywhere. He accepted the stated costs — a map-edge source needs an arbitrarily
   huge number, and this invites *"can I drain the ocean?"* (answered in §5).

Rulings 2 and 3 carry his verbatim words; 1 and 4 are recorded in summary form — if exact wording
matters later, take it from the session record, not from here.

## 3. The player loop, defense spine

1. **Site the source.** She picks a liquid body — a found pond or seep, a drilled well (ManyWaters,
   ruling 3), or a tank pumped in (Liquid Logistics) — behind the approach corridor she wants to
   deny.
2. **Dig.** She drags the **Dig canal** designator across soil; colonists carve it cell by cell
   into `RM_Channel_Empty`. **BUILT.** Dry, the trench already slows a crossing pawn — a soft wall.
3. **Hold the gate.** She leaves the last cell between channel and source undug, so the canal stays
   dry and costs nothing. **This is the decision the loop turns on**: liquid spent is liquid gone
   (ruling 4), so she banks the source until a raid is inbound.
4. **Open it.** Digging that cell primes the source and the first arrival fires immediately, not a
   cadence later. **BUILT.**
5. **Watch it run.** The liquid walks the channel at its own viscosity — water almost at once, tar
   creeping — with fill visible cell by cell and partial fill within a cell.
6. **Watch the source pay.** Its art drops to strained; its inspect pane reads remaining stock, or
   *limitless*. A small pond visibly shrinks at its far edge.
7. **The raid hits.** Water: raiders wade at the wet terrain's cost, slowed and exposed for the
   crossing. Tar or propane: she ignites the channel, the whole length burns for a long time, and
   the fire runs back along the liquid to the source. Slime: entrants effectively cannot cross, and
   climbing out takes long enough to be a death sentence.
8. **After.** The fire burns out, the liquid drains, the floor underneath comes back — **BUILT**,
   releases are recoverable. The source is down by what it spent and refills over seasons
   (ruling 2), so the next raid is fought with a poorer canal unless she has been banking.

Steps 1–4 exist today, as does step 8's drain-and-restore. Steps 5, 6 and 7 — and the fire and the
refill in step 8 — are the mod.

## 4. Mechanics against the code

| Mechanic | State | Detail |
|---|---|---|
| Dig-canal designation, work giver, job | **BUILT** | `Designator_DigCanal` / `WorkGiver_DigCanal` / `JobDriver_DigCanal` carve `RM_Channel_Empty` into diggable soil; refuse edifices, water, existing channel, non-soil |
| Source priming on canal contact | **BUILT** | `CompFluidReservoir.Notify_CanalCellOpened` primes on 8-way adjacency to the building's occupied rect and fires one release at once |
| Recurring release cadence | **BUILT, wrong model** | Two independent releases off `CompTickRare` — drip (`dripVolume`/`dripIntervalTicks`) and re-flood (`reFloodVolume`/`reFloodIntervalTicks`). A **rate that can never run dry**; ruling 4 replaces it with a stock |
| Recoverable release | **BUILT** | `SetTempTerrain` + `QueueRemoveTerrain`; a boxed-in flood self-destroys at `spawnedTick + 2 * FloodingTicks`; `ticksPerTile` is a real per-fluid field with `MaxFloodDurationTicks` derived from it. The three `FLUID_CANAL_FLOOD_TUNING_GAPS_1` defects were fixed 2026-09-02, item closed at 747b0025 |
| Flow speed per liquid | **PARTIAL** | `FluidDef.ticksPerTile` is real and drives the rate; viscosity as a named concept with bands is UNBUILT and belongs to the registry's `viscosityClass` |
| **Spread confined to the channel** | **UNBUILT — the biggest gap** | `Flood_FluidCanal` inherits vanilla's gating and spreads across any open, non-water, non-edifice ground. It does **not** follow the dug channel. §6 |
| Source stock / volume | **UNBUILT** | No stock of any kind exists. §5 |
| Limited vs limitless detection | **UNBUILT** | Nothing inspects a body's extent or its map-edge contact |
| Strained-source graphic | **UNBUILT** | And no art to draw it with |
| Partial fill / fill progression | **UNBUILT** | Exactly one filled state: vanilla's `ShallowFloodwater` |
| Parent body recedes in proportion | **UNBUILT** | Nothing writes back to the source body's cells |
| Filled vs unfilled movement cost | **UNBUILT** | `RM_Channel_Empty` declares `pathCost` 6; no code varies cost with fill state |
| Ignition, long burn, fire reaching the source | **UNBUILT** | ⚠️ UNVERIFIED premise: `About.xml:25-26` claims "vanilla ignition already works on any flammable terrain, so a fluid with flammability > 0 needs [nothing extra]". That is a previous agent's written claim, not a measured fact, and fire in RimWorld attaches to Things and cells — whether TerrainDef flammability is consulted at all is being checked against the decompiled engine. If the premise is false, ignition itself is new mechanism too. "Burns for a very long time" and "lights its source" are unbuilt either way |
| Slime near-uncrossable, slow to escape | **UNBUILT** | The mechanics live in GelatinousSlime (framework §5); the canal only has to be a legal place for slime to sit |
| Irrigation — plants near a filled canal act watered | **UNBUILT here, but SOLVED next door** | No effect of any kind in FluidCanals — but `FloodedCanyon` already ships the whole mechanism and it is copyable nearly verbatim. §11 |
| Liquid roster | **PARTIAL** | One `FluidDef`: `RM_Fluid_Water`. `RM_FluidSpring_Test` is self-labelled a test source, not content |
| Mod Settings | **PARTIAL** | Three fields: `canalFlowEnabled`, `flowRateMultiplier`, `floodVolumeMultiplier`. Every mechanic added below needs its own toggle (2026-09-12 rule) |
| Art | **UNBUILT** | Zero bespoke textures. Channel reuses `Terrain/Surfaces/Gravel`, the test source the drop-beacon sprite, the designator `UI/Designators/Mine`. §7 |

## 5. The source stock model

**Unit.** Stock uses the volume unit the engine already has: `FluidDef.volumePerTile`, the volume
one flooded tile consumes (1 for `RM_Fluid_Water`). One **fill-unit** = enough of *this* liquid to
fill one canal cell. Canal fill, pump draw, burn loss and refill are all denominated in fill-units,
so debits from different consumers compose without conversion.

**Budget.** The rule is per source *cell*: each supplies up to five canal cells. Express it as a
field on the liquid (name TBD, e.g. `canalCellsPerSourceCell`, default 5), so
`bodyCapacity = sourceCellCount * canalCellsPerSourceCell * fluid.volumePerTile`. Because the
budget is per cell, a body's *throughput* is bounded by how much of it a canal actually touches,
independently of how big the body is.

**Limited vs limitless.** On first contact, flood-fill the contiguous run of cells whose terrain
belongs to this liquid's suite. Any cell of that run on the map-edge rect ⇒ **LIMITLESS**;
otherwise **LIMITED** at the capacity above. Cache per body on a map-level owner (a `MapComponent`,
name TBD), invalidated when any cell of the body changes terrain.

**"Can I drain the ocean?" — no, and the reason is throughput, not the number.** (a) An edge-touching
body is flagged limitless: the off-map continuation *is* the reservoir, so conservation of mass holds
without a finite ledger. Encode it as a sentinel flag, not a huge literal — the ruling's semantics
are "a stock large enough that it never matters", and a flag delivers exactly that without anyone
having to pick a magic number, serialize it, or render `999999999 / 1000000000` in a tooltip. (b)
Even against a truly infinite body the per-cell budget caps you at five canal cells per shoreline
cell contacted. Draining the ocean isn't blocked by a rule; it's blocked by having to dig an ocean's
worth of shoreline contact. Say that in the inspect string.

**Refill (ruling 2).** Accrue per body on the owning `MapComponent`, rare cadence, never per tick: a
flat `groundOoze * sourceCellCount` baseline always on, plus a rain term from the map's current rain
rate and a season term (read the exact weather and season accessors from the source; do not guess
them), clamped to `bodyCapacity`. Tune `groundOoze` so a very small natural source takes multiple
seasons — *less punishing* but *quite a while* means slow and certain, not random. A recovering body
regains cells at its edge, so refill is visible.

**Recession, cell by cell.** When stock falls below what the footprint represents, the body gives up
cells: fewest same-liquid neighbours first, tie-broken by greatest distance from the centroid, then
by a deterministic per-cell hash so the order survives a save. That thins the body from the outside
in and never fragments it; refill restores in reverse order. **A real problem here:** a *natural*
lake cell is not temporary terrain, so `RemoveTempTerrain` cannot dry it — receding a natural body
needs a direct write to a dry terrain (name TBD, per suite), irreversible unless the owner records
the original terrain per cell and restores it on refill. Do that recording; a receding pond must not
permanently launder the map's terrain.

**Debits** happen at pulse boundaries only: canal fill debits `volumePerTile` per cell, a burn debits
what it consumes, a pump debits via §8.

### Filling a canal back in — displacement, and the one place liquid is destroyed

**Owner, 2026-09-16:** *"There should also be a way to 'fill in' a canal that displaces liquid BACK.
It does not destroy liquid if there's a place for it to go, but if it would 'overflow' it is
destroyed."*

So the dig designator gains an inverse — **fill in** — and filling a cell that holds liquid pushes
that liquid outward rather than deleting it:

1. Compute the displaced amount: whatever the cell held.
2. Offer it to the connected liquid, nearest first — remaining channel cells below their brim, then
   the source body up to `bodyCapacity`.
3. Whatever finds room is **credited**, and the receiving cells' fill tiers rise, so displacement is
   visible: filling in one end of a canal makes the rest of it deeper.
4. Whatever does not find room **overflows and is destroyed**. This is the ONLY sanctioned place in
   the design where liquid leaves the world without being spent, burned or pumped.

🔑 **Why this matters more than it looks.** It makes conservation of mass a rule with exactly one
stated exception rather than an aspiration with silent leaks, and the exception is one the player
causes and can see. It also gives the defense loop a *reversible* move: a canal is no longer a
one-way commitment of the source's stock — fill it back in before a raid that never came and you
get most of your liquid back. That directly softens the "liquid spent is liquid gone" tension of
loop step 3, which is a balance consequence worth him knowing about.

**Consequences to build:** a fill-in designator, job and work giver mirroring the dig chain; a
`TryCredit`-shaped displacement walk (§8 already has the credit primitive); and an overflow report so
destroyed liquid is disclosed rather than silent — a message or an inspect line, since silent loss in
a conservation-of-mass system reads as a bug.

⚠️ Filling in must also restore the *original* terrain, not leave generic soil. The channel already
knows how to give the floor back on drain (`SetTempTerrain` + `QueueRemoveTerrain`); a fill-in is the
permanent version of the same idea and needs the same care about not laundering the map's terrain.

## 6. The channel-constraint problem

`Flood_FluidCanal` subclasses vanilla's Odyssey `Flood` and inherits its gating: from the seed cell
it walks any open, non-water, non-edifice ground. `RM_Channel_Empty` is deliberately walkable,
passable and not-water precisely so that engine accepts it — which also means the liquid has no
reason to *prefer* it. The design assumes a canal *contains* the liquid, so this is a correctness
problem, not polish. **UNBUILT.**

**A. Gate the spread on terrain, keep vanilla Flood.** Refuse any candidate cell whose terrain is
neither `RM_Channel_Empty` nor already carrying this liquid. *For:* smallest change; keeps Odyssey's
spread, visuals and expiry. *Against:* the candidate test lives on the base class, so whether it is
overridable must be read from the decompiled source first; if it is not, the fallback is a Harmony
patch on a vanilla flood method guarded by an instance-type check so `SeasonalFlood` is untouched.
It cannot express fill fraction, per-cell debits or recession — it buys correctness and no more.

**B. Own the walk: a channel graph on a `MapComponent`.** Drop `Flood` for canal flow; the map owner
keeps the channel cell set and each pulse performs a bounded breadth-first fill over channel cells
only, writing terrain and debiting stock itself. *For:* the only option that can express everything
the design needs — partial fill, exact conservation of mass, recession, ignition propagating along
the liquid, a fill front the player can watch. Still strictly pulsed, so pillar 2 holds. It also
drops the hard Odyssey dependency `About.xml` currently declares, which matters for a public
release. *Against:* the most code, loses Odyssey's presentation, new save-compat surface — **but far
less of that than it sounds**, because a working in-repo precedent exists for every hard part of it
(§11): `RM_MapComponent_CanyonFlood` already owns a phased flood on a `MapComponent`, holds per-cell
dictionaries across save/load, and exposes debug arm/start surfaces for testing. B is a port, not an
invention.

**C. Micro-floods along a precomputed path.** Keep `Flood` for the arrival drama, but spawn one
single-cell release per channel cell along a path computed in advance. *For:* vanilla visuals,
channel-exact. *Against:* many ethereal driver things per fill, awkward lifetimes, and it converges
on B's bookkeeping without B's control.

🔑 **Three independent investigations converged on option B** (2026-09-16, separate agents on
separate questions): the channel-constraint problem wants a channel-aware owner; irrigation wants a
per-cell soak map on a `MapComponent` (§11, already built next door); and ignition wants something
that can walk the liquid backwards toward its source (§12). All three are the same object. That
convergence, not the spread bug alone, is the argument for B.

**Recommendation: B, with A as a stopgap.** Ship A first — roughly a day, and it stops liquid
leaking across open ground, the current mod's worst live behavior — then build B as the real home,
because stock accounting, fill fraction and recession are things vanilla `Flood` structurally
cannot represent. Verify A's override point against the decompiled `Flood` before committing; do not
assume the method is virtual.

## 7. What the player must SEE

Zero bespoke textures exist. The states art is needed for — and §13 says which of these can be
**adopted** rather than drawn, which turns out to be most of them:

1. **Dry dug channel** — reads as a trench, not a gravel path; directional/edge art so a run of cells
   looks like one excavation with walls.
2. **Partially filled channel** — at least three steps (trace / half / brimming), tintable from the
   registry's per-liquid `color`.
3. **Full channel.**
4. **Burning channel** — a burning liquid surface, distinct from vanilla's fire overlay on ordinary
   ground.
5. **Spent channel** — scorched, empty, after a burn.
6. **Source: full / strained / exhausted** — three states on the source building; strained is reused
   for pump draw, per the owner.
7. **Limited vs limitless indicator** — UI, not terrain: an overlay glyph plus the inspect line.
8. **Per-liquid surfaces** — water, salt water, coloured waters, tar, propane, slime R/G/W. Slime must
   not read as tinted water: opaque and matte.
9. **A crossing cue at the channel lip** — the obstacle must be legible at a glance.
10. **Irrigated soil** — a damp, darker ring beside a filled canal. The whole irrigation motivation
    rests on this one visual.
11. **Dig canal designator icon.**
12. **Source buildings** — spring and seep here or in the data pack; the drill head is ManyWaters
    (ruling 3), the pump intake Liquid Logistics.

## 8. The interface other mods use

**Stock is owned here.** FluidCanals' map-level owner is the single writer of every body's stock and
footprint. Liquid Logistics' hardware never writes terrain and never edits stock directly; it calls
(names TBD, shapes fixed):

- `TryDebit(IntVec3 cellInBody, float fillUnits) → float actuallyTaken` — a pump calls this once per
  pulse. Less than requested is the pump's signal to stall; a limitless body always returns the full
  request. Recession, if any, is done by the owner, not the caller.
- `TryCredit(IntVec3 cellInBody, float fillUnits) → float actuallyAccepted` — pumping *in*
  (ruling 3), clamped at `bodyCapacity`, so a tank can top a pond up.
- `StockAt(IntVec3) → float?` and `IsLimitless(IntVec3) → bool` — read-only, for tooltips, gizmos and
  AI. `null` means the cell belongs to no known body.

Tank capacity is in fill-units, so `5 * fluid.volumePerTile` is one tank per the owner's equivalence
and no pump ever needs a per-liquid conversion.

**Liquid properties are declared in the core registry, never here.** `LiquidDef` carries
`viscosityClass` (Thin/Water/Thick/Heavy), `flammable`, `igniteTemp` and `color`, and its
`canalFluid` slot points at a `FluidDef` row. So **viscosity** ⇒ `FluidDef.ticksPerTile`, derived
from `viscosityClass` bands by the registry generator and still an overridable field for tuning;
FluidCanals reads `ticksPerTile` and nothing else. **Flammability** ⇒ intended to be emitted by the
generator onto the flood terrain's `Flammability` stat. ⚠️ **This rests on an UNVERIFIED premise** —
`About.xml:25-26`'s claim that "vanilla ignition already works on any flammable terrain" is a written
claim by a previous agent, never measured; RimWorld's `Fire` attaches to Things and cells, and terrain
may not be consulted at all. Settle it against the decompiled engine before any of this is built,
because if the premise is false then ignition is new mechanism and the defense spine's cheapest
mechanic is not cheap. **Long burn duration and fire travelling back to the source are new behavior
FluidCanals owns regardless** — About.xml's claim, even if true, covers only catching fire. Data packs (ManyWaters,
GelatinousSlime) add rows and hardware and must never need a C# change here.

Every mechanic added under this document ships its own Mod Settings toggle, with sliders where the
number *is* the experience — viscosity scale, ignition delay, burn duration, slime escape time,
refill rate — defaults equal to shipped behavior, all-off leaving a mod that still digs dry
channels (2026-09-12 standing rule).

## 9. Open questions for the owner

1. **Channel depth.** One terrain, or a ladder (shallow trench → deep channel) where depth sets both
   crossing cost and how much a cell holds? Depth is the cheapest lever the defense spine has, and it
   changes the designator, the art list and the stock math.
2. **Sluice gates.** A buildable gate cell that holds liquid back until opened is the natural fit for
   step 3 and would replace the "leave the last cell undug" trick. This mod, or Liquid Logistics?
3. **Does drained liquid come back?** ⚠️ Half-ruled 2026-09-16: liquid displaced by **filling a canal
   in** returns to whatever has room and only the overflow is destroyed (§5). The open half is
   different — when a canal *drains on its own* (a release receding, evaporation), does that volume
   return to the source or is it gone? Symmetry argues return; the defense loop's tension argues loss.
4. **Does a burn consume the liquid?** A propane channel that burns a long time and is still full
   afterwards is free defense. Proposed: burning debits stock continuously — and say whether it also
   empties the *source*, since fire reaching it is your design.
5. **How does fire reach the source?** Cell by cell along the surface (a fuse the player can cut), or
   instantly once any connected cell lights (a punishment)?
6. **Irrigation effect and radius.** ⚠️ Largely answered by §11 — `FloodedCanyon` already does this
   with a decaying per-cell growth multiplier plus a terrain swap to `SoilRich` on recede, both
   settings-gated. What is left for you is the *feel*: what multiplier, what radius from a filled
   cell, how many days the soak lasts after a canal empties, and whether a **partially** filled canal
   irrigates at all. Also whether canal irrigation should permanently upgrade soil the way
   `RecedeFlood()` does, which is terraforming (your 4th motivation) arriving through the side door.
7. **Does slime escape time scale?** ⚠️ Partly answered by §10: Pits already scales it (body size
   against depth tier, health, manipulation). So "flat" is not the simple option, it is the
   *divergent* one — it would give the campaign two different escape grammars. The real question is
   narrower: does a slime canal reuse Pits' curve as-is, or does slime deserve to be harder than a
   pit of the same depth?
8. **What counts as limitless?** A narrow river touches two edges; a rain-fed pond may clip one.
   Should limitless require a minimum body size as well as edge contact?
9. **Should a limitless body ever visibly recede?** "No" is simpler and consistent; "yes, locally,
   then refilling" is more alive and costs the recession code a special case.
10. **Terraforming's floor.** Can a canal permanently convert dry soil to a water terrain the player
    keeps, or does everything drain back and terraforming is only the irrigation side effect?
11. **Does a dry channel block or only slow?** The loop assumes slow. Genuinely impassable to some
    pawns is a pathing decision with raid-AI consequences, worth naming now.
12. **Where do seeps and springs live?** Ruling 3 puts the drill in ManyWaters. Are found natural
    sources this mod's content too, or ManyWaters' — leaving FluidCanals only the test source?

## 10. Established vocabulary to reuse (MEASURED 2026-09-16)

The defense spine overlaps the Pits mod almost exactly, and this repo adopts existing grammar rather
than inventing a parallel one. What Pits already established:

- **The dug-obstacle cost convention lives on a BUILDING, not a terrain**: all three Pits ThingDefs
  use `passability` Standable with `pathCost` **30** (`Pit_OpenPits.xml:39-41`,
  `Pit_DigSites.xml:35-37`, `Pit_Cell.xml:64-66`). `RM_Channel_Empty` is a *terrain* at `pathCost`
  **6** (`FluidCanal_Terrain.xml:16`). 🔑 So his line "an unfilled pit slows movement as per other
  established dug barriers" is **not true today** — a dry channel costs a fifth of what a dug pit
  costs. Matching the established feel means raising the channel's cost toward 30 or moving the
  obstacle onto a building. Naming it because it is a one-line change that makes the dry-trench step
  of the loop actually work.
- **The escape clock already exists**: `PitEscapeUtility` runs a fixed struggle interval
  (`StruggleIntervalTicks()`, 2500 ticks default, tunable through `PitsSettings.struggleIntervalHours`)
  and rolls `EscapeChance(pawn, depthTier)` — body size against depth tier, health percentage,
  manipulation — clamped to `[0.02, 0.95]`, with a failed attempt costing a small "thrashing" hediff
  severity rather than real damage. Reuse this shape wholesale; a slime canal does not need a second
  escape system.
- **"Cannot climb out at all" is already a solved case**: `CompPitFitting`'s `Water` fitting sets
  `BlocksEscape`, documented in `PitFittingType.cs:16` as "no climbing out at all", and
  `Building_PitCell.EscapeBlocked` does the same for a closed gate. Both disable the roll entirely.
  That is the exact precedent for his slime phrasing, already written and already tested.
- **Slow-terrain analogues exist to match**: `RM_Slime_Liquid` at `pathCost` 25
  (`GelatinousSlime/Defs/TerrainDefs/SlimeTerrain.xml:117-136`, whose own description says "wading it
  is like wading warm syrup") and `RM_OozeDeep` at `pathCost` 200
  (`LiquidTypes/Defs/TerrainDefs/RM_Ooze.xml:46-53`). Neither carries any escape or timing mechanic.
- **North-star ids that genuinely transfer**: `pit_occupant_below_floor` and
  `pit_occupied_distinguishable` are the same problem for a slime canal — a stuck pawn must not read
  as standing on the surface staring at the camera. `pit_reads_as_hole` and `pit_covered_invisible`
  are pit-specific and must not be copied.

**What genuinely has no precedent**, so it is new mechanism and should be costed as such: a
*slowed-but-not-captured* crossing (a slip chance), any fluid-conditional `pathCost` on the channel,
and a pawn that is **stuck in place while still spawned**. Pits only knows one state — despawned into
an `innerContainer` (`DestroyMode.Vanish`, which is why its validator asserts
`expect_pawn_despawned`). The closest sketch of in-place stuckness is
`design/Jawa/proposals/tar_pits_deep_design.md`'s hediff-based model, which was never built.

## 11. Irrigation and the MapComponent walk are already built — in FloodedCanyon

🔑 **The two things this document called hardest already exist in a sibling mod.** VERIFIED
first-hand 2026-09-16 by reading the source, not inferred from a doc — `src/RimMandrake/FloodedCanyon/Source/`:

- **`RM_MapComponent_CanyonFlood`** (`RM_MapComponent_CanyonFlood.cs:36`) is a `MapComponent` that
  owns a phased flood cycle end to end — `Phase.Dry` → chime → wall → flood → `RecedeFlood()` — with
  `activeFloodCells`, a `Dictionary<IntVec3, int> soakUntilTick`, stale-entry pruning, and full
  `ExposeData` persistence via `Scribe_Collections` with rehydration guards. It also ships debug
  surfaces (`DebugArmFloodSoon()`, `DebugStartFloodNow()`) that make the whole sequence testable in
  real time without waiting on the natural period.
  ⇒ **This is §6 option B, already working.** Owning a pulsed, map-level, save-safe, per-cell flow
  engine is a solved problem in this repo. Port it; do not design it.
- **`SoakFactorAt(IntVec3 cell, int nowTick)`** (`:66`) returns a decaying per-cell growth multiplier,
  documented "never allocates", gated on `RM_FloodedCanyonSettings.growthCouplingEnabled`.
- **`RM_Patch_Plant_GrowthRate`** (`RM_Patch_Plant_GrowthRate.cs`) is a Harmony **postfix on the
  `Plant.GrowthRate` GETTER**, multiplying on top of the result so every vanilla `GrowthRateFactor_*`
  is still respected — its own comment says exactly that, and it follows a second in-repo precedent,
  RimUtinni's `PlantGrowth/Source/Patch_Plant_GrowthRate.cs`. Guards on settings, `__result <= 0f`,
  a null `Map` (unspawned or in a caravan) and a missing comp.
  ⇒ **This is the irrigation mechanism.** Key it off canal cells instead of flood cells and
  irrigation is done. Harmony is already a baseline dependency (`brrainz.harmony`).
- **`RecedeFlood()`** (`:222`) converts receding flood terrain to `TerrainDefOf.SoilRich` rather than
  plain `Soil` — a permanent fertility upgrade as the visible legacy of water having been there.
  That is a second, Harmony-free irrigation lever, and it is also terraforming.
- Its settings shape is the pattern to copy too: `floodCycleEnabled`, `growthCouplingEnabled`,
  `growthMultiplier`, `soakDecayDays`, and `featureInOtherBiomes` — that last one being CLAUDE.md's
  standing rule that biome-kit mechanics stay usable outside their biome, already honoured.

⚠️ **What is NOT confirmed**, because it needs the engine and RimSage is unreachable from this
machine: the exact member name and interpolation of a fertility growth factor, and whether Odyssey's
`GrowthRateFactor_Drought` exists as named. Those come from repo prose written by earlier sessions,
not from a decompiler. The mechanism above does not depend on them — a postfix multiplier needs no
knowledge of the factors it multiplies — so irrigation can be built without settling either.

## 12. Fire: what is unknown, and what is unaffected by not knowing

**Still UNMEASURED after two independent attempts** (2026-09-16): whether RimWorld consults a
`TerrainDef`'s flammability when spreading fire at all. Both agents were blocked by the same thing —
RimSage has never connected from this machine and no decompiled engine tree is on disk. The
circumstantial case that terrain flammability is real: `TerrainDef` inherits `BuildableDef` and so
*can* carry a `Flammability` statBase, and wooden floors are widely observed to catch and spread fire
with no Thing present. That is suggestive and it is **not evidence**; nobody has read
`Fire`/`FireUtility` to name the method. Settle it on the Desktop before costing ignition.

🔑 **But the design decision does not wait on it**, and this is the useful finding: vanilla `Fire`
self-extinguishes once local fuel is gone. So even if terrain flammability works exactly as
`About.xml` hopes, it buys only *catching* fire. Neither of his two actual requirements —
**"burn for a very long time"** and **"they will also light their source"** — can come from vanilla
`Fire` behaviour, because both require something that knows the shape of the liquid over time. That is
the channel owner of §6 option B.

**Recommended shape:** the `MapComponent` owns ignition state, burn duration and backward propagation
along connected liquid cells, and spawns/despawns vanilla `Fire` per cell purely for visuals and
damage. Bounded per-pulse walk, same shape as the fill; pillar 2 holds. A 200-cell canal alight is
then one component doing a bounded walk, not 200 Things each ticking — which is the option to avoid.

⚠️ **A contradiction I am NOT resolving from the evidence available here** (see also §13's caveat). The fire investigation
found `dubwise.rimefeller`, `sarg.alphabiomes`, `vanillaexpanded.vchemfuele` and `realify.firefoam`
listed active in `deployed/config/ModsConfig.pre-rimdefdump-2026-08-10.xml`, while
`liquids_framework_design.md` §5 states Rimefeller is "not in the campaign list". **That snapshot is
from 2026-08-10 and is not the instrument** — the live list is `ModsConfig.xml` on the Windows
machine, unreachable from here. Both claims may be true of different moments. Check the live list
before either citing Rimefeller as prior art or repeating that it is absent; do not edit either
document on the strength of a five-week-old snapshot.

## 13. The art: partial fill is nearly free, and tar currently looks like water

Surveyed 2026-09-16. The picture is better than "zero textures" suggests, and it contains one real
defect.

🔑 **A fill-level progression already exists, and every liquid in this repo already rides it.**
Vanilla ships depth tiers — `WaterShallow` / `WaterMovingChestDeep` / `WaterDeep` (plus ocean and
polluted variants) off `WaterShallowBase` / `WaterChestDeepBase` / `WaterDeepBase` — each with its own
**edge-aware "Ramp" texture** (`WaterShallowRamp`, `WaterChestDeepRamp`, `WaterDeepRamp`). All 17 of
LiquidTypes' suites (`RM_Tar`, `RM_Ooze`, `RM_Propane`, `RM_AcidWater`, `RM_WaterBoiling`,
`RM_WaterBrine` …) clone those bases and reuse those ramps verbatim.
⇒ **`canal_partial_fill_distinct` costs almost nothing**: express fill as the tier the cell currently
holds — trace/shallow → half/chest-deep → brimming/deep — and the edge-aware art, the depth reading and
the movement cost all come for free from terrain that already exists. It also gives the stock model a
natural quantisation, since a tier is a volume.

**The repo's precedent for one substance in several states** is `GelatinousSlime`'s
`SlimeTerrain.xml`: five terrains (`RM_Slime_Hardened` → `RM_Slime_Rich` → `RM_Slime_Grass` →
`RM_Slime_Mud` → `RM_Slime_Liquid`) driven by a `terrainsByFertility` moisture band. It is a moisture
continuum rather than a depth one, but the shape — several terrains, one substance, one gradient — is
already established here and worth matching.

🔴 **RULED — owner, 2026-09-16: "Agreed that Tar needs the viscosity most of all."** Tar is the top
art priority of this mod. It is also the highest-leverage single fix, because tar is the defense
spine's signature liquid (a burning tar moat) and it is the liquid currently *least* served by tinted
water: water tinted black still ripples like water, which reads as an oil slick rather than as
something a raider wades through. Adopt Alpha Biomes' `AB_Tar` / `AB_TarPits` surfaces first, by the
same `MayRequire` pattern ManyWaters already uses for `AB_SlimeRamp`, and only author bespoke tar art
if adoption cannot carry it.

🔴 **The defect: differentiation between liquids is currently a colour multiply, not a look.** Every
in-repo liquid tints the vanilla water ramp via `<color>(R,G,B)</color>`. So **tar today is tinted
water** — it ripples like water and reads like water — which fails the spirit of
`slime_reads_as_viscous_not_water` and would fail the same test for tar. Real bespoke art for
viscous liquids **exists and is adoptable but not yet adopted**: Alpha Biomes ships
`Terrain/Surfaces/AB_SlimeRamp`, `AB_Tar` / `AB_ArtificialTar`, `AB_LiquidSlime`, `AB_PropaneLake`,
`AB_TarPits` / `AB_TarPuddle` / `AB_TarLakes`. ManyWaters already tints `AB_SlimeRamp` for its slime
rows under `MayRequire="sarg.alphabiomes"`, so the adoption pattern is written — it simply has not
been applied to tar or propane. `AB_TarPits` is also recorded as placed on the frozen world across 62
measured tiles.

**So the authoring list shrinks to four things nothing can be adopted for:**

1. **A dug channel that reads as an excavated channel** — the one genuinely new terrain look. No
   "canal bed" art exists anywhere; `RM_Channel_Empty` is `Terrain/Surfaces/Gravel`.
2. **A strained / depleted source** — no depletion-indicating graphic exists in ANY mod in this repo.
   This is the visual expression of his whole stock ruling and it has no precedent to lean on.
3. **A burning liquid surface** distinct from vanilla's fire overlay on ordinary ground.
4. **Irrigated ground** — a damp ring beside a filled canal. (Partly free: `RecedeFlood()`'s
   `SoilRich` swap already reads as darker, richer soil.)

⚠️ **Caveat on this whole survey, stated because it would otherwise look like measurement.** The
frozen def dump's `DUMP_ROOT` is a Windows path and the live `ModsConfig.xml` is on the Windows
machine, so neither could be read from the Laptop this session. The in-repo XML claims above are
first-hand reads. The **vanilla depth-tier claim and Alpha Biomes' active status are corroborated by
several independently-dated repo artifacts** (frozen-dump comments citing `Terrain_Water.xml` with
line numbers, real BiomeDef tile assignments, working patches against those defNames) — which is
strong, and is still not a fresh `measure`. Re-verify both on the Desktop before art work starts.
