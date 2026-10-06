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

## design pass (FOUNDRY builder, Opus, 2026-10-03)
The spec above stands; this pass orders it so every step is shippable on its own and only one step changes behaviour.

**Step 1: BUILT** (storage, behaviour-neutral). `RM_MapComponent_Excavation.fluidGrid` (byte per cell, 0 = none, else 1 + index into a scribed `fluidPalette` `List<FluidDef>`, cap 254 fluids/map), `FluidAt(c)`, and `SyncFluidIdentity()` run at the end of every pulse and in `FinalizeInit`: stamps `ActiveFluid` on excavated cells with F>0 and no record, clears the record at F=0, gives every body with no fluid `ActiveFluid`. That one call is also the **step-4 save migration**: an old save loads an all-zero grid and every wet cell is stamped. `RM_LiquidBody.fluid` (scribed `fluid`) is set once in `FormBody` from the seed cell's terrain through `RM_FluidIdentity.FluidOfTerrain` (every LiquidDef's terrainSuite -> canalFluid; fallback `RM_Fluid_Water`). Nothing reads either yet, so flow, rendering and the conservation ledger are unchanged. Census: static_call `RimMandrake.FlowWorks.RM_FluidIdentityProof.ProofCensus`; chain `fluid_identity_recorded`.

**Step 2 (next, the behaviour change):** move identity to the WRITERS and delete the sync stamp. Each fillGrid increment knows its source: `ResolveComponent` (recipient takes the donor's fluid: `FluidAt(donor)` for a channel donor, `body.fluid` for a source donor), `ApplyRain` (water; skip a wet non-water cell), `Displace` (credit only cells whose fluid matches), `Building_LiquidDrill` (its yielded canalFluid), the debug fill actions. Then the `PickDonor` filter (skip donor n when r is wet and FluidAt(r) != FluidOf(n)). Keep `SyncFluidIdentity` only as the load-time migration. Selftest first: the pulse is not Verse-free, so the filter goes into `RM_StockMath` as a pure predicate the selftest can drive (the FLOWWORKS_SHARED_SOURCE_STALL_1 pattern).

**Step 3:** retire `ActiveFluid` reader by reader (render/terrain apply, stock capacity per `body.fluid`, drill's one-per-map refusal); `ActiveFluid` survives only as the migration default.

**Risk named:** a FluidDef removed from the mod set leaves a null palette entry after load; `FluidAt` then answers null for those cells and the sync re-stamps them with `ActiveFluid` (a silent conversion). Step 2 must log it once per map instead.

## built so far
- step 1 + step-4 migration: see the commit closing this note (`git log --grep LIQUID_BODY_FLUID_IDENTITY_1`). Item stays OPEN for steps 2-3 and the verify block.

## step 2a BUILT (FOUNDRY builder, 2026-10-05)
`RM_StockMath.FluidsCompatible` (pure; null = permissive) is the `PickDonor` no-mix filter; the pulse stamps the donor's fluid (source: `body.fluid`) on a recipient's first level (identity at the pulse writer). Behaviour-neutral until a second fluid exists (one `ActiveFluid` per map). Selftest cases in `Source/SelfTest/Program.cs` (not runnable here: no dotnet in WSL; DLL builds clean). STILL OWED: writers other than the pulse (`ApplyRain` skip wet non-water, `Displace` same-fluid credit, drill, debug fills), step 3 reader retirement, the unified-null-palette log, the bridge verify. Item stays open.

## step 3 BUILT (FOUNDRY flowworksA, 2026-10-05)
`ActiveFluid` retired as a decider: `RM_LiquidStock` capacity (`FormBody`), `CanSupply`, refill and recession read `body.fluid`; the pulse's source debit unit is the source body's fluid. `ActiveFluid` now appears only as `?? ActiveFluid` — the default for a cell/body a save left unstamped (step-4 migration). Null-palette risk closed: `ReportLostPaletteFluids` (FinalizeInit) warns once per map load with the lost-fluid and affected-cell counts, then the re-stamp is the disclosed migration. Debug fills name their fluid: dev action "Fill excavated cell with fluid..." and static_call `RimMandrake.FlowWorks.RM_FluidIdentityProof.ProofFillWithFluid` ("x,z,fill,FluidDefName"; refuses a cell holding another fluid). OWED: the bridge verify block (two-fluid join, drain, save/load) — needs a live session; item stays open for it.
