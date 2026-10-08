## 1. DEBUGGING

Static review only; nothing was executed in game. Line numbers count from the first line of each inlined file. Several files—including `validation.py`, the quest XML, important ThingDefs, and registration patches—are omitted, so their behavior is **UNVERIFIABLE**.

1. **Moderate eye damage prevents ordinary multi-hit permanent kills.**  
   `Source/RM_CompTentacleEye.cs:59` immediately calls `DriveOffMapWide()`, which destroys the eye. Once accumulated damage crosses 40%, the player cannot continue toward 85%; permanent killing effectively requires a hit that jumps directly across the severe threshold.  
   **Minimal fix:** accumulate damage throughout the withdrawal window; resolve light/moderate outcomes when it expires, while allowing severe damage to resolve immediately.  
   **Severity: high. Confidence: high.**

2. **Light eye retreat leaves the rest of the Great Emergence active.**  
   `Source/RM_CompTentacleEye.cs:107` only extends the cooldown and destroys the eye. The spawned lashes and snares remain, contradicting the emergence letter’s promise that driving off the eye ends the attack (`Source/RM_MapComponent_TentacleWatch.cs:263`).  
   **Minimal fix:** have eye retreat withdraw the emergence’s other limbs. Calling `DriveOffAllLimbs()` is the smallest implementation if the consequence should remain map-wide.  
   **Severity: medium. Confidence: high.**

3. **Missing production-clock entries permanently disable that product.**  
   `Source/RM_CompCapturedSpecimen.cs:138` substitutes the current tick when a product lacks a dictionary entry. Its production window is therefore zero on every check; the entry is written only after a successful roll. This affects new products added to existing tanks, missing older-save data, and product-def replacements.  
   **Minimal fix:** initialize missing entries once during post-load reconciliation, or insert an entry before calculating its first window.  
   **Severity: high. Confidence: high.**

4. **Scribed limb action timers are overwritten after loading.**  
   `Source/RM_CompTentacleLimb.cs:40` resets `ticksUntilAction` for porter, lash, and snare regardless of `respawningAfterLoad`. A porter one tick from depositing gets another full random delay; saving repeatedly postpones actions. The porter also consumes a new random roll during load.  
   **Minimal fix:** initialize those timers only for fresh spawns; rebuild sentinel registration independently.  
   **Severity: medium. Confidence: high.**

5. **Tank production teaches even when placement fails.**  
   `Source/RM_CompCapturedSpecimen.cs:147` ignores `GenPlace.TryPlaceThing()`’s result, then sets `taught` and announces successful production. The product clock also advances despite no delivered product.  
   **Minimal fix:** gate teaching on successful placement and explicitly choose whether failed placement consumes the production event or remains pending.  
   **Severity: medium. Confidence: high.**

6. **Escape uses a different occupant resolver from release.**  
   `Source/RM_CompCapturedSpecimen.cs:198` reads `Props.occupantKindDefName` directly; release uses `YoungKind(Props)`, which follows `occupantLikeTank`. A linked tank can release one species but escape another, particularly when ownership changes or brood ransom is disabled and a display tank enters the hostile escape path.  
   **Minimal fix:** use `YoungKind(Props)` for escape too, and validate the resolved kind and required pawn comp.  
   **Severity: medium. Confidence: high.**

7. **Failed occupant resolution still consumes the captive.**  
   `Source/RM_CompCapturedSpecimen.cs:354` and `:392` clear `occupied` before checking whether a kind exists. Display release can additionally charge goodwill and permanently mark the settlement’s tank freed without spawning anything. Escape similarly destroys the tank before its null-kind check at `:198`.  
   **Minimal fix:** resolve and validate the occupant before committing the state transition; report configuration failure without deleting the captive.  
   **Severity: medium. Confidence: high.**

