**1. DEBUGGING**

Static review of the supplied text only. No build, validator, Scribe round-trip, or game test was run. Line numbers count from the beginning of each inlined file. Historical “MEASURED” comments do not establish that the refactored version works.

1. **Meal metadata has no split or merge protection.**  
   `Source/CompSkillSteeredOutcome.cs:23` stores `intendedFamily` and `cookSkill`, but implements only serialization. If meals stack, different cooks’ or recipes’ products can merge without checking this metadata; splitting requires copying it onto the new comp. Steering can consequently change or disappear during hauling and ingestion. **Fix:** implement split-copy hooks and reject stacking when either field differs. The omitted meal def’s stack limit is **UNVERIFIABLE**. **Severity: high. Confidence: high for the missing safeguards; conditional on stacking.**

2. **Coating state has the same stack problem, including the permanent bonus latch.**  
   `Source/CompDeepfire.cs:21`, `:30`, `:119` provide no general split-copy or stack-compatibility hooks. The special art branch handles only an uncoated art stack’s first coat. Other stackable injected targets can receive a coat for the whole stack at one target’s cost, then lose coating or `bonusApplied` when split or merged. Losing the latch can re-enable permanent rewards. **Fix:** define per-unit coating semantics, split before charging, copy both fields, and require matching state when stacking. **Severity: high. Confidence: high; affected shipped stackable defs are UNVERIFIABLE.**

3. **Fresh-mat age is not preserved across stack operations.**  
   `Source/CompMatVitality.cs:25` has neither split-copy nor merge-age handling. A split can restart the one-day clock; merging differently aged mats leaves no specified age policy. This undermines the supply chain and its shipping constraint. **Fix:** copy age/dead state on split and either prohibit differently aged stacks or implement a conservative age rule. **Severity: high. Confidence: high; fresh-mat stack configuration is UNVERIFIABLE.**

4. **A painting target can despawn without being destroyed, then cause an NRE after pigment consumption.**  
   `Source/JobDriver_ApplyDeepfire.cs:64` checks null/destruction, but not `Spawned`, map identity, designation presence, or remaining coat capacity. A target picked up, minified, equipped, or otherwise despawned can reach `Target.Map.designationManager` at `:78` with `Map == null`. Cancelling its designation also does not stop this work toil. **Fix:** validate those conditions throughout the job and immediately before completion. **Severity: high. Confidence: high.**

5. **Job completion does not prove that payment exists or that application succeeds.**  
   `Source/JobDriver_ApplyDeepfire.cs:74` and `Source/JobDriver_LacquerWornItem.cs:55` destroy whatever is carried, then call a void `AddCoat`. The floor job follows the same pattern. No completion check establishes the carried resource’s def and required count. Conversely, a now-full target can consume pigment while `AddCoat` silently returns. **Fix:** retain the expected cost separately from mutable hauling counts; validate payment and eligibility; make application return success and handle payment/application as one operation. **Severity: high. Confidence: high.**

6. **Zero-cost settings do not produce resource-free jobs.**  
   `Source/LuminousPigmentMod.cs:302` permits zero costs, while `Source/JobDriver_LacquerWornItem.cs:133` still searches for a pigment stack and rejects the job if none exists. Thing and floor work use the same finder. Thus a free coat still requires stocked pigment, and zero enters reservation/hauling code whose behavior is not established here. **Fix:** explicitly bypass resource search, reservation, hauling, and consumption for cost zero—or disallow zero. **Severity: medium. Confidence: high.**

7. **Worn-item lacquer bypasses painting eligibility settings.**  
   `Source/JobDriver_LacquerWornItem.cs:126`, `:185` and `Source/DeepfireWornGlow.cs:40` check coat capacity but not `paintingEnabled` or the apparel/weapon class toggles. The styling checkbox likewise does not use the shared target-class check. Disabling apparel painting still permits new apparel coats through these paths. **Fix:** centralize eligibility and use it in designation, gizmo, styling, job creation, and completion. **Severity: medium. Confidence: high.**

8. **Factionless ground items are rejected by the designator.**  
   `Source/Designator_Deepfire.cs:78` requires every target’s faction to be the player. A factionless garment or weapon on the colony map therefore fails regardless of its comp and class eligibility. **Fix:** apply faction ownership requirements to buildings; use the intended loose-item eligibility policy for apparel and weapons. Exact shipped item faction behavior is **UNVERIFIABLE** from the omitted defs. **Severity: medium. Confidence: high for this rejection path.**

