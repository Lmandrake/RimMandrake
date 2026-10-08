Line numbers below count from the first `using` in each supplied source block. This is a static review; nothing was built or run. The settings implementation, validation script, XML defs, most map components and several patches are explicitly omitted. Their correctness is **UNVERIFIABLE**. Comments claiming prior engine verification are not substitutes for the missing implementation.

## 1. DEBUGGING

1. **The nonlethal venom option acts after the potentially lethal operation.**  
   `Source/MapComponent_ContactVenom.cs:268` calls `TakeDamage`; line 270 subsequently clamps the additional hediff. If the damage pipeline checks lethal severity synchronously, the pawn is already dead before the clamp. Lowering severity afterward cannot undo death. The exact 1.6 death-check timing is **UNVERIFIABLE** from this bundle. **Minimal fix:** cap the venom severity contribution before health-state evaluation, scoped to contact-venom damage; preserve ordinary scratch injury lethality if that is intended. **Severity: high. Confidence: medium.**

2. **The two aura comps serialize the same label.**  
   `Source/HediffComp_PeriodicAreaAttack.cs:329` writes `"ticksUntilBurst"`. `Source/HediffComp_PeriodicAreaAttackSecondary.cs:17` inherits that implementation unchanged. Distinct `compClass` values solve duplicate-comp validation, but do not establish distinct save namespaces. If both callbacks write into the shared hediff node, their independent countdowns collide. The engine’s enclosing Scribe layout is **UNVERIFIABLE** here. **Minimal fix:** give the base a virtual save key and the secondary a distinct, stable key; retain the existing base key. **Severity: high. Confidence: medium.**

3. **Saving during moat ignition loses the remaining front.**  
   `Source/RM_CompFloodIgniter.cs:72` holds `pendingIgnition`; line 73 holds its fractional accumulator. Neither is Scribed. Reloading preserves already-created fires but discards every queued cell, silently shortening the commanded ignition. **Minimal fix:** serialize an ordered cell list and the accumulator, rebuilding the queue on load. **Severity: high. Confidence: high.**

4. **Repeated ignition commands duplicate queued work.**  
   `Source/RM_CompFloodIgniter.cs:97` can run while ignition is already active; line 127 appends another flood fill without clearing or deduplicating the queue. Repeated clicks create an arbitrarily large backlog and repeat attempts on already-burning cells. **Minimal fix:** disable the command while `Igniting`, or maintain a pending-cell set. Revalidate conducting terrain when dequeuing so terrain changes do not ignite stale targets. **Severity: medium. Confidence: high.**

5. **Found-tech progress does not follow research aliases.**  
   `Source/RM_FoundTechStudy.cs:176` saves the project as a plain string. Line 214 compares it directly with the current `defName`. Renaming a research project therefore strands its accumulated points and revealed state even when `RM_DefAliasDef` successfully migrates ordinary def references. **Minimal fix:** canonicalize saved project names during `PostLoadInit`, then merge records resolving to the same project; alternatively migrate to `Scribe_Defs` with an explicit old-string reader. **Severity: high. Confidence: high.**

6. **Terrain aliases cannot reliably reconstruct historical hashes.**  
   `Source/RM_DefAliases.cs:74` guesses the old hash from the old name. It cannot recover a hash that was collision-probed upward. Line 110 also declines migration whenever the current engine resolves that hash—potentially to an unrelated terrain after the def set changes. The resulting failure can be terrain substitution rather than an obvious missing-def error. **Minimal fix:** record actual historical hashes and detect conflicts; ambiguous hashes require version-aware migration, not a guessed fallback. **Severity: high. Confidence: high in the limitation; affected saves UNVERIFIABLE.**

7. **Aliases are single-hop and untyped.**  
   `Source/RM_DefAliases.cs:71` overwrites aliases by old name alone; line 92 resolves only the immediate destination. With `A→B→C`, removing B makes A fail even though C exists. Different def types using the same old name cannot express different destinations. **Minimal fix:** resolve chains with cycle detection, validate conflicting declarations, and optionally include def type in the alias key. **Severity: medium. Confidence: high.**

