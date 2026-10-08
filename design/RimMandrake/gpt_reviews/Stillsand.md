## 1. DEBUGGING

Static review only; nothing was executed in RimWorld. Line numbers restart at the first line of each supplied file. “High confidence” means the defect follows from the supplied code; conditional engine or dependency behavior is identified explicitly.

1. **A gale returns its own newly abducted pawns.**  
   `Source/RM_DuneGale.cs:561, 924–929`  
   `Aftermath()` calls `ReturnAllFor`, which selects every carried record for this map. It does not distinguish pawns taken during this gale from earlier records. A pawn carried away immediately before the storm ends returns immediately, rather than after `returnDays` or the **next** gale.  
   **Minimal fix:** save an originating gale serial on each record; only a later gale may accelerate its return.  
   **Severity: medium. Confidence: high.**

2. **One failed return loses an entire selected batch.**  
   `Source/RM_DuneGale.cs:918–920, 926–938`  
   `TakeWhere` removes all selected records before the caller starts returning them. If the first `Return` throws, the remaining pawns have already lost their records. `Return` also removes a pawn from `WorldPawns` before checking whether a destination map exists. Failure can therefore leave a pawn neither spawned nor world-owned.  
   **Minimal fix:** process records individually; remove each record only after a completed return or explicitly handled terminal outcome. Retain world ownership until a valid destination is established.  
   **Severity: high. Confidence: high.**

3. **Return survival odds leak between unrelated gales and maps.**  
   `Source/RM_DuneGale.cs:845, 884, 920, 928`  
   `aliveChance` is one game-wide field overwritten by every abduction. Timed returns use the latest abduction’s probability; storm-end returns use the returning storm’s extension. Neither necessarily uses the probability belonging to that pawn’s abduction.  
   **Minimal fix:** save `returnAliveChance` per record, migrating old records from the existing component field.  
   **Severity: medium. Confidence: high.**

4. **Dead abductees explicitly do not return.**  
   `Source/RM_DuneGale.cs:960–966`  
   `LostDead` produces a letter and discards the record without returning a corpse. This contradicts the carry setting’s “always comes back, alive or not” behavior.  
   **Minimal fix:** preserve and return the corpse for this outcome; distinguish an unavailable body from a dead pawn.  
   **Severity: medium. Confidence: high.**

5. **The fallback return destination does not enforce ship-only sea-floor access.**  
   `Source/RM_DuneGale.cs:935`  
   A missing original map falls back to `Find.AnyPlayerHomeMap`. If a sea-floor map qualifies as a player home, this directly spawns the pawn there without a ship journey. Whether campaign sea-floor maps qualify is **UNVERIFIABLE** from the omitted map definitions.  
   **Minimal fix:** restrict fallback destinations to eligible surface maps; otherwise retain the pawn pending a valid return.  
   **Severity: high if that map qualification occurs. Confidence: high in the missing restriction; runtime applicability UNVERIFIABLE.**

6. **World-pawn retention after loading is not established.**  
   `Source/RM_DuneGale.cs:827–838, 858–867, 875–884`  
   The record saves a pawn reference, not pawn ownership. Post-load initialization does not re-add tracked pawns to `ForcefullyKeptPawns`. Whether Verse serializes that retention set, and whether `RemovePawn` clears it, are **UNVERIFIABLE** here. The warning branch also records a pawn even after determining it never entered `WorldPawns`.  
   **Minimal fix:** verify the exact Verse contracts, restore retention for valid loaded records, and establish durable ownership before committing an abduction record.  
   **Severity: high. Confidence: medium; engine-dependent.**

