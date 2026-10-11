## Findings

Paths below are relative to `src/RimMandrake/`.

1. **MAJOR — Pump-fed channels can stall permanently after reload.**  
   **Evidence:** `FlowWorks/Source/RM_MapComponent_Excavation.cs:1483-1487` deliberately does not save `driverInputTick`; `:1198-1200` uses that dictionary to seed flow order. `:1098-1103` refuses a pour into a full cell, and `:1547-1549` records an input only when fill rises.  
   **Why:** Reload a source-free, equal-depth channel with a brimming pump outlet and downstream room. Its input seed disappears; equal-key overflow cannot move, and the full outlet prevents the write that would recreate the seed. Hose pour routes expose the same trap.  
   **Design fix:** Add a persisted or reconstructed input-seeding contract, including full outlets. Gate steps 6/8 with a brimming-outlet reload test.

2. **MAJOR — The LiquidDef/FluidDef boundary remains unspecified.**  
   **Evidence:** `FlowWorks/Source/RM_MapComponent_Excavation.cs:1075-1103` exchanges `FluidDef`, while v2 §4.2 credits and saves `LiquidDef`. `FlowWorks/Source/RM_FluidIdentity.cs:25-35` maps only registry rows having both `terrainSuite` and `canalFluid`. `FlowWorks/Patches/LiquidTypes/RM_FluidSurfaceLooks.xml:4` explicitly identifies fluids without registry rows; `RM_LiquidDef_AstrofuelAdoption.xml:43-47,57-68` describes and creates an adopted liquid without a canal mapping.  
   **Why:** “Any liquid” in tanks does not establish that every canal fluid has a tank identity, or that every tank liquid can be poured into a canal. The existing pump conversion policy is **outside this slice**.  
   **Design fix:** Require a mapping census and explicit unsupported/ambiguous conversion behavior before adding credits or nozzle reach. Include FluidDef-only fluids and adopted astrofuel; never substitute water silently.

3. **MAJOR — Legacy flooding and canal stock use incompatible volume conventions.**  
   **Evidence:** `FlowWorks/Source/Flood_FlowWorks.cs:333-343` fills an excavated cell to its entire depth but spends one `volumePerTile`. `FlowWorks/Source/RM_MapComponent_Excavation.cs:1256-1261` spends that same quantity for **one level** from a natural source. `Flood_FlowWorks.cs:97,181,359` also permits a final whole placement from a positive fractional remainder.  
   **Why:** A dry D4 cell receives four exportable levels for a one-tile flood debit. Real hose transport makes these inconsistent budgets economically observable; route-credit tests alone cannot detect them.  
   **Design fix:** Specify the conversion among tank units, grid levels, source-stock units and legacy release volume. Debit actual fill added and refuse unaffordable additions. Add D1/D4, partial-fill and fractional-budget conservation tests.

4. **MAJOR — Disabling legacy flood integration restores competing terrain ownership.**  
   **Evidence:** `FlowWorks/Source/Flood_FlowWorks.cs:333` gates engine ownership on `legacyFloodViaEngineEnabled`; when off, `:353-354` writes temporary terrain and queues its removal even on an excavated cell. `FlowWorks/Source/RM_MapComponent_Excavation.cs:1385-1413` independently renders that cell’s grid fill.  
   **Why:** A later hose-fed pour can replace the flood terrain while the old removal remains queued. That removal can erase the engine’s current liquid appearance without removing its F. The code’s own ownership fix is thereby optional.  
   **Design fix:** Make excavation ownership unconditional. Define the switch’s fallback as refusing that release on owned cells, or retaining engine mediation. Test flood → pump refill → queued recession with the switch off.

5. **MAJOR — Tar cooling bypasses excavation ownership even with integration enabled.**  
   **Evidence:** Engine-mediated placements enter `placedCells` at `FlowWorks/Source/Flood_FlowWorks.cs:336-340`; `:377-390` later writes permanent glass terrain onto those cells directly. Excavation depth remains separately authoritative at `FlowWorks/Source/RM_MapComponent_Excavation.cs:576-617`.  
   **Why:** Cooling replaces an owned channel’s base terrain without reconciling D/F or its restoration record. Pumping the liquid away exposes that disagreement.  
   **Design fix:** Route cooling through an excavation-owned coating/terrain policy. Add drain, deepen, fill-in and reload checks after an engine-mediated tar release cools.

6. **MAJOR — Palette exhaustion silently changes transported liquid identity.**  
   **Evidence:** `FlowWorks/Source/RM_MapComponent_Excavation.cs:303-319` returns key 0 when 254 palette entries already exist. `:1543-1551` nevertheless accepts and fills the cell; `:326-339` subsequently stamps an unrecorded wet cell as `ActiveFluid`. Compaction occurs during load repair at `:256-289,458-460`.  
   **Why:** The next distinct fluid can become the map default, changing subsequent pump exports, tint, fire and heat behavior. Reload-only compaction does not protect a running session.  
   **Design fix:** Compact unused entries before allocation; if no key is available, refuse before changing fill or debiting a tank. Test exhaustion and slot reuse without reloading.

