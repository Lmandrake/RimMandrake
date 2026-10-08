## 1. DEBUGGING

References are to lines within the inlined files; method names identify the relevant code where needed. Nothing was executed. Omitted defs, patches, project files, external assemblies, and earlier save formats are **UNVERIFIABLE**.

### Conditions, save/load, and destructive operations

**1. Opting a map out can leave permanent toxic weather running indefinitely.**  
`Source/RM_Settling.cs:368` — `MapComponentTick()` returns on `!OnWarscar` before checking or ending the active condition. Disable cross-biome applicability while Settling is active, and its permanent condition remains; `RM_GameCondition_Settling.GameConditionTick()` continues applying toxicity independently of that applicability check.

**Minimal fix:** handle condition shutdown and outstanding sweep cleanup before returning for an ungoverned map. Gate the condition’s toxic tick too. **Severity: high. Confidence: high.**

**2. Reloading forgets which pawns the lift front already poisoned.**  
`Source/RM_Settling.cs:195,210,342` — `sweepActive` is saved, but `liftHit` is not. A pawn hit before saving can receive another front dose after loading if it enters a remaining sweep cell. `sweepNextTick` also resets. Persistence of the external grid’s sweep cursor is **UNVERIFIABLE**.

**Minimal fix:** Scribe the hit IDs and scheduling state, and define a save contract for the sweep cursor rather than relying on unspecified external persistence. **Severity: medium. Confidence: high.**

**3. Buried ordnance can reveal into a building constructed since generation.**  
`Source/RM_Settling.cs:272,285–287` — generation checks the cell once, but `RevealCheck()` never rechecks the buried cell’s edifice, roof, terrain, or occupancy. It removes the buried record before spawning the shell. Construction over the cell can therefore cause a conflicting spawn or loss of the hidden record. Exact conflict handling is **UNVERIFIABLE** without the engine.

**Minimal fix:** validate the target cell again; retain the record until successful placement. Define what happens when the cell becomes occupied. **Severity: high. Confidence: high for the missing checks; medium for the resulting engine behavior.**

**4. Several conversions destroy their source before ensuring a replacement exists.**

- `Source/RM_CompTurretAim.cs:118` — destroys the wreck before blueprint placement; placement suitability is never checked, and rotation is forced to north.
- `Source/RM_WarscarRings.cs:140,152` — destroys the ring before resolving the salvaged-ring def.
- `Source/RM_Hospice.cs:126–128` — destroys the walk-in pawn before checking `TryPlaceThing()` success.
- `Source/RM_Hospice.cs:320,323` — resets the cradle even when placing the failed chassis fails.

These paths can consume unique content without producing its replacement.

**Minimal fix:** resolve and construct replacements first, validate placement, check placement results, and commit destruction/reset only after success. Preserve the original rotation where footprints matter. **Severity: high. Confidence: high.**

**5. A missing saved history can crash a working cradle.**  
`Source/RM_Hospice.cs:218,261,362` — an intact chassis can be accepted with no history if no histories resolve. A removed or renamed history def can also load as null. Diagnosis dereferences `history.oddityText` when hospice research is unlocked; inspection dereferences `history.memories.Count` without checking `memories`.

**Minimal fix:** repair or explicitly reject missing histories during load/acceptance, supply fallback diagnosis text, and null-check the memory list. **Severity: high. Confidence: high.**

**6. Saved cradle state is used as an unchecked array index.**  
`Source/RM_Hospice.cs:170,183,353` — `stage` is loaded without validation and indexes `StageLabels`. A future stage migration or malformed save can break labels and inspection.

**Minimal fix:** validate stage and dependent fields during `PostLoadInit`; migrate unsupported stages explicitly. **Severity: medium. Confidence: high.**

**7. Chotrix kill tracking is intentionally lost on save/load.**  
`Source/RM_Chotrix.cs:40–42,51` — `lastVictim` and `victimDragged` are omitted from Scribe. Reloading between a bite, death, and job selection forgets the pending drag. The saved `lastStrike` survives while its associated victim does not.

**Minimal fix:** Scribe the victim reference and drag state, then discard invalid references after loading. **Severity: medium. Confidence: high.**

**8. Older static registries can alias into a newly loaded game.**  
`Source/RM_Chotrix.cs:35,59`; `Source/RM_Totchak.cs:20` (`All`); `Source/RM_OldTongue.cs:24,29` — these registries lack the registered-map identity and stale-entry pruning already used by aerosol screens. Loading another game does not necessarily despawn every old object. The bundle itself documents why `Thing.Map` can then resolve through the new game’s map index.

