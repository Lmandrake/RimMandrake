## 1. DEBUGGING

Line numbers count from the first line of each inlined file. Paths below are relative to `Source/` unless stated otherwise.

This is a source review, not a build or game test. `validation.py`, the fuzz harnesses, several essential defs, and previous source/save fixtures are omitted. Their behavior, def-loading results, and historical Scribe compatibility are **UNVERIFIABLE**. Comments claiming engine behavior are not treated as executable evidence.

1. **Grey Sea defenses were not migrated to the layer-map identity.**  
   `MapComponent_BrineCrystallisation.cs:70`; `RM_Building_BrineElder.cs:258`. Both sweeps require `map.Biome.defName == "RM_GreySea"`. The layer generator uses a floor biome, so pool crystallisation and mining-triggered Elder disturbance do not run there. The same guards also admit surface Grey Sea maps if those maps contain the relevant hazards.  
   **Minimal fix:** use `RM_SeaFloorIdentity.IsFloorOf(map, "RM_GreySea")` in both components.  
   **Severity: high. Confidence: high.**

2. **Chill aurora mechanics have no surface source on layer maps.**  
   `RM_MapComponent_ChillDrownedAurora.cs:232`. `SourceMap()` only accepts `PocketMapParent`. An `RM_SeabedSiteParent` therefore produces null, and `RawSurfaceIntensity()` returns zero. Drowned aurora variation, surges, and collector output consequently remain inactive on the new layer path.  
   **Minimal fix:** resolve the surface tile through `SurfaceTileOf`, then obtain an applicable surface/world aurora provider. Define behavior when no surface map is loaded; merely finding a loaded map is insufficient for unattended floor maps.  
   **Severity: high. Confidence: high.**

3. **Elder trades commit irreversible bookkeeping before delivery succeeds.**  
   `RM_ElderTradeUtility.cs:119`, `:128`, `:143`; `RM_ElderEconomyKernel.cs:116`. `Decide` immediately marks novelty and claims a unique treasure. The offering is then destroyed, while reward placement results are ignored. Failed placement or construction can consume the specimen, novelty premium, and world’s unique treasure entitlement without delivering anything. `Accepted` still reports true.  
   **Minimal fix:** separate quotation from commitment. Retain the offering and reward in owned containers until delivery succeeds; then commit novelty, treasure entitlement, and consumption. On failure, retain a durable pending payout or roll back.  
   **Severity: high. Confidence: high.**

4. **The “never underwater” payout guarantee is explicitly violated.**  
   `RM_ElderTradeUtility.cs:171`, `:206`. The selected jacket’s underlying terrain is not checked. If the wider dry-cell search fails, the function returns `elder.Position`, which the code identifies as deep brine. A crowded or altered map can therefore receive an underwater payout.  
   **Minimal fix:** validate the jacket’s terrain and accessible delivery location; return `IntVec3.Invalid` when no suitable location exists, and reject/defer the trade without consuming anything.  
   **Severity: medium. Confidence: high.**

5. **The destructive trade API does not validate its inputs or current authorization.**  
   `RM_ElderTradeUtility.cs:112`. It dereferences `elder`, `Current.Game`, and `offered`, and does not require the offering to be alive, spawned, eligible, on the Elder’s map, or permitted by current settings. A stale confirmation or another caller can destroy an item from another map or execute trade after the mechanic is disabled.  
   **Minimal fix:** put these checks inside `Offer`, return `Accepted=false` on rejection, and make the dialog respect that result. UI filtering alone does not protect a destructive utility.  
   **Severity: high. Confidence: high.**

6. **Encasement has no rollback for failure after despawning the pawn.**  
   `BrineEncasementUtility.cs:46`, `:57`; `RM_BrineEncasement.cs:118`. The edifice is destroyed first, the pawn is moved into an unspawned jacket, and only then is the jacket spawned. An exception during spawning can leave the pawn owned by an otherwise unreachable object. Even failure before transfer can already have destroyed the edifice. The public utility also does not require `p.Map == map`.  
   **Minimal fix:** validate map identity, jacket class, and placement before mutation. Wrap transfer/spawn in a transaction that restores the pawn on failure. Delay destructive cell clearing until necessary.  
   **Severity: high. Confidence: high.**

