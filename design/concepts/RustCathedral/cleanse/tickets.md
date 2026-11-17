# Proposed work tickets

These are proposal tickets, not ledger writes. Paths beginning Source/, Defs/ or Patches/ below are relative to src/RimMandrake/RustCathedral/ unless an absolute repo-relative path is given. All implementations and tests are future work; none ran here.

Every built-extra switch retains its code and definitions. A fresh-default absence test reads emitted things, active jobs, incidents, letters and state, never absence of loaded defs. Each test also requires a clean log. The positive arm enables the named switch plus only its explicitly declared deferred prerequisites in an isolated fixture; it never counts as a core-bar pass. Disabling during a saved activity suspends it with its identities/materials intact and a readable state, rather than destroying pawns. Update initializer, Scribe fallback, reset and composed defaults together, including a visible old-preference migration. No automatic consent or deletion is implied.

## T1: Defer campaign stage shaping

Source and callers: Source/Hum/RM_MapComponent_BiomeAttitude.cs: SetStage, ClampToStage, DecayIrritation; RM_BiomeAttitudeDef stageParams; current default stage is zero.

Work: Add a Next version stage-integration gate, default off. Keep saved stage but bypass its display ceiling/decay shaping at defaults. The public warning is actual local mood. Do not remove stage APIs or change hidden campaign facts.

Acceptance test: Fresh defaults show the same actual local mood across stored campaign stages; no campaign shaping occurs and the log is clean. Gate on in an isolated campaign fixture exercises the authored stage adapter; record its output separately, never use it to pass the free-biome warning.

## T2: Defer droid commentary

Source and callers: Source/Hum/RM_MapComponent_BiomeAttitude.cs: bandChanged -> MaybeFireCommentary; RM_BiomeAttitudeDef -> CommentaryEntryIndex.

Work: Both ordinary and stage-keyed remarks off by default, labelled Next version. Gate transition callbacks and pending speech; preserve content and selection code.

Acceptance test: Fresh defaults with eligible player droids and real band transitions emit no commentary messages or letters and no errors. Enabling ordinary commentary gives a matching remark on a qualifying transition after its cooldown; stage pools require their own explicit gate.

## T3: Defer curiosity shedding

Source and callers: Defs/ThingDefs_Races/RM_LivingBolt.xml CompSpawner -> HarmonyPatch_WatchedBolts_GateShed.

Work: boltShedEnabled and all persistence/reset fallbacks default off, Next version. Keep the race and its ordinary dance; retain existing drops in old saves without new production.

Acceptance test: Fresh default map with native living bolts run beyond the configured shed interval has no RM_BoltShedCuriosity emitted and a clean log. Gate on produces a curiosity at a valid empty location. This is a state read, not a count of definitions.

## T4: Defer the line-cycle

Source and callers: Source/Hum/RM_LineCycle.cs incident/map tick -> SetLineCycleDrop, still jobs, dust and roll sound; Defs/IncidentDefs/RM_LineCycle.xml.

Work: Line-cycle off and labelled Next version. Stop event eligibility, new still jobs, dust/sounds and transient hum override. If switched off mid-roll, release issued stillness jobs and restore base sound without touching residents.

Acceptance test: Fresh defaults through an eligible duration emit no roll incident, RM_LineCycleStill jobs, memories or roll letters and log stays clean. Gate on plus a qualifying incident produces a progressing front and its jobs/sound. Disabling mid-event leaves no active front, overridden hum or stranded still jobs.

## T5: Defer learned hum literacy without losing eel pricing

Source and callers: Source/Hum/RM_HumReading.cs: exposure map component, GrantTrait, readout comp; same source houses eel-butchery pricing; hull inspect consumes AnyReaderOn.

Work: humReadingEnabled off, Next version. No exposure grants, new reader letters or reader-only baseline cues. Preserve saved traits inertly and all core surface cues. Keep eel-butchery attribution behind the kept fishing predicate independently of literacy; hull callbacks short-circuit if hull feature off.

Acceptance test: Fresh default newcomer earns no RM_HumReader or literacy letter, while baseline work-location warning and actual player eel butchery still affect the same local temper. Gate on accrues real exposure and grants the trait in its eligible state; no direct trait grant counts as the positive arm.

## T6: Defer hum primers

Source and callers: Defs/RecipeDefs/RM_WriteHumPrimer.xml; ThingDefs_Items/RM_HumPrimer.xml; RulePackDefs; book outcomes in Source/Hum/RM_HumReading.cs; Bill.PawnAllowedToStartAnew patch.