7. **Structure wear cannot achieve the configured MTB on ordinary large maps.**  
   `Source/RM_DuneGale.cs:380–405`  
   Scaling the MTB by `NumGridCells / samples` cannot overcome the sampling ceiling: each sampled cell receives at most one hit. On a 250×250 map, 30 samples every 250 ticks give a one-cell structure an expected sampling interval of at least roughly **208 hours**, even if every sample damages it. The configured MTB is eight hours. Larger footprints also receive more opportunities than smaller buildings.  
   **Minimal fix:** roll the configured hazard against eligible buildings, with staggered checks, rather than compensating through randomly sampled map cells.  
   **Severity: medium. Confidence: high.**

8. **Small successive sand movements never erase a track.**  
   `Source/RM_DuneTrackEraser.cs:70–78`  
   Erasure compares only the depth before and after one `SetDepth` call. Repeated changes of `0.04` can move an entire dune through a cell without any call reaching `0.08`. Gale aftermath provides a separate storm-end comparison, but does not repair normal moving-dune erasure.  
   **Minimal fix:** compare against the depth recorded when the print was made, or accumulate displacement while that print exists.  
   **Severity: medium. Confidence: high.**

9. **The track patch’s supposedly guarded initialization can fail outside its guard.**  
   `Source/RM_DuneTrackEraser.cs:43–44, 49–66`  
   `FieldRefAccess("map")` runs as a static field initializer, before the constructor’s `try`. A missing or incompatible field can fail type initialization before the intended diagnostic executes.  
   **Minimal fix:** initialize the field reference inside the guarded startup path and disable callbacks if initialization fails.  
   **Severity: medium. Confidence: high; whether the current field matches is UNVERIFIABLE.**

10. **Saved cave preservation records can prevent restoration of preservation.**  
    `Source/RM_CavePlace.cs:77–86`; `Source/RM_PreciousCaves.cs:357–363`  
    `frozenThings` survives loading, but `TryFreeze` immediately skips anything already registered. There is no post-load reassertion of `rot.disabled`. If Verse does not save that flag, registered items resume rotting permanently while still appearing owned by preservation. The flag’s actual serialization is **UNVERIFIABLE** from this bundle.  
    **Minimal fix:** reapply owned preservation state after load, or rebuild the ownership register and rescan.  
    **Severity: high. Confidence: medium; engine-dependent.**

11. **Cave preservation permanently modifies the corpse’s disappearance timer.**  
    `Source/RM_CavePlace.cs:35–45, 88–90`  
    Freezing writes `vanishAfterTimestamp = 0`; releasing only resets `rot.disabled`. The original timestamp is never restored when the corpse leaves, loses its roof, or preservation is disabled. Moreover, the assumption that **zero disables disappearance** is **UNVERIFIABLE** without the current `Corpse` implementation; zero could instead represent an already elapsed timestamp.  
    **Minimal fix:** verify the sentinel and use scoped suppression, or save and restore the timer with clearly defined elapsed-time handling.  
    **Severity: high. Confidence: high in the irreversible mutation; timer effect UNVERIFIABLE.**

12. **A storage building crossing the cave boundary preserves items outside the cave.**  
    `Source/RM_CavePlace.cs:63–68, 75–86`  
    Encountering one cave cell occupied by a storage building enumerates its entire slot group. `TryFreeze` does not call `InCave`. Outside items can be released at the beginning of a scan and frozen again later during the same scan.  
    **Minimal fix:** require `InCave(comp, t)` before acquiring preservation ownership. Enumerate each storage group once.  
    **Severity: medium. Confidence: high.**

13. **Older caves acquire an empty preservation footprint.**  
    `Source/RM_PreciousCaves.cs:323, 331–334, 357–361`  
    Loading a save without `caveCells` produces an empty list. The previous geometry handoff fields are unsaved, so a surviving `hasCave` flag cannot reconstruct the footprint through this code. Preservation and positional den detection silently stop working for those caves.  
    **Minimal fix:** introduce a save schema version and an explicit legacy-footprint migration or repair path.  
    **Severity: medium. Confidence: high for saves lacking the new field.**