9. **Hediff lights survive pawn departure and can duplicate across maps.**  
   `Source/MapComponent_DeepfireLights.cs:136` registers only on the pawn’s current map. Returning early for an unspawned pawn does not remove an existing light. Registration on another map also does not remove the old map’s entry. Cleanup exists for hediff removal, but no pawn departure/death cleanup or hediff-entry sweep is shown. **Fix:** track each pawn’s owning map and remove stale entries on despawn, death, and transfer; include a cleanup backstop. **Severity: high. Confidence: high.**

10. **Hediff lights trail moving pawns and repeatedly respawn.**  
    `Source/HediffComp_DeepfireGlow.cs:68` updates every 250 ticks; `Source/MapComponent_DeepfireLights.cs:169` destroys and respawns the proxy when its cell changes. A walking pawn can leave its light many cells behind between updates. Multiple visible families multiply the spawn/despawn and glow-grid work. **Fix:** poll movement through the moving-light machinery; reserve the 250-tick check for effect changes. **Severity: medium. Confidence: high.**

11. **Worn intensity is multiplied twice.**  
    `Source/DeepfireWornGlow.cs:64` obtains “full-intensity” hues using `GlowColorFor(..., MaxCoats)`, which already multiplies by `coatIntensity[3]`. `Source/Kernel/RM_DeepfireRules.cs:187` multiplies again by the selected coat’s intensity. With tier-three intensity set to `0.5`, a white three-coat worn item becomes `0.25`, while its ground light is `0.5`. **Fix:** separate hue/value-floor conversion from coat intensity and blend unscaled hues. **Severity: medium. Confidence: high.**

12. **The darkness test subtracts a centre contribution even when the proxy is elsewhere.**  
    `Source/DeepfireWornGlow.cs:103` and `Source/Kernel/RM_DeepfireRules.cs:193` ignore proxy position when subtracting its light. The setting permits a 60-tick movement poll, and teleportation has no one-cell bound. A pawn entering another lamp’s illumination can have that lamp’s contribution incorrectly subtracted, triggering combat penalties in a lit location. **Fix:** use the actual proxy position and contribution, or synchronize the light and grid before evaluating darkness. **Severity: medium. Confidence: high.**

13. **A black light still qualifies as a glowing target.**  
    `Source/DeepfireWornGlow.cs:83` accepts the worn-light lookup without checking emitted RGB. `Source/LuminousPigmentMod.cs:297` allows a zero dark-dye value floor. Black gear can therefore have positive radius and receive penalties while emitting no light. **Fix:** require a nonzero effective emission, with an explicitly chosen visibility threshold. **Severity: medium. Confidence: high.**

14. **Clustering can leave a coated member outside its cluster light.**  
    `Source/Kernel/RM_DeepfireLightBook.cs:88` anchors on a member, choosing the first on a centroid-distance tie. In a default three-cell block, equally colored one-coat cells at `(0,0)` and `(2,2)` share a light anchored at one corner. Their separation is `2.828`; the resulting radius is only `1.5 + 1 = 2.5`. The second coated cell is outside that light. **Fix:** bound cluster radius using the farthest member’s distance plus the intended local coverage, or split groups that cannot be covered. **Severity: medium. Confidence: high.**

15. **Cuisine’s targeting overrides and heartbeat pulse are inert.**  
    `Source/HediffComp_DeepfireGlow.cs:44`, `:49` declare the fields, but no supplied implementation reads them. Darkness detection at `Source/DeepfireWornGlow.cs:83` consults only worn lights. Hair and vermilion therefore receive no authored `1.5` targeting override, and pulse-glow does not pulse. **Fix:** incorporate hediff contributions and their metadata into the pawn-light/combat model, or explicitly remove these advertised behaviors. **Severity: medium. Confidence: high.**

16. **A visual toggle suppresses a god event.**  
    `Source/HediffComp_DeepfireGlow.cs:95`, `:126` place the vermilion stage-three Ishko reaction inside the `hediffGlowEnabled` branch. Turning off light emission also prevents this independently enabled god reaction; turning emission back on can deliver it much later. **Fix:** evaluate the stage event outside the lighting branch and gate delivery through the god setting. **Severity: medium. Confidence: high.**

17. **“Buildable” permanently changes research instead of bypassing a build requirement.**  
    `Source/LuminousPigmentMod.cs:470` finishes the research project. Switching back to Research leaves it completed, and that completion also affects other consumers of the project, including the tank. Applying the setting before a game exists cannot establish completion in a subsequently created game; the press’s research prerequisite remains. Whether `research.IsFinished` itself is safe at startup is **UNVERIFIABLE**. **Fix:** alter the press’s effective construction prerequisite for this setting, preserving actual research progress. **Severity: high. Confidence: high.**