7. **Jacket destruction can orphan contents when ejection fails.**  
   `RM_BrineEncasement.cs:170`, `:178`. The holder is destroyed before `TryDropAll`, and its result/remaining contents are not checked. On a map with no valid drop location, contents can remain inside a destroyed, unsaved holder. The comments say “eject first,” but the implementation does the opposite.  
   **Minimal fix:** establish successful transfer to a surviving owner or valid location before final destruction, with an explicit fallback for every remaining item. Preserve the intended no-yield behavior for dissolution.  
   **Severity: high. Confidence: high.**

8. **Damage sweeps operate on pawn lists that damage can mutate.**  
   `RM_MapComponent_ScaldVentForecast.cs:225`; `RM_MapComponent_ChillAuroraSurge.cs:228`. Scald enumerates the live spawned-pawn collection while applying damage. Despawn during damage can invalidate enumeration. Aurora indexes the live collection forward; removal can skip the next pawn. Brine crystallisation already recognizes this problem and snapshots its collection.  
   **Minimal fix:** snapshot both damage target lists, then revalidate each pawn’s spawned/map state before applying effects.  
   **Severity: high. Confidence: high on the mutation hazard; exact exception behavior depends on the engine collection implementation.**

9. **Surge damage can occur on the same tick as the warning letter.**  
   `RM_MapComponent_ChillAuroraSurge.cs:212`, `:196`. Starting a surge sets `ticksUntilShockCheck=1`. The same `MapComponentTick` immediately decrements it and performs the first shock sweep. Each eligible pawn has a 45% chance of being hit immediately. The documented reaction window is absent.  
   **Minimal fix:** initialize the first check to the intended grace interval, normally `ShockCheckIntervalTicks`, or an explicit warning delay.  
   **Severity: high. Confidence: high.**

10. **Loading an active surge produces a false end and subsequent restart.**  
    `RM_MapComponent_ChillAuroraSurge.cs:374`; `RM_MapComponent_ChillDrownedAurora.cs:136`. `surgeActive` survives saving, but intensity reloads as zero. The first surge rescan ends the saved storm. If the surface aurora remains active, smoothing eventually starts it again, issuing another letter and restarting its shock schedule. Unsaved shock timers also alter exposure across saves.  
    **Minimal fix:** initialize intensity from the authoritative source before reconciling the saved surge, or persist the required state and next shock deadline. Suppress transition notifications during initial reconciliation.  
    **Severity: medium. Confidence: high.**

11. **Tier-1 punishment erases progress toward tier 2.**  
    `RM_GardenDefenseKernel.cs:84–87`. A kill every 3,000 ticks causes a tier-1 arc every time and resets `offenseScore` to zero. Arbitrarily sustained destruction at that cadence never wakes Tarnn. Tier 2 primarily measures offenses concentrated inside the tier-1 cooldown, rather than sustained destruction.  
    **Minimal fix:** maintain separate escalation progress, or subtract the tier-1 cost while retaining cumulative escalation. Define decay explicitly if escalation should eventually forgive old offenses. Preserve existing Scribe keys during migration.  
    **Severity: medium. Confidence: high.**

12. **The Tarnn encounter is not globally one-time.**  
    `RM_GardenDefenseKernel.cs:77–81`. Tier 2 is permitted again after 60,000 ticks. If dormant Tarnn remain—or ambient spawning adds more—another group can wake. There is no durable “this map’s encounter already happened” flag, despite settings text promising a fight that never repeats.  
    **Minimal fix:** add a Scribed completion flag if the encounter must be one-time. Otherwise change the settings text to describe repeatable, bounded waves.  
    **Severity: medium. Confidence: high.**

13. **Garden hooks count unrelated crops and zero-damage heat events.**  
    `Patch_ChillGardenDefense.cs:62`, `:81`, `:100`. The harvest hook accepts every plant harvested by the player on the floor, including plants cultivated aboard the ship. The heat hook similarly accepts every plant and ignores `totalDamageDealt`; an invoked heat callback with zero actual damage still adds four offense points.  
    **Minimal fix:** identify native garden plants explicitly and require positive applied damage for `HeatDamage`. Decide separately whether cutting, harvesting, and uprooting should have different weights.  
    **Severity: medium. Confidence: high.**

