**1. DEBUGGING**

Scope: the supplied text omits the kernels, most Harmony patches, most defs, historical source, and `validation.py`. Their correctness, def loading, refactor parity, and validation coverage are **UNVERIFIABLE**. No game or test execution was performed. References below use one-based lines within each inlined source file.

1. **Defensive discharge can recurse before its cooldown takes effect.**  
   `Source/RM_CompDefensiveDischarge.cs:86` calls `attacker.TakeDamage(shock)` before recording `lastDischargeTick` at line 88. Two adjacent discharge carriers can retaliate into each other while both still appear ready. A configured damaging discharge makes this especially direct; exact EMP notification behavior is **UNVERIFIABLE** from the bundle.  
   **Minimal fix:** record the cooldown before `TakeDamage` and add a re-entry guard, including for the permitted zero-cooldown configuration. **Severity: high. Confidence: high on the ordering defect.**

2. **Wound sharing cannot identify the injury belonging to the current damage event.**  
   `Source/RM_CompWoundLink.cs:53`, `:103` selects the largest injury with `ageTicks <= 0`. Several injuries can be created within one pawn tick, including injuries mirrored by this mechanism. Another damage notification can therefore share the earlier, larger injury again. The function also ignores `totalDamageDealt`, so a zero-damage notification is not rejected. Whether vanilla merges particular injury types is **UNVERIFIABLE** here; merged injuries would present another identification problem.  
   **Minimal fix:** obtain the injuries or severity changes attributable to this damage application; do not use age as an event identifier. Reject zero actual damage first. **Severity: high. Confidence: high.**

3. **Wound sharing heals the original even when no recipient receives a wound.**  
   `Source/RM_CompWoundLink.cs:79`, `:88`, `:180`: matching-tag kin can lack an equivalent remaining body part. Every `MirrorInjury` can return without adding anything, yet `freshInjury.Heal(shareAmount)` still executes. Cross-species groups or amputated kin become free wound mitigation.  
   **Minimal fix:** return success from `MirrorInjury`; heal the source only when at least one transfer succeeds. **Severity: medium. Confidence: high.**

4. **The shared amount can exceed the source wound.**  
   `Source/RM_CompWoundLink.cs:65` has no upper bound on `shareFraction × woundLinkShareMultiplier`. Whenever that product exceeds one, recipients receive more severity than the source contains, while the original can only lose its existing severity.  
   **Minimal fix:** validate the fraction and clamp the effective fraction to `[0,1]` before calculating the amount. **Severity: medium. Confidence: high; activation depends on content tuning.**

5. **“Equivalent” body parts collapse onto the first matching part.**  
   `Source/RM_CompWoundLink.cs:164` matches only `BodyPartDef`. A right-leg injury can become a left-leg injury; repeated leg injuries can all concentrate on the first remaining leg.  
   **Minimal fix:** preserve the body-tree path or sibling identity for identical body plans, with an explicit fallback policy for different bodies. **Severity: low. Confidence: high.**

6. **Kin mending multiplies the advertised healing budget by injury count.**  
   `Source/RM_HediffComp_KinMending.cs:130` applies the full calculated amount to every non-permanent injury. At default tuning and body size one, ten eligible wounds receive approximately 30 total severity/day, rather than the documented three severity/day for the carrier. The predicate also does not establish the documented “tendable” eligibility.  
   **Minimal fix:** allocate one healing budget across eligible injuries, consuming only the severity actually healed. **Severity: medium. Confidence: high on the arithmetic and contract mismatch.**

7. **Psychic-stun cooldown is lost on save/load.**  
   `Source/RM_CompProximityPsychicStun.cs:18` stores `lastTriggerTick`, but the complete class has no `PostExposeData`. Loading restores the sentinel, allowing another emission despite the saved world still being within the cooldown. Existing stun hediffs can mask this until a new eligible pawn approaches.  
   **Minimal fix:** Scribe the field under a distinct, stable key. **Severity: medium. Confidence: high.**