14. **Cave tunnels can contain diagonal gaps between otherwise connected cells.**  
    `Source/RM_PreciousCaves.cs:548–562`; `Source/RM_PreciousCaveGeometry.cs`, `RayToOpen`  
    The ray rounds both coordinates independently. A diagonal ray produces transitions such as `(x,z) → (x+1,z+1)` without carving either orthogonal bridge cell. Radius-one and radius-two chambers do not widen the tunnel. The geometry therefore does not guarantee a cardinally connected entrance. Exact pawn corner-traversal behavior is **UNVERIFIABLE** here. Widening also uses the original shadow direction, rather than the successfully fanned tunnel direction.  
    **Minimal fix:** carve a supercover path with orthogonal bridges and derive widening from the chosen ray.  
    **Severity: medium. Confidence: high in the geometry defect; traversal outcome engine-dependent.**

15. **Shaping one outcrop can make the cave switch to another outcrop.**  
    `Source/RM_PreciousCaves.cs:492–510`  
    After shaping, the code reruns a global `LargestOutcrop`. If trimming makes the original smaller than another outcrop, the cave moves to that other outcrop while `rock`, its label, and its eventual floor material still describe the first.  
    **Minimal fix:** retain the shaped component’s identity, or recompute all material and naming data after selecting a different component.  
    **Severity: medium. Confidence: high.**

16. **Generic cave building placement validates only its center cell.**  
    `Source/RM_PreciousCaves.cs:237–248`  
    `FreeForItem` checks one cell even when the selected def is a multi-cell building. Its footprint can cross walls, other contents, or the map boundary. Actual collision handling depends on `GenSpawn`, but the required placement validation is absent.  
    **Minimal fix:** validate the complete occupied rectangle and required terrain before spawning buildings.  
    **Severity: medium. Confidence: high.**

17. **The wall-mark element can query outside the map.**  
    `Source/RM_CavePlace.cs:168–170, 218–225`  
    The selected floor cell is bounded; its cardinal neighbors are not. `IsNaturalRock` calls `GetEdifice` directly. The documented fallback use in ordinary set pieces can select cells at map edges.  
    **Minimal fix:** make `IsNaturalRock` return false for a null map or an out-of-bounds cell.  
    **Severity: medium. Confidence: high in the invalid query path; precise exception behavior UNVERIFIABLE.**

18. **The den quest can select an unrelated animal elsewhere on the map.**  
    `Source/RM_EventRemainder.cs:224–225`  
    `TryFindDen` matches pawn kind and faction across all spawned pawns, without checking the cave footprint or a recorded den occupant. A wandering animal can make an empty cave qualify, or become the quest target instead of its resident.  
    **Minimal fix:** save the den occupant reference; otherwise require membership in this cave’s footprint.  
    **Severity: medium. Confidence: high.**

19. **The claimed 30-mound cap is only a precondition, not a cap.**  
    `Source/RM_IncidentWorker_SandBusterEruption.cs:69, 80–81, 113–121`  
    At 29 existing mounds, an eruption can schedule several more. Pending tunnels do not count, so multiple eruptions can reserve additional mounds before earlier tunnels finish.  
    **Minimal fix:** clamp the requested count against `30 - existingMounds - pendingMoundTunnels`, and enforce that reservation during execution.  
    **Severity: high at scale. Confidence: high.**

20. **Leviathan retargeting runs every 750 ticks, not 250.**  
    `Source/RM_SandLeviathan.cs:414–423, 569`; `Source/Kernel/RM_LeviathanKernel.cs`, `ShouldRetarget`  
    Visits are processed only when `now % 30 == 0`; valid targets are reconsidered only when `now % 250 == 0`. Those conditions coincide every 750 ticks.  
    **Minimal fix:** save a per-visit last-retarget tick and compare elapsed time.  
    **Severity: medium. Confidence: high.**

