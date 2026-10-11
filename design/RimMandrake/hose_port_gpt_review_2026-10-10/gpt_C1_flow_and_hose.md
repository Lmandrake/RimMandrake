## Findings

Paths below are relative to `src/RimMandrake/`. References to §§ are to the v2 design.

1. **BLOCKER — The mandatory reel-side port prevents ordinary relay chains.**  
   **Evidence:** `GimmeSomeSlack/Source/Hose/HosePorts.cs:40-44` excludes reels from port classification; `RM_MapComponent_Hoses.cs:140-146` discovers feeders separately. A receiving reel fed only by another hose therefore has no `Port()`.  
   **Impact:** §4.1 requires both ports for its own link, so pump → A → B → tank cannot conduct as promised.  
   **Fix:** Define a relay inlet vertex and connect the receiving reel’s hose through it. Require a native neighbour port only for an independently supplied reel. Test forward and reverse traversal through three otherwise isolated reels.

2. **BLOCKER — Step 4 breaks compilation before step 6 lands.**  
   **Evidence:** `GimmeSomeSlack/Source/Hose/HoseFlow.cs:56` reads `useFlowWorksPumps`; `RM_MapComponent_Hoses.cs:486` reads `defaultFluid`.  
   **Impact:** Step 4 deletes these fields while their consumers survive until step 6. The increments are not individually landable.  
   **Fix:** Retain compatibility fields until step 6, or move their deletion into the commit that replaces their consumers. Compile both production DLLs after every increment.

3. **MAJOR — Reactor and bath machine classification names nonexistent comps.**  
   **Evidence:** The actual reactor is `CompLiquidReactor`, at `FlowWorks/Source/Machinery/Kits/RM_LiquidReaction.cs:81`; `RM_LiquidBath` is a static helper, at `RM_LiquidBath.cs:64`, reading a **recipe** extension at `:66-68`.  
   **Impact:** §4.1’s “thing with `RM_LiquidReaction` / `RM_LiquidBath`” cannot identify these origins. Their hoses will not seed the net.  
   **Fix:** Recognise `CompLiquidReactor`; identify bath benches through an explicit port marker or their available recipes’ `RM_RecipeLiquidExtension`. Give native adapter classification precedence over its third-party storage comp.

4. **MAJOR — Lazy lookup cannot discover a newly selected port key.**  
   **Evidence:** `CompHoseReel.cs:82-89` can replace the selected port; `RM_MapComponent_Hoses.cs:320-326` can replace the far port without changing the hose’s end cell.  
   **Impact:** Resolving reels already stored under queried key X can remove stale memberships, but cannot discover that a reel formerly indexed under X now belongs under previously empty key Y. M7 remains incomplete.  
   **Fix:** Specify an independent refresh pass over registered reels, updating both endpoint memberships before origin lookup. Test null → port, X → Y, and replacement by a new thing at the same cell.

5. **MAJOR — A tick key does not prevent stale topology within that tick.**  
   **Evidence:** `CompHoseReel.cs:111-126` deregisters and stows on despawn; `HoseCarry.cs:12` distinguishes carrying, laid and retracting states. Tank acceptance checks only contents/capacity (`Building_LiquidTank.cs:52-63`), not whether a cached route still exists.  
   **Impact:** After one machine builds the cache, another same-tick operation can wind a hose or remove a conductor. A later transfer can still use the cached route. Rechecking `CanAccept` does not solve this.  
   **Fix:** Add invalidation for known hose mutations and validate cached route liveness before transfer. Specify map/load lifetime and cache eviction. Test removal, winding and master-switch changes between two same-tick calls.

6. **MAJOR — Laid state alone permits flow through a failed, invisible hose.**  
   **Evidence:** `RM_MapComponent_Hoses.cs:202-205` stores a failed lay as null without changing carry state; `:289-307` repairs or retracts only on the 250-tick check, sometimes clearing the trail and waiting another interval.  
   **Impact:** §4.1’s eligibility predicate requires state and ports, but no valid lay. Such a hose can transfer liquid while its geometry is refused.  
   **Fix:** Require a successfully validated lay before activating a link, and deactivate immediately when validation fails. Explicitly resolve `Dropped` eligibility: the existing `laid` flag includes dropped hoses, while v2 names only `Laid`.