8. **A tamed escaped captive can still vanish and reinstall the deep.**  
   `Source/RM_CompEscapedCaptive.cs:91` installs any armed pawn reaching registered water. The faction cancellation at `:123` applies only to deliberately released pawns. An escaped animal tamed before arrival remains armed.  
   **Minimal fix:** cancel `armed` when the escapee gains a faction, using the same policy as deliberate release.  
   **Severity: medium. Confidence: high.**

9. **Water selection checks reachability too late.**  
   `Source/RM_CompEscapedCaptive.cs:211` chooses the geographically nearest preferred pool, then checks only that cell and its eight neighbors. If that pool is enclosed or inaccessible, a farther reachable pool—or ordinary water—is never considered. The animal retries the same impossible destination indefinitely.  
   **Minimal fix:** select among reachable shoreline candidates, continuing to subsequent pools when the first candidate fails.  
   **Severity: medium. Confidence: high.**

10. **Water arrival can succeed across blocked diagonal corners.**  
    `Source/RM_CompEscapedCaptive.cs:158` treats any adjacent water cell as arrival, without checking an accessible boundary or line of sight. Two intervening walls can separate a diagonally adjacent pawn from the pool while still awarding the return.  
    **Minimal fix:** require a traversable shoreline connection or a valid touch path before arrival.  
    **Severity: medium. Confidence: high.**

11. **Great Emergence measures total map water, then chooses any pool.**  
    `Source/RM_MapComponent_TentacleWatch.cs:200` uses `pools.Count`, not a connected cluster’s size. Twelve separate two-cell pools satisfy a threshold of 24. `SpawnGreatEmergence()` can then choose one of those tiny pools, despite the claimed “large pool” condition. Pressure is also shared across all pools.  
    **Minimal fix:** identify connected pool clusters, evaluate eligibility per cluster, and choose a seed from an eligible cluster.  
    **Severity: medium. Confidence: high.**

12. **Great Emergence repeatedly selects the same spawn cells.**  
    `Source/RM_MapComponent_TentacleWatch.cs:251` calls `RandomNearbyPoolCell()` repeatedly, but `:271` deterministically returns the nearest cell other than the seed. All additional limbs therefore select the same cell. Bloom then spawns on the seed already used by the first limb at `:260`. No footprint or occupancy check exists.  
    **Failure:** crowding is certain; whether buildings replace, wipe, reject, or overlap one another is **UNVERIFIABLE** because the tentacle defs and engine spawn behavior are not supplied.  
    **Minimal fix:** choose distinct valid footprints, reserve them during construction of the encounter, and announce only successfully spawned payloads.  
    **Severity: high if these are mutually exclusive buildings; otherwise medium. Confidence: high on repeated coordinates, medium on consequences.**

13. **Suppression does not deliver the behavior described to the player.**  
    `Source/RM_MapComponent_TentacleWatch.cs:426` only extends the ambient clock. Existing lashes still attack and existing porters still deposit. `ForceEmergenceNear()` at `:368` explicitly bypasses that clock. Moreover, fouling one cell suppresses ambient spawning across the entire map, because there is one deadline and no pool identity.  
    **Minimal fix:** withdraw existing affected limbs and distinguish chemical suppression from ordinary encounter cooldown if fire should respect chemical suppression. Either implement per-pool suppression or state clearly that the treatment affects every pool on the map.  
    **Severity: medium. Confidence: high.**

14. **Fouling jobs can spend charges after cancellation or duplicate another job.**  
    `Source/RM_JobDriver_FoulPool.cs:24` reserves the suppressant but not the destination. At `:61`, the job ignores whether removing the designation succeeded and consumes charges anyway. Two workers using different stacks can complete the same designation; a cancelled or terrain-replaced target also remains actionable.  
    **Minimal fix:** reserve the destination and recheck designation, registered water, and applicable watch component immediately before consumption.  
    **Severity: medium. Confidence: high.**