7. **MAJOR — Fire can consume replacement water between maintenance checks.**  
   **Evidence:** `FlowWorks/Source/RM_LiquidFire.cs:223-227` throttles maintenance. `:428-450` allows `BurnableFluidAt` to return null, then still accrues burn and calls `BurnOffLevel`. `FlowWorks/Source/RM_MapComponent_Excavation.cs:1048-1070` removes whichever liquid currently occupies the cell.  
   **Why:** Draw the last burning fuel level and pour water before the next fire check: a due burn pulse can destroy water using the old fuel’s accumulator. Replacement burnable fluids also retain progress because `RM_LiquidFire.cs:347-365` never compares their identity with `burningFluid`; that identity is unsaved at `:55`.  
   **Design fix:** Revalidate current fuel and identity inside `BurnPulse`, and reset incompatible progress. Add interleaved draw/pour/burn and reload tests.

8. **MAJOR — Heat budgeting permanently starves some cells and overweights others.**  
   **Evidence:** `FlowWorks/Source/RM_LiquidHeat.cs:97-110` gathers every excavated source; `:112-124` applies the global sampling scale to an excavated prefix starting at index 0 every interval. Only natural cells rotate at `:124-134`.  
   **Why:** Above the budget, later excavated cells never receive heat. Natural cells can receive none at all. Even below that threshold, repeatedly sampled excavation cells receive inflated energy when the combined total exceeds the budget. Gathering remains an unbounded excavation scan.  
   **Design fix:** Rotate both source classes with correct sampling weights, and distinguish gathering cost from credited-cell count. Add multi-room tests above the budget, including hot excavations alongside cold natural liquid.

9. **MAJOR — Natural heat sampling trusts obsolete terrain identity.**  
   **Evidence:** `FlowWorks/Source/RM_LiquidHeat.cs:25,59-62,82-86` caches natural cells and kinds for 15,000 ticks; `:130-134` credits them without checking current terrain or excavation ownership. `FlowWorks/Source/RM_MapComponent_Excavation.cs:978-1000` dries natural cells without calling heat invalidation.  
   **Why:** Recession or excavation can leave dry cells heating/chilling rooms, or cause a newly excavated cell to be counted twice. Whether another invalidation hook exists is **outside this slice**.  
   **Design fix:** Require terrain/depth-change invalidation or current-state validation when sampling. Add recession, restoration and excavation tests during the cache window.

10. **MAJOR — The nozzle increment needs an explicit sealed-cell contract.**  
    **Evidence:** `FlowWorks/Source/RM_MapComponent_Excavation.cs:818,1185` honors shut sluices for displacement and kernel flow. Its public pump methods at `:1075-1103`, and driver writer at `:1511-1560`, contain no seal check.  
    **Why:** Extending reach through those APIs can add or remove liquid from a cell the flow engine treats as sealed. Whether existing pump callers precheck seals is **outside this slice**.  
    **Design fix:** Specify whether pumping overrides a sluice seal, and enforce that decision at the transfer boundary. Step 9 needs closed-sluice/open-sluice/grate tests in both directions, beyond its proposed reach test.

11. **MINOR — Existing pump proof reads the wrong tank for hose routes.**  
    **Evidence:** `FlowWorks/Source/RM_NorthstarProofs.cs:128-137` reports the first eight-adjacent tank and cumulative `Moved`; it does not inspect the remote destination or route.  
    **Why:** That surface reports “none” for a hose-only destination, or reports an unrelated adjacent tank. Adding pump stamp fields does not repair this consumer.  
    **Design fix:** Explicitly update this proof surface, or name its replacement. Read a specified destination’s liquid/unit delta and the credited reel IDs.

12. **MINOR — The proposed offline net gate can drift from production.**  
    **Evidence:** v2 §5.6 calls `HoseNetChecks` a separate “model of the net rules.” The existing production-test discipline explicitly rejects hand transcriptions at `FlowWorks/Source/RM_StockMath.cs:9-19`.  
    **Why:** A correct model can pass while the actual traversal, cache or credit wiring is wrong; batching live proof at step 8 leaves that gap across intermediate landings.  
    **Design fix:** Extract and compile the production Verse-free traversal/cache/credit logic into SelfTest. Add Python wiring checks for actual transfer callers, plus the boundary regressions above.

## Design claims verified

- Canal cells retain per-cell `FluidDef` identity; driver additions check input settings and no-mix compatibility (`RM_MapComponent_Excavation.cs:1533-1555`).
- Natural-source transfers use the source fluid’s own `volumePerTile`, rather than a fixed stock debit (`RM_MapComponent_Excavation.cs:1256-1261`).
- Existing standing liquid and newly admitted liquid have distinct settings semantics; driver increases consult `InputAllowed` (`RM_MapComponent_Excavation.cs:1248-1254,1535-1537`).
- VE adapters are actual `CompLiquidPipeAdapter` machines, supporting v2’s machine classification; the XML does not provide generic third-party net interoperability (`Patches/Machinery/RM_PipeNetAdapters.xml:58-68`).
- No visible C3 production code references GSS.

## Outside this slice

- All cited GSS hose, geometry, style, settings, save-skip and migration implementations.
- `RM_LiquidNet`, pump/tank internals, converters, adapters, reactions and baths: actual traversal, transfer atomicity, conversions, cadences, reach and credit insertion.
- Link-index freshness, relay chains/rings, endpoint merging, route selection and per-tick cache correctness.
- `LiquidDef.color`, full registry/terrain suites, setting defaults/window completeness, aliases, Harmony bootstrap and shared-source build wiring.
- Pump-intake behavior during shoreline recession; any external heat invalidation hooks.
- Save-engine claims, mid-job aliases, settings-file import behavior, proposed harness changes and measured performance.