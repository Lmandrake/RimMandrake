# FlowWorks — mod definition

Status: agent-drafted 2026-09-16 from the owner's bench session, then ruled heavily the same day —
**27 numbered rulings** are recorded below and are his; unnumbered prose is still agent draft.

**The mod is named `FlowWorks`** (ruling 20): `RimMandrake: FlowWorks`, packageId
`mandrake.rm.flowworks`, namespace `RimMandrake.FlowWorks`, prefix `RM_`.

✅ **RENAMED ON DISK 2026-09-16, `FLOWWORKS_BUILD_PROGRAM_1` Phase 1.** The mod folder is
`src/RimMandrake/FlowWorks/`, the packageId `mandrake.rm.flowworks`, the namespace
`RimMandrake.FlowWorks`, and `RimMandrakeFlowWorks.dll` was rebuilt in the same pass so no XML
class field outlives the assembly it names. Phase 1 also **merged Pits, ManyWaters and LiquidTypes
into this one mod** (sub-namespaces `RimMandrake.FlowWorks.{Pits,ManyWaters,LiquidTypes}`, one
assembly) and executed ruling 24's deletions. GelatinousSlime, WreckedMachines and FloodedCanyon
stay siblings.

Position in the family: FlowWorks is the **liquid engine itself** — depth is its primitive (ruling 18),
and excavation plus the built half (canals, terraces, ladders, sluice gates, **pumps, tanks**) is now
roughly half the design (rulings 19-20). Liquid *types* remain rows in the core registry (`LiquidDef`),
per `design/RimMandrake/liquids_framework_design.md` §5.