18. **Settings application misses existing nonbuilding coating lights.**  
    `Source/LuminousPigmentMod.cs:523` invokes the clustering rebuild, which re-registers floors and buildings. Ground apparel, weapons, and other nonbuilding own-light entries are not refreshed. Their radius, intensity, and value floor remain stale until another notification. **Fix:** refresh all registered coating owners after relevant settings change; refresh worn entries at the same time. **Severity: medium. Confidence: high.**

19. **The stockpile-glow toggle changes properties without refreshing existing glowers.**  
    `Source/LuminousPigmentMod.cs:499` edits `CompProperties_Glower.glowRadius`, but does not update existing pigment stacks or re-register their lights. The mod’s own proxy code explicitly calls `ForceRegister` after lighting changes. Existing-grid behavior after a properties-only mutation is **UNVERIFIABLE** without the engine, so the claimed live behavior is not established. **Fix:** explicitly refresh existing resource glowers on affected maps. **Severity: medium. Confidence: medium.**

20. **Coat changes do not explicitly invalidate cached stats.**  
    `Source/CompDeepfire.cs:130`, `:149` change coating state and lighting, but do not clear Beauty or wearer combat-stat caches. The worn debug proof itself acknowledges that stripping and rereading MeleeDodgeChance requires cache clearing. Floor changes notify room stats; the Thing path has no equivalent explicit invalidation. **Fix:** invalidate affected thing/wearer stats and relevant room caches on coating and settings changes. Exact cache duration and incidental invalidation through proxy spawning are **UNVERIFIABLE**. **Severity: medium. Confidence: medium.**

21. **The documented first-sow seed consumption is missing.**  
    `Source/Building_GlowTank.cs:44` gates sowing on fuel; the only shown consumption is blackout handling. With the XML’s zero fuel-consumption rate, no supplied code consumes the seed on a successful sow. Simply adding consumption would then block the remaining cells and future sowing. **Fix:** introduce a scribed established-culture state, consume the starter on successful establishment, and clear establishment on blackout. **Severity: medium. Confidence: high.**

22. **Discovery can be missed permanently after harvesting.**  
    `Source/CompMatDiscovery.cs:30` checks only on long ticks. A mat harvested or destroyed before its next check cannot discover itself afterward. If all nearby mats are removed, possessing fresh mats does not unlock refining. **Fix:** share discovery logic with an appropriate harvest/interaction notification, or schedule the promised faster map-level check. **Severity: medium. Confidence: high.**

23. **Discovery does not actually require a colonist to see the mat.**  
    `Source/CompMatDiscovery.cs:48`, `:50` include prisoners and test only distance to an unfogged cell. A prisoner behind a wall can unlock research. **Fix:** restrict the eligible pawn population and add line-of-sight/visibility checks if “seen” is the requirement. **Severity: medium. Confidence: high.**

24. **Mat replacement ignores insertion failures and leaves the old held Thing alive.**  
    `Source/CompMatVitality.cs:80`, `:87` ignore placement/addition results. The held branch removes the fresh parent without destroying it, then returns even if adding the dead replacement fails. The spawned branch destroys the original before establishing successful placement. **Fix:** implement replacement with failure handling and rollback/drop behavior; destroy the detached original after successful replacement. **Severity: medium. Confidence: high.**

25. **“Diminishing” can increase a reaction.**  
    `Source/Kernel/RM_DeepfireRules.cs:140` replaces every nonzero magnitude with `1` after the threshold. Valid sliders can set a reaction to `0.25`, which subsequently becomes `1`. The standalone function also maps zero to `-1`, although the current caller skips zero. **Fix:** preserve zero and use `sign(amount) * Min(Abs(amount), magnitude)`. **Severity: medium. Confidence: high.**

26. **Every Ideology specialist is classified as titled.**  
    `Source/SumptuaryEngine.cs:96` accepts any role, while its stated rule identifies leader/moral-guide roles. Production specialists consequently receive titled privilege, bedroom rewards, and above-station judgments. **Fix:** explicitly classify qualifying roles, preferably through a configurable role policy. **Severity: medium. Confidence: high.**

27. **Queued styling jobs can all bind to the same insufficient stack.**  
    `Source/JobDriver_LacquerWornItem.cs:133` chooses a concrete stack while `StylingStationLacquer.Apply` builds every queued job. There is no allocation across those jobs. With two three-unit stacks and two three-unit coats, both jobs can select the nearest stack; consuming it leaves the second job targeting a depleted/destroyed source despite sufficient remaining pigment. **Fix:** allocate quantities across queued jobs or resolve the resource when each job starts. **Severity: medium. Confidence: high.**