21. **A fed leviathan can delete somebody else’s corpse.**  
    `Source/RM_SandLeviathan.cs:519–525, 610–648`  
    An increased kill counter triggers `TakeTheBody`, but the fallback chooses any corpse younger than 600 ticks nearby. If the actual victim has already been consumed, moved, or removed by the external swim kit, an unrelated fresh corpse is destroyed instead. Even `v.target.Corpse` is not proof that this leviathan killed that target.  
    **Minimal fix:** capture the actual victim from a kill notification and give one component responsibility for its removal.  
    **Severity: high. Confidence: high.**

22. **A lost pawn reference turns a completed arrival into another arrival.**  
    `Source/RM_SandLeviathan.cs:380–387, 423, 483–486`  
    Pending versus arrived is inferred solely from whether `v.pawn` exists. If a loaded visit loses that reference, it is classified as ready to arrive and generates a new pawn. There is no saved arrival phase to distinguish “not generated yet” from “generated and subsequently unavailable.” Whether a particular destroyed-pawn save produces this null reference is **UNVERIFIABLE** here. Null list entries also remain unfiltered and would fail at `v.Ext`.  
    **Minimal fix:** save an explicit visit phase, migrate old records, filter null entries, and treat a missing pawn in an arrived visit as terminal.  
    **Severity: high. Confidence: high in the ambiguous state representation; specific load trigger engine-dependent.**

23. **A disabled thumper still attracts incident arrivals.**  
    `Source/RM_Thumper.cs:98–104`; `Source/RM_SandLeviathan.cs:204–225`  
    `ChargedThumper` reads only `Charged`, which means fuel exists. It never reads `thumperEnabled`. Switching off thumpers stops their beats but leaves their priority over loud ships, pours, and colonists.  
    **Minimal fix:** use a shared “active caller” predicate that includes settings, fuel, and operational state.  
    **Severity: medium. Confidence: high.**

24. **Swimmer calls choose destinations without checking reachability.**  
    `Source/RM_Thumper.cs:63–73`  
    `CellNear` chooses the closest standable cell, even if a wall or disconnected region separates it from the swimmer. That candidate consumes a call slot and receives a forced job. Subsequent beats can repeatedly interrupt it with the same impossible journey.  
    **Minimal fix:** include `p.CanReach` in destination selection and retain a valid existing call job.  
    **Severity: medium. Confidence: high.**

25. **A gale clears wet cells but retains their attraction point.**  
    `Source/RM_StillsandWater.cs:285–290, 305–308`  
    `ClearAll()` empties `wetUntil` while leaving `lastPourCell` and `drawUntilTick` intact. Leviathans can continue choosing a supposedly erased pour for the rest of its draw duration.  
    **Minimal fix:** clear the pour location and expiry when the gale wipes the water state.  
    **Severity: medium. Confidence: high.**

26. **Still throughput discards completed-cycle overshoot.**  
    `Source/RM_SolarStill.cs:95`; `Source/Kernel/RM_SunKernel.cs`, `StillStep`  
    A completion returns zero rather than subtracting one. At rate 1.7 with a 6,000-tick cycle, 15 rare ticks accumulate 1.0625 cycles, then discard the excess. The rate slider therefore does not deliver its nominal proportional throughput. Added content permitting more than one cycle per rare tick loses whole cycles too.  
    **Minimal fix:** retain fractional remainder; process multiple completions with bounded work and fresh feed checks. If deliberate, expose the quantized effective rate.  
    **Severity: low now, medium with faster content. Confidence: high.**

27. **Still consumption is committed before output success is known.**  
    `Source/RM_SolarStill.cs:133–154`  
    Feedstock is destroyed before resolving water output. A missing water def produces nothing but still records debt. Failed placement is ignored and also records debt. The cycle progress has already reset.  
    **Minimal fix:** establish an output def and placement/holding path before consuming feed; book only successfully produced volume and retain failed output in durable storage.  
    **Severity: medium. Confidence: high.**