Work: Add separate Next version book gate default off to recipe availability, writing job start/progress, book/trader generation and outcome doer. Leave defs and existing books intact but dormant. Do not gate the kept eel hook by book enablement.

Acceptance test: Fresh defaults expose no primer bill, new book/trader offer, writing job or teaching letter; a pre-existing book cannot teach while off, log clean. With book gate on and an eligible reader fixture, real bill completion produces a primer and real reading teaches its specified trait.

## T7: Record deferred drill-state appearances

Source and callers: Source/RustCathedral/RM_CompBorehulkDrill.cs explicitly says per-state graphic swap NOT BUILT; Defs/ThingDefs_Races/RM_Borehulk.xml uses Worn sprite.

Work: No current art task. Keep the Worn resident. On the repair version, specify Unbitted as visibly missing its drill head and Restored as a fitted refurbished head using the existing chosen silhouette; associate saved state and render state, including reload.

Acceptance test: none, this pass commissions no art and the current version never enters Unbitted or Restored; future repair-version art must have its own visual acceptance before that version can pass.

## T8: Defer drill removal and decouple the worn resident

Source and callers: RM_CompBorehulkDrill.CompFloatMenuOptions/InspectLines/Gizmos/overlay -> RM_WornBit.Options and DigArea; Source/RustCathedral/RM_WornBit.cs/Jobs.cs.

Work: wornBitEnabled off, Next version, and enforce it at menu, active job, completion and direct production entry. Worn giant keeps its worn-head inspect, grinding and back-away. No repair teaser, drill area, quest or owned-work dependency at defaults. Preserve saved progress if suspended.

Acceptance test: Fresh default map with a Worn giant offers no unbit work and creates no drill head, quest, yard, repair job or repair letter; giant still wanders/grinds and backs away, log clean. Gate on with real eligible workers can progress drill removal and create the existing head/quest. T9 governs yard emission as an explicit coupled opt-in.

## T9: Defer refurbishment yard

Source and callers: RM_WornBit.FinishUnbit -> RM_WornBitGame yard/quest -> RM_WornBitYard caravan/dialog/fee/timer; Patches/RM_WornBit.xml.

Work: Next version gate defaults off. Guard quest creation, yard placement, caravan options, timers, payment/fight and completion; do not create new world geography at defaults. Preserve an old order suspended without discarding its head or money. Keep the existing chosen heavy transport/truce-yard story for later.

Acceptance test: Fresh defaults contain no RM_RefurbishYard world object, active refurbishment quest, yard payment dialog or yard incident; inspect global state and clean log. Coupled repair and yard gates on: eligible removal starts its actual yard path and delivering the physical head starts the timer. Gate off mid-order changes neither committed payment nor head identity.

## T10: Defer restoration work and branch dialog

Source and callers: RM_WornBit.Options -> RM_WornBitJobs restoration hauling/work -> OpenChoiceDialog/FinishRestoration; Defs/Misc/RM_WornBit.xml.

Work: Guard restoration work, ingredients delivery, choice and completion with Next version parent/subgate; defaults off. Preserve delivered components and work; no political/god effects when suspended.

Acceptance test: Fresh defaults offer no restoration job, ingredient request, choice dialog or restoration letter and log is clean. With coupled repair/restoration gates on and an actual refurbished head/components, real workers deliver, consume and progress work to the existing keep/free dialog; direct precredit is invalid.

## T11: Defer owned giant mining

Source and callers: RM_CompBorehulkDrill.CompGetGizmosExtra/PostDrawExtraSelectionOverlays and RM_ThinkTree_Borehulk -> RM_WornBitDig work nodes.

Work: Guard dig-area UI, work selection and each active mining step with Next version mining gate, default off. Decouple original worn wildlife from RM_WornBit.DigArea/inspect. Existing restored/owned pawns remain visible and idle when off; no mining, special sacrilege callback or repeated refusal spam.

Acceptance test: Fresh defaults produce no dig area gizmo/order, excavation job, mined output or mining letter; an old owned fixture cannot keep mining under the off gate and log is clean. Gate on in an explicitly restored owned fixture executes actual designated surface mining and yields the normal material.

## T12: Defer service cycle

Source and callers: RM_CompBorehulkDrill.MaintenanceLeft/MayDigKept -> WornBit service job and source components/chemfuel.

Work: Service gate under deferred owned system defaults off, Next version. Stop active service steps and material consumption when off; no service deadline on the wild worn resident.