15. **The suppressant finder repeatedly chooses forbidden material.**  
    `Source/RM_WorkGiver_FoulPool.cs:60` checks stack count and reservation but not forbidden status. The job’s first goto toil rejects forbidden material. A nearer forbidden stack can therefore keep winning selection over a usable farther stack, producing repeated failed jobs.  
    **Minimal fix:** filter forbidden stacks in the finder and propagate the intended forced-work policy.  
    **Severity: medium. Confidence: high.**

16. **Lure restraints survive removal from the stake and can survive recovery.**  
    `Source/RM_CompLureStake.cs:123` unregisters a despawned bait pawn without removing `RM_LureStaked`. If that pawn is carried away, moved, or later replaced at the stake, it can retain permanent incapacitation. Recovery does not repair this: `Source/RM_KurrethColumn.cs:176` removes only `RM_KurrethBound`.  
    **Minimal fix:** detach the stake and remove its restraint when bait leaves its valid position/map; strip the lure restraint explicitly when stolen bait is restored.  
    **Severity: high. Confidence: high on the missing cleanup paths.**

17. **The lure registry misses reactivation and ordinary respawning.**  
    `Source/RM_CompLureStake.cs:101` re-registers only on load. Its tick code at `:123` handles live-to-inactive transitions but never inactive-to-live transitions. A carried pawn dropped again can become `HasLiveBait` without returning to the raid registry. Also, `HasLiveBait` at `:34` accepts a pawn spawned anywhere, including another map.  
    **Minimal fix:** define bait validity using map, position, restraint, and stake state; synchronize registration on both transitions and every valid stake spawn.  
    **Severity: medium. Confidence: high.**

18. **Hauling commits staking without confirming delivery.**  
    `Source/RM_JobDriver_HaulToStake.cs:70` ignores the drop result, then calls `TryStake(Victim)` at `:74`. `TryStake()` itself does not require a living, spawned pawn beside that stake. A failed drop can clear the designation and apply the permanent restraint while delivery has not succeeded.  
    **Minimal fix:** require successful dropping and validate the pawn’s resulting map and distance before staking.  
    **Severity: medium. Confidence: high.**

19. **A later first wave overwrites an earlier owed second wave.**  
    `Source/RM_MapComponent_TwoFrontLure.cs:161` writes one pending-wave slot, while the hourly tick continues launching first waves. If another first wave schedules a follow-up before the previous follow-up arrives, the old faction, origin, and deadline disappear—including from subsequent saves.  
    **Minimal fix:** prevent overlapping encounters or replace the slot with a scribed queue of encounter records.  
    **Severity: medium. Confidence: high.**

20. **Two waves can still arrive on the same tick.**  
    `Source/RM_MapComponent_TwoFrontLure.cs:87` processes a due second wave and then continues to the first-wave roll. That roll can spawn another column immediately, contradicting “never both at once.”  
    **Minimal fix:** return after successfully spawning a pending wave, or enforce a minimum interval between all wave arrivals.  
    **Severity: medium. Confidence: high.**

21. **The displayed timing ranges differ from actual timing.**  
    `Source/RM_MapComponent_TwoFrontLure.cs:94` imposes a 0.05-day minimum: the “1 hour” setting actually becomes 1.2 hours. At `:160`, equal delay endpoints become a 500-tick-wide range. Processing only every 2500 ticks further rounds arrival upward by almost an hour.  
    **Minimal fix:** express the MTB directly in hours; honor equal endpoints; check pending deadlines more frequently than the first-wave roll.  
    **Severity: low. Confidence: high.**

22. **Raid origin does not establish either bait targeting or opposite actual entrances.**  
    `Source/RM_MapComponent_TwoFrontLure.cs:196` derives directions from the stake position, not the first wave’s actual entry edge. Fallback entry selection can invalidate the opposite-front relationship. At `:213`, the assault/theft lord receives no bait target. The code establishes an arrival trigger, but does not establish that either column first pursues the offered pawn. Actual target selection is **UNVERIFIABLE** from the omitted/dependency AI.  
    **Minimal fix:** store the actual first entry edge and add an explicit initial bait objective before normal assault/theft behavior.  
    **Severity: medium. Confidence: high on missing information flow.**

