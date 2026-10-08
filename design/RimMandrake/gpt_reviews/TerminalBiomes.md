## 1. DEBUGGING

Reviewed the inlined bundle only. Line numbers start at each file’s first displayed line. No compilation, validation script, or game execution was performed. Omitted XML, dependency implementations, previous versions, and save fixtures are **UNVERIFIABLE**.

1. **The wax timer forgets that a sheet is overdue.**  
   `Source/Kernel/RM_TerminalMiscKernel.cs:21`  
   While moving, an expired countdown becomes negative. The next call treats that negative value as “uninitialized” and resets it to the full period. A colony that does not pause immediately around expiry can postpone extrusion for another 90,000 ticks. **Minimal fix:** reserve `-1` exclusively for initialization and clamp an overdue countdown to zero while moving.  
   **Severity: high. Confidence: high.**

2. **Sun-sphere growth reverses suulk feeding damage.**  
   `Source/RM_Building_SunSphere.cs:98`  
   `RecomputeVisual()` derives radius entirely from culture state every 60 ticks. Feeding subtracts from that same radius. A mature sphere reduced from 6 to 5.85 is restored to 6 on the next culture update, preventing cumulative grazing with the default feed loss. **Minimal fix:** store grazing damage separately and combine it with the culture radius in one visual calculation.  
   **Severity: high. Confidence: high.**

3. **Disabling hull crystallisation does not unlock salted doors.**  
   `Source/RM_GreyHullCrust.cs:61`  
   `IsSalted()` ignores `RM_GreyCrust.Active`; the door-opening postfix uses that ungated result. Turning off the mechanic, Grey Sea, or master switch therefore leaves existing doors locked despite the settings promise. **Minimal fix:** gate the opening restriction with `Active`, retaining the stored salt state for re-enabling. Clear affected reachability caches when effective activation changes.  
   **Severity: high. Confidence: high.**

4. **A current component can move a thing that has transferred to another map.**  
   `Source/RM_MapComponent_ChannelCurrent.cs:350`  
   Registered occupants are checked for `Spawned`, but not `t.Map == map`. A thing transferred between registration scans can remain in the old map’s book while spawned on the destination map. Its movement and sink outcome are then calculated using the old map. **Minimal fix:** remove any occupant whose map differs before processing it.  
   **Severity: high. Confidence: high.**

5. **Sink arrival is not terminal.**  
   `Source/RM_MapComponent_ChannelCurrent.cs:305`, `:503`  
   Sink occupants can be registered again if their cells retain current. The generator does not clear current throughout the basin. Consequently, deposited items can keep moving and pawns can receive repeated sink arrivals and messages. `AddHediff()` is called without checking for an existing Sunk hediff; its precise duplicate-handling outcome is **UNVERIFIABLE**. **Minimal fix:** exclude sink cells from ordinary registration and stepping, and make Sunk application idempotent.  
   **Severity: high. Confidence: high.**

6. **Sink placement can deposit cargo outside the sink or return an occupied, blocked cell.**  
   `Source/RM_MapComponent_ChannelCurrent.cs:545`  
   The radial search does not require `IsSinkCell(c)`, so it can return a cell outside the basin. A cargo float deposited there will not detect sink arrival. If the search fails, the unconditional `return centre` bypasses both standability and pawn occupancy checks. **Minimal fix:** search valid sink cells exclusively; handle placement failure explicitly instead of returning an unchecked cell.  
   **Severity: high. Confidence: high.**

7. **Ford and weir safety checks become stale between scans.**  
   `Source/RM_MapComponent_ChannelCurrent.cs:375`  
   `StepOne()` does not recheck `IsExempt(t)` or whether the current position is arrested. A registered pawn that walks onto a ford or weir can be moved off it before the next 250-tick scan. Checking arrest only after movement does not protect the starting cell. **Minimal fix:** recheck exemptions, arrest, and map ownership immediately before each movement.  
   **Severity: high. Confidence: high.**

8. **Current entry can be missed entirely; the centre is not reliably inescapable.**  
   `Source/RM_MapComponent_ChannelCurrent.cs:126`, `:343`  
   A pawn must still occupy current during a registration scan, then wait another cadence before its first push. Crossing between scans produces neither drift nor warning. After registration, there is also no restriction preventing the pawn from walking out before its scheduled push. **Minimal fix:** detect entry at movement time, or use a sufficiently frequent local pawn check; explicitly implement the centre’s movement restriction if “inescapable” remains the intended rule.  
   **Severity: high. Confidence: high.**

