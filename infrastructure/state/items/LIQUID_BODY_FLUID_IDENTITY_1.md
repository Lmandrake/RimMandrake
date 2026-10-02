# LIQUID_BODY_FLUID_IDENTITY_1 — Fluid identity per liquid body (retire per-map ActiveFluid); the merge rule

Part of the pit collapse (`PIT_SUPERDEEP_COLLAPSE_1` carries the rulings; `design/RimMandrake/flowworks_pits_unified_model_2026-10-02.md` is the one model). A pit is a canal cell dug to SUPERDEEP (D=4) and nothing else.

## spec
[F] + owner Q3 (2026-10-02, typed: *"If (1) is easiest, it's also the best for now."*): **fluids never mix** — chosen because it is the cheapest of the three by reading the code (unified model §7 Q3).
1. **Identity.** `byte[] fluidGrid` beside depth/fill in `RM_MapComponent_Excavation` (0 = none; index into a per-map scribed `List<FluidDef>`), set when a cell's F goes 0→>0 and cleared when F returns to 0 — a pit is not an `RM_LiquidBody`, its components are re-found every pulse, so identity must be per cell. `RM_LiquidBody.fluid` set ONCE in `RM_LiquidStock.FormBody` from the base terrain (startup lookup `LiquidDef.terrainSuite.{shallow,deep,chestDeep}` → `LiquidDef.canalFluid`; fallback water) and sticky like `limitless`.
2. **The no-mix rule = one filter in `PickDonor`:** skip donor n when recipient r is wet and `FluidAt(r) != FluidAt(n)` (a source's fluid is its body's). Nothing else in the rank-ordered flow changes; the filter only removes candidates, so it cannot reintroduce `FLOWWORKS_CHANNEL_OSCILLATION_1` and every move stays −1/+1 for the ledger.
3. **Retire `ActiveFluid`** at every reader: `ResolveComponent` debit unit, `RenderComponentFill`/`ApplyFillTerrain`/`ClearFillTerrain` (cell's fluid), `ApplyRain` (water lands only on dry or water cells), `Displace` (credit only same-fluid cells/bodies; the rest is the disclosed overflow), `RM_LiquidStock` capacity/refill/recession (`body.fluid`), `Building_LiquidDrill` (produce when its outlet is dry or holds its fluid — its "one per map" limitation goes away), `FlowWorksDebugActions`.
4. **Save migration:** a save with no `fluidGrid` stamps its `activeFluid` onto every F>0 cell and every body on load.
Behaviour at a join: the first fluid to reach a dry channel cell (recipient sort order, then `PickDonor`'s fixed direction order) claims it; the other front stops there; drain one side to dry and the other advances. Literal "the channel stays dry" (refuse a dry cell with two differently-fluided wet neighbours) is a one-check variant, not specced.
Not built now: "bigger pool wins" (owner's option 2) — a later resolve pass on this same grid, limited to dug pools.

## verify
Bridge, minimal `flowworks` tier: a water pit and an oil pit, a dry channel dug between them → after N pulses no cell holds a level of the "wrong" fluid, the two fronts meet and stop, total levels per fluid conserved; drain the oil side (sink) → water then advances into the vacated cells; save/load keeps each cell's and body's fluid; an old save (only `RM_activeFluid`) loads with every wet cell stamped.

## criteria
`fill_fluid_distinct` becomes reachable.

## depends
`FLOWWORKS_CHANNEL_OSCILLATION_1` — closed 2026-10-02 at `ddb473416`; nothing blocks this item now.

## northstar
State components: fluid per body before/after joining; the old "unconditional BLOCKED (one ActiveFluid per map)" row is promoted to a real check.
**First script must prove (Q3 no-mix):** (a) per-cell fluid census of the joined component after N pulses — zero cells whose fluid differs from the fluid of the levels that arrived there, and per-fluid level totals equal before/after (no conversion); (b) the meeting boundary is stable across further pulses (no flip, same cells); (c) after draining one side, the other fluid occupies the vacated cells; (d) save/load round-trip of `fluidGrid` and `body.fluid`. Record the expected-first-fail as "today one `ActiveFluid` per map — a second fluid cannot exist" (a ruled-out theory, kept).