7. **MAJOR — Port kind does not distinguish native conductors from visual third-party couplings.**  
   **Evidence:** `HosePorts.cs:55-65` classifies VE/DBH objects as `Pipe` or `Tank`; §4.1 traverses those same kinds as native net members. Existing native traversal recognises its own extension (`FlowWorks/Source/Machinery/RM_LiquidNet.cs:26-38`).  
   **Impact:** Enqueuing a third-party pipe’s cells can bridge neighbouring native pipe runs, contradicting “visual only.” Third-party tanks also cannot be added as `Building_LiquidTank`.  
   **Fix:** Separate visual port classification from native hydraulic eligibility. Only native pipes conduct, native tanks store, and adapters act as machine origins. Test an external pipe between two native runs.

8. **MAJOR — Credit wiring must cover 11 mutation sites, not the cited lookup sites.**  
   **Evidence:** Actual mutations are pump `Building_LiquidPump.cs:152,169,231`; converter `CompLiquidConverter.cs:219,223`; adapter `CompLiquidPipeAdapter.cs:135-139,153-156`; reactor `RM_LiquidReaction.cs:184-185,191`; bath `RM_LiquidBath.cs:148`.  
   **Impact:** §4.2 cites converter/reactor selection ranges and bath `:94`, which only searches. Crediting one leg per machine misses converter input/output or reactor A/B/output routes. Emptying a tank also clears its liquid identity (`Building_LiquidTank.cs:100-104`).  
   **Fix:** Enumerate every successful mutation explicitly; capture identities before removal. Credit each tank leg separately, and never credit item output, venting, terrain-backed baths or unsuccessful operations.

9. **MAJOR — NetFlow’s false result masks the debug provider.**  
   **Evidence:** `HoseFlow.cs:121-125` returns the first non-null result, including false.  
   **Impact:** §4.3 puts NetFlow first and describes it as returning `PumpFlowing(...)`. An inactive stamp therefore prevents debug flow and debug relay propagation entirely.  
   **Fix:** Return null from inactive NetFlow, or explicitly combine real and debug signals. Test a never-credited reel with debug enabled and a multi-hop debug chain.

10. **MAJOR — The collapse deadline is incompatible with unchanged hysteresis.**  
    **Evidence:** `HoseMath.cs:1226-1227` keeps a pump stamp active for 375 ticks; `:52,63-68` measures release from the last **true signal**, then drains over the transition.  
    **Impact:** With shipped defaults, a final credit at tick 0 yields Draining at 875 and Flat at 905—not within `releaseTicks = 500`, as §§4.2/5.7 promise. Minimum plump dwell can extend this further.  
    **Fix:** Either revise the deadline and proof rows to include stamp lifetime, dwell and transition, or deliberately change timing semantics. Test shutdown immediately after a successful credit.

11. **MAJOR — Last-writer stamps are not sufficient for shared hoses.**  
    **Evidence:** Converter and reactor cycles already transfer multiple liquids (`CompLiquidConverter.cs:218-223`; `RM_LiquidReaction.cs:184-191`). §4.2 overwrites one cadence/liquid stamp on every credit.  
    **Impact:** A later short-cadence credit can shorten an earlier still-valid flow window; caller order determines the liquid observed by tint dwell.  
    **Fix:** Specify monotonic flow expiry and deterministic handling of all credits received during a tick. Define “continuous” tint credit across discrete cycles. Test reversed caller order and mixed pump/bath cadences.

12. **MAJOR — Saving `lastLiquid` does not preserve the displayed tint.**  
    **Evidence:** Existing visual state is saved at `CompHoseReel.cs:136-140`. §4.4 deliberately allows `tintLiquid != lastLiquid` during dwell, but saves only `lastLiquid`.  
    **Impact:** Save while liquid B is pending and the hose still displays A; loading cannot reconstruct A. §5.2 additionally says Tint reads `lastLiquid`, contradicting §4.4.  
    **Fix:** Save the displayed tint identity separately. Specify pending-dwell load behaviour and initialise tint explicitly on first credit. Test saving during an unfinished colour switch.