⚠️ **Deleted claim:** this header previously said pumps, tanks and hoses "belong to `RimMandrake:
Liquid Logistics` and are **not** this mod's to build." Ruling 20 contradicts that in this same
document by naming pumps and tanks as FlowWorks' own, and `LIQUID_LOGISTICS_MOD_1` was superseded
2026-09-16 — that mod will never ship. The ruling wins.

Framework pillar 2 — *pulsed spread only, no per-tick fluid sim, ever* — is an owner ruling, and
everything below stays inside it.

**The pit's visual/art spec is a separate document, not absent:**
`design/RimMandrake/pit_trap_visual_interface_spec.md` — five states, the top-down depth grammar,
a Pyrelands palette, and three costed directions with Direction B recommended, awaiting the owner's
ruling. Ruling 27 sequences it after the merge; its own Status section records what rulings 18/19/25/27
falsified in it. Read the two together before drawing anything.

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
| **Spread confined to the channel** | **UNBUILT — the biggest gap** | `Flood_FlowWorks` inherits vanilla's gating and spreads across any open, non-water, non-edifice ground. It does **not** follow the dug channel. §6 |
| Source stock / volume | **UNBUILT** | No stock of any kind exists. §5 |
| Limited vs limitless detection | **UNBUILT** | Nothing inspects a body's extent or its map-edge contact |
| Strained-source graphic | **UNBUILT** | And no art to draw it with |
| Partial fill / fill progression | **UNBUILT** | Exactly one filled state: vanilla's `ShallowFloodwater` |
| Parent body recedes in proportion | **UNBUILT** | Nothing writes back to the source body's cells |
| Filled vs unfilled movement cost | **UNBUILT** | `RM_Channel_Empty` declares `pathCost` 6; no code varies cost with fill state |
| Ignition, long burn, fire reaching the source | **UNBUILT** | ⚠️ UNVERIFIED premise: `About.xml:25-26` claims "vanilla ignition already works on any flammable terrain, so a fluid with flammability > 0 needs [nothing extra]". That is a previous agent's written claim, not a measured fact, and fire in RimWorld attaches to Things and cells — whether TerrainDef flammability is consulted at all is being checked against the decompiled engine. If the premise is false, ignition itself is new mechanism too. "Burns for a very long time" and "lights its source" are unbuilt either way |
| Slime near-uncrossable, slow to escape | **UNBUILT** | The mechanics live in GelatinousSlime (framework §5); the canal only has to be a legal place for slime to sit |
| Irrigation — plants near a filled canal act watered | **UNBUILT here, but SOLVED next door** | No effect of any kind in FlowWorks — but `FloodedCanyon` already ships the whole mechanism and it is copyable nearly verbatim. §11 |
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

`Flood_FlowWorks` subclasses vanilla's Odyssey `Flood` and inherits its gating: from the seed cell
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

**Stock is owned here.** FlowWorks' map-level owner is the single writer of every body's stock and
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
FlowWorks reads `ticksPerTile` and nothing else. **Flammability** ⇒ intended to be emitted by the
generator onto the flood terrain's `Flammability` stat. ⚠️ **This rests on an UNVERIFIED premise** —
`About.xml:25-26`'s claim that "vanilla ignition already works on any flammable terrain" is a written
claim by a previous agent, never measured; RimWorld's `Fire` attaches to Things and cells, and terrain
may not be consulted at all. Settle it against the decompiled engine before any of this is built,
because if the premise is false then ignition is new mechanism and the defense spine's cheapest
mechanic is not cheap. **Long burn duration and fire travelling back to the source are new behavior
FlowWorks owns regardless** — About.xml's claim, even if true, covers only catching fire. Data packs (ManyWaters,
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
    sources this mod's content too, or ManyWaters' — leaving FlowWorks only the test source?

## 10. Established vocabulary to reuse (MEASURED 2026-09-16)

The defense spine overlaps the Pits mod almost exactly, and this repo adopts existing grammar rather
than inventing a parallel one. What Pits already established:

- **The dug-obstacle cost convention lives on a BUILDING, not a terrain**: all three Pits ThingDefs
  use `passability` Standable with `pathCost` **30** (`Pit_OpenPits.xml:39-41`,
  `Pit_DigSites.xml:35-37`, `Pit_Cell.xml:64-66`). `RM_Channel_Empty` is a *terrain* at `pathCost`
  **6** (`FlowWorks_Terrain.xml:16`). 🔑 So his line "an unfilled pit slows movement as per other
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

## 14. Rulings — owner, 2026-09-16, second sitting

**5. Fill is THREE TIERS, reusing vanilla's depth terrains.** Trace/shallow → half/chest-deep →
brimming/deep. The edge-aware ramp art, the wade-depth reading and the movement cost all come from
terrain that already ships (§13), and a tier *is* a volume, so the stock model quantises for free.
Supersedes §13's framing of this as an open question, and answers open question 1.

**6. A canal draining on its own RETURNS its volume to the source.** Symmetry with fill-in
displacement. Conservation of mass is therefore near-total, with **exactly one exception in the whole
design**: overflow when displaced liquid has nowhere to go (§5). Answers the open half of question 3.
⚠️ Consequence he accepted: this removes most of the cost of a mistake, so "bank the source until a
raid is inbound" is a weaker decision than it was under a lossy model. If the defense loop later feels
slack, this is the line to revisit first — not the budget.

**7. Burning consumes the liquid, but VERY slowly — with numbers.** His words:

> *"Yes, but VERY slowly. Going down 1 'fullness' level of the canal should take a day, and thus for
> sources going down 1 level should take 5 days (5:1 density argument again). Thus, for a small burning
> moat, you may be able to pump/pipe liquid into it from a larger (non-burning) source to keep it
> indefinitely filling, because the source is replenishing. A natural source connected off-screen can
> effectively burn forever (a very very long time, as we ruled before... some large number)."*

So burn is a **rate on the tier ladder of ruling 5**, not a timer:

- one canal cell loses **one fill tier per day** while alight ⇒ a brimming cell burns ~3 days;
- a source loses one level per **5 days**, the same 5:1 density relation as the supply budget;
- therefore a **small moat fed by a larger source burns indefinitely**, because inflow outpaces burn —
  that is a designed outcome, not a leak, and it makes piping liquid to a burning moat a real tactic;
- a **limitless source burns effectively forever.**

🔑 This is the first mechanic whose numbers come from the tier ladder, which means ruling 5 is now
load-bearing for ruling 7 — a change to the tier count changes burn duration. Say so in the settings
screen rather than letting a slider move two things silently.

⚠️ One open implementation point: he said a limitless source is *"some large number"*, while §5
recommends a sentinel flag instead. Both give identical play; the flag avoids serialising and
rendering a magic number. Treated as an implementation detail unless he wants the literal.

## 15. Rulings — owner, 2026-09-16, third sitting: this mod is the engine

**8. One engine, in FlowWorks; FloodedCanyon becomes a driver.** The occupancy engine — cells,
fill tiers, hold, recede, soak, conservation bookkeeping — lives here and exposes a driver interface
with a **per-driver recede policy**: `restore-original` for canals, `convert-to` for canyon floods
("death, then soil"). FloodedCanyon keeps its biome, its phase clock and its own settings, and
depends on this mod for motion.

This needs no reversal: framework pillar 2 already reads *"all map motion is event-shaped (flood,
drip, spill, **seasonal**) via the FlowWorks engine"* — seasonal being the canyon case exactly — and
FloodedCanyon is absent from the §5 client map entirely. It grew outside the plan and duplicated the
engine the plan had already named. Add it to that client map as **flood driver client**.

Immediate consequence already filed as `CANYON_FLOOD_ERASES_CANALS_1`: today a canyon flood's
permanent `SetTerrain` destroys a dug canal and returns it as `SoilRich`. Two owners for one cell is
the bug the single engine removes.

**9. Sinks.** His words: *"I suppose we should add Sinks too at the edge of the map that simply
provide drainage from empty canals."* A sink is a map-edge drain: liquid entering it leaves the map.

🔑 **A sink is the exact inverse of a limitless source, and that symmetry keeps conservation honest.**
Under ruling 4 the off-map continuation of an edge-touching body *is* the reservoir, so liquid leaving
through a sink is neither destroyed nor created — it is **transferred off-map**. That means a sink is
NOT a second exception to conservation; overflow (§5) remains the only one. Worth stating plainly,
because "a drain that deletes liquid" and "a drain that returns liquid to the world" look identical on
screen and are very different rules.

What a sink is for: emptying a canal **on purpose and now**, rather than waiting for ruling 6's
passive return. So the player has three ways to clear a channel, with different costs — fill it in
(liquid displaces back, terrain is restored, labor), wait (returns to source, slow, free), or drain to
a sink (fast, liquid leaves the map, needs a sink built at an edge).

**10. This mod needs a new name.** He ruled it, this date: *"clearly the Canals mod needs a better
name now that it's a full liquid engine."* "FlowWorks" now names one driver of a mod that owns
sources, sinks, occupancy, fill tiers, surface flooding and canals.

✅ **Done — `FLOWWORKS_BUILD_PROGRAM_1` Phase 1 executed the rename 2026-09-16.** The former
instruction here ("do not rename anything yet", citing `NAMING_SCHEME_EXECUTION_1`) was wrong: that item
closed 2026-08-31 at `54a8e28d`. Still owed at the next deploy: flipping `mandrake.rm.fluidcanals` to
`mandrake.rm.flowworks` in the live `ModsConfig.xml`, and clearing the old mod folders out of the
game's Mods directory.

**Recommended: `RimMandrake: Liquid Flow`** — packageId `mandrake.rm.liquidflow`, namespace
`RimMandrake.LiquidFlow`, prefix stays `RM_`. It names the thing the mod actually owns (motion), is
liquid-agnostic, and is what a Workshop user would search for.

Rejected, with reasons, so they are not re-proposed:

- **Hydrology / Watercourse / Aquifer** — all say *water*, and the roster's most important liquids are
  tar, propane and slime. The mod would be misnamed on its own headline content.
- **Fluid Dynamics** — implies simulation. Pillar 2 forbids a per-tick sim outright, so this name
  promises the one thing the design rules out.
- **Liquid Engine** — accurate and inert; "engine" is developer language on a store page.

## 16. Rulings — owner, 2026-09-16, fourth sitting: it is ONE mod, called Fluidity

**11. Fluidity.** *"I do want to absorb Many Waters and Canals together into a single Fluidity mod.
All of it. Universal containers, flexible tubing, pumps, surface transient flow, canals, sources &
sinks."* One shipped mod owns the whole liquid domain: the occupancy engine, the liquid roster, the
hardware, and every driver.

He answered the release-cadence objection directly — *"I understand your argument about constant
updates. I don't think that's actually going to happen. We're going to include a big set of options.
Others can extend later via our framework."* So the roster is authored broadly ONCE rather than
accreting, and third parties extend through the registry instead of us shipping rows forever.

⚠️ **This supersedes `liquids_framework_design.md` §5's client map** and, with it, `RimMandrake:
Liquid Logistics` as a separate planned mod — its hoses, portable pumps, universal cargo tank,
universal pump and per-net adapters are Fluidity's. §8's "interface other mods debit against" becomes
an *internal* boundary rather than a cross-mod contract; keep the boundary anyway, because it is what
stops the hardware reaching into the stock bookkeeping directly.

🔑 **The one objection he did NOT overrule, restated honestly because it is now his to manage.**
Many Waters' slime rows tint **Alpha Biomes'** `AB_SlimeRamp` under `MayRequire="sarg.alphabiomes"`
and its bottle art tints **Dubs Bad Hygiene's** texture. Absorbed, those become Fluidity's own soft
dependencies. This is *manageable and not fatal* — `MayRequire` degrades gracefully by design, which
is why my original framing of it as disqualifying was too strong — **but it needs a deliberate
fallback per row**, or slime and tar simply vanish for a player without Alpha Biomes. Ship each
third-party-tinted row with a tinted-vanilla-ramp fallback so no liquid disappears; only its *look*
degrades.

**12. Sluice gates: YES.** A buildable gate cell that holds liquid back until opened. This retires
the "leave the last cell undug" trick of loop step 3 and gives the defense spine a real trigger — dig
the canal at leisure, gate it, open the gate when the raid commits. Now unambiguously this mod's,
since there is only one mod.

**13. Ignition is per-liquid: a creeping fuse OR a detonation.** *"YES on slowly moving ignition (or
simple detonation for some things like astrofuel or chemfuel)."* So the registry row carries the
ignition behaviour: tar and propane burn as a **travelling front** the player can watch and cut,
while **astrofuel and chemfuel detonate**. This answers open question 5, and it answers it better than
either single option — a fuse and a bomb are different fantasies, and the liquid decides which.

Consequence: burn rate (ruling 7, one tier per day) applies to the *fuse* liquids. A detonating liquid
does not burn down a tier a day — it is consumed at once, which needs its own stated cost and cannot
inherit ruling 7's numbers.

## 17. Rulings — owner, 2026-09-16, fifth sitting: the boundary, and three mechanics

**14. Fluidity absorbs the registry — and the boundary is a PRINCIPLE, not a list.** *"(1) all the
way… GelatinousSlime registers into it to make its special version of geneslime. Distillation is
separate: converting one liquid type into another lays outside Fluidity and is a technology and
machine ability, not a liquid property/behavior."*

🔑 **The durable rule, worth more than the mod list it settles:**

> **Fluidity owns what a liquid IS and what it DOES. A machine that TRANSFORMS one liquid into another
> is technology, and lives elsewhere.**

That decides every future case without another ruling — desalination, detox, tar-cracking, boiling,
filtering are all *conversion*, so they stay in `WreckedMachines`' found-industry grammar no matter how
liquid-flavoured they look. Viscosity, flammability, ignition behaviour, colour, depth, wetting and
crossing are *properties and behaviour*, so they are Fluidity's.

So the final shape:

| | |
|---|---|
| **Fluidity** | the registry (`LiquidDef`, generator, `RM_LiquidProperties`), the occupancy engine, canals, sources, sinks, sluice gates, surface transient flow, the roster (absorbing Many Waters), and the hardware (containers, tubing, pumps, adapters) |
| **GelatinousSlime** | stays a sibling that **registers into** Fluidity — its slime is a row; its genes and hediffs ("geneslime") remain its own, because a gene is not a liquid property |
| **WreckedMachines** | distillation and every other conversion, on the principle above |
| **FloodedCanyon** | flood-driver client (ruling 8) |

⚠️ Absorbing the registry makes Fluidity a **hard dependency** for anything liquid-adjacent, and
`LiquidTypes` already ships 17 terrain suites whose defNames other mods patch. That migration is real
work and rides `FLOWWORKS_BUILD_PROGRAM_1` Phase 1 alongside the rename — *not*
`NAMING_SCHEME_EXECUTION_1`, which closed 2026-08-31.

**15. Detonation propagates fast, then the whole run goes.** One mechanism — a travelling front — with
speed as the only difference between a tar fuse and a chemfuel detonation, so a player can *just*
outrun it. ⚠️ The performance case I flagged is now owed as a proof, not a note: "nearly at once"
across a 200-cell run means a great many simultaneous explosions, and that must be measured before it
ships. Bound it centrally (the engine drives the blasts) rather than spawning a Thing per cell.

**16. Limitless = edge contact AND a minimum body size, and it is STICKY.** *"a large body shouldn't be
able to 'flap between' because it can't be reduced, it's limitless once and for all."* Classified once,
never re-evaluated — which removes the hysteresis problem the size floor would otherwise create, with
no tuning and no flicker in the strained graphic.

**17. A dry channel slows heavily — `pathCost` 30, matching Pits.** Makes his own line about "other
established dug barriers" true for the first time; today's flat 6 is a fifth of a dug pit. Raiders
still path through and pay, so a dry trench shapes an approach rather than denying it.

## 18. Filling in natural water — advice he asked for (2026-09-16)

His observation: the rules now let a player fill in naturally occurring shallow water, and *"that
doesn't bug me at all… I had assumed it morphs into whatever terrain is most abundantly beside it.
Your advice is welcome here."*

**His instinct is right, and it needs two guards plus one addition.**

1. 🔴 **Ignore water when computing "most abundant neighbour."** A shoreline cell's most abundant
   neighbour is usually *more water*, so the naive rule fills water in with water and does nothing.
   Take the most abundant **non-liquid** neighbour, and fall back to the map's dominant natural
   terrain when a cell has none.
2. **Land it in two stages: `Mud`, drying to soil.** A cell filled in becomes vanilla `Mud`, which
   after some days becomes the neighbour-derived terrain. Costs no new art, and it reads correctly —
   reclaimed lakebed *should* look raw for a while. It also gives the player a visible "this was water"
   period rather than an instant swap, which is the difference between terraforming that feels earned
   and terrain that pops.
3. **Make the dried result FERTILE — `SoilRich`, not `Soil`.** Reclaimed lakebed is the best farmland
   there is, and this is already the repo's own idiom: `FloodedCanyon.RecedeFlood()` converts flood
   cells to `SoilRich` under the comment *"death, then soil"*. Following it makes filling in shallow
   water a genuine **farming** strategy on a desert world, which serves irrigation — his second-ranked
   motivation — without a single new mechanic.

**Two consequences worth stating, both benign:**

- **Filling in should cost something**, or draining the map becomes free labour with a fertility
  reward. The natural cost is the fill material itself: a fill-in consumes rubble, sand or soil the
  colonists haul. That also explains where the terrain came from, which the "abundant neighbour" rule
  otherwise leaves unexplained.
- **Sticky-limitless cannot be exploited by filling in**, and this resolves itself: supply requires a
  canal to *contact a cell of the body*, so a body filled in has no cells left to contact. The
  classification may outlive the water, but a zero-cell limitless source supplies nothing. No extra
  rule needed — worth writing down precisely because it looks like a hole and is not.

## 19. Canals and Pits — they compose, they do not merge

He raised it 2026-09-16: *"It's worth thinking about how canals interact with Pits too."* The answer
falls out of ruling 14's principle, and it removes work rather than adding it.

**Pits already contains a liquid feature.** `CompPitFitting` ships a **`Water` fitting** whose
documented behaviour (`PitFittingType.cs:16`) is *"no climbing out at all"* — it sets `BlocksEscape`
and disables the escape roll entirely. So a water-filled pit exists today, implemented as an enum
inside Pits with no liquid behind it.

🔑 **The recommended division, following ruling 14 exactly:**

> **Pits owns holes that hold pawns. Fluidity owns liquids and what they do. A trapping slime moat is
> a line of PITS with slime in them — Fluidity never captures anybody.**

Three consequences, each of which deletes planned work:

1. **Fluidity does not need a capture mechanic at all.** §10 recorded that a pawn *stuck in place while
   still spawned* has no precedent in this repo and would be new mechanism. Under this division it is
   never needed: capture is Pits' despawn-into-`innerContainer`, which is built, tested and asserted by
   its own validator (`expect_pawn_despawned`). The slime line of §10's "needs its own mechanism" list
   is struck.
2. **Fluidity does not need its own escape clock.** `PitEscapeUtility` already has the shape his slime
   prose asks for — a struggle interval, a chance from body size against depth tier, health and
   manipulation, and a hard `BlocksEscape` override. Slime supplies the *property*; the pit runs the
   clock.
3. **Pit liquid fittings become Fluidity rows.** The `Water` fitting stops being an enum value and
   becomes "this pit contains liquid X", with `BlocksEscape` derived from that liquid's viscosity
   rather than hardcoded. Then tar, slime and water pits all exist for free, and a *drained* pit
   becomes an ordinary pit again.

**Dependency direction: Pits depends on Fluidity. One way, no cycle.** Fluidity must not depend on
Pits, or the two are mutually required and neither ships alone.

**Pits become the deep cells of the network.** A pit adjacent to a channel is a channel cell with a
much larger volume — which fits ruling 5's tier ladder directly, a pit simply having more tiers than a
trench. That is also exactly what `design/Jawa/proposals/tar_pits_deep_design.md` already imagined
(`CompTarReservoir`, tar moats as passive base defense), so this connects a design that has been
sitting unbuilt to an engine that is about to exist.

**Interaction hazards to settle before building either side:**

- **Digging a canal onto a pit's cell.** `Designator_DigCanal` refuses edifices, but Pits' buildings are
  `passability` Standable and so may not read as edifices — meaning the dig may be *allowed* today and
  produce a cell that is both. Needs an explicit refusal, or an explicit conversion.
- **A canyon flood over a pit** is the same defect already filed as `CANYON_FLOOD_ERASES_CANALS_1`:
  permanent `SetTerrain` over a pit's cell. Fix both with one engine.
- **A covered pit full of liquid** is a visual contradiction — the cover claims the cell is invisible
  while the liquid claims it is a pool. Whichever wins, the other must not be drawn. This is a
  must-show-line problem, not a mechanics problem.
- **Fire reaching an occupied pit.** A burning tar canal that runs into a pit holding a pawn is
  excellent and grim, but the burn model must know the pit has an occupant to damage. Name it now or it
  will be discovered as "fire does nothing to a trapped pawn".
- **Filling in a canal that contains a pit** — does the pit survive, or is it filled too? A rule is
  needed, because both readings are defensible.

## 20. Ruling 18 — Pits IS Canals: depth is the primitive (owner, 2026-09-16)

He overruled §19's composition model, with a better argument than the one it replaced:

> *"I think Pit is indeed precisely the same thing as Canals and it's all one thing. It's effectively
> the only 'z level' we bring into the terrain, and that's fundamental to how fluid flows... so yes it's
> the same thing. Yes people get stuck in pits. Yes they can be used to trap people, dump liquid on
> them, etc. It's all one thing."*

🔑 **Why this is right and §19 was wrong.** RimWorld has no elevation. Both mods invent *below floor
level* independently, and liquid behaviour is **defined** by depth — liquid seeks the low cell, fills to
a level, and how deep it is decides whether you wade, drown or cannot climb out. §19 argued ownership
hygiene; that was the weaker frame, because splitting depth across two mods means **two mods both own
"how deep is this cell"** — the exact two-owners-one-cell defect §15 objects to in FloodedCanyon. So
Pits is absorbed into Fluidity, and `pathCost` 30 (ruling 17) stops being "matching Pits" and becomes
one mod's single answer.

**The unified primitive.** Every excavated cell carries two small integers:

- **`depth` (D)** — how far below floor level, 0 = surface. Set by digging, and by nothing else.
- **`fill` (F)** — how much liquid is in it, `0 ≤ F ≤ D`. Set by the engine.

Everything the family does is then a function of D and F on one cell:

| reads | from |
|---|---|
| crossing cost, and whether a pawn falls in at all | **D** (dry) |
| escape chance, once held | **D** — Pits' own `EscapeChance(pawn, depthTier)` already takes exactly this |
| how much liquid a cell can hold | **D** — a pit is simply a cell with more tiers than a trench |
| which liquid surface is drawn, and the wade cost | **F** — ruling 5's tier ladder |
| whether the occupant can climb out at all | **F × the liquid's viscosity** — replacing `CompPitFitting`'s hardcoded `Water` enum |

🔑 **This collapses three separately-invented ladders into one**: Fluidity's fill tiers (ruling 5),
Pits' `depthTier`, and vanilla's shallow/chest-deep/deep water terrains. One depth scale drives escape,
capacity, crossing and which terrain is drawn. That is the single largest simplification of this whole
design, and it only became visible once the two mods were seen as one thing.

**Canal and pit stop being types and become shapes**: a canal is a connected run of shallow
excavations; a pit is one deep excavation; a dig site is an excavation in progress; a prisoner pit cell
is a deep excavation with a gate. Capture is not a mod boundary, it is a **threshold on D** — a shallow
trench taxes a crossing, a deep one takes the pawn — so it is a continuum rather than two mods'
behaviours meeting awkwardly.

**A mechanic he named in passing and should not be lost:** *"they can be used to trap people, dump
liquid on them."* Liquid poured into an **occupied** excavation acts on the occupant — water drowns,
acid burns, tar plus fire is the grimmest thing in the mod. That is a new interaction, not a
restatement, and it is the strongest single expression of the defense spine.

⚠️ **Two operational cautions, neither an objection.**

1. **The validation unit grows.** modcheck's unit is one whole mod and the north star is per mod
   (owner, 2026-09-15). Pits' checklist is 11 must-show lines and Fluidity's is 13; merged, one
   checklist covers excavation, liquids, hardware, rows, capture and fire. His accepted mitigation —
   grouping every line under its mechanic — still holds, but validating Fluidity will be a longer
   sitting than either mod alone, and it will sit at **REFUSED** for a long time because most lines
   will have no component claiming them. That is the system working, and it should be expected rather
   than discovered.
2. 🔴 **Do not let the merge stall the pit's visual redesign.** `PIT_TRAP_VISUAL_REDESIGN_1` and
   `NORTH_STAR_PIT_PILOT_1` are the **falsification test for the entire north-star system** —
   §9 of `north_star_validation_spec.md` says the design fails if it does not turn the pit red. A
   consolidation that parks the pit fix would remove the one proof that the validation machinery works.
   Fix the pit, then merge it; the merge is a refactor and the pit is evidence.

## 21. Ruling 19 + the scope discipline — four depths, and how to get terraces without a Z-system

**Ruling 19 (owner, 2026-09-16).** Four depths: **shallow, mid, deep, SUPERDEEP** — all read as "how
far below the surface are they?". The player may terrace terrain and fill the terraces with liquids at
varying depths. Terraces can act as pits for capture. **SUPERDEEP is the trapping level.** **Natural
sources are treated as SUPERDEEP.** **Ladders** can be built to climb up and down walls.

He then asked to be challenged: *"How can we capture a lot of great ideas here and gameplay without
inventing a whole z surface and physical fluid flow?"* This section is that answer.

### LAW 1 — We dig down. We never build up.

Depth is a property of **excavated cells only**. The surface is 0 and always will be. There are no
hills, no mounds, no raised earth, no ramps up.

🔑 This one asymmetry kills most of the cost of a Z-system, and the reason is worth stating: a real
elevation model makes height a property of **every** cell, which forces every subsystem to interpret it
— pathing, rendering, line of sight, cover, roofing, projectile arcs. Because nothing is ever *above*
0, none of that is touched: a dug cell is just a cell carrying an integer, and RimWorld already lets a
cell carry a cost and a building.

**Guard this law explicitly**, because every future request will erode it. "Can we have a raised
berm?" is a Z-system in disguise. The answer is a wall, or nothing.

### LAW 2 — Depth affects MOVEMENT and LIQUID. It never affects sight or shooting.

The moment depth grants a height advantage, cover bonus, or line-of-sight change, we own a full
elevation model inside the combat system — and combat is the most interconnected code in the game.

**Cut and stay cut:** height advantage, shooting down into a pit for a bonus, cover from below,
falling damage between levels, thrown objects across levels, multi-level buildings, roofs at
different heights, and pressure/siphons/head-height flow. Every one is defensible in isolation and
each one alone converts this into a different project.

### THE ALGORITHM — fill lowest first, then overflow. That is the whole "physics".

At each pulse (never per tick — pillar 2), over the connected set of excavated cells:

1. Sort by depth, deepest first.
2. Pour available volume into the deepest cells until each reaches `F = D`.
3. **A cell at `F = D` overflows into adjacent cells that have room**, and the sort repeats.

It is a sort plus an overflow. No pressure, no velocity, no simulation — and it produces every
behaviour he asked for:

- **Terraces fill bottom-up.** The deep terrace fills before the shallow one, exactly as water does.
- **A breach into a deeper cell drains the shallower one** — liquid seeks the low point for free.
- **A spillway works.** A deliberately shallow cell between two deep ones becomes an overflow route.
  Nobody codes it; players discover it and feel clever.
- **Draining is a tactic.** Breach into a SUPERDEEP sink and the moat empties in one pulse.

🔴 **The flaw this rule fixes, which the ruling as stated would otherwise have.** If natural sources
are SUPERDEEP and flow is only "fill lowest first", liquid would **never leave a source** to fill a
shallower canal — water does not run uphill, and the entire canal fantasy dies. The **overflow** step
is what saves it: a natural source is a SUPERDEEP cell that is *already full*, so it spills into any
shallower channel dug at its edge. Correct physics, produced by an integer comparison.

### The consequence worth taking: a SOURCE stops being a building

If a source is "a SUPERDEEP cell, full, replenished," then `CompFluidReservoir` and
`RM_FluidSpring_Test` can disappear as concepts. A lake is not a building with a comp — it is deep
full terrain. Limitless (ruling 16) is then "fed from off-map"; limited is "fed by rain, season and
seepage" (ruling 2). Recommended, and flagged as an agent proposal rather than his ruling, because it
deletes two shipped concepts.

### Ladders — the whole vertical-movement system is one boolean

A ladder is a **building on a dug cell that makes the cell exitable**. No vertical pathing, no
climbing animation, no multi-level anything:

| cell | pawn entering |
|---|---|
| shallow / mid | crosses, pays the cost |
| deep | crosses slowly; may need a ladder to leave if flooded |
| SUPERDEEP, no ladder | **falls in and is held** (Pits' machinery, ruling 18) |
| SUPERDEEP, with ladder | walks in and out freely |

🔑 And the ladder is instantly a tactical object made of one flag: **remove the ladder and whatever is
down there is stranded.** That is a jailer mechanic for free — and it is what Pits' prisoner-cell gate
already is, so the two unify.

### Three pieces of exceptional content this buys, at no extra mechanical cost

1. **Terrace farming.** Shallow terraces that hold water, on a desert world, with the reclaim rule
   already making lakebed `SoilRich` (§18). Rice-paddy terracing becomes a player-authored form that
   looks spectacular and needed no new mechanic. It also gives irrigation — his second-ranked
   motivation — something to *build* rather than merely benefit from.
2. **The flood pipeline as a weapon.** Dig SUPERDEEP, let a raider fall in, *then* flood it. Depth
   turns his "dump liquid on them" into a sequence with a decision at each step, and it is the
   strongest expression of the defense spine in the design.
3. **Reading depth for free.** A filled cell shows its depth through vanilla's own shallow /
   chest-deep / deep ramp art (§13). A dry cell needs one inner-shadow edge treatment. Four depths ×
   dry/wet is a small finite art set — where a continuous Z would need arbitrary height rendering.

## 22. Rulings 20-22 (owner, 2026-09-16): FlowWorks, farming, and the one shooting exception

**20. The name is `FlowWorks`.** His proposal, and it beats my `Liquid Flow` suggestion — recorded as
the choice, superseding §15's recommendation. Why it is better: **"Works" carries the *built* half of
the mod** — canals, terraces, ladders, sluice gates, pumps, tanks — which "Flow" alone misses entirely,
and which is now half the design after ruling 19 made excavation the primitive. It reads as flow +
earthworks, it is liquid-agnostic (no "water" trap), it is short and memorable on a store page, and it
promises no simulation.

Per the naming scheme: `RimMandrake: FlowWorks`, packageId `mandrake.rm.flowworks`, namespace
`RimMandrake.FlowWorks`, prefix stays `RM_`. ✅ Renamed on disk 2026-09-16 by
**`FLOWWORKS_BUILD_PROGRAM_1` Phase 1**.
**One check owed before publishing:** confirm no Workshop mod already uses the name
(cannot be searched from the Laptop — WebSearch is dead on this model group; use Fetcher or the
Desktop).

⇒ **Checked 2026-09-16, FOUNDRY bookkeeping pass on `FLOWWORKS_BUILD_PROGRAM_1`:** WebSearch
was NOT dead on this session's model — four distinct queries (plain, steamcommunity-scoped,
fandom/moddb/mod.io-scoped) plus a direct `curl` of the Workshop browse page and an attempted
headless-Chromium render (blocked by a missing `libasound.so.2`, not fixable without `sudo`
here) all returned real, differentiated results and **none named a RimWorld mod "FlowWorks."**
Verdict: **no collision found**, moderate confidence — the one route that would be conclusive
(a live, JS-executed Workshop search; the new Steam Community UI serves an unfiltered
~13,089-item total to a non-JS fetch, not search-filtered results) was not reachable from this
machine. Re-run with a working browser or on the Desktop before publishing; this does not
close the check.
**21. Terrace farming: YES, generally, and feature-gated.** *"YES if we can have this map into farming
easily (don't need that for this scenario, but in general absolutely)."* So irrigation-by-terrace is
built to work everywhere, on its own toggle, and the Jawa campaign is not required to use it — exactly
CLAUDE.md's standing rule that biome-kit mechanics stay usable outside their biome. The mechanism is
already free: §11's soak-factor pattern plus §18's `SoilRich` reclaim.

**22. Dumping liquid on a trapped raider should be VERY effective.** Not a nuisance debuff. A pawn held
in a SUPERDEEP cell that is then flooded is in serious trouble, and with a flammable liquid, finished.

**23. The single shooting exception — and it is the cheap half of Law 2.**

> *"someone in a pit should really only be able to shoot at others at the edges above them, and those
> outside should only be able to shoot into the pit from the edge as well. But that's the only
> mechanic."*

🔑 **Why this does not breach Law 2.** He asked for a **restriction**, never a bonus — no height
advantage, no cover modifier, no accuracy change. That distinction is the whole cost difference: a
restriction is one boolean gate on an existing check, while a bonus reaches into hit chance, cover
math, AI target selection and player expectation. He picked the side that does not own an elevation
model.

**Cheapest honest implementation, and the constraints it must respect:**

- **One patch point.** A Harmony prefix on `Verb.CanHitTargetFrom` (verify the exact member on the
  Desktop — engine internals are UNMEASURABLE on the Laptop) returning false for a disallowed pair.
- **Applies at SUPERDEEP only.** Shallow, mid and deep are unaffected, so a pawn wading a terrace is
  not blinded. This also matches "SUPERDEEP is the trapping pit level" — the rule exists for the
  trapping case and should not leak into the others.
- 🔴 **"At the edge" must mean 8-way adjacency to the pawn's OWN cell**, not adjacency to the whole
  excavated region. Region adjacency needs a flood fill, and `CanHitTargetFrom` is called constantly —
  the check has to be O(1): two depth-grid lookups and an adjacency test. A per-shot flood fill would
  be a framerate defect, and it would also read worse, since "only whoever is right at my lip" is
  exactly the fantasy.
- ⚠️ **The raid AI will not understand it.** Raiders choose targets with their own reachability and LOS
  notions, so denying the shot late can leave them repeatedly trying and failing, or milling about. The
  honest mitigation is to make a SUPERDEEP occupant an invalid *ranged target* for AI selection, not
  merely an illegal shot — otherwise the mechanic reads as broken pathing rather than as depth.
- Consequences worth stating plainly: **turrets cannot shoot into a pit** unless adjacent, and **a
  trapped raider can still shoot whoever stands at the lip** — so capture is not a clean win, which is
  better gameplay and should be deliberate rather than discovered.

## 23. Rulings 24-27 (owner, 2026-09-16)

**24. A source is not a building. Delete the comp.** `CompFluidReservoir` and `RM_FluidSpring_Test`
disappear as concepts — a source is a SUPERDEEP cell at `F = D`, limitless when fed off-map (ruling 16)
and limited when fed by rain, season and seepage (ruling 2). One primitive owns supply, and nothing has
to stay in sync with the depth grid.

⚠️ **The cost he accepted, restated so it is not a surprise:** this deletes the mod's only live-proven
path. All three of FlowWorks' modcheck components assert against that comp (`primed=True`,
`remainingVolume=60.0`, `nextDripTick - nowTick == 2500`) and its walk is written around
`RM_FluidSpring_Test`. The validator and the walk must be rebuilt against the new primitive, and until
they are, this mod has no live proof at all.

**25. Rain fills excavations only where unroofed.** Roofing is the player's lever, and it costs nothing
— RimWorld already tracks roof per cell. ⚠️ It also reopens the covered-pit contradiction of §19: a
roofed pit full of liquid has a cover claiming the cell is hidden and a pool claiming it is not.
Decide which is drawn, or roofing a trap produces a visual lie.

**26. SUPERDEEP captures as if dry; shallower is wadeable.** Fill does not change whether a pawn falls
in — SUPERDEEP always takes them, and *then* the liquid acts on them (ruling 22). No drowning model is
needed, and the **trap-then-flood pipeline is the intended path to lethality**. Consequence he accepted:
a brimming deep canal is a tax, never a barrier, so **stopping power comes entirely from SUPERDEEP
pits** — a water moat alone stops nobody.

**27. Merge first, then fix the pit inside FlowWorks.** Consolidation precedes the pit's art pass, so
sprites are drawn once, against final def names and knowing they must read at four depths.

### The mitigation for what ruling 27 parks — and it costs nothing

Ruling 27 delays the pit's *art*, which would otherwise leave the north-star system with no end-to-end
proof for weeks. It does not have to: **the proof does not need the art.**

Validating Pits' existing DRAFT checklist **right now** takes it from GREEN to REFUSED immediately —
eleven validated must-show lines, no component claiming any of them, so the visual floor refuses the
mod. That is exactly §9's falsification test (*"Pits moves from GREEN to REFUSED-or-RED once its
checklist is VALIDATED"*), it needs no sprite work, and it is one command:

```
python3 src/RimMandrake/Utils/modcheck/cli.py validate Pits --owner-said "<his words>"
```

So the system gets proven today, the art is fixed after the merge as he ruled, and nothing is
sequenced behind anything. Recommended.