8. **Cycle counters discard elapsed-time overshoot.**  
   `Source/RM_HediffComp_KinMending.cs:59` and `Source/RM_CompShardArmor.cs:57` replace the counter with a full interval after crossing zero. A shard cycle configured to 251 ticks consequently repeats every 500 ticks under 250-tick callbacks. Kin mending additionally calculates healing from the configured interval rather than the elapsed interval, under-delivering when callbacks overshoot.  
   **Minimal fix:** carry the remainder forward and account for elapsed cycles, with bounded catch-up where appropriate. **Severity: low. Confidence: high; defaults can conceal it.**

9. **Disabling the shade grid unexpectedly freezes burst recovery.**  
   `Source/RM_HediffComp_ShadeDrivenSeverity.cs:35` returns zero when `shadeGridEnabled` is false. The settings contract says disabling the grid makes consumers experience full sun; this consumer instead preserves the current burst or fatigue stage indefinitely.  
   **Minimal fix:** gate freezing only on `heatDrivenBurstEnabled`; use shade zero when the grid is disabled. **Severity: medium. Confidence: high.**

10. **A nearby hostile scan is not equivalent to acquiring a hunting target.**  
    `Source/RM_CompAquaticAmbusher.cs:100`, `Source/RM_CompHeatBurstPredator.cs:96`, and `Source/RM_CompDrumLure.cs:158` exclude every candidate for which `HostileTo` is false. A current `PredatorHunt` target satisfying that condition cannot trigger these hunting enhancements. Aquatic ambush explicitly claims the scan is behaviorally identical to checking the melee target; it is not.  
    **Minimal fix:** prioritize the current valid hunting/combat target, then apply a separately defined acquisition policy. Actual consumer faction behavior is **UNVERIFIABLE** without their defs. **Severity: medium. Confidence: high on the mismatch.**

11. **Aquatic ambushers can re-hide during an active lunge.**  
    `Source/RM_CompAquaticAmbusher.cs:78` adds invisibility whenever the fresh proximity scan finds no target. The existing-lunge guard lives later inside `TriggerLunge`. If the target leaves the scan radius while the attacker remains in deep water, the comp can hide it during the approach.  
    **Minimal fix:** handle the active lunge state before scanning; keep it visible until that job ends. **Severity: medium. Confidence: high.**

12. **Polling behaviors can overwrite player orders and mental-state jobs.**  
    `Source/RM_CompAquaticAmbusher.cs:132`, `Source/RM_CompDrumLure.cs:222`, and `Source/RM_CompHeatBurstPredator.cs:133` force jobs without checking drafted status, mental state, faction ownership, or permissible current jobs. A tamed carrier can abandon its orders; an affected wild pawn can abandon fleeing or another forced behavior. The false-shade comp already demonstrates explicit guards for these cases.  
    **Minimal fix:** define allowed interruption states and check them before applying buffs or starting jobs. **Severity: high. Confidence: high.**

13. **False-shade opening damage bypasses melee accessibility.**  
    `Source/RM_CompFalseShadeAmbusher.cs:136`, `:177` selects by distance and applies damage immediately, without checking line of sight or legal melee reach. A nearby pawn separated by blocking geometry can receive the scripted strike even if the subsequent melee job cannot reach it.  
    **Minimal fix:** require valid melee accessibility before the opening damage. **Severity: medium. Confidence: high.**

14. **The false-shade attack has a timer, but no pursuit leash.**  
    `Source/RM_CompFalseShadeAmbusher.cs:191` gives `AttackMelee` a 600-tick expiry. Nothing here ends that attack when the prey leaves the ambush radius, despite the stated stationary-ambusher boundary. Exact pursuit behavior depends on the vanilla driver, which is not included.  
    **Minimal fix:** enforce a distance limit during the attack through a driver fail condition or equivalent job control. **Severity: medium. Confidence: medium.**

15. **Heat retreat mistakes every `Goto` for a retreat.**  
    `Source/RM_CompHeatBurstPredator.cs:118` suppresses retreat whenever the current job is any `Goto`, including one leading farther into sunlight. At line 113, already standing in shade also returns without preventing an existing hunt from immediately carrying the pawn out again.  
    **Minimal fix:** recognize an owned retreat job and validate its destination; explicitly maintain recovery behavior until the fatigue tail ends. **Severity: medium. Confidence: high.**