Consequences include phantom chotrix silence, demolition checks against old totchaks, retained game objects, and unrelated panel coordinates.

**Minimal fix:** use map-owned registries or registered-map references, and clear registries on game teardown/load. **Severity: high. Confidence: high.**

**9. Panel inspection lists unread panels from other maps.**  
`Source/RM_OldTongue.cs:80` — the sibling-location condition checks analysis ID and spawning, but not map identity. Coordinates from another settlement appear as though they identify nearby panels.

**Minimal fix:** require the same map, or include the map name and a usable target. Also prune stale entries. **Severity: medium. Confidence: high.**

### Jobs, animals, and settings

**10. “Set off from range” never shoots.**  
`Source/RM_Settling.cs:559–570,588–594` — the workgiver merely checks that the pawn possesses a ranged weapon. The driver walks, waits, and calls `Detonate()`. It consumes no ammunition, performs no verb attack, and ignores actual weapon range and firing restrictions. A weapon unable to shoot from the chosen cell still qualifies.

**Minimal fix:** perform a real weapon attack and let projectile damage trigger the shell, or rename and implement the action as remote detonation with its own eligibility rules. **Severity: high. Confidence: high.**

**11. Shell detonation itself is not established by this bundle.**  
`Source/RM_Settling.cs:480–483` — `Detonate()` applies 200 bomb damage; it does not explicitly explode. Whether this reliably triggers an explosive comp depends on the omitted `RM_BuriedOrdnance.xml`, including hit points and explosive thresholds.

**Minimal fix:** validate the resolved explosive properties against this damage path, or provide an explicit, guarded detonation operation. **Severity: high if the def does not satisfy the contract. Confidence: UNVERIFIABLE.**

**12. Longer reveal settings disable the chotrix’s hurt-after-bite response.**  
`Source/RM_Chotrix.cs:67,77–80` — the comp returns while revealed. Flee detection only runs when `now - lastStrike < 600`. At a reveal duration of ten seconds or more—allowed by the settings UI—the detection window closes before the check can run.

**Minimal fix:** evaluate the hurt/flee transition before the reveal-window return. **Severity: medium. Confidence: high.**

**13. The lone-prey rule is checked only when choosing a target.**  
`Source/RM_Chotrix.cs:142–149,168` — after selection, a normal `AttackMelee` job can continue for 900 ticks without checking `IsLone()`. Another pawn can join the prey before the bite, contradicting “never a group of two or more.”

**Minimal fix:** add an ongoing target-validity check, especially immediately before attacking. **Severity: medium. Confidence: high.**

**14. Disabling chotrix does not disable all chotrix effects.**  
`Source/RM_Chotrix.cs:209`; `Source/RM_GeigerChoir.cs:79–87` — an existing flee timer still produces flee jobs without checking `chotrixEnabled`; existing chotrix still silence the choir. The master setting stops hunting and cloak maintenance but leaves these effects.

**Minimal fix:** gate both consumers and clear incompatible active state when disabling the mechanic. **Severity: medium. Confidence: high.**

**15. Disabling totchak does not stop an already announced, awake totchak.**  
`Source/RM_Totchak.cs`, `CompTotchak.CompTick()` — the disabled check occurs only inside `d.Awake && !announced`. Once announced, an awake totchak bypasses it. `JobDriver_TotchakGnaw` also lacks an ongoing enabled check, so an existing gnaw job continues damaging walls.

**Minimal fix:** check disabling independently of announcement state; end active gnaw jobs and transition to the intended disabled state. **Severity: medium. Confidence: high.**

**16. Pool drawing does not revalidate the order at completion.**  
`Source/RM_ReactionPools.cs:353–362,465–482` — eligibility checks cooldown and skip-bloom at job selection, but completion checks only pool existence and `poolsEnabled`. A phase can become bloom during travel/work; a pawn can then be burned despite skip-bloom being enabled. Cancelling `drawWanted` also does not stop the pending draw.

**Minimal fix:** recheck `drawWanted` and `CanDrawNow()` at completion. Specify whether the job draws the selected phase or the completion phase. **Severity: high. Confidence: high.**