23. **The hive generator creates no dungeon enclosure.**  
    `Source/RM_GenStep_AntHiveDungeon.cs:192` and `:210` paint roofs and optional terrain. They neither clear obstructing rock/buildings nor construct surrounding walls. On open terrain the “rooms” are roof patches that can be entered from any direction; a resin plug can be walked around. In existing rock, painting a corridor does not excavate it. Roof-support behavior is **UNVERIFIABLE**, but no support is constructed here.  
    **Minimal fix:** plan and excavate walkable interiors, build enclosing walls and supported roofs, then validate room connectivity before spawning residents.  
    **Severity: high. Confidence: high.**

24. **The water-distance field is effectively a boolean toggle.**  
    `Source/RM_GenStep_AntHiveDungeon.cs:121` and `:172` only ask whether the center is itself registered water. A value of 12 provides the same exclusion as 0.01. Room footprints and connecting corridors can overlap pools even when their centers pass.  
    **Minimal fix:** enforce clearance against registered water across every planned room/corridor footprint.  
    **Severity: medium. Confidence: high.**

25. **The room chain permits loops, duplicate centers, and queen-less hives.**  
    `Source/RM_GenStep_AntHiveDungeon.cs:178` accepts candidates without checking earlier rooms, separation, standability, or corridor feasibility. A reverse hop can return to the entrance. If placement stops immediately, the one-room result passes the `rooms.Count == 0` check at `:73`, but population begins at room index 1, so no queen is generated.  
    **Minimal fix:** reject overlapping/backtracking geometry and inaccessible corridors; require a minimum viable chain before committing the hive.  
    **Severity: medium. Confidence: high.**

26. **Freeing bound animals ignores physical access and some defenders.**  
    `Source/RM_KurrethColumn.cs:164` requires only Euclidean proximity. A colonist behind a wall or resin plug can free an animal through it. The guard test at `:168` recognizes only the `RM_Kurreth` race, allowing other defender races introduced through the hive extension to be ignored.  
    **Minimal fix:** require accessible touch range and identify guards through a defender tag/extension rather than one race name.  
    **Severity: medium. Confidence: high.**

27. **Quest success means “no binding hediff,” not “recovered.”**  
    `Source/RM_KurrethColumn.cs:394` succeeds whenever every living victim lacks `RM_KurrethBound`. `SpawnBound()` explicitly declines already-spawned victims; `SpawnCamp()` still changes phase. A victim elsewhere, a failed handoff, or a mod removing the hediff can therefore satisfy recovery without being rescued from this camp/hive.  
    **Minimal fix:** track successful placement and explicit freeing for each victim; reconcile exceptional ownership changes separately.  
    **Severity: medium. Confidence: high.**

28. **Camp placement discards the cell-search failure result.**  
    `Source/RM_KurrethColumn.cs:296` passes `centre` as an out parameter and ignores the boolean result. The subsequent spawn calls use that value even if the search failed. Initializing it to `map.Center` does not preserve that fallback across an out assignment.  
    **Minimal fix:** branch on failure and select a validated fallback before changing pawn ownership or spawning guards. The helper’s exact failure output is **UNVERIFIABLE** here.  
    **Severity: medium. Confidence: high on unchecked failure.**

29. **“Lost forever” does not finalize the held pawns.**  
    `Source/RM_KurrethColumn.cs:439` sends a letter and signal, but does not remove victims from the kidnap tracker/world-pawn storage or destroy them. The no-hive timeout uses this path; the hive deadline separately destroys bound victims at `:364`. These are materially different terminal ownership states. Whether omitted quest XML performs additional cleanup is **UNVERIFIABLE**.  
    **Minimal fix:** centralize loss finalization, preserving freed victims and explicitly disposing of or retaining the remaining held victims according to the declared outcome.  
    **Severity: medium. Confidence: high on the C# omission; medium overall.**