16. **A lure can remain assigned after its movement job has failed or been replaced.**  
    `Source/RM_CompDrumLure.cs:119`, `:171`, `:195` claims the target after issuing one ordinary `Goto`. There is no reachability check, job-ownership check, maximum-distance check, or timeout in this state machine. With `luredHediff == null`, a living same-map target can remain assigned indefinitely after the job is interrupted. With a marker, the stall lasts until removal; its configured duration is **UNVERIFIABLE**.  
    **Minimal fix:** verify reachability, require successful job assignment, and clear ownership when the owned movement job ends or a deadline expires. **Severity: medium. Confidence: high.**

17. **Lure cleanup is skipped for downed, dead, or despawned predators.**  
    `Source/RM_CompDrumLure.cs:53` returns before the disabled-setting cleanup. There are also no death/despawn cleanup overrides. Turning the feature off while its carrier is downed therefore leaves the target reference and marker intact until another mechanism removes them or the carrier resumes ticking normally.  
    **Minimal fix:** perform owned-state cleanup before the activity guard and from death/despawn lifecycle hooks. **Severity: medium. Confidence: high.**

18. **The tether does not enforce “visible target.”**  
    `Source/RM_CompTetherPull.cs:176` checks geometric line of sight, but never checks pawn invisibility or perceptibility. Invisible hostile pawns remain candidates.  
    **Minimal fix:** apply the appropriate pawn-perception eligibility check during acquisition. **Severity: medium. Confidence: high.**

19. **Rescue targets can take priority over enemies.**  
    `Source/RM_CompTetherPull.cs:195` selects the closest member of the combined hostile/rescue set. A nearby downed colonist wins over a farther enemy, contradicting both the method’s “hostile … else” contract and the settings tooltip.  
    **Minimal fix:** track separate hostile and rescue candidates and return the hostile candidate first. **Severity: medium. Confidence: high.**

20. **`TryRope` bypasses its own operating constraints.**  
    `Source/RM_CompTetherPull.cs:205` accepts null, dead, off-map, out-of-range, or obstructed targets; it also ignores cooldown, `CanWork`, and an existing tether. Null produces an NRE after counters and state have already changed. Other callers can overwrite an active tether without notifying its host.  
    **Minimal fix:** validate before mutation. Keep any intentionally unrestricted proof operation separate. **Severity: medium. Confidence: high.**

21. **Tether despawning does not release host state.**  
    `Source/RM_CompTetherPull.cs:146` releases an unavailable host only when `CompTick` runs. There is no `PostDeSpawn` release. Removing or relocating a reeling building can retain its target and skip the host’s release callback, including the lance’s power reset.  
    **Minimal fix:** release and notify the host during despawn; validate retained target state after load/spawn. **Severity: medium. Confidence: high.**

22. **Sand submersion lacks its null-def guard.**  
    `Source/RM_CompSandSwim.cs:234` passes `Ext.submergedHediff` directly to `HediffMaker.MakeHediff`, although the `Submerged` property and `Surface` explicitly allow that field to be null. An extension-only consumer with the field missing reaches an invalid hediff creation path. Whether extension validation rejects it is **UNVERIFIABLE** because that file is omitted.  
    **Minimal fix:** guard the runtime operation and require the def in extension validation. **Severity: medium. Confidence: high on the unsafe path.**

23. **Sand-swim kill signs ignore the master switch and actual attack state.**  
    `Source/RM_CompSandSwim.cs:325` emits funnel filth and an underground-attack narrative whenever the victim died on swim terrain. It never checks `sandSwimEnabled` or whether the killing attack followed a breach. The always-installed marker continues forwarding kills while swimming is disabled.  
    **Minimal fix:** gate the notification and associate it with a recorded breach/attack event. Do not require current submersion, because the attacker surfaces before striking. **Severity: low. Confidence: high.**