14. **A grav engine somewhere on the map does not enforce ship-only access.**  
    `PlaceWorker_NeedsGravEngine.cs:33`; `RM_SeaDiveHatch.cs:61`. Placement ignores the proposed location and ship membership. A hatch can be built elsewhere on the same map, then continue functioning after the engine is removed because use-time validation never checks it. This is acknowledged as a stand-in in About.xml, but it still fails the stated campaign constraint.  
    **Minimal fix:** verify hatch membership in the actual gravship structure during placement and use. The precise Odyssey membership API is **UNVERIFIABLE** from this bundle.  
    **Severity: high. Confidence: high.**

15. **Missing sea generators silently select the fallback generator.**  
    `RM_SeaDiveHatch.cs:47`, `:58`, `:69`. Entry checks dictionary membership, not successful generator resolution. If a listed sea’s generator is missing, the hatch remains enterable and generates whichever fallback its def declares. The comment claiming this fallback is only reachable on a non-sea tile is false.  
    **Minimal fix:** distinguish resolution failure from an unsupported biome; refuse first generation with a useful reason rather than generating the wrong floor.  
    **Severity: medium. Confidence: high.**

16. **Exit placement ignores failure and bounds in its fallback path.**  
    `GenStep_PlaceSeaDiveExit.cs:25`, `:28–30`. The second random-cell search can also fail, but its result is used anyway. If it succeeds near an edge, the clearing radius includes out-of-bounds cells, which are passed to `GetThingList`. Placement also validates only the center, not the exit footprint or an approach.  
    **Minimal fix:** require a successful footprint/approach search, bounds-check every clearing cell, and abort generation explicitly if no safe exit location exists.  
    **Severity: high. Confidence: high.**

17. **The Chill animal-count setting does not control the whole initial population.**  
    `GenStep_SeaFloorFauna.cs:107`; `Defs/MapGeneration/RM_SeabedGenerators.xml:111`, `:114`. The weighted sampler seeds the configured number, but the generator also includes vanilla `Animals`. Floor life copies the roster and multiplies animal density by 30, making the second population mechanism consequential. Exact final counts are **UNVERIFIABLE** without vanilla generation execution.  
    **Minimal fix:** designate one initial population generator. Treat ongoing replenishment as a separate setting/budget, and describe the configured count accurately.  
    **Severity: medium. Confidence: high on the two generation mechanisms.**

18. **Legacy rare-species rounding is discontinuous and undercounts fractional expectations.**  
    `GenStep_SeaFloorFauna.cs:57–63`. With `totalToSpawn=3`, commonality `0.16` yields one animal with probability `0.16`, although the computed expectation was `0.48`. Raising commonality to `0.17` makes the rounded count one every time. A tiny content edit therefore causes a large population jump.  
    **Minimal fix:** stochastic-round `expected = totalToSpawn * commonality`: spawn `floor(expected)` plus a roll for its fractional part. If commonalities are intended as relative weights, normalize them first.  
    **Severity: medium. Confidence: high.**

19. **Overlapping rime seeds can suppress districts instead of enlarging them.**  
    `GenStep_ChillRimeTerraces.cs:106`. If an earlier district has already painted a later seed, the later seed is discarded immediately and its queue never expands. The claimed positive relationship between Krellik clustering and district size is therefore not reliably implemented. Fallback seeds are also not deduplicated at `:79–81`.  
    **Minimal fix:** compute each seed’s growth against the original terrain eligibility and union the resulting cells, or allow traversal through existing terraces without repainting. Select unique fallback seeds.  
    **Severity: medium. Confidence: high.**

20. **Expired Scald discharges can still damage pawns after loading or re-enabling.**  
    `RM_MapComponent_ScaldVentForecast.cs:99`, `:117`. Discharge runs before checking `phaseEnd`. Its absolute deadline continues aging while the setting is disabled. Re-enabling an expired phase-2 state on a 15-tick boundary can emit a stale discharge before the next 60-tick phase update.  
    **Minimal fix:** reconcile phase expiration before effects; never apply discharge when `now >= phaseEnd`. Specify whether disabling pauses or cancels the cycle.  
    **Severity: medium. Confidence: high.**