30. **Theft letters and quests are batched by time, not column.**  
    `Source/RM_KurrethTheft.cs:256` has one map-wide pending list and deadline. `:326` makes one quest from the entire batch. Two columns stealing within 600 ticks become one column; a slower column stealing across multiple windows becomes multiple quests. `:321` describes every victim using the last theft’s exit direction.  
    **Minimal fix:** group pending thefts by captured lord/encounter ID and finalize each column independently. Pass the lord ID directly from its notification rather than rediscovering it through the carrier.  
    **Severity: medium. Confidence: high.**

31. **The path cache survives games and never removes carriers.**  
    `Source/RM_KurrethTheft.cs:119` is a static dictionary with no removal or reset. The 40-sample limit bounds each entry, not the number of entries. It retains stale paths across loads and separate games in the same process; reused pawn IDs can inherit another game’s trail. The comment that loading falls back to a straight line is therefore unreliable.  
    **Minimal fix:** make the cache encounter/map scoped, remove entries on carrier departure/death, and discard it when rebuilding runtime state.  
    **Severity: medium. Confidence: high.**

32. **Oil-boil weather and its mechanics disagree for up to 249 ticks.**  
    `Source/RM_OilBoil.cs:248` synchronizes the condition only every 250 ticks. Shots during the initial weather window cannot flash the haze; after weather exit or disabling the setting, yield and sparks remain active until synchronization. The yield patch at `:320` checks neither the toggle nor current weather.  
    **Minimal fix:** synchronize on weather transitions and use one authoritative active-state predicate for sparks and yield.  
    **Severity: medium. Confidence: high.**

33. **Lightning is recorded as an attribution timestamp, not a spark.**  
    `Source/RM_OilBoil.cs:359` only writes `lastLightningTick`. The condition later scans existing fires at `:169`; a strike that creates no fire has no direct haze ignition path. A strike on another map can also relabel an unrelated local fire as lightning because the timestamp is global. Whether each vanilla strike necessarily creates a qualifying fire is **UNVERIFIABLE**.  
    **Minimal fix:** spark the actual struck cell on its actual map; keep attribution attached to that event instead of a static timestamp.  
    **Severity: medium. Confidence: high on the missing direct path and global attribution.**

34. **The natural-placement checkbox cannot enable natural placement.**  
    `Defs/BiomeDefs/RM_FeverWood.xml:45` fixes `generatesNaturally` to false. The setting only changes the worker score. As shipped, switching the checkbox on cannot deliver its advertised world-generation behavior.  
    **Minimal fix:** either apply the setting to `generatesNaturally` before world generation or describe it as a scoring gate that requires an external def change.  
    **Severity: medium. Confidence: high.**

35. **Heat is gated by an undeclared, different package.**  
    `Defs/BiomeDefs/RM_FeverWood.xml:186` puts `RM_SunHeatExtension` behind `MayRequire="mandrake.rm.biomes"`, although the class belongs to the declared Creature Behaviors dependency. A mod list satisfying FeverWood’s declared dependencies can silently omit this heat configuration. Whether the additional package is present in the campaign is **UNVERIFIABLE**.  
    **Minimal fix:** remove the additional gate if the declared dependency provides the complete mechanism; otherwise declare and explain the actual requirement. Preserve the shared vanilla-temperature route for the campaign’s one kind of heat.  
    **Severity: medium. Confidence: high on the packaging mismatch.**

36. **The wreck-field definition has an undeclared external type requirement.**  
    `Defs/MapGeneration/RM_FeverWoodWreckField.xml:12` unconditionally names `RimMandrake.Wreckage.RM_GenStep_WreckField`. Neither that implementation nor a Wreckage dependency appears in the bundle’s source or `About.xml`. Its density def is external too.  
    **Minimal fix:** declare the required package or gate the entire optional GenStepDef and its registration on that package. Whether another declared dependency supplies it transitively is **UNVERIFIABLE**.  
    **Severity: high for a minimal declared-dependency installation. Confidence: high on the undeclared requirement; medium on actual load failure.**