13. **MAJOR — New stamps need lifecycle resets.**  
    **Evidence:** `CompHoseReel.cs:111-126` resets the existing state machine on despawn; `:533-548` stows and resets in `ReelIn()`. The move proposes adding stamps while leaving these behaviours unchanged.  
    **Impact:** A recently credited hose can be stowed and redeployed onto an unrelated route, then refill visually from its old stamp without a new transfer.  
    **Fix:** Clear flow leases on pickup, stowing, despawn and redeployment; define tint retention separately. Test redeployment before the previous stamp expires.

14. **MAJOR — Pour mode can starve a usable liquid behind an unusable first tank.**  
    **Evidence:** `Building_LiquidPump.cs:184-191` selects the first canal-capable tank before searching destinations; `:211-228` then rejects incompatible/full destinations without trying another tank.  
    **Impact:** Water first, tar second, and only a tar-filled channel with room: nothing pours. Larger multi-liquid hose nets make this common.  
    **Fix:** Select a feasible tank/destination pair, continuing to later tanks when no destination accepts the first liquid. Add that exact two-liquid case.

15. **MAJOR — Converter selection can permanently starve later viable inputs.**  
    **Evidence:** `CompLiquidConverter.cs:206-217` returns when the first eligible input cannot produce a batch.  
    **Impact:** A nearby salt-water tank holding one unit blocks a farther tank holding enough for its two-unit batch. A blocked output likewise prevents consideration of another convertible liquid.  
    **Fix:** Continue searching viable inputs; retain a diagnostic only if none can run. Test insufficient first input and blocked first product on a shared net.

16. **MAJOR — Bath completion can succeed without paying its liquid cost.**  
    **Evidence:** `RM_LiquidBath.cs:106-113` checks availability beforehand; `:145-148` searches again at completion and silently does nothing if the source is gone. No stock reservation is retained.  
    **Impact:** Disconnect the hose or drain the tank during crafting: the completed iteration consumes no liquid. Real hose splitting exposes this existing defect.  
    **Fix:** Secure the required units for the craft, with defined cancellation/refund behaviour, or make completion conditional on a successful debit. Test disconnect and competing consumption mid-craft.

17. **MAJOR — Existing relay discovery defeats the claimed constant-cost endpoint resolution.**  
    **Evidence:** `RM_MapComponent_Hoses.cs:130-164` repeatedly builds ordered reel lists through `RelayAt`, `FeedersOf` and `Loops`; even a cached lay computes `FeedersOf(r)` in its key at `:193`.  
    **Impact:** Moving these calls unchanged into link refresh leaves nested scans/sorts over all reels. A dictionary lookup does not make the complete operation O(1).  
    **Fix:** Build relay adjacency once per refresh and reuse it for flow, drawing and loop checks. Profile those production paths, including `World()`’s whole-map snapshot (`:49-73`), rather than only the proposed net model.

18. **MAJOR — The offline “model” does not prove the production graph.**  
    **Evidence:** Production traversal is Verse-bound (`RM_LiquidNet.cs:1-3,46-113`); §5.6 proposes a separate Verse-free model rather than a shared production kernel.  
    **Impact:** The model can pass while real classification, indexing, eligibility or credit placement remains wrong. The listed tests also omit most converter/reactor/adapter/bath transfer cases above.  
    **Fix:** Extract the production traversal, routing, cache and stamp rules into the tested pure kernel. Add Python checks for XML/runtime binding and caller coverage; include mixed liquids, endpoint non-merging, ring termination and all four pipe/hose switch combinations.

19. **MAJOR — The move manifest misses embedded resource and class paths.**  
    **Evidence:** `CompHoseReel.cs:91-93` hard-codes three GSS texture paths; `GimmeSomeSlack/Defs/Hose/RM_HoseReelStyles.xml:16,28,40,52` hard-codes the old graphic class.  
    **Impact:** Moving textures plus changing `HoseStyles.Root` leaves gizmo icons unresolved. “texPaths only” for style defs leaves old runtime class names.  
    **Fix:** Include these replacements explicitly and scan every moved source/XML string. Validate all texture and class references with GSS absent.