Acceptance test: Fresh defaults contain no service job, timer/refusal/letter or service material consumption; log clean. Coupled owned/service gates on: the real job takes its ingredients, services the fixture and restores its existing mining eligibility. Disabling mid-service preserves deposits without continuing work.

## T13: Defer remote favours and free autonomous boring

Source and callers: RM_WornBitGame comms offer/request/timed visit -> RM_WornBitDig free/favour work and return edge transfer.

Work: Both favour and free-bore predicates off by default, Next version. Guard requests, travel/timers, auto-boring and callbacks. No invisible despawn when disabled during a visit; suspend with visible state pending an ordinary exit.

Acceptance test: Fresh defaults expose no favour comms option, visit pawn, autonomous mining job, arrival/departure letter or mined output and log is clean. Coupled gates on in a completed free-branch fixture produce a real request, useful work elsewhere and readable departure; Cathedral directed mining stays excluded.

## T14: Defer repair world continuity and landing penalties

Source and callers: RM_WornBitGame.ExposeData, NoticeLandings/map callbacks, world-pawn and arc slot tracking.

Work: Persist old state but stop progression/respawn/quest/landing consequences under the Next version arc parent. The worn native placement must not need a global quest slot. Never clean unrelated arcs or heads as part of a default test.

Acceptance test: Fresh defaults keep arc slot inactive and emit no repair respawn, landing irritation, quest or associated letter; native Worn placement works, log clean. Coupled arc gate on resumes a saved valid arc on return without duplicate giant/head/quest; off preserves the saved identities and no new consequence.

## T15: Defer branch politics and god adapters

Source and callers: RM_WornBit.Announce/AnnounceChoice; src/RimUtinni/Rites/Source/Patch_WornBitChoice.cs; Patches/RUT_WornBit_Junkers.xml in Utinni layer.

Work: Next version politics gate defaults off for goodwill/irritation/reward callbacks. Preserve campaign identity mapping; it is data, not an extra emitter. Keep god deltas off under the pre-existing rite deferral, even if plain repair is later opted in; require separate rite-version consent to enable that part.

Acceptance test: Fresh defaults create no keep/free choice rewards, faction changes, god deltas or letters; inspect actual ledgers and log. Explicit coupled repair/politics on executes the original political fork once. Rite/god on-arm is not first-version acceptance and cannot be invoked by the ordinary repair switch.

## T16: Defer ship boarding and remove the kept dance caller

Source and callers: Source/Hum/RM_JobGiver_ResonantDance.BuildFigure -> RM_HullBolts.ShipEdgeAnchor; gravship Harmony launch -> RM_HullBolts.Board.

Work: hullBoltsEnabled off, Next version. Guard edge attraction, conversion, boarding letter and all launch paths; local dance chooses active cause/self anchor. No hull feature may be necessary for core bolt motion.

Acceptance test: Fresh default landed ship/liftoff causes no converted RM_HullBolt, edge attraction, boarding letter or log error; local cause warning still works. Gate on under actual qualifying launch boards the existing hull pets and produces the defined arrival sign. No forced Board direct call substitutes for launch.

## T17: Defer hull-pet life

Source and callers: RM_HullBolts.cs pawn comp ticks/return-to-hull/figure tree/inspect; Defs/ThingDefs_Races/RM_HullBolt.xml.

Work: Gate extra hull movement, resistance modifications and inspect callbacks under its Next version parent, defaults off. Keep already-saved pawns visible; do not destroy them or leave a tick exception.

Acceptance test: Fresh defaults have no emitted hull pet or pet-life job/letter and log is clean. Gate on with an isolated existing hull-pet fixture runs its hull jobs and resistances; gate off suspends those custom behaviours without a missing pawn. Distinguish static native properties from optional behavioural modifications in the adapter.

## T18: Defer remote witness ledger

Source and callers: TradeDeal/Corpse butcher/Pawn.Kill hooks -> RM_HullBolts.Witness; pry records; game-component ledger and readerSaw.

Work: Witness off, Next version. Guard every event hook and tell job, not only landing payment. Preserve old records dormant; no remote sale changes local standing at defaults.

Acceptance test: Fresh defaults and sales/butchery/destruction yield no witness records, tell jobs or consequence letters and log clean. Coupled hull/witness on plus a genuinely present relevant bolt records the act once and emits its existing tell. No-bolt and unrelated-map controls stay empty; transit limitations remain next-version design debt.

## T19: Defer uneasy landing payoff

Source and callers: RM_GameComponent_HullBoltWitness map scan/appliedMaps -> irritation and Uneasy hum letter; RM_HumReading readout.