9. **The 15-tick processor substantially changes the kernel’s advertised speeds.**  
   `Source/RM_MapComponent_ChannelCurrent.cs:127`, `:398`  
   Actual intervals become approximately `ceil(cadence / 15) * 15`, because each step rearms from the processing tick. A surge-centre pawn’s kernel cadence is 22 ticks, but movement occurs every 30. An item’s 44 becomes 45, so items no longer drift at half the pawn rate. Higher strength values also collapse onto identical effective speeds. **Minimal fix:** preserve accumulated time with `due += cadence`, or process frequently enough to honour the minimum supported cadence.  
   **Severity: medium. Confidence: high.**

10. **The surge grab can cross an intervening wall and bypass arrest.**  
    `Source/RM_MapComponent_ChannelCurrent.cs:224`, `:240`  
    The two-cell grab tests its destination, not its intermediate cell. It also omits source-cell arrest and activation checks. Thus it can move a pawn through a blocked intermediate cell, pull someone from an arrester, and act when `BeginSurge()` is called while current is disabled. **Minimal fix:** validate both steps and source arrest, and gate the grab with effective activation.  
    **Severity: high. Confidence: high.**

11. **Channel and bank markers can overlap, producing the wrong surge grab direction.**  
    `Source/Kernel/RM_ChannelKernel.cs:33`, `:41`  
    `SetFlow()` leaves an old bank band intact; `SetBankBand()` sets a band even when the cell already has a lane. Overlapping channel authoring can therefore leave a channel cell marked as bank. The grab then follows its downstream flow rather than pulling inward from the bank. **Minimal fix:** clear `Band` when assigning a channel lane, and reject bank-band assignment on channel cells.  
    **Severity: medium. Confidence: high.**

12. **Current processing incurs full-map costs on maps with no channels.**  
    `Source/RM_MapComponent_ChannelCurrent.cs:271`, `:305`  
    With default settings, every attached map allocates three map-sized arrays and repeatedly scans pawns and haulables, even with no authored current. Empty grids are also exposed for saving. **Minimal fix:** persist or derive an authored-current flag and return before allocation and scanning on inactive maps; invalidate the flag when authoring changes.  
    **Severity: medium. Confidence: high.**

13. **“Load and launch” does not launch the cargo float.**  
    `Source/RM_Thing_CargoFloat.cs:105`  
    The action only loads items from the float’s exact cell. It neither finds an adjacent current nor moves the float into it. A float prepared on the bank stays on the bank; the advertised nearby loading is also absent. **Minimal fix:** validate a launch destination and perform the push, and scan the advertised loading radius. Report a rejected launch when no destination exists.  
    **Severity: medium. Confidence: high.**

14. **Cargo transfers can orphan items, and unloading can report success with contents still held.**  
    `Source/RM_Thing_CargoFloat.cs:81`, `:117`  
    Loading despawns a thing before checking `TryAdd()` success. A failed addition leaves it unspawned and outside the container. Unloading ignores the remaining contents, clears `loaded`, and announces arrival even if placement failed. **Minimal fix:** restore failed additions to their original location; retain loaded state or an unload command until the owner is empty.  
    **Severity: high. Confidence: high.**

15. **The cargo float’s holder traversal contradicts its accepted cargo.**  
    `Source/RM_Thing_CargoFloat.cs:38`, `:115`  
    `GetChildHolders()` claims cargo cannot contain holders, but the loading predicate accepts other floats and minified containers. Holder traversal therefore omits nested contents. **Minimal fix:** enumerate child holders from the container using the engine’s holder utility, or explicitly reject holder cargo. The resulting engine-specific traversal failures are **UNVERIFIABLE**, but the inconsistency is explicit.  
    **Severity: medium. Confidence: high.**

16. **Several lamps can dispatch the same giant, permanently abandoning earlier targets.**  
    `Source/RM_GreyLampResponse.cs:188`, `:216`  
    Giant selection does not exclude a giant already breaking another lamp. Within one advance, each subsequent lamp can replace its job. All those lamps are nevertheless latched as Answered. Other job interruptions have the same problem: dispatch is treated as completed response. **Minimal fix:** reserve a giant per target and distinguish assigned, completed, and failed responses; retry failed assignments while the lamp remains eligible.  
    **Severity: high. Confidence: high.**