37. **Map scans are synchronized and repeat even where no pools exist.**  
    `Source/RM_MapComponent_TentacleWatch.cs:342` scans every cell on every map at daily cache expiry, including maps with zero registered water. Released captives independently scan every cell at `Source/RM_CompEscapedCaptive.cs:194`; successful searches do not set a retry cooldown, so repeatedly interrupted travel can rescan every 60 ticks. All those checks use shared tick boundaries.  
    **Minimal fix:** consume the tenant’s registered-water collection, invalidate it on terrain changes, stagger checks, and throttle successful destination searches too.  
    **Severity: medium at campaign scale. Confidence: high.**

Several critical runtime checks remain **UNVERIFIABLE**, rather than established defects:

- **Fatal-hit callbacks:** eye/limb damage handlers obtain `parent.Map` after damage. If lethal destruction precedes the callback, harvesting and map-wide consequences can be lost. Verify the actual 1.6 ordering and retain the map/position through the destruction path.
- **Harmony coverage:** `RM_OilBoil.cs:327` targets one exact `Launch` overload; `:342` targets base `Projectile.Impact`. Coverage of overriding projectile classes and replacement combat systems is not established. The mishandle target’s current signature/callers are likewise unverified.
- **Double patching and ordering:** only one bootstrap is shown. There is no evidence of an actual duplicate patch, but no supplied runtime patch inventory establishes ownership, target resolution, or ordering against other mods.
- **Cask consumption:** the omitted young-cask def determines whether opening consumes exactly one cask and how failed `DoEffect()` paths interact with consumption.
- **Tick wiring and def loading:** omitted tank, tentacle, pawn, and stake defs determine ticker types, required comps, inheritance, and cross-reference resolution. GenStep/designator/workgiver registration is not supplied.
- **Save-key renames and validation coverage:** no pre-refactor save schema or validation script is present. Historical compatibility and the claimed offline checks are unverified. No explicit worker-thread execution is shown; an actual thread-safety failure cannot be asserted.

## 2. LIKELY FUTURE COMPLICATIONS

- **The generic captivity component is mechanically tied to one species’ campaign system.** `RM_CompCapturedSpecimen.cs:147` teaches the pool warning, while release routes to the deep and gift machinery. Adding venom, egg, or blood vessels risks counting unrelated captives as the deep’s young and triggering unrelated ecological consequences. Separate production/containment from occupant-specific release, tally, and teaching policies.

- **Pending obligations are fragile across settings changes and placement failure.** `RM_MapComponent_TentacleWatch.cs:184` removes due gifts before checking the ransom toggle or successful placement. Disabling the setting while gifts mature cancels them permanently; an unsuccessful grant also has no retry. Decide and expose whether toggles pause or cancel already-created obligations.

- **Saved metadata will outlive its defining content.** Product clocks use ThingDefs; settlement overrides freeze absolute counts; keeper selection uses settlement names; hive alarms retain a saved tag. Def replacement, town renaming, or changing defender tags can leave old saves with obsolete behavior. Explicit migration rules are needed for these identities, not just null-list repair.

- **Hive centers are insufficient persistent geometry.** Sealing, farm placement, and raid-back arrival all infer structure from centers. Content adding branches, destroyed passages, expanded rooms, or multiple hives will need recorded interiors, corridors, entrances, and hive identity. Nearest-center logic cannot reliably identify “behind the intruder.”

- **Ambient persistence needs a population policy.** No lifetime or active-limb cap is visible in the supplied comps. If the omitted defs provide neither, passive feelers/sentinels and unchallenged attackers accumulate indefinitely. Their actual lifetime is **UNVERIFIABLE**.