28. **Water accounting has incompatible production and ingestion semantics.**  
    `Source/RM_SolarStill.cs:154`; `Source/RM_StillsandWater.cs:84–92`  
    Still production books litres. Ingestion independently books one unit’s litres, regardless of units consumed. If output water carries `RM_CompWaterVolume`, the same water is charged again when drunk; multi-unit ingestion can also be undercounted. The shipped output comp wiring and any ledger-side compensation are **UNVERIFIABLE** because those files are omitted.  
    **Minimal fix:** define one charge event, carry provenance if needed, and use the actual consumed count for ingestion accounting.  
    **Severity: medium. Confidence: high in the conflicting call sites; shipped double charging UNVERIFIABLE.**

29. **“Witness” thoughts affect every spawned colonist.**  
    `Source/RM_SolarStill.cs:164–169`  
    `WitnessDeadDistilled` applies the memory map-wide, including pawns far away or behind opaque walls. There is no witness eligibility test.  
    **Minimal fix:** check the intended radius and visibility, or rename and document it as a colony-wide consequence.  
    **Severity: medium. Confidence: high.**

30. **A beam’s saved path loses the state used to calculate damage.**  
    `Source/RM_Verb_MirrorBeam.cs:52–53, 350, 356–365`  
    `path` is saved, but `pathCells` and `hitCells` are neither saved nor rebuilt. **If Verse resumes a saved burst**, the empty `pathCells` changes the divisor to one, while lost `hitCells` permits previously hit neighbor cells to be hit again. Effects are also not reconstructed. Whether the base verb resumes bursts is **UNVERIFIABLE** from the bundle.  
    **Minimal fix:** rebuild `pathCells` after load, persist hit history, and explicitly restore or terminate presentation state.  
    **Severity: high. Confidence: high in the missing state; resumed-burst applicability engine-dependent.**