**17. Disabling pools leaves their corpse-dissolution hazard active.**  
`Source/RM_ReactionPools.cs:214–217,257` — `MapComponent_ReactionPools.MapComponentTick()` never reads `poolsEnabled`. Existing pools continue destroying corpses while taps are disabled.

**Minimal fix:** gate the hazard, or expose and document a separate hazard switch. **Severity: medium. Confidence: high.**

**18. Ring repair does not validate the delivered payment.**  
`Source/RM_WarscarSalvage.cs`, `RM_JobDriver_RepairRing.MakeNewToils()` — completion destroys whatever is currently carried and marks the ring working. It checks neither component def nor count and does not confirm that the ring remains repairable.

**Minimal fix:** require two industrial components and a currently failing, installed ring at completion; consume exactly two. **Severity: medium. Confidence: high.**

**19. Several cancelled or disabled orders can still complete.**  
`Source/RM_Settling.cs:509,585,623`; `Source/RM_WarDustUses.cs`, `JobDriver_DustBlight.MakeNewToils()` — existing jobs do not recheck `defuseWanted`, `triggerWanted`, `warDustEnabled`, or `warDustBlightCureEnabled`. Cancellation can still detonate a shell; disabling dust mechanics can still consume material and apply toxicity.

**Minimal fix:** add ongoing failure conditions and repeat the decisive checks before destructive completion. **Severity: medium. Confidence: high.**

**20. Walk-ins can target an unreachable cradle indefinitely.**  
`Source/RM_Hospice.cs:105–114` — cradle choice uses distance alone. The selected interaction cell need not be reachable. The comp also treats any current `Goto` as sufficient without checking its destination, and never checks `hospiceEnabled` or `hospiceWalkInEnabled` after spawning.

**Minimal fix:** choose a reachable cradle, compare the current job’s target, gate ongoing walking, and provide a fallback when no reachable cradle remains. **Severity: medium. Confidence: high.**

**21. Glower shielding’s advertised master switch has no shown control over plate apparel.**  
`Source/RM_GlowerShield.cs:12`; `Source/RM_GlowerShield.cs`, `RM_CompGlowerShield.For()` — panels are gated, but plates are described as plain apparel with XML `equippedStatOffsets`. No supplied code suppresses those offsets when `glowerShieldingEnabled` is false, although the settings tooltip promises “both do nothing.”

**Minimal fix:** put plate resistance behind a setting-aware stat contribution, or split the settings and correct the tooltip. The omitted apparel/patch XML is **UNVERIFIABLE**. **Severity: medium. Confidence: high for the missing supplied gate.**

### Timing, arithmetic, and world state

**22. Dead-ring protection persists briefly after the engine disappears.**  
`Source/RM_WarscarRings.cs:60,72–75` — wake state updates only on rare ticks. Protection can remain active for roughly 250 ticks after takeoff. A calibrated dead ring runs the base calibration pass *before* recomputing wake state, allowing one stale scrub pass.

**Minimal fix:** refresh wake state before calibration and invalidate it on engine spawn/despawn or ship departure. **Severity: medium. Confidence: high.**

**23. The guaranteed working ring is tied to attempt index, not successful placement.**  
`Source/RM_WarscarRings.cs:218–237` — if index zero exhausts its placement attempts, later rings may be dead or failing. The first actual placed ring is therefore not guaranteed working.

**Minimal fix:** force the first successfully placed ring live and working, using `placed.Count`. **Severity: medium. Confidence: high.**

**24. Permitted wind thresholds can remove the intended hysteresis.**  
`Source/Kernel/RM_SettlingKernel.cs:14,21`; `Source/RM_Settling.cs:383,388` — the UI allows calm threshold 0.8 and end threshold 0.4. Constant wind 0.6 then satisfies both predicates, repeatedly starting and ending Settling without a weather change.

**Minimal fix:** enforce `endWind > calmThreshold`, with a visible explanation when adjusting either value. **Severity: medium. Confidence: high.**

**25. Pool cycle length is shortened by integer division.**  
`Source/RM_ReactionPools.cs:48–49,125–127` — the real cycle is `4 * (CycleTicks / 4)`, not `CycleTicks`. It can be up to three ticks shorter. Floating sliders can produce non-divisible tick counts.

**Minimal fix:** calculate phase from normalized position within `CycleTicks`, or round the total cycle to a multiple of four and display that value. **Severity: low. Confidence: high.**