Work: Off by default under Next version return gate and hull parent. Guard landing mutation and reader inspect branch; preserve saved ledger and do not clear it while dormant.

Acceptance test: Fresh default actual Cathedral landing applies no hull-ledger irritation, arrival letter or uneasy inspect and log clean. Coupled gates on consume an eligible saved ledger exactly on an actual return and show the existing consequence; a map that merely already has a ship is a negative control.

## T20: Defer cold marks

Source and callers: RM_HullBolt comp age/markSince; hull map draw and mark history/inspect in RM_HullBolts.cs.

Work: Next version marks off by default. Gate all age, overlay and inspect emission; current marks are not uniformly protected by hullBoltsEnabled. Saved mark metadata remains dormant.

Acceptance test: Fresh defaults never create cold mark state, overlay or inspect text even after elapsed days and log clean. Coupled hull/marks on with sufficient actual time produces its mark and visible overlay. Off mid-mark suppresses overlay without deleting the pet.

## T21: Defer spying dilemma and pry jobs

Source and callers: Hull game tick MaybeReveal/choice letter; RM_HullBolts float-menu and pry job.

Work: Next version dilemma off by default. Guard reveal timer, letter availability, orders, active pry completion and its charge; no automatic campaign reveal. Preserve existing letter/choice state dormant without choosing for the player.

Acceptance test: Fresh defaults create no reveal/dilemma letter or pry option/job and log clean. Coupled hull/witness/dilemma gates on and legitimate existing observation state make the letter and choices available, and an actual pry follows the chosen branch once. A map-wide unrelated reader is a negative observation control for later repair.

## T22: Defer hull-pet mood memories

Source and callers: RM_HullBolts.cs game-component nearby line-of-sight memory scan.

Work: hullBoltPetMemoryEnabled off, Next version; no memory application while parent disabled. Retain existing memories for ordinary game expiry.

Acceptance test: Fresh defaults create no RM_HullBoltsSeen memory or related message despite eligible colonists near an old hull-pet fixture, log clean. Coupled hull/pet-memory on grants the ordinary configured memory after a valid observation interval.

## T23: Defer Cathedral campaign progression emissions

Source and callers: src/RimMandrake/Utils/gm_blackboard_shadow.py: Regard/exposure/fall/offer/survey/descent advance; fixtures and adapters.

Work: Only Cathedral progression emission predicates default off, Next version; keep shared blackboard and unrelated campaign functions untouched. Retain state/read APIs; suppress live stage changes, Cathedral would_fire scheduling and dormant offers/fall outputs. This is a dependency consumer change, not a campaign redesign.

Acceptance test: Fresh defaults under a Cathedral-relevant blackboard workload emit no Cathedral stage/offer/fall/survey/descent events or player letters; unrelated campaign functions still run and log clean. Explicit Cathedral gate on reproduces eligible Cathedral records from the actual fixture. Shadow would_fire is not a playable quest proof.

## T24: Defer built mission and boon offers

Source and callers: src/RimUtinni/CathedralPass/Source/CathedralFavours.cs and Defs/QuestScriptDefs/RUT_CathedralAssailantMissions.xml; CathedralPassMod switches; RustCathedral/selftest_rustcathedral_offers.py.

Work: The historical absence claim is stale: retain built quest/code. cathedralMissionsEnabled and cathedralBoonsEnabled default off, Next version; guard incident/direct quest-node entry, letters and grants without disabling pass targeting.

Acceptance test: Fresh defaults even under an eligible campaign fixture create no active mission quest, offer letter, boon item or boon grant and log clean. Explicit mission/boon and campaign progression on generate the qualifying offer and its existing earned boon; ordinary pass flag behaviour remains available.

## T25: Disable legacy planet scoring pending retirement decision

Source and callers: Source/RustCathedral/RM_BiomeWorker_RustCathedral.cs and RM_RustCathedralMod.cs biomeRarityFactor UI/scribing.

Work: Recommendation: retire alternate-planet scoring/rarity because it fights permanent no-worldgen. Do not delete without owner decision; inert required worker identity can remain. Disable/remove player access to planet-generation functionality now; this is not a Next version feature or toggle. Local authored-tile maps still use kept defs.

Acceptance test: No settings/menu/workflow offers new planets or climate rarity, and any legacy score path cannot place this biome in a generated planet; ordinary fixed-world biome resolution and local layout still work with clean log. There is intentionally no feature-on worldgen acceptance arm.

## T26: Defer coolant-load chemistry

Source and callers: Defs/ThingDefs_Items/RM_CoolantEelCatch.xml ingestible outcomeDoer -> Defs/HediffDefs/RM_CoolantLoad.xml.