21. **Scald “hull border” heat also charges for internal partitions.**  
    `RM_MapComponent_ScaldImmersionBerth.cs:93`. Every room’s complete cardinal border is counted. Shared internal walls contribute to neighboring rooms’ loads even though the ship’s exposed hull has not changed. Subdividing a fixed exterior increases environmental heat input.  
    **Minimal fix:** count boundary faces exposed to the external medium, excluding boundaries between enclosed ship rooms. Keep the resulting energy in vanilla room temperature.  
    **Severity: medium. Confidence: high.**

22. **Suit charging and drain use roofs rather than actual thermal shelter or charger access.**  
    `RM_CompHeatedSuitBattery.cs:160`, `:200`. Any roof stops battery drain, even over a cold, unenclosed work site. A tiny roof can therefore preserve charged protection indefinitely. Recharging requires only distance and `PowerOn`, so it also works through walls or from another inaccessible room.  
    **Minimal fix:** base drain on the wearer’s actual thermal conditions or explicitly defined heated shelter. Require an accessible charger in the appropriate room. Read vanilla temperature; do not introduce a second heat model.  
    **Severity: medium. Confidence: high.**

23. **The floor-light checkbox secretly controls mechanical storms and power.**  
    `RM_MapComponent_ChillDrownedAurora.cs:155`, `:196`. Disabling `chillDrownedAuroraEnabled` makes the intensity accessor return zero. Surges consume that accessor, so switching off lighting also disables storm damage and collector generation while the separate surge setting remains enabled.  
    **Minimal fix:** separate aurora sensing from its visual presentation toggle, or explicitly expose and describe the dependency in settings.  
    **Severity: medium. Confidence: high.**

24. **The master switch does not make the mod “fully inert.”**  
    `GenStep_SeaFloorFauna.cs:31`; `GenStep_ChillRimeTerraces.cs:61`; `RM_SeabedFloorLife.cs:72`, `:136`; `RM_BrineEncasement.cs:131`. Generation paths lack the master gate, copied biome life can continue, density reassertion remains active after runtime disabling, and existing jackets continue smothering. Persistent ambient cold also remains. Some of those behaviors are deliberate, but the master tooltip does not describe them.  
    **Minimal fix:** define and document the actual master-switch contract, including restart effects and surviving hazards. Gate generation features consistently where intended; retain a guaranteed escape route for existing divers.  
    **Severity: medium. Confidence: high.**

25. **Gallery rewards can be permanently lost.**  
    `RM_ReturnGallery.cs:214`, `:243`. `solved=true` is set before validating reward defs or successful placement. A missing def, null map, or failed placement permanently closes the only reward path.  
    **Minimal fix:** track successful delivery separately from solving, with a Scribed pending-reward state that can retry without duplicating already delivered rewards.  
    **Severity: medium. Confidence: high.**

26. **Gallery commands remain active with the master switch off.**  
    `RM_ReturnGallery.cs:174`, `:206`. Neither gizmo generation nor `Mark` checks settings. Existing galleries can still be solved and spawn rewards while master-disabled. Conversely, the probing workgiver stops on `scaldReturnGalleryEnabled`, even though settings describe that flag principally as generation-affecting.  
    **Minimal fix:** choose explicit generation and runtime semantics. Enforce runtime authorization in `Mark`, not only in the workgiver or gizmo.  
    **Severity: medium. Confidence: high.**

27. **The gallery’s “day” penalty is six game hours.**  
    `RM_ReturnGallery.cs:84`, `:222`. `JamTicks=15000`; elsewhere the code correctly identifies 60,000 ticks as a day. Every wrong-mark message and description promises a day.  
    **Minimal fix:** use 60,000 ticks, or change the text to six hours.  
    **Severity: low. Confidence: high.**