17. **An unreachable lamp is marked answered permanently.**  
    `Source/RM_GreyLampResponse.cs:214`  
    Returning `true` after finding the lamp unreachable causes the kernel to add its Answered latch. Opening the hull later will not trigger a response until the lamp’s burn cycle resets. **Minimal fix:** return failure for unreachable targets, with a retry cooldown to avoid repeated walk-ins.  
    **Severity: medium. Confidence: high.**

18. **Disabling both lamp responses leaves stale latches behind.**  
    `Source/RM_GreyLampResponse.cs:70`  
    Only `Lit` is cleared. Watched, Scraped, and Answered survive. Kernel cleanup discovers vanished lamps through `Lit.Keys`, so after that dictionary is cleared it cannot remove those stale entries. Re-enabling may suppress warnings or giant responses indefinitely. **Minimal fix:** reset the entire burn book together.  
    **Severity: medium. Confidence: high.**

19. **Watcher warnings can be consumed before a watcher is successfully ordered.**  
    `Source/RM_GreyLampResponse.cs:120`  
    `watched.Add()` precedes the shared cooldown, current-job check, and rim-cell search. If any prevents ordering, later retries have `first == false`, so the player never receives that lamp’s first warning. **Minimal fix:** separate “walk-in attempted” from “warning delivered,” and latch the warning only after successful ordering.  
    **Severity: medium. Confidence: high.**

20. **Continuous burn is sampled, not tracked.**  
    `Source/RM_GreyLampResponse.cs:58`, `:76`  
    A power loss or dowsing entirely between 250-tick samples is invisible. Newly lit lamps can also receive a full interval immediately. The settings promise that switching a lamp off “at any point” completely resets it is therefore false. **Minimal fix:** observe glow-state transitions and reset immediately, or describe the sampling tolerance honestly.  
    **Severity: medium. Confidence: high.**

21. **Settings do not stop already-running destructive jobs.**  
    `Source/RM_GreyLampResponse.cs:216`; `Source/RM_JobDriver_FeedOnGlow.cs:1` — `MakeNewToils()`  
    Activation gates prevent job assignment, but FeedOnGlow and BreakGlow do not fail when their effective setting becomes false. A suulk continues eating, and a reefback can still destroy its lamp after the owner switches the mechanic off. **Minimal fix:** add the effective setting to each job’s fail conditions, and let existing cleanup handle departure.  
    **Severity: medium. Confidence: high.**

22. **Lid-dark dimming is overwritten by normal well updates and is not persisted.**  
    `Source/RM_MapComponent_WellLedger.cs:226`, `:314`  
    Dimming writes radius once. Subsequent Opening/Waning updates restore the ordinary radius. New wells also do not inherit darkness, and no ledger field records that dimming is active. **Minimal fix:** Scribe a dimming state and incorporate it into every visual calculation, including opening and post-load restoration.  
    **Severity: high. Confidence: high.**

23. **The gardener cannot advance pending openings when all wells are closed.**  
    `Source/Kernel/RM_WellKernel.cs:154`; `Source/RM_MapComponent_WellLedger.cs:288`  
    Both layers return when there are zero wells, making the pending-opening branch unreachable precisely when the map is entirely dark. **Minimal fix:** remove both empty-well guards and allow the pending branch to run independently.  
    **Severity: medium. Confidence: high.**

24. **A well’s closure warning is attempted only once.**  
    `Source/Kernel/RM_WellKernel.cs:123`  
    If nobody owns anything nearby at the exact transition into Waning, `warn()` returns false and is never retried. A player who subsequently establishes work around that waning well gets no warning. **Minimal fix:** retry during Waning while `warningLetterFired` is false.  
    **Severity: medium. Confidence: high.**

25. **The final waning colour step is unreachable.**  
    `Source/Kernel/RM_WellKernel.cs:36`, `:46`, `:65`  
    While a well remains Waning, remaining lifetime is positive, so the step is at most 2. Step 3 coincides with Closed, when the skylight is destroyed. The well therefore never reaches the stated cool-dead colour; it disappears from a factor of at least 0.6. **Minimal fix:** define the intended visible steps explicitly and map the final live interval to the final colour.  
    **Severity: medium. Confidence: high.**