8. **Area attacks have no protection against hitting one Thing multiple times per burst.**  
   `Source/HediffComp_PeriodicAreaAttack.cs:100` visits cells independently; line 131 snapshots each cell’s Things; line 168 damages every occurrence. A multicell building appearing in several visited cell lists receives several hits, making footprint size an undocumented damage multiplier. **Minimal fix:** deduplicate Things across the burst and define distance using the nearest occupied cell or another explicit rule. **Severity: high. Confidence: high for any Thing returned by multiple cell lists.**

9. **The die-off outbreak has no generation-wide end.**  
   `Source/RM_CompScriptedDieOff.cs:141` defaults to cloning its own def. Every child starts a fresh lifetime and spread budget through line 95. Individual death at eight hours does not make the outbreak die at eight hours; successful descendants can keep propagating indefinitely. Absence from `wildPlants` does not constrain this reproduction path. **Minimal fix:** inherit an absolute outbreak expiry and a bounded generation or shared spread budget, or spawn nonspreading children. **Severity: high. Confidence: high.**

10. **Ticker compatibility is inadequately enforced.**  
    `Source/RM_CompCrackFall.cs:65` implements only `CompTickRare`, despite targeting trees that the supplied comments identify as Long-ticked. Such a tree never rolls or completes its warning. Conversely, `Source/RM_CompScriptedDieOff.cs:102` implements only normal ticking. `Source/CompProperties_ActiveGasEmitter.cs:88` rejects Never but incorrectly accepts Rare and Long parents even though its implementation requires Normal. Actual consumer ticker overrides are **UNVERIFIABLE** because their defs are omitted. **Minimal fix:** implement the appropriate ticker with correct elapsed time and validate supported parent ticker types. **Severity: high. Confidence: high in the mismatch; current wiring medium.**

11. **Batched gas and aura ticks discard elapsed intervals.**  
    `Source/Gas_Damaging.cs:71`, `Source/Gas_Transmuting.cs:57` and `Source/HediffComp_PeriodicAreaAttack.cs:46` subtract `delta`, then reset to a full interval and execute once. For an interval of 120 and a countdown of 120, `delta=300` produces one effect instead of two and discards the 60-tick remainder. **Minimal fix:** preserve the remainder and explicitly choose bounded catch-up, aggregated damage, or coalescing. Do not claim equivalence with per-tick behavior until that policy is tested. **Severity: medium. Confidence: high.**

12. **Structure eating ignores batched delta and has an extra tick between bites.**  
    `Source/RM_CompStationEater.cs:231` uses `tickIntervalAction` but ignores its elapsed-tick argument. Line 242 decrements by one invocation. At ordinary cadence, setting 180 at line 250 leads to 180 decrement-only calls followed by the next bite: a 181-tick separation. **Minimal fix:** accept `delta`, subtract elapsed ticks, and preserve the remainder when scheduling the next bite. **Severity: medium. Confidence: high.**

13. **An existing eating job ignores later disabling and satiation.**  
    `Source/RM_CompStationEater.cs:231` checks neither settings nor `eater.Satiated`. Those checks occur when selecting jobs, not while executing them. Disabling tar beasts can leave an already-running eating job damaging buildings; the generic eater can continue past its awake-time limit until the target dies. **Minimal fix:** add execution-time end conditions for satiation and the applicable mechanic gate. **Severity: medium. Confidence: high.**

14. **Contact sampling iterates a collection that its own damage can mutate.**  
    `Source/MapComponent_ContactVenom.cs:129` retains `AllPawnsSpawned` directly. `Scratch` can kill and despawn the current pawn. Removing it shifts the following entry left while the loop increments, skipping that pawn. Declaring the reference `IReadOnlyList` does not create a snapshot. **Minimal fix:** snapshot the pawn list before damage, as the weather code already does. **Severity: medium. Confidence: high.**