28. **Several implemented settings have no controls.**  
    `Source/LuminousPigmentMod.cs:44`, `:46`, `:53` declare and serialize research cost, press work amount, tank grow days, tank yield, and tank power, but `DoWindowContents` exposes none of them. These values are read; they are inaccessible through the promised settings interface. **Fix:** add controls with units, bounds, and reset defaults. **Severity: low. Confidence: high.**

29. **Family settings discard all saved selections when array length changes.**  
    `Source/LuminousPigmentMod.cs:196` accepts the saved list only when its length exactly matches the current array. Adding a family loses every old toggle; reordering families silently transfers toggles to different families. **Fix:** serialize by stable family key and migrate positional legacy data using its original order. **Severity: medium. Confidence: high.**

30. **Unchanged lights are repeatedly re-registered.**  
    `Source/MapComponent_DeepfireLights.cs:176` always sets color/radius and calls `ForceRegister`; hediffs invoke this periodically even while stationary and unchanged. Worn sweeps use the same unconditional update pattern. **Fix:** retain the last emitted color/radius/cell and re-register only when one changes. **Severity: medium at scale. Confidence: high.**

The following checks remain **UNVERIFIABLE**, rather than demonstrated defects:

- **Reservation argument positions:** `Source/JobDriver_ApplyDeepfire.cs:51` and `Source/JobDriver_LacquerWornItem.cs:30` pass `job.count` as the third reservation argument and `-1` as the fourth. Verify the actual overload. If those parameters are `maxPawns` and `stackCount`, the quantity is in the wrong slot. Use named arguments.
- **Recipe inheritance and ingredient valuation:** expand `CookMealFineBase` for the deepfire recipes. Assert exactly the intended ingredients/products, a unit-count interpretation for pigment, and the intended plain-recipe skill requirement. Parent definitions and the pigment’s nutritional configuration are absent.
- **Cuisine visibility:** `Source/LuminousPigmentMod.cs:621` mutates two stove recipe lists without showing recipe-cache invalidation or treatment of existing bills. The comment claiming no `recipeUsers` field conflicts with the supplied refining XML’s use of it. Actual 1.6 resolution and caches require verification.
- **Generation registration:** `Source/GenStep_ShoreMats.cs:18` implements generation, but no supplied map-generator registration proves that it runs on campaign maps.
- **Defs and patches:** proxy saveability/category/comps, fresh-item ticking, meal comps/outcome doer, thought stages, WorkGiver registration, terrain tags, Beauty/Melee parts, and designator insertion cannot be checked because their files are omitted.
- **Save compatibility:** prior class names and Scribe labels are absent. No historical rename or successful migration can be established.
- **Validation coverage:** `validation.py` and the fuzz harness are omitted. Their assertions, exit behavior, and coverage cannot be reviewed.

**2. LIKELY FUTURE COMPLICATIONS**

- **The family system has several competing sources of truth.** The mutable family table, cached weights, positional settings, two hard-coded recipe-name arrays, XML recipes, and hediff definitions must evolve together. `Source/LuminousPigmentMod.cs:196`, `:615` already expose two failure points. Move family identity, recipe association, weight, enablement, and outcome definition into one validated registry.

- **Legacy saves need explicit migration policy.** `Source/CompDeepfire.cs:55` defaults a missing permanent-bonus latch to false. A previously rewarded coated item with an absent/renamed latch could become eligible again after stripping. Normalize old state using versioned fixtures; do not infer historical rewards solely from current coat count. Per-Thing coats also lack the floor grid’s load-time normalization.

- **Other mods can invalidate the combat assumptions.** Curve inversion assumes monotonically increasing output. StatPart ordering determines which transformations occur before the “final” penalty calculation. Another ShotReport postfix can overwrite this multiplier, or this mod’s clamp can truncate another mod’s target-size changes. The actual patch order and duplicate registrations are **UNVERIFIABLE**; inspect them against the campaign assembly set.

- **Private bindings create failure boundaries.** Styling fields, ShotReport fields, terrain internals, and reflective build-menu refresh depend on exact shapes. A changed field can produce a type-initialization failure instead of a disabled feature. The reflection bridges also invoke methods without a complete exception boundary; Ninefold’s “Never throws” comment is not supported by its implementation. Validate signatures before installing each feature and isolate optional compatibility failures.

- **The styling UI depends on vanilla geometry and acceptance ordering.** Hard-coded row heights and button positions can overlap after another mod changes the dialog. Whether accepting simultaneous hair changes replaces or preserves queued lacquer jobs is **UNVERIFIABLE** from this bundle.