28. **The plant-growth finalizer suppresses unrelated failures and leaves incomplete state.**  
    `Patch_SeabedPlantGrowthGuard.cs:23–36`. It swallows every exception on a seabed map, including exceptions from other Harmony patches, then logs only once for the process. There is no repair of partially initialized calculator state. Harmony finalizers cover the original method and other patches, so this is broader than guarding one temperature lookup. [Harmony documentation](https://harmony.pardeike.net/v2/articles/patching)  
    **Minimal fix:** remove the speculative guard until a reproducible failure exists, or guard the specific failing operation and construct a valid fallback. Retain full diagnostic information for unexpected exceptions.  
    **Severity: high. Confidence: high on suppression; downstream consequences are UNVERIFIABLE.**

29. **NaN market value earns the maximum silver payout.**  
    `RM_ElderEconomyKernel.cs:131`. For NaN, `scaled < MaxSilver` is false, so the expression selects 1,000,000 silver. The purported numeric safety guard converts invalid data into the richest payout.  
    **Minimal fix:** reject non-finite/negative market values and invalid stack counts before arithmetic. Distinguish invalid input from genuine positive overflow.  
    **Severity: medium. Confidence: high.**

30. **Cosmetic effects consume the gameplay random stream conditionally on camera state.**  
    `RM_MapComponent_ChillAuroraSurge.cs:277`, `:300`. Viewed-map dressing performs `Rand` draws; unviewed-map dressing skips them. Mechanical shocks use `Rand` too. Camera choice and cosmetic settings can therefore change later gameplay rolls. The same pattern appears in BoilShroud.  
    **Minimal fix:** isolate cosmetic randomness using a separate generator or `Rand.PushState`/`PopState` in `finally`, with an appropriate visual seed.  
    **Severity: medium. Confidence: high.**

31. **Mining disturbance triggers from job assignment, before actual mining.**  
    `RM_Building_BrineElder.cs:277`. The sweep checks the job’s target distance to the Elder, but neither the miner’s distance nor whether mining has begun. A pawn walking toward a distant jacket with a `Mine` job can disturb the Elder before reaching it.  
    **Minimal fix:** notify on an actual mining action against the jacket, or verify the active mining toil and contact distance.  
    **Severity: medium. Confidence: high.**

32. **The Elder’s advertised 48-step charge requires 49 float additions.**  
    `RM_Building_BrineElder.cs:61`, `:85`. IEEE-754 single-precision accumulation of `1f/48f` produces approximately `0.99999958` after 48 additions. The `charge >= 1f` condition is first satisfied on step 49. This affects the initial charge duration; the longer discharge cooldown dominates subsequent cycles.  
    **Minimal fix:** derive charge from an integer elapsed-tick counter, or use an explicit completion threshold consistent with the intended duration.  
    **Severity: low. Confidence: high.**

The following engine-boundary issues need verification before release. They are not established runtime defects from the supplied source:

- **Rare-tick dispatch — UNVERIFIABLE.** `RM_CompHeatedSuitBattery.cs:140`; `RM_BrineEncasement.cs:131`. Battery drain, encasement smothering, sentinel squirts, Tarnn zaps, and Elder charge depend on rare callbacks. Pawn attachment alone does not establish dispatch, and the essential ticker defs are omitted. Verify exact callback counts while spawned, worn, held, and unloaded; implement the appropriate normal/worn tick path if needed. **Potential severity: high. Confidence: high that verification is missing; failure itself unverified.**

- **Held-pawn death and corpse ownership — UNVERIFIABLE.** `RM_BrineEncasement.cs:131–158`. The holder increments a hediff but does not explicitly tick contents or perform a lethal-state check/corpse transfer. Whether the severity setter alone kills this unspawned pawn, and where its corpse ends up, requires the engine and omitted hediff def. Verify death inside the jacket, save/load afterward, and mining release. **Potential severity: high. Confidence: medium.**

- **Garden kill detection — UNVERIFIABLE in its current hook position.** `Patch_ChillGardenDefense.cs:78–96`. Detection requires `Dead` and a non-null `Map` inside a patch on the base `Thing.PostApplyDamage` implementation. The supplied bundle does not establish override ordering or despawn timing. Kills occurring outside this damage callback have no detector here. Use a verified death notification, capture map/position before destruction, and deduplicate reports. **Potential severity: high. Confidence: high on incomplete hook coverage; exact engine timing unverified.**

- **EMP stunning ordinary living creatures — UNVERIFIABLE.** `RM_Building_BrineElder.cs:185`. A pawn having a stunner and EMP having `causeStun` do not prove that every ordinary human or animal is eligible for EMP stun. Verify flesh/mech/implant eligibility and explosion reach from the Elder’s occupied footprint. Add an explicit living-creature stun if vanilla EMP does not supply it. **Potential severity: high. Confidence: medium.**

- **Missing Elder def handling — UNVERIFIABLE engine behavior.** `RM_Building_BrineElder.cs:268–269`. A failed lookup is passed directly to `ThingsOfDef` before any guard. Resolve and check both defs first. Whether this currently throws depends on the omitted lister implementation. **Potential severity: medium. Confidence: high on the unguarded argument path.**

- **Harmony targets, ordering, and duplicate application — UNVERIFIABLE at runtime.** `Patch_ChillGardenDefense.cs:59`, `:78`; `RM_SeabedFloorLife.cs:119`. There is no supplied patch inventory or full assembly compilation result. Several patches select methods without overload signatures; reflection-driven field accesses require exact names and types. Add startup checks for targets, expected fields, and patch multiplicity. Specify ordering only for actual conflicts. Harmony supports explicit argument-type selection. [Harmony annotations](https://harmony.pardeike.net/v2/articles/annotations.html)

## 2. LIKELY FUTURE COMPLICATIONS

- **Save identity needs migration rules, not just stable field names.** `RM_ElderTradeUtility.cs:51`, `:68` stores integer tile identities and textual novelty keys. Def renames, pawn-kind changes, xenotype changes, and revised novelty rules can silently make old specimens novel again. Stuff is currently ignored: different materials of the same item def share one key. Normalize floor tiles to their surface origin explicitly, version the key scheme, and maintain aliases. Historical renames are **UNVERIFIABLE** without previous versions.

- **A moving hatch can detach floor content from economic provenance.** `RM_SeaDiveHatch.cs:61`; `RM_ElderTradeUtility.cs:51`. The economy takes the current source map’s tile, while entry validates its current biome. If vanilla retains a generated pocket map across ship movement, the old floor could acquire a new tile’s ledger. Portal reuse behavior is **UNVERIFIABLE** here. Record immutable generation provenance and test travel between two seas with an existing floor.

- **The claimed treasure extension point does not exist in XML.** `RM_ElderTradeUtility.cs:45`. The pool is a private static string array. An XML patch cannot append treasures to that array. New treasure content currently needs a Harmony/reflection intervention or a source edit. Introduce a Def-backed treasure table, including construction requirements and uniqueness identity.

- **Oxygenation cannot safely support overlapping providers.** `RM_MapComponent_ChillOxygenation.cs:44`, `:78`. Pump A shutting down removes cells still supplied by pump B. Persisted cells can also survive after their provider disappears. Store provider-owned regions or reference counts and rebuild derived coverage from surviving providers on load.

- **The self-oxidizer contract needs source-versus-target semantics.** The fire gate tests one `relevantThing`, while ignition supplies an instigator. A self-oxidizing target plant, its emitted flame, and subsequent spread need not carry the same identity. Existing fires and mods spawning `Fire` directly also need a policy. Actual vanilla routing is **UNVERIFIABLE** from the bundle.

- **Global biome mutation will conflict with customization mods.** `RM_SeabedFloorLife.cs:72`, `:116`. Reassertion overwrites floor density customization with surface-derived values. It also depends on startup order and private cache fields. Distinguish restoring an accidental reset from overriding a deliberate user setting; expose effective densities and validate reflection fields before modification.

- **Scale changes both cost and gameplay.** `RM_ElderEconomyKernel.cs:29`, `:44` linearly scans tile records and seen keys. The trade dialog repeats novelty checks while rebuilding and sorting map-wide item lists. Sentinel/Tarnn scans multiply by their populations; synchronized sweeps concentrate work on the same ticks. Use runtime indexes rebuilt after Scribe load, stagger map sweeps, and budget cosmetic scans independently.

- **The mineable holder remains unsafe under exceptional lifecycle events.** `RM_BrineEncasement.cs:164`. Map removal, holder replacement, mod removal, destruction modes, and blocked ejection must preserve pawn ownership deliberately. “Clear and destroy contents” is not a general save-safe fallback for campaign colonists.

- **Gallery reference loss can make the puzzle impossible.** `RM_ReturnGallery.cs:111`, `:123`. Missing outlets are skipped. A lost true-return outlet leaves remaining branches markable but none correct; all outlets disappearing leaves no recovery path. Persist sufficient puzzle identity independently of the physical references and define repair/failure behavior.

- **Thread safety is conditional on serial execution.** `MapComponent_BrineCrystallisation.cs:58` shares a mutable static scratch list across maps. Economy mutations described as “atomic” have no synchronization. No concurrent invocation is demonstrated in the bundle, but parallel ticking or reentrant callbacks would break those assumptions. Prefer instance/local scratch storage and explicitly require game-thread access for ledger mutation.

- **Generation connectivity can be invalidated after its check.** `RM_SeaFloorBandsExtension.cs:27`; `Defs/MapGeneration/RM_SeabedGenerators.xml:66`. Terrain connectivity is established before formations, the Grey basin, ruins, wrecks, and chunks finish placement. The final navigable map—not merely terrain passability—needs an exit/landing-to-content reachability check. Reject invalid band shares, non-finite parameters, and impassable base terrain before generation.

## 3. UNLEVERAGED OPPORTUNITIES

- **Make offline validation test the actual adapters as well as kernels.** Compile the complete assembly against the campaign’s exact RimWorld/Harmony references. Load defs with inheritance and cross-reference resolution; verify class names, comp properties, tickers, job drivers, workgivers, generator membership, and terrain tags. The supplied validation script’s coverage is **UNVERIFIABLE**.

- **Add deterministic behavioral counterexamples to the actual kernel harness.** Include spaced kills versus burst kills, cooldown boundaries, repeated tier-2 attempts, NaN market values, unresolved treasures, and failed-delivery rollback. Extract vent phase progression and connectivity/rime algorithms into pure kernels where useful. A Python mirror should not substitute for executing the shipped C#.

- **Use save fixtures as a release gate.** Round-trip an occupied jacket, a dead occupant, a partially charged worn suit, an active surge, every vent phase, a jammed gallery, missing outlet references, and a claimed unique treasure. Load an older save and save it again. Compare ownership, keys, deadlines, and entitlements—not just whether loading throws.

- **Settings can expose effective behavior.** Show “new maps,” “restart,” and “immediate” consistently; disclose dependencies; show disabled protection as “battery simulation disabled” rather than “charged: 0%.” Add per-section resets and a compact diagnostic view for source sea, generator, aurora source/intensity, vent deadlines, charge, and pending rewards.

- **Expose actionable hazard state cheaply.** Battery depletion warnings, estimated charge time, smother deadline, and vent phase are already derivable from existing state. They would help players make decisions without requiring new mechanics or art.

- **Share physical checks among related effects.** BoilShroud, footprints, suit charging, and immersion heat can use common room/exposure queries. This reduces contradictory interpretations of “indoors,” “warm,” and “hull,” while keeping vanilla temperature as the single heat model.

## 4. EXTENSIONS BEYOND THE MOD

- **A campaign-wide environment interface could replace repeated biome-name routing.** `RM_SeaFloorIdentity` can expose authoritative origin, environment, weather source, temperature, and access mode. Other seabed content could then support pocket and planet-layer maps through the same contract.

- **The Elder ledger can support museums, research specimens, and archaeological exchanges.** Reuse the novelty and world-unique entitlement kernels after adding transactional delivery, versioned identities, and Def-backed reward tables. Keep permanent entitlement records separate from physical spawned rewards.

- **The garden kernel can support ecological or faction retaliation elsewhere.** Separate reporting, scoring, and effect execution; define cumulative escalation and one-time encounters explicitly. Other mods could contribute offenses without patching this mod’s internal methods.

- **The encasement lifecycle can become a shared campaign service.** Ice, resin, mineral shells, wreck capsules, and engulfing creatures all need safe held-pawn ticking, death, Scribe ownership, release, and map-removal handling. Centralize those guarantees before sharing the current implementation.

- **Ship environmental logistics should remain in the existing thermal and power systems.** Future pressure, coolant, and immersion content can apply loads to vanilla rooms and power networks. Cosmetic disturbance should read those systems; introducing a separate “ship heat” resource would undermine the campaign’s “one kind of heat” constraint.