24. **Changing a nonzero rumble volume does not update a playing rumble.**  
    `Source/RM_CompSandSwim.cs:297` sets volume only when creating the sustainer. Moving the slider from 100% to 25% leaves an existing uninterrupted rumble at its previous volume; zero works because it ends the sound.  
    **Minimal fix:** track the effective playing volume and recreate the sustainer when it changes, as the heat soundscape already does. **Severity: low. Confidence: high.**

25. **Cached false shade follows moving or newly downed bodies.**  
    `Source/RM_FalseShade.cs:98`, `:107` rechecks only spawn/map membership, then uses the pawn’s live position. Until the next refresh, a formerly stationary pawn casts false shade while moving; a newly downed pawn remains a lure too.  
    **Minimal fix:** repeat the cheap dead/downed/moving eligibility checks in `FalseShadeAt`, or invalidate immediately on those transitions. **Severity: medium. Confidence: high.**

26. **Harvested sight blockers can remain opaque for 2,000 ticks.**  
    `Source/RM_CompSightBlocker.cs:102` refreshes plant qualification only on the long tick. A harvest resetting growth below the threshold leaves the old blocking registration until that callback—up to 0.8 in-game hours. This affects targeting immediately after an observable removal of foliage.  
    **Minimal fix:** refresh after harvest/growth-reset operations while retaining coarse updates for ordinary growth. **Severity: medium. Confidence: high.**

27. **Movable sight blockers have no normal-tick movement refresh.**  
    `Source/RM_CompSightBlocker.cs:61`, `:102`, `:108` can update a changed occupied rectangle, but only spawn, rare, and long hooks call that code. A movable consumer serviced only through normal/interval ticking leaves blocking cells at its previous position. The actual ticking configuration of consumer defs is **UNVERIFIABLE**.  
    **Minimal fix:** provide a throttled normal/interval refresh or a movement callback, with an early-out for unchanged position. **Severity: medium. Confidence: high on the conditional defect.**

28. **Ranged hits qualify for the documented melee rescue roll.**  
    `Source/RM_CompGrappler.cs:93`, `:119` checks only that the damage instigator is another pawn. A distant bullet can break holds with the same probability as the specified third-pawn melee hit.  
    **Minimal fix:** check melee damage provenance, or explicitly change the mechanic and its descriptions to permit ranged rescue. **Severity: medium. Confidence: high.**

29. **Single-cell adhesive surfaces perform full-map scans.**  
    `Source/RM_CompAdhesiveSlick.cs:64`, `:67` allocates a list and examines every spawned pawn even at the default radius zero. With `W` web surfaces and `P` pawns, this produces approximately `W × P` candidate checks per scan period, although each surface needs only its own cell’s occupants. Dense web content makes this a foreseeable CPU/GC problem.  
    **Minimal fix:** use the thing grid for radius zero and bounded local queries for nonzero radii. **Severity: medium. Confidence: high on complexity; measured cost is UNVERIFIABLE.**

30. **Specimen proof counters report attempted placement as successful placement.**  
    `Source/RM_CompResearchSpecimens.cs:121`, `:122` ignores the placement result and records the input thing’s remaining stack count. Failed placement can report specimens spawned; merging can make that object unsuitable for measuring the quantity placed. Early-return paths also leave previous static proof values intact.  
    **Minimal fix:** reset proof fields at entry and count successfully placed units independently of the temporary stack object. **Severity: low. Confidence: high.**

31. **The reel proof bypasses the behavior most likely to fail in play.**  
    `Source/RM_CompTetherPull.cs:270` calls `ReelStep` without the operating gate or timer. `ProofPull` repeatedly invokes it without advancing ticks. Consequently, its position delta cannot establish correct cadence, continued power/manning checks, stun duration, or interaction with ordinary pawn jobs.  
    **Minimal fix:** retain this as a movement-unit proof, but add a production-tick integration proof with elapsed ticks and host-state transitions. **Severity: medium for validation reliability. Confidence: high.**