15. **Disabling contact venom does not freeze its clocks.**  
    `Source/MapComponent_ContactVenom.cs:109` skips processing, but deadlines remain absolute game ticks. After a long disabled period, re-enabling can cause an immediate scratch or immediate pruning, contradicting the stated freeze behavior. **Minimal fix:** shift stored timestamps by disabled elapsed time or use an enabled-time clock. If elapsed time is intended to count, change the setting’s explanation accordingly. **Severity: medium. Confidence: high.**

16. **Contact expiry is maintenance-dependent rather than an eligibility rule.**  
    `Source/MapComponent_ContactVenom.cs:176` refreshes `lastContactTicks` before checking whether the previous contact expired. Expiry is evaluated only by the 2500-tick pruning pass at line 193, using strict `>`. Old contact state can survive substantially beyond its interval and be revived on re-entry. **Minimal fix:** evaluate expiry during sampling before refreshing the row; keep pruning as storage cleanup. **Severity: low. Confidence: high.**

17. **Contact sampling becomes quadratic in a crowded stand.**  
    `Source/MapComponent_ContactVenom.cs:158` calls the linear `IndexOf` at line 203 for every contacting pawn. With P pawns and K retained contacts, the pass costs O(P·K), not merely one dictionary lookup per pawn. **Minimal fix:** maintain an unsaved pawn-to-row index rebuilt after loading and updated after removals, or use keyed runtime records. **Severity: medium at scale. Confidence: high.**

18. **The calm gate defeats the stated local fear radius.**  
    `Source/RM_CompGatherableCalmGated.cs:133` returns true for map-wide `StoryDanger.High` before checking distance. A high-danger raid on the opposite side of the map therefore dries the sheltered herd. **Minimal fix:** remove the unconditional map-wide gate or require a local corroborating threat. **Severity: medium. Confidence: high.**

19. **“Never yield under fear” has an unchecked window.**  
    `Source/RM_CompGatherableCalmGated.cs:104` accrues fullness before updating fear, and line 106 checks fear only every 250 ticks. `Active` reads cached calm, so a newly frightened animal can remain gatherable until the next scan. Fullness is also frozen rather than dried away. **Minimal fix:** update fear before accrual and revalidate it when permitting gathering; define separately whether fear preserves or removes stored fullness. **Severity: medium. Confidence: high.**

20. **Water locking strands displaced pawns on land.**  
    `Source/RM_CompWaterLocked.cs`, `CompTick`, stops movement and interrupts the job when the pawn is already on dry ground. It provides no recovery route. A mother knocked or spawned onto land can repeatedly start and lose jobs without returning to water. **Minimal fix:** provide an explicit recovery action to valid water, or constrain paths before movement and handle displacement separately. **Severity: medium. Confidence: high. Exact line omitted here because this finding spans the supplied `CompTick` block.**

21. **The vapor wander validator probably swaps destination and root.**  
    `Source/RM_CompVaporDrifter.cs:112` declares `(pawn, root, dest)`, whereas the supplied anchor validator declares `(pawn, dest, root)`. Both trailing arguments have the same type, so the compiler cannot catch an inversion. If the anchor ordering matches the engine, line 120 validates the column root rather than the proposed destination, allowing wandering outside the leash. The engine delegate invocation is **UNVERIFIABLE** here. **Minimal fix:** verify the invocation and use the correct positional order. **Severity: high. Confidence: medium.**

22. **Day/night temperature offsets switch abruptly instead of interpolating.**  
    `Source/GameCondition_EnvironmentalWeather.cs:279` selects one offset through `IsDaytime`; it does not lerp between the two as the extension describes. The condition’s fade only handles its beginning and end. It also bases thermal day/night on the glow value this mod darkens, coupling biome darkness to thermal scheduling. **Minimal fix:** interpolate using an explicitly chosen daylight curve or astronomical time independent of the darkness patch. **Severity: medium. Confidence: high.**