**26. Pool cell ownership becomes stale when terrain changes.**  
`Source/RM_ReactionPools.cs:95–103,161–165,222–258` — cells are captured at spawn and never updated. Replaced terrain remains tinted and dissolves corpses; newly added reaction-liquor terrain is ignored. Adjacent pools can also claim overlapping cells through the ten-cell scan.

**Minimal fix:** maintain explicit pool membership and update it on terrain changes, or validate terrain before rendering and processing hazards. **Severity: medium. Confidence: high.**

**27. Crater yields remain cached after crater changes.**  
`Source/RM_Settling.cs:243–256` — `craterIdx` is built once. Removing or adding crater buildings does not change film caps or dust yields until reload.

**Minimal fix:** invalidate on relevant spawn/despawn, or derive the answer from current cell contents. **Severity: medium. Confidence: high.**

**28. Panel “reveal chance” retries until the placement quota fills.**  
`Source/RM_OldTongue.cs:155–162` — the loop tests every available wall-adjacent cell until enough panels are placed. With many candidates, even a low reveal chance usually fills the quota. It does not behave like a chance applied to a fixed number of placement attempts, as the settings field comment describes.

**Minimal fix:** test only the intended number of candidates, or rename/document the control as a per-candidate acceptance probability. **Severity: medium. Confidence: high.**

**29. Bileworm acceleration stops at the start of rotting.**  
`Source/RM_BilewormGas.cs`, `RM_CompBilewormGas.CompTickInterval()` — progress is advanced only while `RotStage.Fresh`, and capped at `TicksToRotStart`. Corpses outside drinking range then resume ordinary rot speed, despite the stated rule that nearby corpses rot faster than their own clock.

**Minimal fix:** advance rottable corpses through the intended stages; cap only where the design requires it. **Severity: medium. Confidence: high.**

**30. Bileworm interval processing cannot account for multiple crossed periods.**  
`Source/RM_BilewormGas.cs`, `CompTickInterval(int delta)` — a successful hash check always applies exactly `Props.intervalTicks` of rot. If `delta` crosses several periods, only one period is credited. The actual deltas used by RimWorld’s pawn scheduler are **UNVERIFIABLE** here.

**Minimal fix:** accumulate elapsed ticks and process the elapsed periods, or use an explicitly bounded elapsed-time calculation. **Severity: medium under large deltas. Confidence: high for the arithmetic limitation.**

### Sound, integration, and performance

**31. The choir names the wrong projector def and does not check whether sources are active.**  
`Defs/ChoirDefs/RM_GeigerChoirDef.xml`, `<hum>`; `Source/RM_GeigerChoir.cs:153,158–183` — XML names `RM_WarscarProjector`; supplied ring code resolves `_Live`, `_Dead`, and `_Salvaged`. Missing names are silently skipped. Meanwhile, any listed aerosol screen can hum even when unpowered or disabled because source selection checks proximity alone.

**Minimal fix:** use the actual ring names and filter hum sources through their live state and master setting. Existence of a separate unsuffixed alias is **UNVERIFIABLE**. **Severity: medium. Confidence: high.**

**32. Cosmetic sound consumes the gameplay random stream.**  
`Source/RM_GeigerChoir.cs:190–193,232,240,295` — camera-dependent clicks and pitch variation use global `Rand`. Camera position, selected caravan, choir settings, and available jars can therefore alter later simulation randomness.

**Minimal fix:** use an isolated cosmetic RNG or a scoped `Rand` state restored in `finally`. **Severity: medium; potentially high for deterministic multiplayer. Confidence: high.**

**33. Jar sound repeatedly scans all glower plants for every nearby jar.**  
`Source/RM_GeigerChoir.cs:199–206,210–232` — every six ticks, each audible jar resolves plant defs, allocates lists, and scans all matching plants across the map to count a four-cell neighborhood. Refresh also resolves five source groups every thirty ticks.

**Minimal fix:** resolve immutable def lists once and count nearby plants through local cells or a cached spatial index. **Severity: medium at scale. Confidence: high.**

**34. The Wasteland bridge loses nesting context and does not identify the pollution grid being modified.**  
`Source/RM_AerosolScreen.cs:309–316` — nested `DoFall` calls overwrite `fallMap`; the inner finalizer clears the outer context. `SetPollutedPrefix()` also ignores `__instance`, so a pollution write to another map during a fall is tested against the wrong map’s screens.

**Minimal fix:** save/restore previous context through Harmony `__state`, and verify the target grid belongs to that context map. **Severity: medium. Confidence: high.**