31. **Beam curvature converts radians to degrees before calling a radians function.**  
    `Source/RM_Verb_MirrorBeam.cs:307`  
    Multiplying the sine argument by `57.29578f` produces rapid oscillations instead of the intended smooth curvature. `Mathf.Sin` takes radians. [Unity documentation](https://docs.unity.com/en-us/engine/6000.7/manual/scripting/programming-math/unity-engine-math/class-mathf)  
    **Minimal fix:** remove `* 57.29578f`.  
    **Severity: medium when curvature is nonzero. Confidence: high.**

32. **`beamTotalDamage` is not a stable burst damage budget.**  
    `Source/RM_Verb_MirrorBeam.cs:137–146, 350`  
    Every primary shot damages its cell, including repeated hits on the same cell, but damage is divided by the number of **unique path cells**. With \(N\) successful primary shots and \(U\) unique path cells, nominal primary damage can approach `beamTotalDamage × N/U`, before neighbor damage. Walls collapsing many shots onto one blocking cell create another concentration case.  
    **Minimal fix:** divide by shot count for a shot budget, or deduplicate primary hits and budget actual hit cells for a cell budget.  
    **Severity: medium. Confidence: high.**

33. **Beam visuals lack the bounds guard used by beam damage.**  
    `Source/RM_Verb_MirrorBeam.cs:156, 230–253`  
    The path includes width, deviation, and target drift. At a map edge it can leave bounds. `TryGetHitCell` guards its LOS predicate; `BurstingTick` does not, then creates targets and effects from the resulting cell. Exact exception behavior of those Verse helpers is **UNVERIFIABLE**.  
    **Minimal fix:** bound the visual path and apply the same guarded LOS predicate.  
    **Severity: medium. Confidence: high in the invalid-cell path.**

34. **Pawn and turret beams use different sunlight policies.**  
    `Source/RM_Verb_MirrorBeam.cs:98–109`  
    Turrets use pinned-sun elevation and the shade grid through `FactorAt`; pawn casters use celestial glow and roof/weather checks. Pawn beams never query cast shade. At identical exposure they can therefore have different availability and strength. External modifications to celestial glow are **UNVERIFIABLE**, but the shade omission is explicit.  
    **Minimal fix:** route both through the common sun policy, with explicit per-caster exceptions if intended.  
    **Severity: medium. Confidence: high.**

35. **Zuurrik burial observes one member but destroys the whole swarm.**  
    `Source/RM_MapComponent_Zuurrik.cs:191–208, 217–238`  
    Quietness is measured around `swarm[0]`. Other members can still have work elsewhere and nevertheless be destroyed. Conversely, inaccessible blood or an unusable corpse near the first member can keep the entire swarm active indefinitely.  
    **Minimal fix:** evaluate actionable work around all members or tracked feeding sites, and bury members individually when appropriate.  
    **Severity: medium. Confidence: high.**

36. **Zuurrik growth measures initial blood rather than food eaten.**  
    `Source/RM_MapComponent_Zuurrik.cs:212`  
    Fatness increases by at least one whenever burial completes, even if colonists cleaned everything and the swarm ate nothing. Corpses eaten do not contribute. This directly contradicts growth “by what this one ate.”  
    **Minimal fix:** accumulate actual feeding/filth-consumption notifications and use that saved amount.  
    **Severity: medium. Confidence: high.**

37. **The blood scan cap does not cap scanning work.**  
    `Source/RM_MapComponent_Zuurrik.cs:112–117, 144–149`  
    The limit counts accepted distinct cells, not examined filth. Large numbers of non-sand or duplicate blood entries still get scanned, with linear `Contains` checks. Cluster selection then performs up to 360,000 pair comparisons per poll, synchronized across maps. The first 600 accepted cells also bias detection against later clusters.  
    **Minimal fix:** use a cell hash set and spatial buckets; separately bound inspection work and stagger maps.  
    **Severity: medium at scale. Confidence: high.**

38. **The main settings panel cannot accommodate its supplied controls.**  
    `Source/RM_StillsandMod.cs:41–62`  
    The panel appends cave, water, swimming, sound, and track controls without a scroll view or `maxOneColumn`. Its content already exceeds a normal settings viewport. The gale and event panels use the same pattern while adding arbitrary def-driven rows. Controls can wrap into unseen columns or become inaccessible.  
    **Minimal fix:** apply the scroll implementation already used by glass-chain and skeleton settings; measure actual content height and enforce one column.  
    **Severity: medium. Confidence: high.**

39. **Horizon warnings alter drop-raid placement.**  
    `Source/RM_HorizonWarning.cs:129–138, 162–163`  
    Every raid worker qualifies, but unset `spawnCenter` is replaced with a pawn **edge-entry** cell. According to this file’s stated arrival-mode contract, center and cluster drops honor that preset too. The warning consequently changes those raids into edge-positioned drops. Exact vanilla arrival behavior is **UNVERIFIABLE** without the game code.  
    **Minimal fix:** restrict the edge warning to compatible arrival modes; preserve drop modes’ own placement rules.  
    **Severity: high if the stated arrival contract holds. Confidence: high in the unconditional override.**

40. **The forced-entry context is thread-local but not reentrant.**  
    `Source/RM_HorizonWarning.cs:74–90`  
    Every nested `IncidentWorker.TryExecute` clears the current thread’s forced entry, including unrelated incidents. Its finalizer also clears any outer context. Another mod triggering a nested incident before the outer entry lookup defeats the announced bearing.  
    **Minimal fix:** save the previous context in per-invocation Harmony `__state` and restore it in the finalizer.  
    **Severity: low currently, medium with interacting incident mods. Confidence: high.**

41. **Horizon patch startup has no isolation or exact signature selection.**  
    `Source/RM_HorizonWarning.cs:49–55`  
    All three patches are applied without target-null checks or exception handling. A failed later patch leaves an earlier partial installation. Name-only resolution also leaves overload selection exposed to drift. Injected names such as `result`, `extraValidator`, and `queued` must match the selected target contract. [Harmony argument-injection documentation](https://harmony.pardeike.net/v2/articles/patching-injections.html)  
    **Minimal fix:** resolve and validate all exact signatures first; install as a guarded group with rollback and reported status.  
    **Severity: medium. Confidence: high in the startup fragility; current target compatibility UNVERIFIABLE.**

The following requested checks cannot be closed from this bundle:

- **Ledger Scribe compatibility:** `RM_WaterLedger.cs` is omitted. The kernel comment claiming unchanged keys does not demonstrate unchanged keys, defaults, ownership, or migrations.
- **Settings bootstrap:** several `Mod` subclasses assume every subclass is instantiated. Actual RimWorld loader behavior and packaging are **UNVERIFIABLE** here. Failure of that assumption would also affect constructor-installed sun-table patches.
- **XML loading and wiring:** most defs and patches are omitted. Ticker types, comp attachment, workgiver/job definitions, recipe availability, stat-part installation, dependencies, and beam damage definitions are **UNVERIFIABLE**.
- **Double patching and ordering:** no complete assembly startup/build configuration or installed patch inventory is supplied. Duplicate installation cannot be established or excluded.
- **Validation coverage:** `validation.py` and the other claimed fuzz harnesses are omitted. Their assertions, exit codes, compilation inputs, and mutation sensitivity are **UNVERIFIABLE**.
- **“Never ignites”:** removing explicit ignition calls does not establish the behavior of the omitted `beamDamageDef` and its damage worker.
- **Outdoor beam heat:** whether `PushHeat` produces meaningful thermal effects at exposed sand cells requires the game’s temperature behavior; it is **UNVERIFIABLE** here.

## 2. LIKELY FUTURE COMPLICATIONS

- **Save references need saved phases and ownership rules.** The gale record and leviathan visit currently rely on referenced objects remaining available. Removed defs, butchered bodies, abandoned maps, and cross-map movement need explicit terminal states and migrations. Preserve existing Scribe keys when adding these states.

- **Def-driven settings need stable identifiers and migration.** Cave overrides, emergence switches, and incident odds use names as permanent keys. Renaming a def/key silently abandons its settings. Duplicate emergence keys couple unrelated rows. Maintain aliases and validate uniqueness.

- **New content can supply invalid numerical configurations.** `RM_LedgerBook.Pay` accepts negative litres and then increases debt while decreasing paid totals. `Draw` accepts negative or nonfinite values. Other kernels assume valid intervals, weights, thresholds, and burst counts. Validate at def/settings boundaries and protect the public kernels.

- **Global postfixes remain order-sensitive.** Another postfix can re-enable a recipe or table after Stillsand disables it. `RM_StatPart_SunPowered.TransformValue` divides out outdoor/temperature penalties without establishing that those penalties were actually applied exactly once. Other stat mods can change that assumption.

- **Reflection sits on potentially hot paths.** `RM_DriftSwim.DuneFieldActive` invokes reflection and allocates an argument array during swim queries. `RM_LoudDraws.First` scans the entire ThingDef database on each lookup (`RM_EventRemainder.cs:172–190`). More swimmers, incidents, and content defs amplify these costs. Cache delegates and opted-in def sets.

- **Shared context is unsafe for nested or parallel generation.** `RM_PreciousCaveContext.Current` is global (`RM_PreciousCaves.cs:96`), and furnishing restores it to null rather than restoring a previous context. Nested generation can lose an outer cave context. Actual concurrent use is **UNVERIFIABLE**; the field provides no protection.

- **Arrival promises are disconnected from actual incident completion.** Horizon plumes expire at the scheduled tick (`RM_HorizonWarning.cs:230`), while the incident may retry for another hour or never execute. Settings changes between announcement and execution can also change bearing enforcement. Track pending arrival identity and final outcome.

- **Water interoperability needs units and provenance.** `WaterDef()` substitutes a DBH bottle by name (`RM_SolarStill.cs:159–161`) and assumes one item per litre. Bottle volume, cooling ingestion effects, and debt hooks are **UNVERIFIABLE**. Hydration appraisal similarly needs adapters rather than assuming every need containing “Thirst” has compatible percentage semantics.

- **Destructive placement needs recoverable output.** Dust-devil lifting despawns an item before trying two placements; failure of both has no durable holding path. Skeleton conversion destroys the corpse before placing the skeleton. Added large buildings and crowded maps make these failure paths more likely.

- **Disabling systems can strand existing state.** Zuurrik’s master switch prevents burial processing as well as new wakes (`RM_MapComponent_Zuurrik.cs:84–96`). The rumble switch is read only while startup mutates external extensions. Settings need an explicit distinction between stopping new events, stopping ongoing effects, and requiring restart.

## 3. UNLEVERAGED OPPORTUNITIES

- **Build offline validation around cross-component failures.** Highest-value cases are: a failing first pawn return in a multi-record batch; a resumed beam burst; a lost reference after arrival; diagonal cave entrances; cumulative subthreshold sand movement; 29 mounds plus pending tunnels; and complete producer→consumer water accounting. Kernel-only tests cannot establish those behaviors.

- **Add an exact-assembly compatibility check.** Compile the whole production assembly against pinned RimWorld 1.6 and campaign dependencies. Reflect every Harmony target, overload, injected argument, and private field. Report each feature as installed, unavailable, or failed. This would expose uncertainty before loading a save.

- **Make XML validation semantic.** Beyond parsing, check cross-references, runtime class inheritance, required comps, ticker types, complete building footprints, finite ranges, unique settings keys, optional-def fallbacks, and that each setting has a reachable consumer.

- **Use real mutation tests.** `SkeletonSelfTest.Program.PlantedBreak` exercises a separate deliberately stuck calculation; it does not mutate production and demonstrate that the suite fails. Mutate the compiled production threshold/state transition and require a failing test process.

- **Expose operational status in settings.** Include patch availability, missing optional consumers, pending returns/visits, restart requirements, effective rates, and explicit “new maps only” scope. Add search, section navigation, reset-to-def defaults, and calculated relative cave-row probabilities.

- **Register actual state changes once.** A committed sand-change notification could drive tracks, singing dunes, burial refresh, and wet-sand erasure. `Patch_SlipFace` currently observes a requested target before the dune engine decides whether to commit it; an actual-change hook avoids false sound/warning events.

- **Preserve outcomes as records.** A small saved event history—abducted pawn, actual victim, return result, den occupant, and arrival cancellation—would support readable signs, reliable letters, diagnostics, and migration without repeated proximity guesses.

## 4. EXTENSIONS BEYOND THE MOD

- **Campaign-wide map-entry policy.** Centralize eligible destination maps and required transport. Gale returns, rescue incidents, creature arrivals, and ship landings should share the rule that the sea floor is accessible only by ship.

- **Reusable sunlight service.** Export one exposure query containing elevation, roof, cast shade, weather attenuation, and reason. Other solar machinery and reflected-light creatures can consume it. Thermal consequences should remain in vanilla temperature and damage systems.

- **Reusable carried-pawn lifecycle.** The repaired gale registry could support kidnapping, washed-away survivors, rescue returns, and off-map expeditions. Reuse requires durable pawn ownership, explicit phases, transactional completion, and save migrations.

- **A generic place record for caves and dens.** Save geometry, occupant identity, claimed state, and preservation policy independently from furnishing. Other campaign mods could add shrines, lairs, shelters, or wreck interiors without duplicating cave bookkeeping.

- **A shared volume/provenance contract.** Water-producing items, stills, drinking, pouring, thumpers, and upper-tier theology can use explicit litres and one accounting event. This would prevent both conversion errors and debt duplication.

- **Arrival warnings as a service rather than a broad interception.** Other mods could supply arrival mode, entry constraints, timing, and cancellation callbacks. That supports caravans and migrating giants without rewriting drop placement or guessing which entry lookup belongs to an incident.