23. **The environmental condition’s mechanic gate leaves ambient effects running.**  
    `Source/GameCondition_EnvironmentalWeather.cs:82` gates pawn ticking, and line 190 gates cell effects. `ForcedWeather` at line 251, density factors at line 300, temperature and electricity ignore that gate. A disabled gated condition can still force weather or disable electricity. **Minimal fix:** apply the mechanic gate consistently to its virtual effects, returning neutral values, unless the setting deliberately exposes separate controls. The actual UI contract is **UNVERIFIABLE**. **Severity: medium. Confidence: high.**

24. **The advertised global damage multiplier has holes.**  
    `Source/DeathActionWorker_ScaledExplosion.cs:49` deliberately leaves `damageAmount=-1` unscaled, so default-damage explosions remain damaging at multiplier zero. `Source/RM_CompStationEater.cs:255` does not read the multiplier at all; lottery explosions likewise use engine-default damage. **Minimal fix:** resolve sentinel defaults before scaling and route kit damage through a common scaling function. Clearly define any exceptions. **Severity: medium. Confidence: high; exact settings wording UNVERIFIABLE.**

25. **Tar-beast pace is a one-time, three-band setting.**  
    `Source/RM_CompTarBeast.cs:46` applies pace only once; line 88 maps every value to one of three severities. Changing the setting does nothing to existing beasts, and intermediate values have no distinct effect. The saved `paceApplied` flag preserves this across reloads. **Minimal fix:** expose three named presets if that is intended, and refresh existing beasts when settings change; otherwise implement the advertised continuous relationship. **Severity: medium. Confidence: high.**

26. **The tar-beast building limit cannot exceed the eater’s def limit.**  
    `Source/RM_CompTarBeast.cs:119` ORs the settings limit with `eater.Satiated`, which independently enforces `Props.maxStructuresEaten`. With the default eight, setting twelve still stops at eight. **Minimal fix:** use one effective limit for tar beasts, read by both job selection and sinking. **Severity: medium. Confidence: high.**

27. **Disabling tar beasts does not disable this wake path.**  
    `Source/RM_CompTarBeast.cs:269` reads the pump radius factor but never `tarBeastEnabled`; line 283 still activates dormancy. The beast’s normal comp subsequently returns before its initialization work when disabled. **Minimal fix:** gate wake causes consistently, including the relay and applicable native wake configuration. Full emergence behavior is **UNVERIFIABLE** without the bulge def. **Severity: medium. Confidence: high for this wake path.**

28. **Solvent hunting consumes its trigger before confirming success.**  
    `Source/RM_CompTarBeast.cs:48` sets `paceApplied`; line 53 consumes the solvent wake; the return value from `TryStartMentalState` is ignored. A rejected transition loses the request permanently and never retries. **Minimal fix:** track hunt initialization independently and commit consumption only on success, or retain pending hunt state. **Severity: medium. Confidence: high.**

29. **“Nobody left to hunt” actually means no free colonists.**  
    `Source/RM_CompTarBeast.cs:124` sinks the permanent manhunter when `FreeColonistsSpawnedCount==0`. Prisoners, slaves, visitors, enemies and animals can remain, contradicting the preceding claim that it hunts every pawn. **Minimal fix:** query the intended huntable population or explicitly define colony absence as the sinking rule. **Severity: medium. Confidence: high.**

30. **Lottery yield depends on how work is partitioned into calls.**  
    `Source/RM_CompWorkedLottery.cs:142` subtracts one portion and rolls once. A single input of three portions yields one result and leaves two completed portions waiting for future positive input; three separate inputs yield three results immediately. **Minimal fix:** process completed portions in a bounded loop, with a validated positive threshold and a destruction/map check after each result. **Severity: medium. Confidence: high.**