**35. Track-grid API drift can repeatedly throw during map ticking.**  
`Source/RM_Settling.cs:51–70,315–317,354–357` — reflection finds methods by name without verifying signatures. Invocations are uncaught. A changed return type, overload, or callback signature can break ending Settling and then repeatedly break active sweeps.

**Minimal fix:** resolve exact signatures, validate return types, catch invocation failures, log once, and switch to a local fallback. **Severity: high when the integration changes. Confidence: high.**

**36. The missing-grid fallback drops the lift-front mechanic and scans the whole map immediately.**  
`Source/RM_Settling.cs:318–323` — without the grid, every film cell is wiped synchronously. There is no visible moving front or front exposure, and map-sized cleanup happens inside condition termination.

**Minimal fix:** implement a local batched sweep independent of the track grid; use the external API only to erase tracks alongside it. **Severity: medium. Confidence: high.**

### Validation defects and unverified contracts

**37. The offline settings check does not enumerate all settings or prove their wiring.**  
`validation.py:28,65–69` — checks iterate a manually maintained `DEFAULTS` dictionary. It omits biome rarity, aerosol/ring controls, glower shielding, and cross-biome settings. A quoted field name anywhere passes the Scribe check; a token anywhere after `DoWindowContents` passes the UI check. Neither verifies a gameplay reader.

**Minimal fix:** enumerate declared settings, check actual Scribe calls and controls, and maintain an explicit reader/effect contract for each setting. **Severity: high for validation reliability. Confidence: high.**

**38. The script’s claimed compile and Harmony-target verification is absent.**  
`validation.py:17–18,70–91` — checking `Compile Include` strings, Harmony reference text, and target-name tokens does not compile C#, resolve overloads, verify patch parameter bindings, or inspect patched owners. Most omitted XML is not validated by an engine-equivalent def loader either.

**Minimal fix:** add an offline build against the pinned 1.6 assemblies, reflection-based target/signature checks, and a resolved-def validation stage. Kernel fuzz tests and their coverage are **UNVERIFIABLE** because they are not supplied. **Severity: high. Confidence: high.**

**39. Test restoration overwrites user preferences with defaults.**  
`validation.py:28`, `DEFAULTS` consumed by `_restore()` — restoring a tested setting to the hard-coded default loses its pre-test value. The restoration call can also fail, leaving the test setting active.

**Minimal fix:** capture each original value before mutation and restore it in an outer `finally`; report restoration failures as suite failures. **Severity: medium. Confidence: high.**

**40. Proof hooks alter the current campaign and sometimes manufacture the state being tested.**

- `Source/RM_WarscarMark.cs:123–155` — adds severity to the first existing colonist, then manually arms the floor. This cannot establish that the floor’s real tick callback works.
- `Source/RM_ChatrakSnap.cs:232–267` — spawns persistent animals, sweeps every eligible chatrak on the map, and directly starts the mental state instead of testing its natural giver.
- `Source/RM_LoosenedPanel.cs`, `RM_LoosenedPanelProof.ProofWork()` — leaves the produced crate behind and lacks guaranteed cleanup on exceptions.

The mark tests depend on previous severity; snap tests expect `armed 1` although the sweep can arm unrelated animals.

**Minimal fix:** use isolated test maps/pawns, snapshot and restore state, clean up in `finally`, and observe real transitions without setting the expected result manually. **Severity: high. Confidence: high.**

Additional release-critical checks remain **UNVERIFIABLE**:

- **Tick dispatch:** pawn/apparel comps mostly override `CompTick`, the bileworm uses `CompTickInterval`, and the mark floor uses `CompPostTick`. Confirm actual 1.6 dispatch and interval forwarding before accepting any cadence test.
- **Harmony signatures:** especially `DoExplosion`, `CommonalityOfAnimalNow`, toxic methods, and reflected `SetPolluted`. Name-only targeting does not establish compatible overloads or argument names.
- **Defs and patches:** ticker types, inherited comps, workgiver priorities, research wiring, minifiability, and explosive properties are omitted.
- **Calibration research:** `RM_OldTongue.ProjectorCalibrated` has no supplied consumer; calibration uses `Props.calibrated`. Whether research exposes a separate calibrated def is omitted.
- **Scribe migration:** no earlier source/save fixture is supplied, so historical key or class-name compatibility cannot be certified.
- **Heat contract:** resolved inheritance of `RM_BloomAcid ParentName="Flame"` needs inspection. The supplied XML does not establish which inherited flame behaviors remain.