26. **Frozen cadence does not freeze external aging.**  
    `Source/RM_MapComponent_WellLedger.cs:138`, `:288`, `:299`  
    Frozen mode affects the ordinary ticker only. Gardener advancement can still close wells and lid-dark ending still adds age. **Minimal fix:** apply the frozen rule to external aging hooks too, or change the setting description to distinguish ordinary aging from event-driven aging.  
    **Severity: medium. Confidence: high.**

27. **Crop transport destroys plant state beyond def and growth.**  
    `Source/RM_CompCageCropSnapshot.cs:98`, `:127`  
    Uninstall destroys the original plant and reinstall constructs a fresh one. Health, age, and any other persisted plant state are lost; damaged plants are recreated fresh. World-space offsets also are not transformed for a changed cage rotation. Whether shipped cages permit rotation is **UNVERIFIABLE** because their XML is omitted. **Minimal fix:** preserve the actual plants in a holder, or serialize the required state and cage-local coordinates.  
    **Severity: medium. Confidence: high.**

28. **Cryoponics patches affect any plant placed inside the vat.**  
    `Source/RM_Patch_ChillGrowers.cs:25`, `:55`, `:68`  
    No patch checks the plant’s sow tag or intended cryogenic eligibility. Temperature growth is forced to 1, and terrain-tag death is suppressed, for unrelated plants another mod permits there. The terrain exception also remains for cryoponics vats when their bath is inactive. **Minimal fix:** restrict exceptions to eligible Chill plants; retain the floor-bed exception separately and require an active bath for the vat exception.  
    **Severity: medium. Confidence: high.**

29. **Pane-strike frequency changes harmless litter, not lethal strikes.**  
    `Source/RM_TerminalBiomesMod.cs:125`  
    The only supplied gameplay read of `twilightPaneStrikeFrequency` is the light-shed probability. The pane incident worker does not read it. The “Pane strikes / Frequency” control therefore misrepresents its effect. **Minimal fix:** connect the multiplier to actual strike scheduling, or relabel it “background flake frequency” and expose strike frequency separately.  
    **Severity: medium. Confidence: high.**

30. **Suulk pressure scaling ignores its switch and counts the wrong things.**  
    `Source/RM_TerminalBiomesMod.cs:178`; `Source/RM_IncidentWorker_SuulkArrival.cs:45`, `:82`  
    Scaling is unconditional. The count includes stationary and unlit player glowers; it does not use the ledger’s mobile-glower query. Turning off constellation scaling changes nothing. The multiplier also saturates: at four glowers, 1× already produces probability 1, so 3× cannot increase it. **Minimal fix:** use one shared count, honour the scaling switch, and apply the frequency multiplier to scheduling rather than a capped eligibility probability.  
    **Severity: medium. Confidence: high.**

31. **Other visible settings have no supplied gameplay consumer.**  
    `Source/RM_TerminalBiomesMod.cs:177`, `:181`  
    `twilightChainAvailability` and `twilightChartsAgeEnabled` are persisted and exposed, but no supplied implementation reads them for restocking or chart aging. Consumers in omitted/dependency code are **UNVERIFIABLE**. **Minimal fix:** connect each control to its mechanic, or disable it with an explicit “not implemented” explanation.  
    **Severity: medium. Confidence: high for this bundle.**

32. **Cage passability changes omit explicit map-cache invalidation.**  
    `Source/RM_TerminalBiomesMod.cs:179` — `RM_TwilightPassabilityApplier.Apply()`  
    The applier mutates shared `ThingDef.passability` from settings-window frames without notifying existing maps. The promised region rebuild is not initiated anywhere in the supplied code. Exact cache behaviour is **UNVERIFIABLE**. **Minimal fix:** apply only on a value transition and explicitly invalidate affected path, region, and reachability data; expose the same apply path to non-UI settings setters.  
    **Severity: medium. Confidence: medium.**

33. **The mobile-light interval is much longer than its justification claims.**  
    `Source/RM_CompGlowerMobile.cs:63`  
    At the 60-ticks-per-second convention used elsewhere in this bundle, 250 ticks is approximately 4.17 seconds, not a quarter-second. A moving light can remain registered several cells behind its owner, affecting both crops and glow-seeking behaviour. **Minimal fix:** use a shorter movement check or movement notification, with an explicit cost/accuracy target.  
    **Severity: medium. Confidence: high.**