- **Sound suppression has competing owners.** `RM_MapComponent_TentacleWatch.cs:550` restarts ambient sound without consulting Creature Behaviors’ hush state. The source acknowledges one overlap, but map switching and additional silence sources broaden it. A shared reason-counted suppression service would avoid premature restoration.

- **Map-scoped assumptions limit reuse.** `RM_OilBoil.cs:192` flashes on the first affected map, although the condition tick iterates all affected maps. Registering the condition globally would process a spark on the wrong map. Recovery similarly requires the original map to remain loaded; unloading a persistent hive can turn recoverable theft into a terminal loss.

- **Static state and events need lifecycle boundaries.** The theft path cache already demonstrates leakage. Hidden faction caches and alarm subscriptions also need explicit game/session ownership if initialization can repeat. Parallel tick mods would additionally require a documented main-thread contract; current threaded interaction is **UNVERIFIABLE**.

## 3. UNLEVERAGED OPPORTUNITIES

- **Make offline validation exercise the adapters, not only the arithmetic.** The strongest regression cases here are sequences: missing product key → hourly check; save/load one tick before porter action; repeated small eye hits; unreachable nearest pool with reachable second pool; overlapping raid schedules; failed drop; stolen staked animal → recovery. Kernel-only compilation cannot establish those behaviors.

- **Add a complete def-wiring audit.** Resolve XML classes against the built assemblies, check cross-references and inheritance, verify required comps/tickers, and inspect registration patches. Run it against both declared dependencies and the campaign mod list. `validation.py`’s current capabilities remain **UNVERIFIABLE**.

- **Validate Harmony targets offline.** Resolve each exact target against the installed 1.6 assembly and enumerate relevant overrides. Runtime startup should report the intended targets and patch owners. This catches drift before a failed `PatchAll()` becomes an unexplained missing mechanic.

- **Turn settings into a usable control surface.** Add search, sections, per-section reset, numeric entry, units, dependent-control disabling, and explicit “new maps only” labels. Normalize linked ranges when edited instead of silently interpreting inverted values elsewhere. Show effective ambient probability, raid timing, and whether a campaign XML override supersedes a slider.

- **Expose existing state in inspection text.** The machinery already knows pressure, suppression remaining, porter anger, owed gifts, and pending raid arrival. Showing these would make settings tuning and bug reports substantially more diagnostic without inventing colony-wealth protection.

- **Give important consequences typed records.** A scribed pending-event object would replace three parallel gift lists and support retries, versioning, origin identity, and cancellation reasons. The same small abstraction could carry raid waves and theft batches.

- **Separate diagnostics from destructive proof actions.** Read-only state dumps could report pool clusters, active limbs, registry membership, captive flags, and pawn ownership. Existing proof methods generate animals, alter conditions, and force deadlines; they do not themselves establish assertions or restoration. The old smoke-test statement in `About.xml` should not serve as evidence for the refactored build.

## 4. EXTENSIONS BEYOND THE MOD

- **A shared captive-vessel framework** could serve other campaign animals once containment is separated from deep-specific consequences. Products, upkeep, escape, and captive memory are reusable; release destinations and ecological effects should be supplied by content.

- **A registered-water topology service** could support shoreline jobs, suppression, pool encounters, rescue windows, and other biome hazards. One authoritative collection with connected components would replace repeated scans and inconsistent interpretations of a “pool.”

- **A shared living-bait handoff mechanism** could serve traps, kidnappings, sacrifices, and rescue quests. It should own attachment, restraint cleanup, transfer, and explicit recovery state across maps and world-pawn storage.

- **The reaction event system can support content-driven dungeon responses**—reinforcement chambers, alarm-dependent exits, and parasite intervention—after hive geometry and defender identity become explicit.

- **Keep campaign invariants at these boundaries.** Other mods should feed the same temperature/insulation model rather than adding a second heat resource. Deep gifts can deliver salvage or information, while any extension that actually reaches the sea floor should continue through the ship travel mechanism. No ship or sea-floor implementation is included here; its integration is **UNVERIFIABLE**.