## 2. LIKELY FUTURE COMPLICATIONS

- **Family tags do not enforce mutual exclusion.** `RM_WarscarMark.CarriesOtherMark()` prevents further accrual when another mark exists, but does not remove an existing overlap. If another mod adds its mark later, both sets of effects can remain. External twin behavior is **UNVERIFIABLE**. Define a campaign-wide ownership/migration rule.

- **Settings mutate shared defs destructively.** `OldLineTurretTuning`, `RM_ChatrakSnapStartup`, `RM_WarscarMarkStartup`, and `RM_WarscarStartup` multiply, erase, or remove data. Reloadable settings and future initialization changes will need immutable baselines; reversing a setting cannot reconstruct erased rows or offsets.

- **Research progression depends on repeated map access.** `GenStep_InscribedPanels` distributes the default three panels across three kinds, while their sets require two or three readings. Destroyed or inaccessible panels create additional travel requirements. The campaign’s actual ability to supply replacement maps is **UNVERIFIABLE**.

- **Multiple screens and panels need explicit combination rules.** Aerosol coverage is a union, calibration work stacks independently, and glower shielding selects by resistance offset while taking that same panel’s gas factor. Added content could make “strongest resistance” select weaker gas protection.

- **Save state needs a versioned schema.** Pool phases use numeric indices; cradle stages use numeric positions; histories and conditions retain def references. Reordering phases, deleting histories, or adding stages requires migrations and fixtures.

- **Multi-layer worlds need layer-aware warning identities.** `PollutedAhead()` returns an `int`, and caravan warnings remember that integer. Preserve complete `PlanetTile` identity when supporting additional world layers.

- **Main-thread assumptions are implicit.** Static lists/dictionaries, global RNG, Unity material creation, and mutable `Phase()` evaluation are unsynchronized. Compatibility with parallel simulation/rendering mods is **UNVERIFIABLE**; those integrations need an explicit execution contract.

- **Scale amplifies global scans.** Hunting checks can approach quadratic pawn work; wall searches scan all artificial buildings; jars multiply plant scans; pools issue a draw call per cell. Measure these with synthetic large-map populations.

## 3. UNLEVERAGED OPPORTUNITIES

- **Test the adapters around the kernels.** Add save/load cases for a half-complete sweep, carried ring payment, pending kill drag, occupied buried cell, missing history, and settings changed during a job. Arithmetic fuzzing cannot detect these failures.

- **Generate a settings audit from one schema.** Store default, bounds, application timing, dependencies, persistence key, and effect owner together. Use it to build controls and validation coverage. Show restart-required values separately from currently effective values.

- **Provide settings diagnostics.** Resolve biome-list entries, report unknown names, warn about overlapping wind thresholds, and show unavailable FlowWorks/track integrations and unresolved choir sources.

- **Expose structured readouts.** Return condition counters, sweep progress, ring wake reason, draw eligibility, and registry counts as structured values. Substring assertions such as “HackingSpeed” or “follow” do not verify the relevant numeric behavior.

- **Cache immutable lookup data.** Resolve choir sources, common defs, and reflection signatures once. Use local-cell queries for short-radius effects.

- **Make replacements transactional.** One helper could resolve output, validate placement, transfer saved identity, commit replacement, and preserve the source on failure across salvage, refit, hospice, and panels.

## 4. EXTENSIONS BEYOND THE MOD

- **Aerosol screening can become a shared campaign API.** Retain one coverage service and one toxic-exposure patch set. Consumers should register screens through a lifecycle-safe interface with explicit exposure categories and calibration behavior.

- **Hazard cleanup should own its sweep independently.** A reusable sweep engine could erase film, tracks, ash, or other deposits while guaranteeing batching and save persistence. Track rendering should be an optional subscriber.

- **Salvage and hospice can share identity-preserving conversion machinery.** Other wrecks and damaged machines need the same placement, payment, history, and failure-recovery guarantees.

- **Readable signs can share a signal system.** Silence, clicks, tracks, overlays, and inspection text could consume common hazard/predator signals, with cosmetic randomness isolated from simulation.

- **The sea-floor access rule is UNVERIFIABLE here.** No supplied code implements ship-only access or map transitions. Reusing these mechanics there should preserve the campaign’s existing ship access boundary and use its existing heat model; neither boundary can be certified from this bundle.