32. **Harmony failure reporting can falsely say an installed guard is off.**  
    `Source/RM_FlightJobStartGuard.cs:40`, `:45`, `:50` installs the flight prefix before installing the diagnostic prefix. If the latter fails, the catch reports “guard is off” without undoing the first patch. Diagnosis then begins from false patch-state information.  
    **Minimal fix:** isolate the two installations and report their actual states separately. **Severity: low. Confidence: high.**

Additional requested checks remain **UNVERIFIABLE**:

- Old capstan fields versus the new comp’s Scribe keys, duplicate legacy writes, and migration behavior: the former implementation is absent.
- Harmony target signatures, ordering, context cleanup, exception handling, and duplicate installation for sight, sun heat, pinned sun, tracks, and other omitted patches.
- Whether each consumer’s ticker dispatch reaches its required comp callbacks.
- Def references, XML inheritance, ThinkTree insertion ordering, hediff stages/removal rules, and `About.xml` dependencies.
- Kernel boundary conditions, float/int conversions, graph algorithms, pool eviction, and the actual validator’s assertions.
- Thread-safe operation under a threading mod. The visible code assumes main-thread mutation; no worker-thread compatibility is demonstrated.

**2. LIKELY FUTURE COMPLICATIONS**

- **Shared Scribe namespaces constrain composition.** `RM_CompTetherPull.PostExposeData` uses generic names such as `target`, `pulls`, and `snaps`; multiple copies or another comp using those names can collide within the thing’s save node. Several other comps use generic counter names too. Preserve released keys, but establish unique keys and explicit migrations for new combinations. Identical names alone do not prove compatibility with the omitted capstan implementation.

- **Multiple behavior comps will compete for job ownership.** Aquatic ambush, drum lure, heat retreat, home tether, and future content can all act on one race. Independent polling plus `InterruptForced` makes the result depend on callback order. Introduce an explicit interruption policy and ownership token before stacking these mechanics.

- **Propagation can spend the origin’s response budget first.** `RM_CompReactionSource.TriggerReaction` propagates before responding locally. A propagation rule consuming the shared budget can leave nothing for the source that was actually disturbed. The omitted rules determine whether this happens today. Reserve local response cost or make response order an explicit rule.

- **Suppression enforcement is distributed.** `TriggerReaction` checks suppression, but `TryActivateFromPropagation` does not visibly repeat that check; the plant alarm also enters its response directly. Omitted callers/responders may protect those paths. Future callers can bypass that protection unless suppression is enforced at the public activation boundary.

- **Ecology can reproduce without consuming its limiting resource.** `RM_CompVerminBreeder.FoodExistsNearby` accepts mere item presence without consumption or reachability. One inaccessible food stack can support many breeders. `RM_CompDungSeeder.SeedYoungCreature` has no visible population ceiling. Existing vermin-cap correctness is **UNVERIFIABLE**, but dung-created population can still amplify breeding, scans, and saves.

- **Faction and ownership assumptions will break mixed populations.** `RM_CompParentalEnrage.FindGuardian` chooses by race/adulthood/proximity without matching faction. A tamed adult can answer for a wild calf and be forced against an approaching pawn of its own faction. Multiple calves also maintain independent cooldowns, so one nursery can rouse several adults.

- **Automatic comp insertion checks the properties class, not the runtime comp class.** `RM_SandSwimStartup` detects only `RM_CompProperties_SandSwim`. Another mod adding the same runtime comp through bare `CompProperties` can produce two swimmers, duplicated cosmetics, and duplicate save keys. Compare `compClass` as well.

- **“One kind of heat” needs an integration invariant.** `RM_CompHeatCook` deals direct Burn damage independently of ambient heat pushing; sun-scald and burst fatigue have separate severity mechanisms. Those distinctions may be intentional, but settings and thermal protection must explain their relationship. The omitted heat patches make double application and protection consistency **UNVERIFIABLE**.

- **Global caches and scratch collections assume stable defs and serial execution.** Deep-water sets, swim-terrain sets, biome rosters, and `RM_GlareBlind.scratch` lack invalidation or synchronization. Runtime def modification, parallel ticking, or re-entrant callbacks can invalidate those assumptions. Keep live Verse operations on the main thread and expose explicit cache rebuilding where supported.