Work: Add Next version chemistry toggle off by default at outcome execution; preserve def/old hediff so normal recovery completes. No new chemistry effect or covert substitute while off.

Acceptance test: Fresh default real eel consumption produces ordinary nutrition but no new RM_CoolantLoad, chemistry letter or custom stat effect, log clean. Gate on consuming the same catch applies its existing residue and subsequent decay. Pre-existing hediff recovery still works when off.

## T27: Defer random canal shock

Source and callers: Defs/Misc/RM_NegativeFishingOutcomes.xml -> vanilla negative-catch selection.

Work: Next version shock off by default; gate eligibility and direct execution rather than deleting the def. Preserve ordinary fishing, eel catch and kept irritation.

Acceptance test: Fresh default eligible fishing, including forced negative-outcome eligibility in a labelled control fixture, never selects/executes the coolant electrical burn or its letter and log clean. Gate on plus eligible vanilla outcome executes the defined shock and letter. Direct damage injection is not an on-arm proof.

## T28: Defer curiosity pickup pricing

Source and callers: HarmonyPatch_WatchedBolts.cs TryStartCarry overloads -> NotePickup and session-local chargedCuriosities; same file NoteKill is kept.

Work: Add independent Next version pickup gate off, retain code/defs. Do not use it to disable living-bolt protection. Prevent duplicate callbacks if future feature enabled; retain old curiosity objects with no default pickup penalty.

Acceptance test: Fresh defaults hauling an old curiosity through both carry overloads changes no attitude and emits no pickup warning/letter; player killing a living bolt still disturbs local mood, log clean. Gate on prices a real eligible pickup once, including after reload, with harmless-haul control unchanged.

## T29: Specify and implement the local maze and shortcut roles

Source and callers: Existing wall scatter only; promised geometry in frozen sheet §1/§5 and November answer. No complete dedicated maker found.

Work: Build the missing local-map layout consumer from definition.md and M2, including role labels saved by original object identity, visible divider warning, actual guard chambers, public-side escape/deposit points and one breach offence per structural opening. Reuse ordinary wall mining and shared engine data; no worldgen, puzzle or random trap system.

Acceptance test: M2 export and actual path queries agree on declared size/water/orientation range. A real crew can reach free salvage/exit without crossing held ground, a marked cut changes route and actual irritation, and unmarked rubble removal does not. Random-clump and hidden-divider controls fail B1/B2; no direct band setter counts.

## T30: Connect sacred consequences and nonritual restitution

Source and callers: GenStep_ScatterSacredWalls currently only owns buildings; AffectStanding exists; general first-hit/claim and credit path not found.

Work: Implement the definition's game-level sacred offence/payment ledger keyed by original map/structure identity. Use the existing Utinni integration to resolve the actual Enclave faction and route the once-only sacred destruction (including stripping) or claim signal to its goodwill, not permanent-enemy Arsenal goodwill. Damage while standing and unclaimed raises only fast irritation/warning, without a receipt or Enclave debit; destruction after claim cannot debit again. Preserve the ruled debit and vanilla relation hysteresis and let the existing relation-change handlers apply isolation, without scheduling an army. Keep local hum standing as a mirror, with a first-non-calm floor while any sacred receipt remains unpaid. Neither the latch nor the mirror expands guard pursuit. Provide public-side Repay damage with positive replacement-value bill, persisted partial deposits and destroyed-site marker. Keep global receipts through neighbouring-map travel, origin-map unload/removal, reload and marker restoration; reconcile local mirrors on return without charging again. Deep episodes use the transaction mechanism with distinct local-standing receipts, never Enclave credit. Ordinary diplomacy can restore relation but cannot silently settle a material receipt. Derive the hum mirror from local deep standing minus unpaid sacred receipt debits, clamped to existing bounds, then apply the unpaid display floor after ordinary band calculation; do not write the mirror as another faction debit. Repayment credits no more than actual original faction loss, with no surplus positive goodwill, no local/global double credit and no reversal of past prisoners/cancelled requests/departed ships. No new faction, settlement, ritual or campaign quest.

