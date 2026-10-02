# BELT: pit owner answers (Q1-Q4) — 2026-10-02

Owner answers (OWNER.jsonl lines 187-188, `PIT_SUPERDEEP_COLLAPSE_1`): Q1 ladder = prison door (card);
Q2 spikes D=4 only (card); Q3 typed: *"Analyze which of these is most feasible in the game/code. If (1)
is easiest, it's also the best for now. I had thought (2) would be easiest and it isn't bad either. (3)
seems like a huge mess with little payoff."*; Q4 typed: *"The pit has to be as wide as the creature to
hold it. Otherwise it gets out."*

## Task 1 Q3 feasibility — read from source, `src/RimMandrake/FlowWorks/Source/`

### Today's behaviour (MEASURED by reading, 2026-10-02, at 639722ff3)

- **There is exactly ONE fluid per map.** `RM_MapComponent_Excavation.activeFluid` (scribed
  `RM_activeFluid`, defaults to `RM_Fluid_Water`). Every reader takes it: flow debit
  (`ResolveComponent` → `stock.TryDebit(... ActiveFluid.volumePerTile ...)`), render
  (`RenderComponentFill`, `ApplyFillTerrain`, `ClearFillTerrain`), rain (`ApplyRain`), fill-in
  (`Displace`), body capacity at formation (`RM_LiquidStock.FormBody`), body refill/recession
  (`RM_LiquidStock.Pulse`). `Building_LiquidDrill` refuses to produce when its liquid's canal fluid
  differs from `ActiveFluid` and says so in its own doc comment ("one per map this pass").
- **Bodies carry no fluid.** `RM_LiquidBody` has id / limitless / stock / capacity / cells / receded /
  truncated — no FluidDef. A natural source is ANY undug cell whose BASE terrain `IsWater`
  (`IsNaturalLiquid`), whatever liquid it depicts.
- **A pit is not a body.** Excavated cells hold only `depthGrid`/`fillGrid` bytes. "Components" are
  re-found every pulse by a cardinal BFS from `excavatedCells` (`DoPulse`) and never stored.
- **The exact moment a channel joins two pits:** on the next pulse `DoPulse`'s BFS walks through the
  new channel and both pits land in ONE `pulseComponent`; `ResolveComponent` sorts recipients
  deepest-first then by source/sink hop order (`ComputeFlowOrder` + `RM_StockMath.MayFlowBetween`, the
  oscillation fix) and moves integer levels by `PickDonor` (gravity / overflow). Because every level is
  the one map fluid, they simply equalise; there is no identity to conflict. **So "water pit meets oil
  pit" cannot happen today — the second fluid cannot exist on the map.**
- **Two natural bodies joined by a canal never merge.** `FormBody` floods only over undug `IsWater`
  cells (8-adjacency); a canal cell has D≠0 so `IsSourceCell` is false and the flood stops at it. Each
  body keeps its own record, stock and sticky classification; each source cell debits only its own body.

### Option 1 — fluids don't mix (CHEAPEST, RECOMMENDED)

Sketch:
1. `byte[] fluidGrid` beside depth/fill (0 = none; index into a per-map scribed `List<FluidDef>`
   palette). A cell's fluid is set when its F goes 0→>0 and cleared when F returns to 0.
2. `RM_LiquidBody.fluid` (FluidDef), set ONCE in `FormBody` from the base terrain via a startup lookup
   `LiquidDef.terrainSuite.{shallow,deep,chestDeep}` → `LiquidDef.canalFluid`; fallback water. Capacity
   and refill read `body.fluid`, not the map. Sticky like `limitless` (ruling 16 shape).
