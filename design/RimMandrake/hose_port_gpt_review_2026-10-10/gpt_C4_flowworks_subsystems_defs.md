## Findings

Paths below are relative to `src/RimMandrake/FlowWorks/`.

1. **BLOCKER — Supplied swept-away source has an unmatched closing brace.**  
   **Evidence:** `Source/Rivers/RM_WorldComponent_SweptAway.cs:151` closes the method, `:152` the class, `:153` the namespace; `:154` adds another `}`.  
   **Why it matters:** As supplied, this file cannot compile if included in the production project. Passing Verse-free hose tests cannot establish the design’s promise that each increment leaves FlowWorks loading cleanly. Project inclusion is outside this slice.  
   **Design fix:** Add a full production-build baseline gate to step 0, correct the brace, and require both production DLL builds at every code-changing increment.

2. **MAJOR — Step 9 lacks a negative source-eligibility test for water-tagged solid terrain.**  
   **Evidence:** `Defs/ManyWaters/TerrainDefs/RM_DeepSand.xml:128` declares `Freshwater`, `:136` supplies the `Water` tag, and `:158` supplies a recreational-swimming exclusion. Its header explicitly describes sand behaving like water for fishing only.  
   **Why it matters:** Neither the water tag nor water-body type proves that a nozzle occupies pumpable liquid. Step 9 specifies a reach test and one live row, without testing this shipped counterexample. Whether the existing pump already rejects deep sand is **outside this slice**; this finding is a missing design gate, not a proven current pump exploit.  
   **Design fix:** Specify that nozzle eligibility uses the pump’s liquid-source validation and accounting. Add offline cases rejecting deep sand and dry terrain, alongside accepted registered liquids, disabled liquids, and exhausted finite sources.

3. **MAJOR — Weir washing can orphan liquid containers when placement fails.**  
   **Evidence:** `Source/Rivers/RM_Weir.cs:327-331` treats any nearby haulable item as held catch. `:421` despawns each item before `:422` attempts placement; `:423-426` handles success only, with no failure restoration or ownership transfer.  
   **Why it matters:** This affects nearby player supplies, not merely generated fish or drift. A failed placement leaves a container unspawned and unowned by this method. River-side pumping sites expose this existing loss path.  
   **Design fix:** Add a pre-port correction: preserve ownership until placement succeeds, or restore/retain failed items. Gate it with an injected-placement-failure test asserting item identity, stack count, and contents survive—not just the number successfully washed.

4. **MINOR — The settings inventory misses a separate FlowWorks Mod/settings owner.**  
   **Evidence:** `Source/ManyWaters/RiverSteamSettings.cs:23` declares another `ModSettings` class; `:31-32` persist its two keys. `:50` declares `RiverSteamMod`, `:56` independently loads those settings, and `:59-61` declares the “FlowWorks: Water effects” settings category.  
   **Why it matters:** V2 §2.3 describes one settings owner, and §8 plans around that inventory. The supplied assembly also declares an independent owner and screen, which must be accounted for when proving defaults and all-off behavior. Actual bootstrap/menu behavior is outside this slice.  
   **Design fix:** Extend step 0 to inventory every `Mod` subclass, settings file, and screen. Explicitly preserve this owner, or separately specify its consolidation and migration; include river steam in the all-off proof.

## Design claims verified

- Production is an appropriate reel default relative to the plain pump: `Defs/LiquidTypes/ThingDefs/RM_LiquidPump.xml:33`. The pump is also explicitly minifiable at `:29`.
- Drilling is a separate acquisition path: `Source/Drilling/Building_LiquidDrill.cs:137` extracts subsurface reserve, and `:148-150` commits it through driver fill, subtracting pending units only on success.
- The drill checks fluid enablement before extraction: `Source/Drilling/Building_LiquidDrill.cs:110`.
- The supplied sources distinguish fishable water-tagged terrain from literal liquid; nozzle tests must preserve that distinction.

## Outside this slice

- Pump/tank runtime, `RM_LiquidNet`, converters, adapters, reactions and baths: merging/splitting, relay traversal, route crediting, mixed-liquid transfers, cadence, cache freshness and runtime cost remain unverified.
- Liquid registry mappings, natural-body budgets and excavation internals: source identity, depletion, unit conversion and draw/pour conservation cannot be established from terrain XML alone.
- Container jobs, material rules and revert behavior: definitions alone do not establish successful transfers or rollback.
- GSS hose code, shared-source changes, production project inclusion, Harmony bootstrap, aliases, settings import, load ordering and mid-job save compatibility.
- Assertion inventories, proof manifests, live performance and save-loading results. No build or runtime test was executed.