34. **The lure’s long-tick proximity check can miss an entire approach.**  
    `Source/RM_Comp_VaeuliskLure.cs:67`  
    A pawn can enter and leave the 1.9-cell radius between checks. Thus proximity sampling is not equivalent to detecting harvest-job start, contrary to the comment. The exact engine Long interval is **UNVERIFIABLE** here. **Minimal fix:** add a direct interaction/harvest trigger and use a more frequent spatial proximity mechanism for passing pawns.  
    **Severity: medium. Confidence: high.**

35. **Hatch exclusion is not enforced throughout channel generation.**  
    `Source/RM_GenStep_TwilightChannels.cs:68`, `:80`, `:81`  
    Only `AuthorChannel()` receives the exclusion list. Basin painting and weir placement do not; stake placement also lacks an exclusion test. A basin can overlap an existing hatch exclusion even when channel authoring skipped it. Whether the hatch exists before this genstep runs is **UNVERIFIABLE**, making the wider landing guarantee unproven. **Minimal fix:** validate the basin and every dressing footprint against the same exclusion geometry.  
    **Severity: high. Confidence: high for the missing checks.**

36. **Crust cannot jacket the whole footprint as advertised.**  
    `Source/Kernel/RM_CrustKernel.cs:31`  
    The cap is `hullCells / 3`, not the whole hull. Growth adds at most one patch per check, independently of ship size, so “whole hull by a quadrum” also deteriorates as hull size increases. **Minimal fix:** either implement the stated coverage target with size-normalized spawning, or describe the actual one-third cap and size-dependent timescale in settings.  
    **Severity: medium. Confidence: high.**

37. **The scatter patch’s static call state is unsafe under reentrancy or concurrency.**  
    `Source/RM_Patch_ScatterThingsClusterCenterGuard.cs:67`  
    An inner call can consume the outer call’s saved cluster size and restore it onto the wrong instance. The finalizer uses the same shared state. This does not require multithreading; nested calls suffice. Whether vanilla causes nesting is **UNVERIFIABLE**, but other patches can. **Minimal fix:** use per-invocation Harmony `__state`; avoid temporarily mutating shared genstep configuration if concurrent generation is supported.  
    **Severity: high. Confidence: high for the failure mechanism.**

38. **The scatter postfix can override another patch’s refusal.**  
    `Source/RM_Patch_ScatterThingsClusterCenterGuard.cs:90`, `:124`  
    It checks only `result.IsValid`, then unconditionally writes `__result = true`. A prior postfix can legitimately reject a valid cell; this patch reverses that rejection. It also affects every clustered scatter genstep, not just this mod’s failing scatter. **Minimal fix:** preserve a false result, verify bounds, and scope the workaround to the required scatter definitions.  
    **Severity: medium. Confidence: high.**

39. **Scald introduces a separate protection kind despite the campaign’s “one kind of heat” rule.**  
    `Defs/DamageDefs/RUT_Scald.xml:37`, `:42`  
    The def explicitly excludes ordinary heat protection and uses `RM_ScaldArmor`; steam exposure separately names `RM_ScaldProtection`. This creates a distinct defensive channel. Actual damage-worker treatment is **UNVERIFIABLE**, but the authored protection contract conflicts with the project fact. **Minimal fix:** use the campaign’s shared heat protection category/stat while retaining the wet-burn presentation and non-igniting worker.  
    **Severity: high. Confidence: high for the rule conflict.**

40. **Validation overwrites the owner’s settings with shipped defaults.**  
    `validation.py:504`, `:514`, `:518`  
    Each flip restores `default`, not the value present before testing. A successful validation run therefore changes customized preferences. The final chain deliberately verifies this unwanted state. **Minimal fix:** snapshot all original values before mutation, restore them in a suite-level `finally`, and verify restoration against that snapshot.  
    **Severity: high. Confidence: high.**

41. **The settings “round trip” does not test Scribe persistence.**  
    `validation.py:504`  
    The test writes and reads live fields through the bridge. It never saves, recreates the settings object, or reloads. A missing Scribe call or incorrect default can pass. **Minimal fix:** add serialization/reload tests for settings and representative gameplay state; retain bridge flips as a separate mutation test.  
    **Severity: high. Confidence: high.**