Acceptance test: M1 plus actual state traces show an isolated sacred destruction/claim debits the real Enclave relationship once and holds the local hum above calm even below the hostility threshold; quiet leaves the receipt/floor, actual public-side silver payment settles it and removes its floor. Several debts keep the floor until the last is settled. Damage while a sacred work is standing and unclaimed must leave Enclave goodwill and unpaid receipts unchanged, including across reload; its later destruction or claim debits once. A real hostility flip makes staged Enclave guests prisoners, cancels their active trade request and removes the passing ship as applicable; no raid is scheduled and guards keep the same footprint. Payment credits the actual faction debit and restores future contact only at real relation recovery; unrelated losses and past diplomatic effects are retained. Travel to a neighbouring Cathedral map, unload/delete the origin map, reload, partial delivery and duplicate completion cannot forgive, replay or double-credit a receipt; revisiting restores the same deposit marker. Nonplayer damage, carrier death, insufficient funds and blocked deposit consume no extra material. Test separate deep-standing payment and an externally gifted relation: neither can farm faction or local credit. A mutant that pays only the local ledger fails even if it shows success text.

## T31: Unify attribution, saved minor events and recoverable standing

Source and callers: RM_CathedralFishing session-local job/catch counters; RM_WatchedBolts; RM_HumReading eel-butchery hook; RM_AttitudeKernel and MapComponent.

Work: Give kept acts map/source/actor identities and saved deduplication. Minor fishing/cuts/bolt kill affect fast irritation only; sacred receipts and Enclave goodwill are global, deep standing local, and neither comes from ordinary catch counters. Remove current catch-standing debit from default path, leave source history explicit as replaced rule. Keep real butchery pricing independent of T5 literacy. Bound cue ordering to next avoidable escalation, not a literal zero-tick claim.

Acceptance test: M1 trace matches real line-start/catch/abort, destruction and butchery. Actual nonplayer fishing/crossfire and bought-eel hauling do not debit player state; repeated callback/reload does not charge an old act; the minor arm starts calm and debt-free, real fishing first raises the attributed band and cue, then matched cancellation/quiet versus continued-fishing arms show return to calm versus a sustained raised warning without permanent standing loss. A calm reading with no prior recorded rise is invalid; an omitted-fishing-input mutant fails. Sacred/deep receipts persist until T30 payment. No reader/primer/hull gate is on.

## T32: Provide an honest sensory-warning instrument

Source and callers: MapComponent hum sustainers and camera switching; current stage ceiling can suppress actual band; current live layer counts cannot prove hearing.

Work: Wire arrival advice and minimum baseline inspect/work-site cue without literacy. Add actual audio and normal-zoom comparison/replay protocol with causal ordering export. Keep sound and visual mute/fallback scope honest, no lore explanation. This instrument requires a real later listening/look session; no simulated audibility claim.

Acceptance test: With every kept mechanic on, a newcomer under ordinary colony workload locates the active cause and cancels before its next avoidable escalation; no-source/background arms do not mimic the cue. Actual sound persists and changes across normal/paused map switches and reload, no wrong-map hum, no campaign locks. No credible offline sensory substitute exists.

## T33: Locate displeasure through reachable bolt behaviour

Source and callers: RM_JobGiver_ResonantDance.BuildFigure centres on self or ShipEdgeAnchor, with no active-offence location.

Work: Implement active-source registry consumer, rotation among reachable causes and warn-on-source fallback when unreachable/no bolt. Retain actual pattern/stiffness/freeze language with public current mood; detach hull anchor as T16. Ignore dead/inactive/cancelled causes after an honest decay tail; never point at an innocent haul. With only unpaid-bill pressure and no active cause, bolts retain non-calm stiffness without gathering at work, while the hum inspector names each unpaid damage bill and its originating Cathedral world tile on origin and neighbouring maps.

Acceptance test: M1/M2 prove source ids/path reachability, then real overlapping fishing/breach/innocent-haul work produces bolts/cues at correct active sources under busy-colony defaults; cancellation clears active attraction without clearing saved sacred debt. No ship/reader/line-cycle required; inaccessible-source and destroyed-bolt controls still permit location. In floor-only arms on origin and neighbouring maps, including after reload, innocent haulers attract no bolts and the bill/tile inspect line remains available.

## T34: Specify held ground and repair response target lifecycle

Source and callers: No complete garrison planner established; RM_IncidentWorker_CathedralResponse uses LordJob_AssaultThings and map-wide vanilla-infestation blocker.

Work: Define/export native held footprints and patrol routes from T29. Scope targets and hostility to those grounds and the actual working live-metal drill; exit on removed/ineligible/unreachable target, no colony hunt. Fix vanilla blocker to use matching qualifying eligibility. Keep pre-existing campaign pass as an input, not a replacement quest. Enclave diplomatic hostility changes contact, never the held-ground footprint or pursuit boundary.