3. **`PickDonor` gains one filter:** skip donor n if r is wet and `FluidAt(r) != FluidAt(n)` (a source's
   fluid is its body's). That is the whole no-mix rule. Everything else is unchanged.
4. Render/clear/rain/displace read the cell's fluid, not `ActiveFluid`. Rain adds water only to cells
   that are dry or already water. `Displace` credits only same-fluid cells/bodies; the rest is the
   already-disclosed overflow. Drill: produce when the outlet is dry or holds its fluid (its "one per
   map" limitation disappears).
5. Save migration: on load with no `fluidGrid`, stamp `activeFluid` on every F>0 cell and every body;
   then `activeFluid` stops being read (field kept for load only, then removed).

Behaviour at the join: the first fluid to reach a dry channel cell (deterministic: recipient sort order,
then `PickDonor`'s fixed N/E/S/W direction order) claims it; the other front stops at the boundary. The
two fluids stand side by side and never cross. Drain one side (sink, fill-in, evaporation) and its cells
go back to F=0/no fluid, so the other fluid advances — "until one is drained" falls out for free.

Risk: LOW. The filter only REMOVES donor candidates from an already-proven flow, so it cannot create a
new cycle (the oscillation fix's `MayFlowBetween` still governs) and cannot break the conservation
ledger (every move is still −1/+1). Real cost is the plumbing in step 4 (~10 call sites of
`ActiveFluid`) and one new byte grid in the save.
Nuance vs the card wording: the card said "the joining channel stays dry". Literal stays-dry needs one
more check (a dry cell with two differently-fluided wet neighbours receives from neither). The natural
build is "the fronts meet and stop"; this pass specs that and notes stays-dry as a one-check variant.

### Option 2 — the bigger pool wins (more work: 1 plus a resolve pass)

Needs everything in option 1 (a per-cell identity is required to know there ARE two pools), plus:
a per-pulse pass that, when a component holds two fluids in contact, measures each side's same-fluid
connected volume, picks the larger (limitless always wins; tie-break by cell index) and rewrites the
loser's `fluidGrid` cells. Risks: (a) a natural body losing means rewriting natural BASE terrain across a
lake (not the temp layer) plus `originalTerrain` records, and it re-classifies a body ruling 16 says is
classified once — so restrict conversion to excavated pools only and let natural bodies just no-mix;
(b) cascades within one pulse (A converts B, B now touches C); (c) the owner's own trade-off — one
careless dig flips an oil trap. Adds: an oil trap can be flushed with water, which is a real tactic.
Option 1's grid is a strict prerequisite, so choosing 1 now loses nothing if 2 is wanted later.

### Option 3 — murky sludge: why it is a mess

A blend either needs a sludge FluidDef per PAIR (N² defs, terrain tiers and art each) or a per-cell
composition vector, which breaks the integer-level grid every rule (flow, ledger, displacement, stock)
is written on; then drowning/poison/ignition need weighted rules and each component needs its own
conservation ledger. Large cost, payoff is one more liquid to draw and balance.

### Recommendation
**Option 1.** It is the easiest by a wide margin (one filter on the existing donor picker plus
replacing the per-map field with a per-cell/per-body one, which the per-body-fluid work [F] needs in
EVERY option anyway). By his rule, 1 wins for now; 2 is a later add-on on the same grid.

## Task 2 Q4 width rule

- **What RimWorld exposes:** every pawn occupies exactly ONE cell (pawn `ThingDef.size` is 1×1; pathing
  is single-cell), so "width" cannot be read off the footprint. The usable stat is **`Pawn.BodySize`**
  (= `RaceProps.baseBodySize` × current life stage's `bodySizeFactor`) — the same stat [G] already uses
  for spike damage, so the ruled pairing ("bigger = harder to hold AND hurt more") is kept.
  `graphicData.drawSize` is art-dependent (any mod can draw a rat at 3×), so it is rejected.
- **Definition.** Required width `W = max(1, round(sqrt(BodySize)))` — BodySize read as a footprint area
  in cells, sqrt as its side. Bands: BodySize < 2.25 → W=1; 2.25–6.25 → W=2; 6.25–12.25 → W=3.
  A pawn is **held** at a D=4 cell only if some **W×W square made entirely of D=4 cells contains its
  cell**. One-cell pits therefore hold everything under 2.25 (humans and most animals).
  ⚠️ Example sizes (vanilla human 1.0; thrumbo/elephant ~4) are from memory, UNMEASURED; the band
  numbers are a proposal for his word, as a Mod Setting multiplier.
- **Escape = the trap rule does not apply.** The exit veto in `SUPERDEEP_HOLDER_RETIRE_1` (reachability
  veto + per-move floor) gains one condition: `held = D==4 && !loweredLadderHere && PitWidthAt(c) >= W`.
  A pawn that is not held simply walks out like any canal — normal pathing and the depth movement
  cost; no roll, no special job. It still took fall damage and spikes on the way in (descent event is
  independent of width).
- **Edge cases:** evaluated live, so a creature that GROWS (life stage) past the pit's width climbs out;
  filling in a neighbour cell can shrink the square and free it; a 1×10 trench is 1 wide (the square
  test, not cell count); diagonal trenches do not count; downed pawns cannot move so stay regardless;
  a too-wide creature is never "trapped" for capture-down purposes and cannot make a superdeep room a
  prison; flying pawns are not decided here (separate question if needed). Inspect line on the pawn:
  "too big for this pit — can climb out".

## Task 3 doc/items edited
- `design/RimMandrake/flowworks_pits_unified_model_2026-10-02.md`: §3.1 (fluid identity per cell/body,
  no-mix, width rule replaces the "no limit at D=4" DEFAULT), §3.2 (held only if wide enough; "gets
  out" = walks out), §3.4 (spikes D=4 only; ladder prison-door climbing), §3.5 (no-mix behaviour), §2
  + §3.5 + §5 (oscillation item now CLOSED at `ddb473416` — stale "waits on it" text deleted), §4.1
  PitDepthTier row, §6 table (waits-on-oscillation column dropped; last column now the answer that
  shapes each item), §7 rewritten as answers with the Q3 analysis and the Q4 definition.
- Items: `LIQUID_BODY_FLUID_IDENTITY_1` (spec rewritten to the no-mix build, verify, depends),
  `PIT_FILL_EFFECTS_1`, `SUPERDEEP_HOLDER_RETIRE_1` (step 5 = width rule; verify), `CANAL_BOTTOM_SPIKES_1`,
  `LADDER_PRISON_DOOR_1`, `SUPERDEEP_PRISON_ROOM_1`, `EXCAVATION_WALL_ART_1` (no shallow spike art),
  `FLOWWORKS_DOOR_FAMILY_1` (open question now points at the width rule), `PIT_SUPERDEEP_COLLAPSE_1`
  (one line under [J]).

## Task 4 Northstar bars
Added a **"First script must prove"** line to the `## northstar` of: `LIQUID_BODY_FLUID_IDENTITY_1`
(per-cell fluid census, stable boundary, drain-then-advance, save round-trip), `PIT_FILL_EFFECTS_1`
(per-cell effect by fluid id), `SUPERDEEP_HOLDER_RETIRE_1` (held matrix {small,large}×{1×1, 1×5, 2×2}
+ fill-in flips it), `CANAL_BOTTOM_SPIKES_1` (placement census by depth), `LADDER_PRISON_DOOR_1`
(reachability {colonist,hostile,prisoner}×{lowered,raised} + prison break), `SUPERDEEP_PRISON_ROOM_1`
(confinement follows width). Nothing committed (FORBIDDEN in this brief) — the window commits.