42. **The offline script omits the all-seas catch check and does not exercise kernels.**  
    `validation.py:162`, `:326`  
    `sea_catch_alive_checks()` exists but is absent from the `__main__` aggregate. No kernel test is invoked by that entry point. Compile-list discovery checks only top-level `Source/*.cs`, omitting unlisted files under `Source/Kernel`. Any DLL satisfies the assembly check, including a stale one. **Minimal fix:** include the omitted check, recurse source discovery, and run a reproducible kernel compile/test step that fails on stale build output.  
    **Severity: high. Confidence: high.**

43. **Several validation helpers can hide or mishandle failures.**  
    `validation.py:128`, `:455`  
    `catch_checks()` records a malformed/missing rare table, then indexes `rare[0]`, crashing if none exists. `_ok()` accepts `{}` because it rejects only explicit `success is False`. Def-resolution checks establish presence, not correctness of required fields or references. **Minimal fix:** guard missing tables, require explicit success for contracts that provide it, and assert required resolved fields and load errors.  
    **Severity: medium. Confidence: high.**

The following are specific runtime/save checks that should not be mistaken for confirmed failures:

44. **Two ordinary refuelable siblings may not survive vanilla fueling and Scribe correctly.**  
    `Source/RM_Building_SunSphere.cs:26`  
    Identifying seed and food locally does not establish how vanilla refueling jobs, glower fuel gating, or each comp’s save keys distinguish them. Those implementations and `RM_SunSphere.xml` are omitted. **UNVERIFIABLE. Minimal fix if confirmed:** use one ordinary feed comp plus a dedicated seed mechanism, with distinct persisted state and explicit interaction routing.  
    **Potential severity: high. Confidence: medium.**

45. **Deep-Scribing a value-type crop snapshot needs an actual engine round trip.**  
    `Source/RM_CompCageCropSnapshot.cs:31`, `:50`  
    The snapshot is a struct, whereas the well implementation explicitly chooses a reference type for deep collection persistence. Whether the relevant Scribe implementation supports this struct correctly is **UNVERIFIABLE**. **Minimal risk-reduction fix:** use an exposable reference record and verify a save made while the cage is minified, including def references and nonzero offsets.  
    **Potential severity: high. Confidence: medium.**

46. **The claimed S7-off recovery path is not established by the supplied configuration.**  
    `Source/RM_TerminalBiomesMod.cs:103`; `Defs/HediffDefs/RUT_ScaldExposure.xml:1`  
    The grant condition has the S7 gate, but the exposure comp’s supplied configuration names weather and protection without a gate. Stopping future grants does not inherently stop existing exposure while steam continues. The shared comp implementation is **UNVERIFIABLE**. **Minimal fix if it lacks an effective gate:** make existing exposure use its recovery rate whenever S7 is off.  
    **Potential severity: high. Confidence: medium.**

Harmony target signatures, the two death-drop callbacks, XML inheritance/type resolution, and any Scribe key/type renames from the refactor are **UNVERIFIABLE** without the engine/dependency code, omitted defs, and previous save fixtures. The bundle does not establish a specific fatal XML load error or a duplicate installation of the same Harmony patch.

## 2. LIKELY FUTURE COMPLICATIONS

- **Ship state is being inferred from spawned map contents.** The daily salted-door prune only examines colonist buildings on loaded maps (`RM_GreyHullCrust.cs:148`). Minified, held, travelling, or ownership-changed doors can lose their salt state despite still existing. Prefer a door comp, or prune from actual destruction notifications rather than absence from map lists.

- **The crust clock belongs to the berth rather than a particular ship.** A replacement engine or visiting ship inherits the map’s accumulated `crustDays`. Returning to another map encounters another clock. Define whether neglect follows the hull, the visit, or the berth before supporting multiple ships.

- **More light controllers will fight over the same fields.** Culture, grazing, well lifecycle, darkness, mobile registration, and any breathing-glow dependency need one composition rule. Otherwise content additions will restore damage, override darkness, or strand cached light. The sun-sphere conflict already demonstrates this (`RM_Building_SunSphere.cs:98`).

- **“Never stranded” is not proven by a read-only launch postfix.** The vessel is the campaign’s only access route. Recoverability also depends on reachable clearance work, capable crew, and pane-impact collateral damage. The skyfaller’s omitted explosion and spawn configuration makes damage to nearby travel hardware **UNVERIFIABLE**. Test blocked access and incapacitated crews, not just the accepted/rejected report.

