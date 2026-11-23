**I would support repeatable scene contracts, but would not promise exact replay from “save + Rand state” alone.** The strongest verified counterexamples are frame-updated simulation managers, camera-dependent tick rates, and pathfinding jobs reading mutable state.

I checked Multiplayer’s 1.6 source directly. Several vanilla decompiler pages were unavailable; I treat your READ facts as supplied evidence and explicitly identify older-source corroboration below. I could not verify every 1.5 implementation or exhaustively audit all DLC code.

**1. Calling `DoSingleTick()` repeatedly — confidence: high on the identified hazards; unknown on complete equivalence.**

Multiple ticks per frame are normal. An unrestricted loop becomes different because it changes which frame-level work occurs between simulation steps.

| System | Finding and implication |
|---|---|
| Regions, rooms, power, glow | **A concrete simulation dependency.** Multiplayer explicitly runs region cleanup/rebuilding, power-network updates, and glow updates during ticks and commands because vanilla normally runs these in `MapUpdate()`. A bare loop can retain stale manager state. [Implementation](https://github.com/rwmt/Multiplayer/blob/master/Source/Client/AsyncTime/AsyncTimeComp.cs) |
| Post-tick visuals | Multiplayer explicitly processes `map.postTickVisuals`, including managing `ticksThisFrame`. This work must be considered separately from `DoSingleTick()`. [Implementation](https://github.com/rwmt/Multiplayer/blob/master/Source/Client/AsyncTime/AsyncTimeComp.cs) |
| `PawnTweener` | Multiplayer substitutes the root position during simulation. Therefore a supposedly cosmetic, frame-smoothed position can leak into simulation callers. [Patch](https://github.com/rwmt/Multiplayer/blob/master/Source/Client/Patches/Determinism.cs) |
| Real-time reads | Frame time and wall time are different hazards: `Time.deltaTime`/frame counters repeat within a frame; `DateTime.Now`/`Stopwatch` continue advancing. A verified vanilla example is `GameConditionManager.MapBrightnessTracker.Tick`, whose delta-time read Multiplayer replaces with a constant. [Patch](https://github.com/rwmt/Multiplayer/blob/master/Source/Client/Patches/Determinism.cs) |
| Pathfinding jobs | Tick-locked delivery does **not** establish deterministic computation. Multiplayer documents jobs reading live pawn positions while pawn ticking changes them. Its active tick implementation completes scheduled jobs before pawn ticks; the alternative snapshot implementation is currently inside `#if false`. [Active completion](https://github.com/rwmt/Multiplayer/blob/master/Source/Client/AsyncTime/AsyncTimeComp.cs), [race explanation](https://github.com/rwmt/Multiplayer/blob/master/Source/Client/Patches/PathFinderPatch.cs) |
| Camera/VTR | **Yes, camera-dependent simulation update rates exist in 1.6.** Multiplayer patches `GenTicks.GetCameraUpdateRate`, projectile `UpdateRateTicks`, and world-object rates. Its replacement chooses rates 1 or 15 according to whether a map/world is being viewed. Exact vanilla thresholds and affected-type inventory: **unknown here**. [Patch](https://github.com/rwmt/Multiplayer/blob/master/Source/Client/Patches/VTRSyncPatch.cs) |
| Sound, sustainers, real-time motes/flecks | Their requests may occur during ticks while frame/audio processing advances differently. Exact effects depend on the effect’s clock and maintenance mode. Complete 1.6 audit: **unknown**. Do not use a tick-only run to establish audible or rendered behavior. |
| Windows and long events | A loop does not pump Unity’s GUI, scene loading, or queued long events. Multiplayer stops simulation when long events are queued. [Tick loop](https://github.com/rwmt/Multiplayer/blob/master/Source/Client/Patches/TickPatch.cs) |
| GC | Allocation-triggered collection can still occur inside the loop. GC does not require rendering; its timing can affect wall-clock-sensitive code and worker scheduling. |

For `TickInterval(delta)`, record the actual delta passed to each watched thing. Audit mods that retain single-tick assumptions, including interval checks that do not account for elapsed ticks. Pin the camera **and** effective update rates for comparisons.

Multiplayer’s fast simulation is useful prior art: its catch-up loop uses a **25 ms work budget**, yields for long events, and ticks controlled map/world contexts. It is substantially more machinery than repeatedly calling vanilla `DoSingleTick()`. [Source](https://github.com/rwmt/Multiplayer/blob/master/Source/Client/Patches/TickPatch.cs)

Also: never invoke the loop recursively from `MapComponentTick`/`GameComponentTick`; use a controlled main-thread boundary outside an existing tick.

**2. What Multiplayer patches — confidence: high for the linked current implementations; historical 1.5 details partly unknown.**

| Category | Verified implementation | Relevance to your same-process replay |
|---|---|---|
| Rand per map/world | Saves separate RNG states and pushes/restores them around ticking and commands. [Map](https://github.com/rwmt/Multiplayer/blob/master/Source/Client/AsyncTime/AsyncTimeComp.cs), [world](https://github.com/rwmt/Multiplayer/blob/master/Source/Client/AsyncTime/AsyncWorldTimeComp.cs) | Capturing every relevant RNG matters. Splitting vanilla’s stream by map is optional and changes the apparatus. |
| Loading and deferred-work RNG | Seeds game/map loading, map finalization, long-event actions and callbacks. [Seeds](https://github.com/rwmt/Multiplayer/blob/master/Source/Client/Patches/Seeds.cs) | **Directly relevant:** restoring RNG only after loading misses randomness used to reconstruct state. |
| Unique IDs | Separates interface-created IDs, prevents certain loading-time reinitializations, handles temporary negative IDs. [Unique IDs](https://github.com/rwmt/Multiplayer/blob/master/Source/Client/Patches/UniqueIds.cs) | Allocation history and UI activity can matter even in one process. |
| Thing-ID blocks | I could not verify the alleged block allocator in the current source or retrieve the relevant 1.5 implementation. | **Unknown as a historical claim.** Dedicated per-context allocation is principally useful when contexts advance independently. |
| Pathfinding threading | Forces completion before concurrent pawn mutations; documents a snapshot alternative. [Sources above](https://github.com/rwmt/Multiplayer/blob/master/Source/Client/Patches/PathFinderPatch.cs) | **Relevant in one process:** thread scheduling still varies. |
| `System.Random` / Unity RNG | Compatibility helpers redirect selected call sites to `Verse.Rand`; they are not a universal interception of every RNG. [Helpers](https://github.com/rwmt/Multiplayer-Compatibility/blob/master/Source/PatchingUtilities.cs) | **Relevant:** those generators are not restored by restoring `Verse.Rand`. |
| Hashing and ordering | Replaces map/object-dependent hashes, supplies a glower comparer, patches hash combination. [Hash patches](https://github.com/rwmt/Multiplayer/blob/master/Source/Client/Patches/HashCodes.cs) | Reference hashes can change when objects are reconstructed. Process-specific hash salts are chiefly a cross-process concern. |
| Real-time/camera reads | Tweener, brightness and VTR patches described above. | **Relevant in one process**, unless clocks, frame schedule and viewing context are controlled. |
| Async map time | Maintains map clocks and installs/restores time contexts. [Async time](https://github.com/rwmt/Multiplayer/tree/master/Source/Client/AsyncTime) | Independent map clocks are a Multiplayer feature; a single global tick schedule does not need that architecture. |
| UI actions and getters | Executes synchronized commands on ticks; prevents interface-side mutation of simulation caches and other state. [Command execution](https://github.com/rwmt/Multiplayer/blob/master/Source/Client/AsyncTime/AsyncTimeComp.cs), [patches](https://github.com/rwmt/Multiplayer/blob/master/Source/Client/Patches/Determinism.cs) | **Relevant:** inspection and open UI can change execution history. Network serialization itself is cross-client machinery. |

The same-process/cross-machine distinction is therefore not a clean division by category. Most underlying hazards matter to both; networking, independently advancing maps, and runtime/hardware differences add further requirements.

**3. Save, run, reload, restore Rand, repeat — confidence: high that this is insufficient as a general guarantee. Exact replay rate: unknown.**

Concrete divergence candidates:

- **Run 1 starts warm; run 2 starts reconstructed.** Unsaved caches, pending requests, dirty-manager state and transient driver/render state need not survive serialization.
- **Loading consumes randomness.** Multiplayer’s loading seeds are direct evidence that load-time RNG deserves control. Restoring the stream afterward cannot undo already-generated state. [Loading patches](https://github.com/rwmt/Multiplayer/blob/master/Source/Client/Patches/Seeds.cs)
- **Statics and mutated Defs survive loading.** A save reload does not restart assemblies. With 300 mods, static dictionaries, object references, settings, external responses and independent RNGs require individual auditing.
- **Reconstructed objects can have different reference hashes and collection construction histories.** Same process does not mean same objects. However, a `HashSet` is not randomly reshuffled on every enumeration, and dictionary iteration is not automatically a divergence.
- **Different frame/camera/UI histories and pathfinding races** remain relevant.
- **Saving can itself mutate state.** Multiplayer specifically removes a saving-time write to `Pawn_RecordsTracker.battleActive`. [Patch](https://github.com/rwmt/Multiplayer/blob/master/Source/Client/Patches/Determinism.cs)

**Ordinary wholesale Thing-ID renumbering is not supported by the evidence.** Historical vanilla `Thing.ExposeData` saves/restores IDs, and current Multiplayer carries tween positions across reload keyed by `thingIDNumber`. Newly reconstructed helper objects and allocator side effects are separate concerns. [Historical serialization](https://github.com/RimWorld-zh/RimWorld-Decompile/blob/master/Assembly-CSharp/Verse/Thing.cs), [current reload](https://github.com/rwmt/Multiplayer/blob/master/Source/Client/Saving/SaveLoad.cs)

For a meaningful comparison, reload the baseline **before both runs**, establish the same initialization barrier, then restore scene RNG. Compare watched state and event sequences at every tick to locate the first divergence.

Multiplayer has functioning replay support, but I found **no published exact-replay percentage** for vanilla 1.6 or a 300-mod list. Replay support alone does not establish your proposed guarantee. [Replay documentation](https://github.com/rwmt/Multiplayer/wiki/Replays-%28save-files%29)

**4. Cheaper repeats — confidence: medium; ratings are engineering judgments, not measured benchmarks.**

| Approach | Feasibility / risk | Assessment |
|---|---|---|
| **(i) Declarative rectangle stamp** | High feasibility for narrow fixtures; high rollback risk | Good default for fresh actors and known structures. Clearing cells does not reset world pawns, quests, faction relations, memories, lords, map components, allocator history or outside references. Destruction itself can trigger consequences. |
| **(ii) Scribe rectangle to memory** | Feasible serialization; very high arbitrary-pawn restoration risk | A rectangle is not a closed object graph. Jobs, relations, equipment, holders, ownership and targets cross its boundary. You must distinguish restoring original identities from cloning with new identities. |
| **(iii) Fresh small pocket map** | Plausible; medium/high integration risk | Better spatial cleanup boundary. Still shares world state, statics and vanilla RNG. Empty generation still constructs map grids/managers and mod components. Generation cost: **unknown; benchmark your list**. |
| **(iv) Many cells on one map** | High throughput feasibility; high independence risk | Useful for screening. Shared rooms/regions, temperature, power, listers, AI target searches, reservations, events and RNG create cross-talk. Walls alone do not provide independence. |

Verified prior art for memory serialization is Multiplayer’s `ScribeUtil.WriteExposable`/`ReadExposable`, including cross-reference resolution and post-load initialization. Its full save/reload also avoids a normal scene reload. These are stronger precedents than assuming prefab functionality constitutes rollback. [Scribe utilities](https://github.com/rwmt/Multiplayer/blob/master/Source/Client/Saving/ScribeUtil.cs), [full reload](https://github.com/rwmt/Multiplayer/blob/master/Source/Client/Saving/SaveLoad.cs)

**Gravship takeoff/landing, PrefabDef, Sketch and portals do not establish arbitrary rectangle snapshots.** Whether gravships internally use Scribe for the particular transfer path: **unknown here**. Likewise, I could not verify a general 1.6 “copy pawn” serializer suitable for reuse.

Registered pocket maps should participate in normal map ticking—an inference from your tick-order evidence—but their effective VTR, lifecycle, removal conditions and mod behavior require verification. Older [Pocket Dimensions](https://github.com/CaptainMuscles/CM_Pocket_Dimension) demonstrates playable auxiliary maps, not a benchmark of vanilla `GeneratePocketMap`.

A single PRNG stream does not by itself prove statistical dependence between every outcome. It does mean changing one cell’s execution changes which random draws other cells receive. Treat simultaneous copies as a clustered experiment.

**5. Telemetry — confidence: high on the design; overhead and complete hook coverage require measurement.**

My recommendation is one observer after the **complete tick**, sampling cached references to the approximately 20 watched things into preallocated records. Use compiled/cached field access, primitive IDs and bounded event buffers. Serialize and transmit outside the hot paths. Record `(run, tick, phase, sequence)`; add frame number for presentation events.

| Hooks | Required interpretation |
|---|---|
| `TakeDamage`, `PostApplyDamage`, `Pawn.Kill` | Record attempted damage separately from actual damage and resulting health/death. Health changes can also occur through direct hediff operations. |
| `StartJob`, `EndCurrentJob` | Capture the old job before transition, end condition, requested job, and actual resulting job. Multiple transitions can happen within one tick. |
| Reservations | Include successful/failed reservation attempts and bulk cleanup paths such as release-all variants. Distinguish ordinary, physical-interaction and attack-target reservations. |
| `SpawnSetup`, `DeSpawn`, `Destroy` | Capture map/position before removal. Patch relevant overrides that bypass base implementations. Distinguish despawn, death, destruction, transfer and loading. |
| Mental states, incidents | Record attempts, return values and actual resulting state. An unsuccessful attempt is not a state transition. |
| Errors, letters, messages, windows | Resolve exact overloads; avoid duplicate records from overload delegation. A window being added does not prove its contents were drawn. |
| Sound, flecks, motes, effecters | Separate request, accepted creation and presentation. Watch region/time as well as owner: some effects have no Thing owner. `PlayOneShot` misses sustainers. |

A useful 1.6 primary precedent is Zombieland’s live patch audit: it verifies actual `StartJob`, `Kill`, mental-state and combat behavior, including cases where “patch installed” did not establish the intended effect. [Audit](https://github.com/pardeike/Zombieland/blob/master/TEST_PATCH_AUDIT.md)

Harmony traps:

- Already-inlined callers can bypass a patch; patch early and exercise controlled events.
- Generic reference-type implementations may be shared; value-type specializations may differ.
- Use exact struct signatures. Avoid `object[] __args`, boxing, reflection and stack traces on frequent calls.
- A base-method patch does not cover an override that never calls base.
- Other prefixes/postfixes can change arguments, skip originals, or modify results after your observer.
- Finalizers must preserve exceptions. Logging hooks need recursion protection.

These limitations are documented by [Harmony’s edge-case guide](https://harmony.pardeike.net/articles/patching-edgecases.html) and [argument-injection guide](https://harmony.pardeike.net/articles/patching-injections.html).

Prior art worth reusing:

- [Dubs Performance Analyzer](https://github.com/Dubwise56/Dubs-Performance-Analyzer/tree/develop/Source): selective tick/update/GUI instrumentation and patch inspection; not a semantic event recorder.
- [HugsLib `ModBase`](https://github.com/UnlimitedHugs/RimworldHugsLib/blob/master/Source/ModBase.cs): lifecycle callbacks and mod infrastructure; not a REPL.
- [Prepatcher](https://github.com/Zetrith/Prepatcher): assembly rewriting; not runtime eval.
- [RimBridgeServer](https://github.com/pardeike/RimBridgeServer): an existing 1.6 automation bridge with semantic inspection, DPA integration and a **restricted lowered Lua subset**. Potential overlap with your apparatus.
- A maintained general-purpose 1.6 C# REPL/debug-inspector probe suitable for direct reuse: **unknown**.

**6. Draw-time truth — confidence: medium on proposed probe locations; exact Odyssey frame formula unknown.**

Use three separate assertions: **resolved graphic**, **submitted draw**, and **visible pixels**. They establish different things.

| Target | Useful probe boundary |
|---|---|
| Pawn animation/material/transform | Pawn renderer/tree, relevant node worker and final draw request/submission. Include animation worker outputs and material/property-block values. |
| Ordinary dynamic Thing | Concrete `Graphic.DrawWorker`/`DrawAt` implementation and managed mesh-submission wrapper. Base `Graphic.Draw` alone is incomplete. |
| Static Thing | `Graphic.Print`/`Printer_Plane` during section mesh rebuilding, plus section mesh submission. There may be no per-Thing call each frame. |
| Flecks/motes/effecters | Creation plus their concrete draw/batch paths. Effects can be batched and lack a Thing owner. |
| UI text | Scope the actual window’s content call and capture relevant `Widgets`/GUI text calls during `Repaint`, including rectangles and clipping context. |

The exact active 1.6 signatures and paths should be resolved against the installed assembly; I could not independently verify every choke point you named.

**Recording selected draw submissions for N frames is practical in principle. Recording every `Graphics.DrawMesh` call “for these things” is not automatically attributable.** That API receives mesh/material/transform/camera information, not a RimWorld Thing. Carry provenance from higher-level draw requests; deferred or parallel work can break a simple ambient “current Thing” variable.

Unity also documents that `DrawMesh` queues rendering rather than immediately producing pixels. A submission can still be culled, occluded, transparent or altered by shaders. [Unity documentation](https://docs.unity3d.com/2022.3/Documentation/ScriptReference/Graphics.DrawMesh.html)

Patch managed wrappers or call sites: native Unity methods generally do not support ordinary Harmony prefixes/postfixes. [Harmony documentation](https://harmony.pardeike.net/articles/patching-edgecases.html)

For Odyssey flight:

- Your `AnimationTick` observation establishes a tick-derived clock for that property.
- It does **not** establish how flight selects a graphic, whether it uses AnimationDef keyframes, or its phase offset.
- The exact formula involving `flyingAnimationTicksPerFrame`, frame count, takeoff phase and any per-pawn offset is **unknown from the retrievable sources**.
- Consequently, I cannot endorse `floor(T / ticksPerFrame) % count`.

Instrument the actual frame/material resolver and record its inputs. Once verified, computing the logical frame from complete state may be straightforward; reproducing the final smoothed draw transform can additionally require frame state.

**7. Offscreen rendering — confidence: high on RenderTexture feasibility and the prior-art limitation; medium on a fully unobtrusive 1.6 implementation.**

**Yes**, Unity supports manual camera rendering into a RenderTexture. However, Progress Renderer’s implementation **temporarily changes the player camera and camera-driver view rectangle**, renders, then restores them. It therefore does not prove an independent second-camera solution. [Implementation](https://github.com/Scherub/rw-progress-renderer/blob/master/Source/MapComponents/MapComponent_RenderManager.cs)

It explicitly supports weather rendering. Pawns/effects require their draw submissions to exist and pass RimWorld’s own visibility decisions; moving only a second Unity camera may not cause those submissions. IMGUI windows require a separate UI capture path.

Map Preview is a terrain/map-generation preview, not evidence of complete live pawn/effect/UI rendering. [Project description](https://github.com/m00nl1ght-dev/MapPreview/blob/main/README.md)

Window focus is unnecessary when the player continues running in the background; that is separate from minimized-window behavior and having a working graphics context. [Unity setting](https://docs.unity3d.com/2022.3/Documentation/ScriptReference/Application-runInBackground.html)

For consecutive-tick capture, implement:

`tick → required visual preparation → render at that tick → capture acknowledgement → next tick`

Advancing N ticks and then rendering cannot recover the intervening frames. Store both tick and frame identifiers. Exact visual replay additionally requires controlling presentation clocks.

**8. Calm-profile escape routes — confidence: medium on this working inventory; exhaustive 1.6 coverage unknown.**

**An exhaustive “every vanilla mechanism” list is not verified.** The table distinguishes routes, and marks uncertain DLC routing instead of treating all notifications as incidents.

Here, **incident** means the normal execution route should pass through `IncidentWorker.TryExecute`; **direct** means that hook alone is insufficient. Historical source corroborates several core mechanisms, but does not establish every 1.6 detail.

| Mechanism | Route / what survives storyteller suppression |
|---|---|
| Queued incidents, scenario incident schedules | **Incident.** Already queued work remains relevant under your READ facts. |
| Quest raids/incidents | **Incident** for the quest parts you inspected. |
| Other quest actions | **Mixed:** direct pawn delivery/spawning, conditions, signals, lord changes and job effects need separate observation. |
| Wild-animal population replenishment | **Direct spawner.** Historical implementation creates pawns without an incident. [Source](https://github.com/RimWorld-zh/RimWorld-Decompile/blob/master/Assembly-CSharp/RimWorld/WildAnimalSpawner.cs) |
| Wild-man arrival / existing wild-man aggression | Arrival can be an **incident**; existing-pawn behavior and retaliation are **direct**. |
| Predator hunting | **Direct AI/jobs.** |
| Hunting/taming revenge and nearby pack retaliation | **Direct mental-state/retaliation logic**; it need not spawn a new pack. Historical code explicitly handles damage and failed recruitment/taming. [Source](https://github.com/RimWorld-zh/RimWorld-Decompile/blob/master/Assembly-CSharp/Verse/AI/Pawn_MindState.cs) |
| Social fights | **Direct interactions/mental states**; your random-mental-state flag covers the ordinary random gate, not necessarily forced calls. [Historical source](https://github.com/RimWorld-zh/RimWorld-Decompile/blob/master/Assembly-CSharp/RimWorld/Pawn_InteractionsTracker.cs) |
| Berserk, fire-starting spree, drug binge, other breaks | **Direct mental-state machinery.** Existing and explicitly induced states require attention even when random starts are disabled. |
| Inspiration / catharsis | **Direct pawn systems.** Catharsis is a consequence of recovery, not a separate incident generator. Exact 1.6 inspiration gates: **unknown**. |
| Food poisoning, vomiting, disease progression, infection, withdrawal, overdose, starvation, temperature injury | **Direct ingestion/health/jobs.** Disabling random disease incidents does not freeze existing health processes. Historical ingestion code directly applies food poisoning. [Source](https://github.com/RimWorld-zh/RimWorld-Decompile/blob/master/Assembly-CSharp/Verse/Thing.cs) |
| Lovin, pregnancy, birth, animal reproduction, egg hatching | **Direct jobs/health/comps.** Eggs directly generate pawns; Biotech adds further birth/gestation machinery. [Hatcher source](https://github.com/RimWorld-zh/RimWorld-Decompile/blob/master/Assembly-CSharp/RimWorld/CompHatcher.cs), [Biotech](https://store.steampowered.com/app/1826140/RimWorld__Biotech/) |
| Auto-slaughter, ordinary slaughter, hunting | **Direct work/job systems.** |
| Existing enemies, turrets, traps, friendly fire, explosive ammunition | **Direct combat.** Storyteller suppression does not pacify existing actors. |
| Ordinary weather changes and lightning | **Direct weather system.** Historical lightning events directly cause explosions/fire. [Source](https://github.com/RimWorld-zh/RimWorld-Decompile/blob/master/Assembly-CSharp/RimWorld/WeatherEvent_LightningStrike.cs) |
| Flashstorm, eclipse, heat wave/cold snap | Usually **incident entry**, then continuing **game-condition effects**. Already-active conditions remain relevant. |
| Seasonal/day-night temperature, room heat exchange, heaters/coolers, geothermal/other heat sources | **Direct environmental/building systems.** |
| Roof collapse, unsupported structures, fire spread, heat ignition | **Direct structural/fire systems.** |
| Random “Zzztt” | **IncidentWorker_ShortCircuit.** Historical Def confirms this. Rain-exposed electrical faults and other short-circuit callers must be audited separately. [Def](https://github.com/RimWorld-zh/RimWorld-Core/blob/master/Core/Defs/Storyteller/Incidents_Map_Misc.xml) |
| Burning batteries/chemfuel, explosive creatures/buildings, active wicks | **Direct explosive comps.** Historical implementation also notifies nearby pawns of danger. [Source](https://github.com/RimWorld-zh/RimWorld-Decompile/blob/master/Assembly-CSharp/RimWorld/CompExplosive.cs) |
| Deep-drill infestation | An **IncidentWorker exists**; do not assume each drill tick directly rolls/spawns infestation. Exact 1.6 scheduling route: **unknown here**. [Patch precedent](https://github.com/TheFarawayDev/Far-s-Rimworld-Modding/blob/main/WhyInfestations/Source/WhyInfestations.cs) |
| Self-tame | **Incident** in historical vanilla Defs; distinguish ordinary taming jobs. [Def](https://github.com/RimWorld-zh/RimWorld-Core/blob/master/Core/Defs/Storyteller/Incidents_Map_Misc.xml) |
| Existing hives, insect/other pawn spawners, opened caskets, dormant defenders | **Direct component/container/activation routes**, even if an incident originally placed them. Exact 1.6 inventory: **unknown**. |
| Royalty permits, psycasts, mech-cluster condition causers | **Mixed.** Trooper delivery, strikes, abilities and existing condition machinery cannot all be covered by incident suppression. [Royalty mechanisms](https://store.steampowered.com/app/1149640/RimWorld__Royalty/) |
| Ideology rituals, duels, sacrifices, role/precept demands, slavery and associated behavior | **Mixed ritual/lord/job/thought systems**; individual ritual rewards may invoke incidents. Exact routing per reward: **unknown**. [Ideology mechanisms](https://store.steampowered.com/app/1392840/RimWorld__Ideology/) |
| Biotech mech gestation / boss summoning | Gestation is **direct production**. Boss summoning is a distinct mechanism; exact incident/quest route: **unknown**. |
| Pollution, wastepack dissolution, retaliation | **Mixed.** Multiplayer explicitly relocates world pollution and goodwill updates into simulation ticks. Retaliatory incidents are a separate stage. [Source](https://github.com/rwmt/Multiplayer/blob/master/Source/Client/AsyncTime/AsyncWorldTimeComp.cs) |
| Anomaly ambient/monolith event selection | **Unknown exact gating.** Some manifestations are incidents; do not assume every selector obeys `enableStoryteller`. |
| Existing Anomaly entities, containment escapes, infections, corpse/shambler activity, flesh growth, psychic rituals | **Mixed direct entity/health/map/ritual systems.** Complete path inventory: **unknown**. [Expansion mechanisms](https://store.steampowered.com/app/2380740/RimWorld__Anomaly/) |
| Pit-gate/undercave collapse | **Direct map-component behavior** is evidenced by Multiplayer’s deterministic collapse patch. [Patch](https://github.com/rwmt/Multiplayer/blob/master/Source/Client/Patches/Determinism.cs) |
| Odyssey tile mutators, biome hazards, gravship travel/landing events, site timers and traps | **Mixed; exact per-feature routes unknown.** Include vacuum/temperature hazards and destination-generated threats. [Odyssey mechanisms](https://store.steampowered.com/app/3022790/RimWorld__Odyssey/) |
| Ordinary job interruption | **Direct AI:** hunger/rest/recreation, schedules, danger response, target destruction, failed reservations/pathing, lord duties, drafting/orders and invalidated toils. No incident required. |

For the bridge, this argues for observing **effects and their causes**—spawn, damage, fire, condition/weather change and job interruption—alongside incident attempts. An incident-only calm profile cannot establish environmental isolation.

**9. Corrections and dangerous incompleteness in the READ facts — confidence: high on the first three; otherwise stated limits.**

- **Path results being tick-locked is compatible with nondeterministic path computation.** The documented within-tick race is the most consequential qualification. [Evidence](https://github.com/rwmt/Multiplayer/blob/master/Source/Client/Patches/PathFinderPatch.cs)
- **The `DoSingleTick` ordering omits dependencies outside that method.** Manager updates, post-tick visuals, camera context and frame state matter. [Evidence](https://github.com/rwmt/Multiplayer/blob/master/Source/Client/AsyncTime/AsyncTimeComp.cs)
- **`IncidentWorker.TryExecute` is a useful observation point, not a universal environment boundary.** Direct effects and existing systems bypass it.
- **A tick-derived animation clock does not prove state-only rendered truth.** Graphic selection, transforms, visibility and shaders remain separate.
- **`noAnimals` is destructive**, so it invalidates ordinary animal/flight fixtures. Likewise, disabling damage can remove the opportunity a combat contract needs.
- **`pauseOnError` does not automatically stop your manual tick loop.** Your driver must honor the stop condition.
- **A save is a serialization boundary, not a process snapshot.** Restore at a balanced Rand-stack boundary and account for loading itself.
- **The 10,000-message cap needs a narrower interpretation:** it does not establish coverage of every logging channel, and resetting a count does not establish that “once” suppression has been cleared.
- I found no source-backed reason to reject your exact tick cap/order, flight fields, initial Rand seeding, or utility-existence statements. Their exact match to your installed 1.6 revision remains **not independently verified**.

For your result taxonomy, missing render evidence should remain **COULD NOT LOOK**; lost telemetry or an invalid tick driver is **APPARATUS FAULT**. Neither should become MOD FAILURE merely because the expected event was absent.