20. **MINOR — The save whitelist names the wrong job-driver namespace.**  
    **Evidence:** `RM_HoseJobs.xml:9,18` and `Jobs/JobDriver_CarryHoseEnd.cs:7` place drivers under `.Hose.Jobs.`  
    **Impact:** §§5.7/6 describe or allow `.Hose.JobDriver_*`; that whitelist rejects legitimate mid-job saves. The broad type-alias prefix itself still works.  
    **Fix:** Use the two exact `.Hose.Jobs.JobDriver_*` names, including both legacy prefixes in fixtures.

21. **MINOR — The promised settings screen still omits a user-facing timing control.**  
    **Evidence:** `HoseSettings.cs:127-139` exposes transition/release but no minimum dwell; `:212-214` explicitly identifies `minPlumpDwell` as lacking a control.  
    **Impact:** v2 counts it as user-facing and newly uses it for tint switching, while retaining the omission.  
    **Fix:** Add the dwell control and its toggle/value proof row; keep only migration fields internal.

22. **MINOR — Station reach needs a defined geometry test.**  
    **Evidence:** `Building_LiquidPump.cs:73-79` uses a radius around `Position` of `reach + rect.Width / 2`; `RM_PumpingStation.xml:91-92,132-133` specifies reach 4 for a 3×2 station.  
    **Impact:** The implementation uses a 5.5-cell position-centred search, rather than an explicit four-cell distance from the footprint. The proposed tests do not pin this asymmetry.  
    **Fix:** State whether the current approximation is intentional; otherwise measure distance from the occupied rectangle. Test each side and corner.

## Design claims verified

- `RM_LiquidNet` currently conducts cardinal pipe cells, treats tanks as endpoints, has a 1,500-cell cap and no cache (`RM_LiquidNet.cs:14-24,79-110`).
- `TankToFill` rechecks acceptance and prefers an already populated compatible tank; topology-only caching must preserve this (`:117-131`).
- Pump cycles are 250 ticks; each successful level represents five tank units. Stations request two/four levels, stopping early when no transfer succeeds (`Building_LiquidPump.cs:90-102`; `RM_PumpMath.cs:7,11`).
- Reel-side selection chooses one edge-sharing neighbour; relays are discovered separately (`HosePorts.cs:85-110`; `RM_MapComponent_Hoses.cs:130-146`).
- Saved reel state uses the listed `rmHose*` keys; the existing map component has a save-skip patch (`CompHoseReel.cs:131-155`; `RM_MapComponent_Hoses.cs:1036-1065`).
- `RM_UniversalCargoTank` uses the same single-liquid tank class and is minifiable (`RM_LiquidLogistics.xml:69-90`).
- Registry tint is real: FreshWater and Tar have distinct colours; the old tint-table comment is stale (`RM_LiquidDefRegistry.xml:27-33`; `HoseMath.cs:1363-1380`).
- Existing converter/reactor code supports different liquids in different tanks on one net; pipes have no stored liquid identity.
- The alias’s prefix-plus-suffix mapping accommodates the actual `.Jobs.` namespace.

## Outside this slice

- Engine implementation of Scribe/class resolution, def aliases, Harmony ordering and cross-mod duplicate-def replacement.
- GSS migration/style-picker/core files, shared-source accessibility, csproj wiring, FlowWorks patch application and main settings-window integration.
- Actual settings filenames/import implementation, About.xml ordering and mixed-version startup detection.
- Existing SelfTest counts, proof manifests, validation scripts, texture existence and art-ledger operations.
- Excavation/stock internals: conservation, source identity, debit/pour failure semantics and actual natural-body support.
- Third-party adapter API behaviour and adapter defs. Native pumps require a `canalFluid`; several visible registry rows lack one, so optional nozzle support for every registered liquid cannot be established here.
- Any additional `TanksFor`/`TankToFill` callers in the other consult slices, and measured runtime performance.