- **Performance scales with all things, not the handful of glowers.** SeekGlow scans `AllThings` and performs reachability checks; lamp watch allocates dictionaries and snapshots on synchronized 250-tick boundaries (`RM_GreyLampResponse.cs:76`). Well site search can make up to 60 × 200 predicate attempts per request (`RM_MapComponent_WellLedger.cs:184`). Large colonies and several loaded floors need indexed candidates, staggered work, and retry backoff.

- **Content additions require duplicated immunity maintenance.** `RM_ScaldWalker` is in the supplied biome roster but absent from both supplied steam immunity lists. Other immunity paths are **UNVERIFIABLE**. Replace species-name lists with a shared native/protection extension and validate that every native has the required coverage.

- **Save schema and numeric input need explicit validation.** Channel grids are adopted independently, so partially missing data can leave lanes without valid directions. Settings receive no post-load finite/range checks. Reject inconsistent grids together, validate sink bounds and enum values, and maintain old-version save fixtures.

- **Standalone and composed packaging can diverge.** About.xml retains EnvironmentalHazards as a separate dependency, while constructor comments describe it as folded. SeaShores extension types also lack a direct listed dependency; transitive coverage is **UNVERIFIABLE**. Validate both supported package arrangements, including one Harmony installation and one seam registration.

## 3. UNLEVERAGED OPPORTUNITIES

- **Make kernel regressions part of the advertised offline command.** Add deterministic cases for overdue wax while moving, empty wells with pending openings, failed warning retries, every waning boundary, and cadence rounding. Follow with adapter tests for settings-off behaviour and the sphere/grazing interaction. Pure-kernel fuzzing alone cannot detect that interaction.

- **Build a save-fixture suite around transitions.** Include a minified planted cage, differently filled seed/feed stores, a dimmed well, pending replacements, a scar-eligible Sunk pawn, loaded nested cargo, and a travelling salted door. Assert state after reload, not merely that serialization completes.

- **Replace proof hooks with controlled adapter seams.** The Grey proof methods bypass ordinary cadence and some activation/map checks. Inject deterministic clocks and randomness into test adapters, then assert dispatch, completion, failure, and off states separately. This would cover more than advancing counters and counting spawned things.

- **Turn settings into an accurate operational view.** Show effective activation, why a child option is inactive, whether changes affect existing objects or new generation, and which controls remain unimplemented. Add section resets, search, numeric entry, and a single change-application path shared by UI and automation. Avoid reapplying def mutations every rendered frame.

- **Expose useful forecasts from existing state.** Lamp burn time, next warning, well remaining lifetime, and hull clearance count already exist. Inspection lines or alerts could make these hazards assessable without adding another simulation system.

- **Use actual current membership for well siting.** `FindWellSiteCell()` checks a terrain tag (`RM_MapComponent_WellLedger.cs:184`). The current already provides authored membership, even if terrain painting failed or another mod replaced the terrain. Combining both checks cheaply closes that mismatch.

## 4. EXTENSIONS BEYOND THE MOD

- **Extract a campaign-wide light-state interface.** Other luminous plants, creatures, machinery, and predators could contribute base radius, damage, darkness, and power modifiers through one persisted calculation. This would also give AI a stable query for effective light rather than raw `GlowRadius`.

- **Share movement safety with FlowWorks.** A small common contract for map ownership, arrest, valid movement edges, and terminal destinations would let surface rivers and seabed channels use the same safety rules. Cargo should consult the same arrest query as movement rather than independently interpreting arrester comps.

- **Provide ship-attached environmental state.** Salt, deck obstruction, cargo, and future contamination belong to objects that travel through holders and maps. A reusable gravship state/clearance interface would prevent each biome from inventing its own map-scan approximation.

- **Standardize heat protection across the campaign.** Keep steam exposure, boiling-water contact, and solar heating as different delivery mechanisms while using the owner’s single heat-protection contract. Other biome mods can then reuse exposure clocks without introducing incompatible apparel currencies.

- **Reuse the validation machinery only after separating its guarantees.** Static def checks, pure simulation tests, adapter integration tests, serialization tests, and live engine checks should report distinct outcomes. A campaign-wide dashboard can then distinguish a loaded def from a working mechanic and a mutated field from a preserved save.