Acceptance test: M1/M2 targeting matrix plus real target/route trace: ordinary public crew is not pursued, retreat ends pursuit, a drill response selects the actual offending drill and exits after destruction/removal/eligibility loss, non-live-metal drills retain vanilla infestation. Low/high threat and reload do not select a bedroom or leave a targetless infinite lord.

## T35: Finish settings and standing-rule integration

Source and callers: RM_RustCathedralSettings owns prefixed Hum/Walls Scribe, resets and SettingsKit UI; current biomeRarityFactor is not a runtime master; biome heatKind legacy.

Work: Add true mechanics master and missing kept subgates with scope labels; synchronize effective/default/reset/Scribe/composition choices and visible explicit-pref upgrade. Apply T25 no-worldgen and shared geometry-only sun; all DLC assumed, native roster unaltered, unsupported cross-biome off. Saved residents/debts do not vanish. Sacred-consequence off suspends new debits and the hum floor but retains global receipts and actual Enclave diplomacy; no relation reset or replay on re-enable. Pool-placement off is explicitly new-local-map-only, retaining existing ordinary terrain hazards.

Acceptance test: Fresh defaults enable every kept subsystem and disable every next-version emitter; resetting and save/reload preserves that effective manifest. Each major feature off and all-off halt pending/new own effects with clean log while terrain/residents load and debt stays dormant; sound mute preserves visual cue. No rarity-worldgen UI or bespoke sun multiplier remains.

## T36: Build the shared trace, export and recoverable proof instruments

Source and callers: validation.py, RM_RustCathedralHumProof.cs, RM_WornBitProof.cs and Source/SelfTest arithmetic exist but do not provide full event/path/reload/whole proof.

Work: Build M1 then M2 then M3 interfaces: read-only fingerprints, cell/footprint/path export, event/source/actor/debit/target/receipt/resident traces, actual Enclave goodwill/relation-kind/contact/callbacks, global sacred receipt and local mirror snapshots, pool terrain/provider/entry-exposure traces, snapshot diff and isolated saved recovery manifest. Separate stimulus job orders from observation. Negative mutants must fail; unavailable readings say UNMEASURED. Do not use proof cleanup that destroys global yards/heads.

Acceptance test: Calibrate as models.md requires: real engine state and offline traces agree exactly on identities/material/debt/classification and on documented timing tolerance, missing/wrong-map control fails, midway/reordered and neighbouring-map runs retain causal evidence. Require a real above-calm fishing input before any quiet-recovery pass; continued-fishing control remains raised. Distinguish terrain-caused exposure from matched dry-ground ambient heat/pollution. Local-ledger-only sacred credit must fail against actual Enclave contact reads. Interruption restores the baseline save/settings and leaves unrelated state untouched. No game action is performed during this design pass.

## T37: Constrain actual eel paths and preserve resident signs

Source and callers: RM_CathedralFinish.cs WaterWander endpoint validator; eel EnvironmentalHazards water-lock comp guarded by composed package; shared comp stops dry motion only.

Work: Use real water-only route selection/consumer checks; keep shared engine unchanged. Cover composed intended load and honest mod guard linkage. If water disappears, leave visible stranded eel with sign, no silent destruction/teleport. Verify native temperature/pollution survival and ordinary death evidence for all residents.

Acceptance test: M2 traversed paths and real state reads never use dry cells when water route exists; disconnected pools do not induce land travel. Filling water under a resident leaves identity and readable stranded/death state, not disappearance. Dry native map has no eel placement; no DLC-absent tier required; log clean.

## T38: Defer passive worst-band standing drain

Source and callers: RM_MapComponent_BiomeAttitude.MaybeDrainGoodwill -> RM_AttitudeKernel.DrainDelta; goodwillDrainEnabled currently true.

Work: goodwillDrainEnabled and all shipped/scribed/reset defaults off, Next version. Keep arithmetic and saved window data, stop all passive debt/latch changes while off. Core sacred/deep transaction effects remain enabled.

Acceptance test: Fresh defaults held at a genuinely reached worst band over its former drain window gain no passive standing debt/letters and log clean; actual sacred/deep act still debits. Explicit gate on executes the existing interval/cap behaviour in an isolated fixture; it is not used to pass current recovery.

## T39: Defer the built survey hail

Source and callers: src/RimUtinni/CathedralPass/Source/CathedralSurvey.cs; Defs/QuestScriptDefs/RUT_CathedralSurveyMisdirection.xml and incident/choice-letter defs; CathedralPassMod.

Work: cathedralSurveyEnabled off, Next version. Guard eligibility, direct quest-node path, hail signal, responses/payment and pending letters; preserve suspended saved quest state. No changes to pass targeting or unrelated Empire pursuit.