**3. UNLEVERAGED OPPORTUNITIES**

- **Make offline validation exercise adapters and saves, not only kernels.** The visible `SwimEnv` translates live jobs, positions, weather rolls, and effects into kernel calls; correctness there can fail despite perfect pure-kernel tests. The omitted test suite’s coverage is **UNVERIFIABLE**. High-value additions are:

  | Boundary | Required regression case |
  |---|---|
  | Damage | Two retaliating discharge carriers; two wounds in one tick; zero-damage notification |
  | Transfer | No equivalent recipient part; repeated left/right parts; effective fraction above one |
  | Healing | One versus ten wounds with the same per-pawn daily budget |
  | Saves | Reload during psychic cooldown, lure, tether, and recovery |
  | Lifecycle | Disable, down, despawn, relocate, and respawn an active carrier |
  | Cadence | Non-divisible intervals and large callback deltas |
  | Targeting | Invisible enemy; closer rescue target; unreachable prey |
  | Proofs | Failed/merged specimen placement and timed production reeling |
  | Harmony | Exact signature resolution and installed-prefix/postfix counts |

- **Turn settings into an inspectable control surface.** `RM_CreatureBehaviorsSettings.DoWindowContents` is one long listing with no visible search, section reset, or consumer inventory. Add searchable groups, per-group defaults, and “used by these loaded defs” information. Show effective lance range/strength by fabric using the existing `ProofStuffTable` calculations. Normalize persisted numeric values on load, independently of slider rendering.

- **Describe toggle timing and retained effects precisely.** Aquatic and lure cleanup occurs on a later scan and can be blocked by activity guards; several heat effects intentionally freeze; shard armor remains. Settings should state those consequences and distinguish stopping new effects from removing existing ones.

- **Use `ConfigErrors` to reject silent or hazardous content.** Many properties lack validation. Check required extensions, pawn-only carriers, finite numbers, ordered ranges, safe radial radii, plant-only germination targets, filth-only leavings, and compatible hediff classes. Validate assembled consumer XML, including patches, rather than only this toolkit’s defs.

- **Expose structured runtime evidence.** Extend the tether’s existing outcome codes to reactions and lures: rejected target reason, owned job, cooldown remaining, budget spent, suppression rejection, and successful spawn count. Keep proof results per invocation/map rather than in unreset global “last result” fields.

- **Reuse spatial bookkeeping.** Sense-web nodes, sight blockers, and moving shade already use registration concepts. Similar per-map indexes for grapples, kin tags, and local hazards would avoid repeated full-map scans and provide one place to rebuild derived state after loading.

**4. EXTENSIONS BEYOND THE MOD**

- **Treat tether pulling as a campaign-wide host interface.** `IRM_TetherPullHost` can support ship winches, rescue equipment, salvage machinery, and creature-operated pulls. Centralize validation, movement, release, and save behavior before adding hosts; keep fabric tuning and operating costs in host data.

- **Share targeting and interruption policies across creature kits.** The same neutral-prey exclusion and forced-job hazards appear in several comps. A reusable target policy should distinguish hunting prey, hostile combatants, perceived intruders, and owned pawns without making each content pack recreate those decisions.

- **Reuse truthful versus perceived environmental layers.** `RM_ShadePerception` separates destination selection from physical heat exposure. Other campaign content can use that distinction for decoy shelter, misleading sound, false food signals, or camouflage while preserving the underlying environmental simulation.

- **Make save compatibility and def validation toolkit-wide contracts.** Stable keys, old-save fixtures, registration rebuilding, exact Harmony signature checks, and consumer schema checks belong across RimMandrake’s shared assemblies. Kernel extraction should require both kernel tests and preserved live-state transcripts.

- **Integrate sea-floor content through ship arrival and map lifecycle.** The supplied code does not establish any sea-floor access mechanism. Reuse these behaviors after a ship delivers pawns or creates/loads the destination map; exercise despawn, cross-map references, and registry reconstruction there. Swim-capable fauna should remain local ecology, with ship-only access preserved.