- **The engine layer is not thread-safe or reentrant.** `Source/MapComponent_DeepfireLights.cs:81` uses a mutable two-field static cache; the book reuses mutable scratch state; dictionaries and engine mutations are unsynchronized. Concurrent calls can associate one map with another map’s component. Keep these adapters on the main thread and state that contract explicitly. Actual campaign worker-thread callers are **UNVERIFIABLE**.

- **Large populations amplify observer work.** Each titled pawn’s commoner-observation thought scans the map and recomputes gear scores. Multiple hediffs per pawn also synchronize their periodic updates. Cache the map-wide “offending commoner exists” result and update it from gear/role changes.

- **Clustering savings depend on content homogeneity.** The key includes coat count, kind, and packed color. Varied dyes and mixed tiers can approach one proxy per member; the quoted hall-light estimate is not a general bound. Benchmark fragmented colors, sparse groups, several maps, and large rooms.

- **Settings currently overwrite external balancing.** `Source/LuminousPigmentMod.cs:675` reapplies compiled mood bases. Other mods’ XML changes to those values disappear on settings application. Capture resolved baseline values once, or define an explicit ownership policy for these numbers.

**3. UNLEVERAGED OPPORTUNITIES**

- **Build settings around observable consequences.** Add search/group navigation, numeric entry, per-group reset, and presets. Display actual steering probabilities, lifetime hours, combined furniture costs, and approximate light counts. Validate relationships such as furniture cap versus base cost and coat intensity/radius ordering. With all DLCs assumed, explain or hide the rankless-only toggle.

- **Correct misleading settings text.** `Source/LuminousPigmentMod.cs:247` calls the project hidden although it is visible and locked. `Source/Building_GlowTank.cs:82` treats zero grace as “never kills,” while the slider labels it as hours before killing. Give zero a named “Disabled” state and show rare-tick timing resolution.

- **Apply settings through explicit change notifications.** Compare old/new values, then refresh affected glowers, stat caches, rooms, recipe availability, and eligibility. A full clustering rebuild on every settings close does unnecessary work while still missing other consumers.

- **Extend offline validation beyond the kernels.** Compile all adapters against the exact campaign DLLs; inspect Harmony targets and private fields; resolve XML inheritance and references; check ticker/comp contracts; and maintain old-save fixtures for every persistent field. Add lifecycle cases for split/merge, cancellation during work, zero cost, pawn transfer/death, queued lacquer jobs, and settings changes. Kernel arithmetic alone cannot expose these adapter failures.

- **Test properties that reveal integration mistakes.** Examples: worn and ground emission match for one item; every cluster member has intended coverage; diminishing never increases magnitude; failed application never consumes pigment; splitting conserves state; departure leaves no pawn proxy on the old map.

- **Add invariant diagnostics to the existing JSON reports.** Report orphan proxies, stale-map pawn keys, own/cluster membership mismatches, actual carried payment, meal metadata, and replacement failures. The current proof entry points often call `AddCoat` directly, bypassing the designator and job paths where several defects reside.

- **Batch dirty-block rebuilds.** Area stripping and bulk painting currently rebuild blocks repeatedly. Collect dirty block IDs and rebuild each once per operation. Also let queued work reselect resources, allowing multiple smaller stacks to satisfy a cost.

**4. EXTENSIONS BEYOND THE MOD**

- **Expose a shared pawn-emission service.** Gear and cuisine currently maintain separate light lifecycles. A service accepting emission contributions, visibility conditions, targeting metadata, and movement ownership could support other luminous campaign content while removing duplicated cleanup and self-light subtraction logic.

- **Turn skill steering into a data-defined cuisine service.** Reuse stable family IDs, cook snapshots, weighted fallback, repeat outcomes, and caps without depending on the compiled Deepfire table. Other cuisine mods could then supply outcome definitions through XML rather than extending static lists.

- **Separate the status policy from pigment.** `Source/SumptuaryEngine.cs:58` already reads generic goods. Extend that contract with explicit rank classification and optional room contributions so later prestige materials do not need Deepfire comps or assumptions about every Ideology role.

- **Validate the supply chain through ship transport.** Sea-floor sourcing, held-item ageing, and ship-map transitions are **UNVERIFIABLE** here. Campaign integration should test the one-day clock across the actual ship journey and keep sea-floor access tied to the ship. Thermal extensions should use the campaign’s existing ambient-temperature system; the tank’s missing FlowWorks water gate remains a separate content requirement.