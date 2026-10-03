# RimMandrake: Hostile Flora — validation walk
subject: src/RimMandrake/HostileFlora  (packageId `mandrake.rm.hostileflora`)
deps: `mandrake.rm.biomes` (modDependencies, load after); behaviour is the shared `mandrake.rm.creaturebehaviors` reaction mechanism
list: biomes tier (mod folded into the composed 'RimMandrake: Baroque Biomes' when active under the folded name)
status-hint: HOSTILE_FLORA_FIRST_SCRIPT_1 — minimal wave: one animal def (gallowroot) hosting the reaction mechanism; first script drafted, never run live

Sources: `src/RimMandrake/HostileFlora/About/About.xml` description, `Defs/ThingDefs_Races/RM_Gallowroot.xml`, `src/RimMandrake/CreatureBehaviors/Source/RM_CompReactionSource.cs`.

## must be true
- Every def the mod ships (ThingDef and PawnKindDef `RM_Gallowroot`) loads and resolves, and a bogus name reads notFound. → defs_resolve.every_shipped_def_resolves
- The gallowroot is an animal def (ThingDef + race + PawnKindDef), never a Plant, with `manhunterOnDamageChance` 0 so the reaction mechanism is its only aggression path. → UNCOVERED: static source check only (`static_checks`), no live field read needed
- The def carries `RM_CompProperties_ReactionSource` with SameKindWithinRadius propagation and an ActivateSelf response naming `RM_SwarmAggression`, and that mental state def resolves live. → defs_resolve.reaction_comp_loaded_on_def
- Hurting one gallowroot wakes same-kind neighbours within the radius into `RM_SwarmAggression` (shared event budget). → reaction_cluster.neighbours_swarm_when_one_is_hurt
- With `reactionSourceSpawnEnabled` off, no neighbour swarms. → reaction_cluster.mechanism_off_control_no_swarm
- The mod's only settings are the shared `reactionSourceSpawnEnabled` and `reactionSourceBudgetMultiplier`, which are exposed and round-trip. → settings_roundtrip.reactionSourceSpawnEnabled_round_trips, settings_roundtrip.reactionSourceBudgetMultiplier_round_trips
- The event budget caps the cascade (eventBudget 6 total across propagation and the origin's own response). → UNCOVERED: needs a cluster of more than 6 and a mental-state reader; owed to the first live run
- A proximity trigger, the rooted-idle read, real art and biome placement. → UNCOVERED: the About lists them as unbuilt (HOSTILE_MOBILE_PLANTS_1 owes them)

## the walk
1. [D] `jawa/get_defs` over every def derived from `Defs/**/*.xml` plus `MentalStateDef/RM_SwarmAggression`: `foundCount` equals the request, `notFound` empty; a bogus def reads notFound   # defs_resolve
2. [D] `jawa/mod_settings_field` get/set/get on the two shared fields   # settings_roundtrip
3. [B] `jawa/spawn_pawn` x3 `RM_Gallowroot`, `jawa/damage` one, step ticks, `jawa/pawn_get` on the neighbours (UNMEASURED while `pawn_get` has no mental-state field)   # reaction_cluster
X. [S] (human pass) the placeholder tortoise art reads as a creature that is not quite an animal; owner decides.

## north star
state: DRAFT
validated-hash:

No owner north-star bars are drafted for this mod yet.

## anti-guessing notes
RULED OUT: "gallowroot should be a Plant def so it can be rooted" — a RimWorld Plant cannot move or fight; the owner's ruling (2026-09-22) is a real animal def (About.xml).
RULED OUT: "the mod needs its own settings class" — the shared event budget is the one load-bearing number and already a toggle plus dial in CreatureBehaviors; `static_checks` confirms both fields exist there.