31. **Rolling another trap postpones an armed trap.**  
    `Source/RM_CompWorkedLottery.cs:201` unconditionally resets the fuse. Continuing work can reroll traps and repeatedly extend the deadline rather than letting the first trap detonate. **Minimal fix:** reject further trap arming while armed, preserve the earliest deadline, or pause work pending disarm/detonation. **Severity: medium. Confidence: high.**

32. **The beast-wake depth comparison has inconsistent indexing.**  
    `Source/RM_CompWorkedLottery.cs:183` increments depth before comparing against threshold four. The first signal follows processing indices 0–3, rather than processing index four, despite the property describing a zero-indexed threshold. **Minimal fix:** compare the consumed stratum index or rename/document the property as completed-portion count. **Severity: low. Confidence: high.**

33. **Trap weighting eventually becomes nonfinite.**  
    `Source/RM_CompWorkedLottery.cs:194` exponentiates the unbounded lifetime depth even after stratum selection clamps to the last table entry. At the default 1.3, sufficiently deep shafts produce float-infinite trap weights, invalidating ordinary weighted sampling. Exact sampler failure behavior is **UNVERIFIABLE** because that implementation is absent. **Minimal fix:** cap weighting depth or normalize weights using bounded/logarithmic arithmetic. **Severity: medium. Confidence: high.**

34. **Glow override precedence contradicts its own claimed policy.**  
    `Source/BiomeGlowPatches.cs:220` searches forward and returns the first matching condition at line 231, while its comment claims the most recently registered condition wins. Under the stated registration ordering, an older override defeats a newer clearing event. **Minimal fix:** define explicit priority and a deterministic tie-breaker, or search backward if newest registration is the intended rule. **Severity: medium. Confidence: high under the ordering stated in the bundle.**

35. **Clearing brightness does not clear permanent sunlight suppression.**  
    `Source/BiomeGlowPatches.cs:293` reads only the biome extension. An active override can restore ordinary brightness while sunlight-gated stats still read false. **Minimal fix:** give override conditions an explicit sunlight-suppression policy and resolve brightness and sunlight eligibility together. **Severity: medium. Confidence: high.**

36. **Warbling ignores player-selected color and leaves altered light when disabled.**  
    `Source/RM_Comp_WarblingGlow.cs:103` always uses def-level color; line 109 overwrites the live color. A player color choice cannot remain the animation’s center. Disabling at line 55 simply returns, leaving the last animated color and radius in place. **Minimal fix:** retain a per-instance user baseline, distinguish animation writes from user changes, and restore the baseline on disable. **Severity: medium. Confidence: high.**

37. **Warbling can register the same light twice per update.**  
    `Source/RM_Comp_WarblingGlow.cs:109` changes color through a setter described as registering the light; line 119 then explicitly registers after changing radius. This repeatedly rebuilds lighting for an intermediate state, particularly costly with many lamps. **Minimal fix:** set radius first and perform one necessary registration; skip negligible color changes. Actual setter cost is **UNVERIFIABLE** without the engine implementation. **Severity: medium at scale. Confidence: medium.**

38. **Transmutation accepts invalid replacements and destroys the original first.**  
    `Source/Gas_Transmuting.cs:128` dereferences list entries without null checks. More seriously, line 165 destroys the original before line 167 spawns an unchecked replacement. A nonplant replacement is accepted; a spawn/construction failure leaves permanent loss. **Minimal fix:** validate entries, finite positive weights and plant replacement types in config validation; construct and validate the replacement before destroying the original. **Severity: medium. Confidence: high.**

39. **Clamped surge/recede arithmetic can drift in the wrong direction.**  
    `Source/RM_AxisKernel.cs:48` clamps each application; line 84 computes recede from the requested forward delta. Starting at 0.95, applying +0.10 gives 1.00; receding −0.09 gives 0.91—fresher than the original despite a positive residual. **Minimal fix:** represent an unclipped baseline plus surge offset, or recede each cell from its actual applied forward change. Whether the omitted component compensates is **UNVERIFIABLE**. **Severity: medium. Confidence: high in the arithmetic counterexample.**

