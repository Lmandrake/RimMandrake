**The core idea is feasible, but the design is not ready to build as written.** The strongest problems are in arrival bookkeeping, damage-hook semantics, and flyer lifecycle—not the knockback arithmetic.

Confidence labels below: **Confirmed** means established by the supplied files/facts; **source-backed** means additionally supported by inspected public source, whose extra details should be checked against your exact installed 1.6 assembly; **risk** means a concrete failure scenario requiring verification.

1. **High — A flyer can remove a trapped colonist’s prisoner-of-the-pit status. §§2, 4.2, 7. Confirmed.**

   `RM_SuperdeepTrapState.Tick` prunes jumpers when `!p.Spawned`. Launch an own-faction pawn already held in a pit, and its jumper flag disappears during flight. `RM_Patch_PawnFlyer_LandInPit` then returns because the takeoff cell was already superdeep, so landing does not restore that flag.

   With the normal own-faction carve-out, `Captures(p)` becomes false and the colonist can cease being held. Constraining the knockback destination to D = 4 does not repair its status afterward.

   **Fix:** preserve held/jumper state across the flyer, change FlowWorks’ pruning semantics, or initially exclude pawns already inside pits. The claim “no FlowWorks change needed” is too broad.

2. **High — `damagedThings` guarantees one damage application, not one execution of your postfix. §§3.1, 4.1. Confirmed/source-backed.**

   A postfix runs after an ordinary early return. The base method returns when a thing was already damaged; it also adds a thing to `damagedThings` **before** checking `ignoredThings`. Therefore an unconditional enqueue can push an ignored pawn or enqueue an already-processed pawn again.

   Record eligibility before the call, including prior membership and ignored status; maintain your own deduplication keyed by **explosion identity and pawn identity**. Checking only whether the pawn appears in `damagedThings` afterward is insufficient. [DamageWorker source](https://raw.githubusercontent.com/Chillu1/RimWorldDecompiled/master/Verse/DamageWorker.cs)

   The protected visibility is not a problem for Harmony. The virtual dispatch limitation is real: inherited implementations reach the base patch; overrides that bypass base do not. Audit the worker classes actually used by loaded DamageDefs. Also account for other patches skipping the original. [Harmony injection documentation](https://harmony.pardeike.net/v2/articles/patching-injections.html)

3. **High — `requiresWound` cannot be implemented reliably by the proposed postfix alone. §§3.1, 4.1. Confirmed.**

   `ExplosionDamageThing` returns `void`; the actual `DamageResult` from `TakeDamage` is local. Neither hediff count nor membership in `damagedThings` tells you whether this application wounded the pawn.

   Choose explicitly between:
   - **Reached and eligible:** push even when armor absorbs everything.
   - **Actually wounded:** capture the actual damage result at the damage call, with correctly scoped explosion context.

   This matters for shields, armor, damage immunity, zero damage, and patched damage workers. Do not implement `requiresWound` using a health-delta approximation and describe it as exact.

4. **High — The final explosion tick destroys the object before your flush. §4.1. Confirmed/source-backed.**

   Running the postfix after destruction is valid. Reading the explosion’s live map and internal lists then is not: the inspected implementation clears and returns its damage/cell collections during despawn.

   The request needs a captured map, explosion identity, origin cell, and relevant immutable blast data. The proposed tuple lacks several of these. Cache the pawn’s takeoff cell and map before `MakeFlyer`, too. [Explosion source](https://raw.githubusercontent.com/Chillu1/RimWorldDecompiled/master/Verse/Explosion.cs)

   **Cheap decisive test:** use a blast whose only affected cell is processed on its final tick. Verify that the queued push executes after the explosion disappears.

5. **High — Vanilla flyers can silently invalidate your collision and pit guarantees. §§3.4, 4.2, 7. Source-backed.**

   The inspected `PawnFlyer` checks its destination periodically. If invalid, it searches around that destination within roughly four cells. That search does not preserve your travelled line, wall boundary, first-pit stop, or held-in-pit constraint. [PawnFlyer source](https://raw.githubusercontent.com/Chillu1/RimWorldDecompiled/master/RimWorld/PawnFlyer.cs)

   Its jump-target predicate also rejects fogged cells. A perfectly legitimate involuntary destination can therefore trigger redirection simply because it is fogged. [JumpUtility source](https://raw.githubusercontent.com/Chillu1/RimWorldDecompiled/master/RimWorld/JumpUtility.cs)

   A landing-only prefix does not prevent earlier redirection. If you retain flyers, control both periodic destination correction and final landing, scoped specifically to your flyer. A small subclass becomes justified here.

6. **High — Same-tick explosions produce order-dependent damage protection. §§4.1–4.3, 7. Confirmed consequence of the supplied wave/container facts.**

   Explosion A processes a pawn and flushes, despawning it. Explosion B ticks afterward and no longer finds that pawn in the cell. Reverse their order and the survivor, damage, and throw direction can differ.

   Multiple requests collected before a flush also need an explicit policy: first, strongest, combined vector, or sequential displacement. The tick number is not an explosion identifier.

   An end-of-map-tick flush reduces the immediate same-tick problem, but does not solve later blasts missing a pawn during flight. The first explosion’s `damagedThings` does not provide protection or deduplication for other explosions.

   This is a material combat change, especially with barrages. “Order does not matter” is false beyond the narrow cell-postfix ordering described in §7.

7. **High — Landing validation is underspecified and cannot be reduced to “nearest standable cell.” §§3.4, 4.2. Confirmed/risk.**

   A fallback must preserve all relevant constraints: bounds, collision boundary, pit entry, inability to leave a held pit, and pawn-specific terrain rules. A standable cell across a wall or on the far lip is an invalid fallback.

   Several flyers can choose the same empty cell; a pawn can move into it; a door can close; a cover can appear or collapse. Short flights reduce the interval but do not eliminate the case.

   Define deterministic fallback along the original allowed segment, including what happens when **no valid cell remains**. Check the drop result before treating landing as successful. Scope any `RespawnPawn` patch to your flyer so it does not change vanilla jumps and other mods’ flyers.

8. **High — Jobs and carried things are not preserved as cleanly as the design claims. §§4.2, 7. Source-backed.**

   `SuspendCurrentJob` performs job cleanup. Non-suspendable jobs are terminated; cleanup can drop carried things according to the job’s carry policy. Pawn despawn also clears reservations. Consequently, a captured job queue is not a captured, intact job driver with intact reservations. [Job tracker source](https://raw.githubusercontent.com/Chillu1/RimWorldDecompiled/master/Verse.AI/Pawn_JobTracker.cs), [Pawn source](https://raw.githubusercontent.com/Chillu1/RimWorldDecompiled/master/Verse/Pawn.cs)

   `flyWithCarriedThing:true` cannot guarantee preservation if job cleanup already dropped the item. For the hose, verify its **physical holder and cell**, not just the table state `Dropped`.

   VEF’s published `MakeFlyer` transpiler modifies job handling, making the active-VEF check a functional requirement. [VEF patch source](https://github.com/notfood/RimWorld-VanillaExpandedFramework/blob/main/Source/VEF/Abilities/Harmony/PawnFlyer_MakeFlyer.cs)

9. **High — Carried pawns need their own policy. §§3.2, 3.3, 4.2, 7. Confirmed omission/risk.**

   Excluding the pawn **being carried** does not exclude its spawned carrier. A rescuer or kidnapper can be thrown while holding another pawn.

   Decide whether the passenger stays carried, drops at takeoff, or lands separately. Decide whose mass contributes to distance and whether both receive pit fall damage. The existing FlowWorks landing postfix processes `FlyingPawn`, not every pawn transported with it.

   Otherwise a downed pawn can be independently throwable on the ground but effectively exempt from blast and fall consequences while carried. Hauling heavy items has the same missing effective-mass question.

10. **Medium–high — Default filtering contradicts the stated exclusions. §§3.1, 5. Confirmed.**

    “Any unextended harmsHealth explosion at 50%” also includes vanilla unextended harmful DamageDefs. Omitting an extension from Flame does not exclude it from that fallback.

    Define an explicit exclusion policy or give excluded defs an explicit zero-force extension. “Other mods” cannot be inferred merely from absence of your extension.

    Set the fallback to zero initially. A modded explosion using a harmful damage type is not necessarily a pressure blast.

11. **Medium–high — Impact damage lacks a timing and lifecycle contract. §§3.4–3.5, 4.1. Confirmed omission.**

    Is damage applied when planning, at launch, or at landing? If applied before launch and it kills the pawn, another dead/spawned check is required before making the flyer. If delayed, preserve the intended collision target and attribution, and decide what happens if that target disappears.

    Specify zero-distance impacts, door destruction, pawn-pawn damage order, and impact-triggered reactions. Drain a snapshot of pending work so damage callbacks cannot reprocess a half-drained queue.

    Supplying an instigator helps attribution; it does not guarantee that goodwill, battle logs, and the subsequent FlowWorks fall kill all attribute correctly. FlowWorks currently constructs fall damage without the explosion instigator.

12. **Medium–high — “No FlowWorks change” overlooks additional receiving-side cases. §§2, 7. Confirmed.**

    The flyer postfix skips any takeoff cell with superdeep excavation—even an intact **covered** D = 4 cell. Throwing someone from a cover into an adjacent open pit therefore misses the forced-descent call.

    Also:
    - “Captured” means held by FlowWorks’ grid rule, not converted into a RimWorld prisoner.
    - Holding depends on ladder settings, ladder position, faction/jumper status, and sufficient pit width.
    - A lowered ladder permits exit even though forced arrival still causes a fall.
    - The position detector needs an existing baseline; it does not catch every arbitrary position assignment in every lifecycle state.

    The ordinary outside-ground → open-pit flyer route is supported. The universal claim is not.

13. **Medium — Downed pawns are unproven, not known to be categorically incompatible. §§3.2, 4.2, 8.2. Source-backed/risk.**

    The inspected factory does not impose a downed-pawn exclusion. JecsTools explicitly excludes downed pawns in both entry paths, so it provides no evidence for your proposed downed support.

    Test both **already downed before damage** and **downed by this explosion**. Verify posture, health, ownership, and landing—not movement alone.

    The flyer ticks its contents during flight, so audit death from bleeding or another health effect before landing, including corpse handling. Ordinary flyer state is scribed, making normal save/load plausible; that does not prove these exceptional paths safe. [PawnFlyer source](https://raw.githubusercontent.com/Chillu1/RimWorldDecompiled/master/RimWorld/PawnFlyer.cs)

14. **Medium — Mental states, raid AI, prisoners, and exits need behavioral tests, without assuming they all break. §§3.2, 4.2, 8.2. Risk.**

    A flyer is neither an automatic mental-state reset nor a guarantee of uninterrupted AI behavior. Job interruption and reissue can affect duties, targets, hauling, and reservations.

    Test a berserker/manhunter, a real assault-lord raider, a retreating raider, a prisoner outside its cell, and a forming-caravan pawn. Observe behavior after stun expires.

    Bounds clamping prevents an out-of-bounds drop; it does not prevent a resumed exit job from leaving immediately from an edge cell. Despawn into a flyer is not itself `ExitMap`, so do not emit escape/caravan notifications merely because the pawn became unspawned. [Pawn lifecycle source](https://raw.githubusercontent.com/Chillu1/RimWorldDecompiled/master/Verse/Pawn.cs)

15. **Medium — Geometry mixes movement, collision, and presentation rules. §§3.4, 4.2. Confirmed omission/risk.**

    `map.pathing.For(pawn).pathGrid` does not automatically include FlowWorks’ per-request pit customizer. Pit rules still require explicit handling.

    Define precedence when a pit cell is also occupied, flooded, covered, or blocked by an edifice. Define whether downed pawns count as collision obstacles. Specify Euclidean distance versus number of grid transitions; diagonal rays and rounded endpoints otherwise produce inconsistent impact damage.

    The flyer arc provides no physical ceiling collision. Choose an explicit policy for roofs and overhead mountain. A low visual arc under a roof can be acceptable, but it should be intentional. Standing atop or inside passable furniture, fogged destinations, and forbidden cells also need distinct policies; voluntary path restrictions are not automatically appropriate for forced movement.

16. **Medium — The numerical examples and kernel tests disagree with the formula. §§3.3, 8.1. Confirmed arithmetic.**

    For a reference-mass human, force 1 and maximum 3:
    - At distance 1, radius 1.9: `round(3 × (1 − 1/1.9)) = 1`, not approximately 2.
    - At distance 1, radius 2.9: the result is 2, not 3.

    K-07 omits the mass multiplier from §3.5. K-01 is valid for unobstructed distance calculation, not arbitrary final movement through different obstacles. K-12 tests queue/cap bookkeeping, not just a spatial kernel.

    Also define radius-zero handling, exact integer conversion, stable epicentre seed identity, and whether pit stops cause zero impact. Ignoring inventory mass is a balance choice; it is not a physical requirement inherited from prior art.

17. **Medium — Several scene PASS conditions can pass for the wrong reason. §8.2. Confirmed.**

    Strengthen these assertions:
    - **wall/door:** hediff count and door HP can change from the explosion itself. Record damage application type, source, amount, and timing.
    - **pit_colonist/pit_enemy:** `RecentDescents` contains no forced/walked flag. Assert exactly one descent-count increment, expected pawn/cell, and actual held/jumper state.
    - **pit_cover:** the blast may damage the cover directly. Isolate weight triggering and allow the trigger interval after landing.
    - **settings_off/heavy/flying_skip:** prove the wave actually processed the pawn. Otherwise “not moved” proves nothing.
    - **save_mid_flight:** prove the save contains the pawn inside a flyer; after reload count that identity across spawned pawns, holders, corpses, and world pawns.
    - **barrage_perf:** record successful launches and missed/accepted damage applications. A barrage can look cheap precisely because most pawns vanished into flyers.

    Exact event records are stronger and cheaper than inferred hediff-count outcomes.

18. **Medium — The test plan omits the highest-risk transitions. §8. Confirmed omission.**

    Prioritize these before 10,000 random grids:
    - Ignored pawn, duplicate callback, fully absorbed damage, wound-required mode.
    - Final explosion tick; two explosions with reversed tick order.
    - Held own-faction pawn thrown within its pit.
    - Covered D = 4 takeoff into open D = 4.
    - Destination blocked mid-flight; two flyers sharing a destination; fogged destination.
    - Carrying an item and carrying a pawn.
    - Death during flight; save/load before a pit landing.
    - One real raid-lord scene and one active-VEF run.

    Pure fixture tests establish kernel behavior. They cannot establish engine adapters, Harmony dispatch, job restoration, or FlowWorks arrival semantics.

19. **Medium — Scope and complexity exceed the demonstrated owner requirement. §§1, 3–5, 9. Design judgment.**

    The owner clearly requires a forced route into pits. That does not yet establish approval for global combat displacement, collision damage, pawn-pawn impacts, broad DamageDef fallback, and numerous settings.

    Simpler viable alternatives:
    - **Smallest functional version:** Bomb-only, adjacent open pit in the outward direction, one-cell position displacement after damage processing, `Notify_Teleported`, and an explicit FlowWorks arrival notification—or a proven initialized detector. No impact damage or flyer lifecycle.
    - **Visible pit-entry version:** the same narrow eligibility with a short flyer; handle destination correction and initially skip already-in-pit pawns and carriers.
    - **General knockback later:** add distance, mass, collision damage, and more DamageDefs only after the arrival and lifecycle contracts are proven.

    The existing `TryJumpInto` demonstrates that position assignment plus notification is already an accepted receiving-side route. A brief visual effect can make a one-cell displacement readable without containerizing the pawn.

20. **Low–medium — The performance and review-completion claims are too optimistic. §§4.3, 6, 8. Confirmed omission/design judgment.**

    The substantial costs include pawn despawn/respawn, job cleanup, reservation changes, cache notifications, and flyer ticks—not three grid checks. A per-explosion cap is not a per-map workload cap. Define whether the cap counts requests, eligible pawns, or successful launches, and how winners are selected.

    Naming a patch to satisfy F10’s regex is a discovery aid, not functional evidence. F10 should close only from a verified blast → displacement → exactly one forced pit descent.

**Verdict:** proceed with a narrow pit-entry prototype. The normal outside-pit flyer landing seam is useful, but global `PawnFlyer` knockback needs explicit handling of damage eligibility, destination correction, overlapping explosions, carried contents, and FlowWorks state preservation before it is dependable.