Acceptance test: Fresh defaults under an otherwise eligible survey condition have no survey quest, hail letter, response dialog or finder-fee payment and log clean. Gate and its campaign parent on generate the real hail and existing response path; switching off an old hail does not auto-answer or pay it.

## T40: Defer built descent and revelation

Source and callers: src/RimUtinni/CathedralPass/Source/CathedralDescent.cs; Defs/CathedralDescent/RUT_CathedralDescent_Opening.xml and Address.xml; CathedralPassMod.

Work: cathedralDescentEnabled off, Next version; guard opening, site generation, admission, direct quest call, address and revelation outputs. Keep saved state/content dormant. Do not remove or rewrite hidden campaign canon.

Acceptance test: Fresh defaults at an eligible campaign state produce no descent opening/site, admission order, address dialog or revelation letter and log clean. Explicit descent/campaign gates on perform the existing eligible opening/site/address sequence. Off never deletes a pawn already at a saved site; safe visible suspension is required.

## T41: Defer giant mood freeze

Source and callers: Defs/ThinkTreeDefs/RM_ThinkTree_Borehulk.xml -> RM_ThinkNode_ConditionalAttitudeBand before work/wander.

Work: Add Next version giant-freeze gate default off; leave peaceful back-away, ordinary idle and worn grinding on. Do not use it to stop the main bolt warning. Keep the separate already-deferred line-cycle off.

Acceptance test: Fresh default giant at an actually reached worst mood does not acquire a hum-forced freeze job, roaches still clean, bolts still display/freeze, log clean. Gate on in the isolated giant fixture exercises its existing hum freeze; harm/back-away priority remains correct.

## T42: Defer self-repairing pattern hull

Source and callers: Defs/ThingDefs_Buildings/RM_PatternHull.xml: Odyssey build designation, dead/live metal cost and rare-tick CompSelfhealHitpoints; Utils/ship_contributions.py consumer.

Work: Next version pattern-hull gate off. Hide construct/bill/blueprint availability and gate active self-heal; keep def/art/code and ordinary already-built structure/airtightness intact. Apply surface-register bans to available catalogue/inspect text; disabled content must not reveal hidden self-assembling-metal origin.

Acceptance test: Fresh default native map/ship has no pattern-hull build option, blueprint, construction job or newly emitted hull/letter and log clean. Existing isolated pattern hull fixture loses no identity/airtightness but heals no damage while off. Gate on allows actual construction on valid substructure and real rare ticks self-heal damage; invalid ground control refuses.


## T43: Restore the ruled stationary toxic pools

Source and callers: Owner ruling in design/Jawa/worldbuilding/the_forgotten_war.md:232 and sheet §6.5/§8/§9; no ToxicWater/IrradiatedWater/SulfuricWater consumer found in the Cathedral source, defs or patches. RM_RustCathedral_Biome.xml currently defines ordinary metal ground/water edges, not these hazards.

Work: Resolve the current terrain providers and inherited exposure behaviour for the ruling's toxic main pools, irradiated patches and sulfuric-looking edges; record actual names/factors and required mod integration rather than treating historical references as a current measurement. If a provider cannot resolve, report the dependency gap: do not substitute harmless water, true acid, a custom spreading hazard or unrelated ambient pollution. Consume those existing hazard terrains in the local layout under a new-local-maps pool-placement control, default on. Stable visible boundaries and inspect text must warn before entry; keep dry public routes, exits and deposit approaches outside the hazard. Distinguish pools from viable eel canals and preserve native-water/drinking contracts. Do not redesign a shared hazard engine or generate/paint a planet. Extend T29/T32/T36 and M1/M2/M3 for pool placement, causal exposure and visual readability.

Acceptance test: Current resolved provider manifest and actual pool cells exist on fresh default native maps, including canal-free maps. Matched unprotected entrants on toxic pool versus adjacent dry metal at the same heat/pollution show additional terrain-attributed harmful exposure on entry/dwell and its cessation on exit; protected controls use the provider's actual mitigation. Sulfuric-looking edges remain recognisable before entry in a normal-zoom look; an unwired cosmetic-only pool mutant fails. M2 and real path reads show safe public salvage/retreat/repayment approaches with guards active; resident paths and season replay do not solve hazard risk by deleting life or turning pools off. Pool cells and behaviour persist through reload. Placement off omits new pools on a fresh local map, changes no existing cells, labels that scope honestly and leaves a clean log; on restores the default placement.