40. **Several Harmony targets remain insufficiently constrained.**  
    `Source/BiomeGlowPatches.cs:90` resolves `PostApplyDamage` by name despite documenting its parameters; line 106 similarly resolves back-compat by name. Installation success does not prove the intended overload was patched. Argument-name binding also makes patches sensitive to parameter-name changes. **Minimal fix:** resolve exact signatures, assert parameter names/types, and inspect installed owners and patch counts. Define ordering where another mod can overwrite the same result. Harmony documents both [argument binding](https://harmony.pardeike.net/v2/articles/patching-injections.html) and [ordering controls](https://harmony.pardeike.net/v2/articles/priorities.html). Actual target drift, double installation and competing patches are **UNVERIFIABLE** here. **Severity: medium. Confidence: high in the fragility.**

No specific shipped XML def can be declared unloadable from this bundle: the XML is omitted. Likewise, historical Scribe field/class renames from the refactor cannot be reconstructed without the preceding version.

## 2. LIKELY FUTURE COMPLICATIONS

- **“One kind of heat” needs an ownership rule.** `GameCondition_EnvironmentalWeather` can grant a carrier independently of its direct-damage toggle (`:117`, `:131`); wet-bulb and pulse conditions provide additional exposure paths. Adding content can accidentally stack vanilla heat illness, carrier exposure, wet-bulb severity and scald damage. Actual present duplication is **UNVERIFIABLE**. Define which mechanism owns heat accumulation and which mechanisms merely supply exposure.

- **Protection is not automatically interchangeable between routes.** Gas uses direct `AdjustSeverity`, while wet-bulb explicitly sums apparel protection. The gas comment’s claim that masks and resistance are handled by the hediff requires verification against that hediff’s implementation. A generic severity adjustment alone does not establish a protection contract.

- **Ship movement stresses map-local registrations.** Contact plants, barriers and living-bole markers register at spawn and deregister at despawn. Arrival letters remember biome names globally. Exercise movement to an existing map, repeated biome arrivals, despawn/re-spawn and map abandonment. Whether the omitted arrival patch detects existing-map landings, including sea-floor arrivals, is **UNVERIFIABLE**.

- **Research migration needs idempotence.** `RM_FoundTechKnowledge.Import` adds imported points (`Source/RM_FoundTechStudy.cs:252`). Calling it again doubles progress. Migrators need a saved completion marker or provenance. Multiple study sources for one project also need consistent thresholds and gate keys; otherwise one source’s configuration can determine another source’s availability.

- **Static subscriptions and lazy caches need lifecycle boundaries.** Beast relays subscribe to a process-wide event. Alias dictionaries are published before construction finishes (`Source/RM_DefAliases.cs:57`), and other registries use similar lazy initialization. Concurrent access could observe incomplete state; actual worker-thread access is **UNVERIFIABLE**. Map teardown must also demonstrably unsubscribe relays.

- **Path restrictions will collide with other customizers.** The body-size prefix declines requests already carrying a customizer. That creates exceptions to “large creatures cannot enter.” Composition, native-grid ownership, invalidation after growth/body-size/settings changes, and disposal are **UNVERIFIABLE** because the map component is omitted.

- **Hot paths grow with installed content.** Every celestial-glow query scans active conditions once any override exists anywhere (`Source/BiomeGlowPatches.cs:219`). Aura bursts allocate a list per visited cell (`Source/HediffComp_PeriodicAreaAttack.cs:131`). Herd fear scans synchronize on global tick modulo (`Source/RM_CompGatherableCalmGated.cs:106`). Cache effective map state with explicit invalidation, reuse safe buffers, and stagger scans.

- **Generic APIs contain campaign-specific behavior.** All territorial-anchor defense and wandering receive water restrictions; tar-beast sinking names `"RM_TarDeep"` directly. Reusing these classes for land guardians or another liquid will silently import inappropriate behavior. Make terrain constraints explicit configuration.

## 3. UNLEVERAGED OPPORTUNITIES

**Offline validation should cover orchestration, persistence and binding, not only arithmetic.** The validation script and self-test implementation are **UNVERIFIABLE**. The highest-value regression cases are:

| Production surface | Required regression |
|---|---|
| Contact venom | Lethal contribution with nonlethal enabled; first pawn dies without skipping the next |
| Contact clocks | Disable/re-enable; expired re-entry; missing pawn reference; unequal saved list lengths |
| Aura persistence | Two independent countdowns survive save/load |
| Batched cadence | Equal elapsed ticks split into different `delta` sequences preserve the declared policy |
| Ignition | Save midway; repeated command; changed terrain before dequeue |
| Lottery | One large work input versus several smaller inputs; second trap roll; deep finite weights |
| Migration | `A→B→C`; duplicate aliases; historical terrain collision; research-record rename |
| Targeting | Wander root valid/destination invalid and the reverse |
| Surge | Boundary saturation; recede direction; interrupted surge; save during recede |
| Settings | Change each setting after its mechanic has already initialized |

Build a separate compatibility check against the exact supported game assemblies that verifies patch targets, overloads, argument binding and installed patch counts. Keep this distinct from tests claiming actual in-game behavior.

**Mod Settings could expose a much clearer operating contract.** Generate controls from a mechanic registry containing scope, dependencies, default, current value and application timing: immediate, next interval, newly spawned objects, or map generation only. Give multipliers precise affected-route descriptions. Provide per-section reset and presets. Warn visibly about enabling an option whose necessary content/API is unavailable. UI quality, persistence and actual control wiring remain **UNVERIFIABLE** without `RM_EnvironmentalHazardsMod.cs`.

**Validate relationships between defs.** Existing checks mostly validate individual numbers. Cheap cross-def checks could reject:

- Non-Gas emitter targets and nonplant transmutation targets.
- Unsupported ticker types.
- Nonfinite numbers, reversed ranges and nonpositive production/work thresholds.
- Inconsistent study thresholds/gates for the same project.
- Duplicate save labels on one hediff.
- Carrier hediffs whose damaging comps ignore the owning mechanic gate.
- Missing protection-stat readers and incompatible damage/armor-category wiring.

**Expose inspectable state through the existing machinery.** Effective hazard rate, next scheduled application, active protection, pause reason and mechanic gate status can come from the same values used by execution. This would make settings changes reviewable and turn many “it seems inactive” reports into concrete state reports.

## 4. EXTENSIONS BEYOND THE MOD

- **A campaign-wide heat service is the strongest reuse opportunity.** Weather, wet rooms, sunlight, warm terrain and steam could submit exposure to one accumulator with one protection policy, one recovery policy and one lethal-state owner. This directly supports “one kind of heat” while letting each biome supply different causes.

- **Def aliases could become shared campaign migration infrastructure**, but only after gaining typed declarations, chain resolution, conflict reporting and explicit historical terrain hashes. Also migrate def names stored as ordinary strings; patching Scribe def lookup alone is insufficient.

- **Found-tech study can support campaign discovery without biome-specific implementations.** Artifacts, organisms, wrecks and resources can unlock research through the existing project-keyed store. Shared project configuration and idempotent imports are prerequisites.

- **Ship arrival can supply a single campaign event contract.** Publish destination map, biome and arrival cause once; narration, discovery, hazard briefings and sea-floor onboarding can subscribe. Whether the current omitted patch supplies a reliable arrival seam is **UNVERIFIABLE**.

- **Environmental interaction APIs could replace hardcoded cross-mod assumptions.** Terrain hazard tags, bounded outbreak IDs, protected-region queries and versioned suppression interfaces would let other campaign mods interact with these systems without naming individual terrain defs or binding reflection to one method signature.