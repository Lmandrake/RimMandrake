# Proposal tickets

Designer-authored specifications only. No game code, engine, bridge or source changes have been made. T headings are local references, not ledger items. All future implementation includes an offline negative control and an ordinary job/state read with all kept mechanics on; no proof scene locks weather clear. Dependencies keep their own engine rules.

## T1: placement worker

Capability: Existing tile-score worker and rarity slider for alternative-world generation; retained as built evidence, outside the campaign/player promise.
Why: Recommend retiring active biome scoring and the rarity UI because producing alternative planets contradicts the standing no-worldgen ruling. Hard-disabled in every version, never placed on a next-version wishlist; retain inert type only if load compatibility requires it.
Calls searched: RM_TheSump.workerClass -> RM_BiomeWorker_TheSump.GetScore; biomeRarityFactor in RM_TheSumpMod.cs.
Hard-disable GetScore participation and remove rarity/new-planet offers; preserve an inert compatible worker type if needed. This is prohibited worldgen, not an opt-in future feature.

Acceptance test: Static call-graph/def-registration test proves no world-placement path can participate, with no alternate-planet UI; state read on the existing fixed map before/after reload shows unchanged world tiles and compatibility resolution; log clean. No on arm exists because the standing ruling forbids it.

## T2: retired mutator ports

Capability: Authored RM_TarLakes TileMutatorDef and LandmarkDef, with tar patches; these are compatibility content, not authority to generate a new planet.
Why: Recommend retiring active tar-lake world placement/landmark hooks for the same no-worldgen reason. Saved identifiers may remain inert; nothing here authorizes changing the fixed planet.
Calls searched: RM_TarLakes TileMutatorDef -> TileMutatorWorker_Patches; LandmarkDef; registration via engine def discovery.
Make RM_TarLakes world placement/landmark hooks unreachable in every configuration; preserve saved def identifiers. Never add a next-version worldgen checkbox.

Acceptance test: Static call-graph/def-registration test proves no world-placement path can participate, with no alternate-planet UI; state read on the existing fixed map before/after reload shows unchanged world tiles and compatibility resolution; log clean. No on arm exists because the standing ruling forbids it.

## T3: poured moat

Capability: Buildable slow tar floor, Chemfuel cost placeholder, burned spent terrain and ability to re-pour.
Why: A buildable defence perimeter is a separate military system; natural tar and ordinary fire already make land and signature whole.
Calls searched: No current consumer found by named-symbol search in source/defs and read-only HEAD blobs; earlier inventory search_scope records the promised behaviour separately from its present body.
Gate the complete Sump-specific producer, offered player action, scheduled job/incident/letter and consumer callbacks; leave shared engine code/defs in the tree. Keep all acquisition/research links behind the same effective gate.

Acceptance test: With shipped defaults on a fresh full Sump map, poured moat contributes no active instances, offered actions, jobs, incidents, letters, effects or queued callbacks (state read, not a def-count), including after reload; the log is clean. Enable its clearly labelled Next version setting with required companion extras in the same group: execute its ordinary producer/action and observe the named state/effect present. Disable again mid-operation: no new effects or lost pawns/items; retained tar, life and ordinary work continue. Compatibility defs and seated animal/plant bodies remain loadable.

## T4: fuse post

Capability: Player ignition queues connected poured/natural tar terrain and starts vanilla Fire at a staggered rate; not the same mechanism as the gate-aware liquid front.
Why: Command ignition is a military action, not required to cross, work or clean natural tar.
Calls searched: No current consumer found by named-symbol search in source/defs and read-only HEAD blobs; earlier inventory search_scope records the promised behaviour separately from its present body.
Gate the complete Sump-specific producer, offered player action, scheduled job/incident/letter and consumer callbacks; leave shared engine code/defs in the tree. Keep all acquisition/research links behind the same effective gate.

Acceptance test: With shipped defaults on a fresh full Sump map, fuse post contributes no active instances, offered actions, jobs, incidents, letters, effects or queued callbacks (state read, not a def-count), including after reload; the log is clean. Enable its clearly labelled Next version setting with required companion extras in the same group: execute its ordinary producer/action and observe the named state/effect present. Disable again mid-operation: no new effects or lost pawns/items; retained tar, life and ordinary work continue. Compatibility defs and seated animal/plant bodies remain loadable.

## T5: legacy burn support

Capability: TimedTerrainBurn and smoke-column support were built for the old TarBlaze. TheSump has no TarBlaze def/consumer now; code presence does not make a smoke wall.
Why: A bespoke smoke wall consumer is not necessary for ordinary ground; shared support remains owned by EnvironmentalHazards.
Calls searched: No current consumer found by named-symbol search in source/defs and read-only HEAD blobs; earlier inventory search_scope records the promised behaviour separately from its present body.
Keep shared burn/smoke support in EH; gate only Sump consumer/registration. No new smoke-wall consumer is required now.

Acceptance test: With shipped defaults on a fresh full Sump map, legacy burn support contributes no active instances, offered actions, jobs, incidents, letters, effects or queued callbacks (state read, not a def-count), including after reload; the log is clean. Enable its clearly labelled Next version setting with required companion extras in the same group: execute its ordinary producer/action and observe the named state/effect present. Disable again mid-operation: no new effects or lost pawns/items; retained tar, life and ordinary work continue. Compatibility defs and seated animal/plant bodies remain loadable.

## T6: belch flood

Capability: Tar-pit incident selects tar epicentre, releases a real tar flood and letter; FlowWorks owns spread and cooled front, TheSump redirects cooling to Glasswalk.
Why: A special incident rewrites familiar routes independently of ordinary exposure. The colony loop works without a scripted flood.
Calls searched: No current consumer found by named-symbol search in source/defs and read-only HEAD blobs; earlier inventory search_scope records the promised behaviour separately from its present body.
Gate IncidentWorker.CanFire/Execute and incident selection, letter and queued producer; generic FlowWorks floods remain available to their owner.

Acceptance test: With shipped defaults on a fresh full Sump map, belch flood contributes no active instances, offered actions, jobs, incidents, letters, effects or queued callbacks (state read, not a def-count), including after reload; the log is clean. Enable its clearly labelled Next version setting with required companion extras in the same group: execute its ordinary producer/action and observe the named state/effect present. Disable again mid-operation: no new effects or lost pawns/items; retained tar, life and ordinary work continue. Compatibility defs and seated animal/plant bodies remain loadable.

## T7: duckboards

Capability: Cheap fast clean wood floor, flammable and slow when tar filth accumulates; Brindeth no longer yields WoodLog despite old comments.
Why: Recommend retiring the separate duckboard buildable: vanilla wood flooring already supplies its fast-when-clean, foulable, flammable route behaviour. Until the owner decides, park it switched off as next-version content; preserve its ruled behaviour if restored.
Calls searched: Floors designation auto-discovers RM_Duckboards; vanilla filth path cost/cleaning and terrain burning. Glasswalk is separate, not a prerequisite.
Default-off next-version gate hides only the bespoke duckboard offer. Ordinary vanilla floor offers/filth/cleaning remain. Do not restore Brindeth WoodLog yields.

Acceptance test: With shipped defaults on a fresh full Sump map, duckboards contributes no active instances, offered actions, jobs, incidents, letters, effects or queued callbacks (state read, not a def-count), including after reload; the log is clean. Enable its clearly labelled Next version setting with required companion extras in the same group: execute its ordinary producer/action and observe the named state/effect present. Disable again mid-operation: no new effects or lost pawns/items; retained tar, life and ordinary work continue. Compatibility defs and seated animal/plant bodies remain loadable.

## T8: glasswalk slips

Capability: Shared slippery-walkway watcher applies damage-free stun to moving/hauling pawns, with toggle and chance.
Why: Random harmless falls add an independent interruption beyond the permanent route travel cost; deletion leaves the route tradeoff readable.
Calls searched: RM_SlipperyWalkway tag on RM_Glasswalk -> EH RM_MapComponent_GlasswalkSlip; settings in RM_EnvironmentalHazardsMod.cs.
Gate Sump-tagged slip processing/producer locally; do not turn off unrelated slippery terrain in EnvironmentalHazards. Glasswalk remains filth-proof and permanently slower than clean paving.

Acceptance test: With shipped defaults on a fresh full Sump map, glasswalk slips contributes no active instances, offered actions, jobs, incidents, letters, effects or queued callbacks (state read, not a def-count), including after reload; the log is clean. Enable its clearly labelled Next version setting with required companion extras in the same group: execute its ordinary producer/action and observe the named state/effect present. Disable again mid-operation: no new effects or lost pawns/items; retained tar, life and ordinary work continue. Compatibility defs and seated animal/plant bodies remain loadable.

## T9: vault seal

Capability: Normal-ticking shelf scans held things, disables rot, forbids items and scribes its seal ledger.
Why: Perfect preservation is a storage system beyond route/exposure/recovery; ordinary shelves and refrigerators cover current food storage.
Calls searched: RM_TarVault comps -> RM_Comp_TarVaultSeal.CompTick -> ledger; RM_TheSumpProof.ProofVault directly calls it.
Gate shelf offer, scan, extraction menus and source recipes together; disabling/reloading/despawning must restore saved rot/forbidden flags safely without destroying contents.

Acceptance test: With shipped defaults on a fresh full Sump map, vault seal contributes no active instances, offered actions, jobs, incidents, letters, effects or queued callbacks (state read, not a def-count), including after reload; the log is clean. Enable its clearly labelled Next version setting with required companion extras in the same group: execute its ordinary producer/action and observe the named state/effect present. Disable again mid-operation: no new effects or lost pawns/items; retained tar, life and ordinary work continue. Compatibility defs and seated animal/plant bodies remain loadable.

## T10: vault extract

Capability: Menu consumes one weak/strong solvent per stack administratively from anywhere on map, unseals original in place; no solvent destroys/replaces it with ruined goods.
Why: Solvent-gated release/ruined goods belongs to the deferred preservation system; basic cleaning must not call it.
Calls searched: RM_Comp_TarVaultSeal float menus -> ExtractOne; RM_TarRuinedGoods; local weak/strong solvent scans.
Gate ruin conversion and extraction alongside vault sealing; no active solvent scan for the default colony. Releasing a saved item must not reseal it before hauling.

Acceptance test: With shipped defaults on a fresh full Sump map, vault extract contributes no active instances, offered actions, jobs, incidents, letters, effects or queued callbacks (state read, not a def-count), including after reload; the log is clean. Enable its clearly labelled Next version setting with required companion extras in the same group: execute its ordinary producer/action and observe the named state/effect present. Disable again mid-operation: no new effects or lost pawns/items; retained tar, life and ordinary work continue. Compatibility defs and seated animal/plant bodies remain loadable.

## T11: kethrel shell

Capability: Real ThingOwner shell with mass thresholds, armour/speed hediff stages, whole-body directional graphics, saved contents and inspect tab.
Why: Wearable stolen scrap creates an equipment ecology beyond ordinary animals; the seated kethrel remains a plain animal.
Calls searched: RM_Kethrel race comp -> RM_CompKethrelShell; custom render node/ITab reads shell state; TheSumpProof direct hook.
Keep the ordinary kethrel. Gate shell modifiers, custom render stages and ITab, not just pickup. Release held goods visibly once on disable; never vanish them.

Acceptance test: With shipped defaults on a fresh full Sump map, kethrel shell contributes no active instances, offered actions, jobs, incidents, letters, effects or queued callbacks (state read, not a def-count), including after reload; the log is clean. Enable its clearly labelled Next version setting with required companion extras in the same group: execute its ordinary producer/action and observe the named state/effect present. Disable again mid-operation: no new effects or lost pawns/items; retained tar, life and ordinary work continue. Compatibility defs and seated animal/plant bodies remain loadable.

## T12: kethrel pickup

Capability: Rare-tick searches weapons/listed scrap near tar, respects forbidden/value/home-area checks and sends an idle animal toward reachable distant scrap; close pickup has no reach/LOS check.
Why: Scrap seeking/ownership transfer is the producer of that deferred shell system, not a need for ordinary fauna.
Calls searched: RM_CompKethrelShell.CompTickRare -> Decide -> PickUp or seek; item ownership/LOS rules are here.
Gate pickup AND seek jobs/rare ticks before any map scan or ThingOwner transfer. CreatureBehaviors hauling and ordinary feeding must keep working.

Acceptance test: With shipped defaults on a fresh full Sump map, kethrel pickup contributes no active instances, offered actions, jobs, incidents, letters, effects or queued callbacks (state read, not a def-count), including after reload; the log is clean. Enable its clearly labelled Next version setting with required companion extras in the same group: execute its ordinary producer/action and observe the named state/effect present. Disable again mid-operation: no new effects or lost pawns/items; retained tar, life and ordinary work continue. Compatibility defs and seated animal/plant bodies remain loadable.

## T13: kethrel molt

Capability: Automatic loaded molt, player coax command with best able Animals colonist/charge chance, and death/despawn release of carried items.
Why: Automatic/coaxed molt and handling charge exist only to release shell contents. Safe release for old saves is compatibility, not permission to run the extra.
Calls searched: RM_CompKethrelShell.CompTickRare, gizmo/handler path and PostDeSpawn release; ThingOwner holds actual goods.
Gate automatic/coaxed molt and charges; retain one-time visible release for saved held goods/death. Do not leave a loaded invisible ThingOwner when shell is off.

Acceptance test: With shipped defaults on a fresh full Sump map, kethrel molt contributes no active instances, offered actions, jobs, incidents, letters, effects or queued callbacks (state read, not a def-count), including after reload; the log is clean. Enable its clearly labelled Next version setting with required companion extras in the same group: execute its ordinary producer/action and observe the named state/effect present. Disable again mid-operation: no new effects or lost pawns/items; retained tar, life and ordinary work continue. Compatibility defs and seated animal/plant bodies remain loadable.

## T14: capstan combat

Capability: Powered host, turning top and shared tether pull for visible enemies, one-cell reel, mass/size/struggle snap, damage and line cues.
Why: A powered tether weapon is a separate combat mechanic. Deleting its player behaviour does not remove tar resistance.
Calls searched: RM_CapstanTurret and PitRigged def -> RM_CapstanTurret host -> CreatureBehaviors RM_CompTetherPull; TheSumpProof.
Gate the complete Sump-specific producer, offered player action, scheduled job/incident/letter and consumer callbacks; leave shared engine code/defs in the tree. Keep all acquisition/research links behind the same effective gate.

Acceptance test: With shipped defaults on a fresh full Sump map, capstan combat contributes no active instances, offered actions, jobs, incidents, letters, effects or queued callbacks (state read, not a def-count), including after reload; the log is clean. Enable its clearly labelled Next version setting with required companion extras in the same group: execute its ordinary producer/action and observe the named state/effect present. Disable again mid-operation: no new effects or lost pawns/items; retained tar, life and ordinary work continue. Compatibility defs and seated animal/plant bodies remain loadable.

## T15: capstan rescue

Capability: With no enemy, shared tether can acquire downed colonists and pull them toward the powered turret.
Why: Automatic friendly towing adds a rescue system; vanilla carrying already serves ordinary casualties.
Calls searched: RM_CompTetherPull acquisition fallback reads capstanFriendlyPull host field when no enemy.
Gate the complete Sump-specific producer, offered player action, scheduled job/incident/letter and consumer callbacks; leave shared engine code/defs in the tree. Keep all acquisition/research links behind the same effective gate.

Acceptance test: With shipped defaults on a fresh full Sump map, capstan rescue contributes no active instances, offered actions, jobs, incidents, letters, effects or queued callbacks (state read, not a def-count), including after reload; the log is clean. Enable its clearly labelled Next version setting with required companion extras in the same group: execute its ordinary producer/action and observe the named state/effect present. Disable again mid-operation: no new effects or lost pawns/items; retained tar, life and ordinary work continue. Compatibility defs and seated animal/plant bodies remain loadable.

## T16: drawjoint learning

Capability: Deep strata yield preserved draw-joints; study two consumes them and unlocks capstan research, plus shared analyzable grants traction-lance research; ordinary and pit-rigged material variants.
Why: Artifact-driven research is a second progression loop, and removing it cannot gate retained bitumen, solvent or routes.
Calls searched: RM_DigStratumTable yields RM_PreservedDrawJoint; its analyzable comp grants traction-lance research; RM_CapstanTurret research and material recipes consume it.
Gate Sump draw-joint lottery yields, study offers, capstan-local recipe/research and cross-grant to traction-lance; leave independently earned CreatureBehaviors technology alone.

Acceptance test: With shipped defaults on a fresh full Sump map, drawjoint learning contributes no active instances, offered actions, jobs, incidents, letters, effects or queued callbacks (state read, not a def-count), including after reload; the log is clean. Enable its clearly labelled Next version setting with required companion extras in the same group: execute its ordinary producer/action and observe the named state/effect present. Disable again mid-operation: no new effects or lost pawns/items; retained tar, life and ordinary work continue. Compatibility defs and seated animal/plant bodies remain loadable.

## T17: salvage winch

Capability: Ordered unpowered hook drags wrecks, corpses and downed beasts along ground; refuses standing/too-heavy targets and cannot lift; own research after capstan.
Why: Ground towing is a separate salvage interaction owned by the shared tether engine; ordinary hauling suffices for current goods.
Calls searched: RM_SalvageWinch def/research -> CreatureBehaviors RM_CompSalvageWinch and RM_SalvageWinchRules; CreatureBehaviors validation.
Gate the complete Sump-specific producer, offered player action, scheduled job/incident/letter and consumer callbacks; leave shared engine code/defs in the tree. Keep all acquisition/research links behind the same effective gate.

Acceptance test: With shipped defaults on a fresh full Sump map, salvage winch contributes no active instances, offered actions, jobs, incidents, letters, effects or queued callbacks (state read, not a def-count), including after reload; the log is clean. Enable its clearly labelled Next version setting with required companion extras in the same group: execute its ordinary producer/action and observe the named state/effect present. Disable again mid-operation: no new effects or lost pawns/items; retained tar, life and ordinary work continue. Compatibility defs and seated animal/plant bodies remain loadable.

## T18: dig lottery

Capability: Manual Mining work, progress/depth persistence, four weighted strata, increasing trap weight and deep-dig wake signal; most loot is vanilla salvage placeholders plus real draw-joints.
Why: Excavation with strata/treasure is the runner-up signature; it loses to the owner experience sentence about ordinary resistance.
Calls searched: RM_DigShaft comp -> EH RM_WorkGiver_WorkLottery/JobDriver -> RM_CompWorkedLottery -> RM_DigStratumTable; deep wake relay.
Gate the complete Sump-specific producer, offered player action, scheduled job/incident/letter and consumer callbacks; leave shared engine code/defs in the tree. Keep all acquisition/research links behind the same effective gate.

Acceptance test: With shipped defaults on a fresh full Sump map, dig lottery contributes no active instances, offered actions, jobs, incidents, letters, effects or queued callbacks (state read, not a def-count), including after reload; the log is clean. Enable its clearly labelled Next version setting with required companion extras in the same group: execute its ordinary producer/action and observe the named state/effect present. Disable again mid-operation: no new effects or lost pawns/items; retained tar, life and ordinary work continue. Compatibility defs and seated animal/plant bodies remain loadable.

## T19: dig disarm

Capability: Fuse countdown, deterministic Mining threshold and failure detonation; automatic disarm WorkGiver does not prefilter skill. Weight/whole-body-remains ConfigErrors are built.
Why: Timed traps and qualified disarm only exist to support deferred excavation.
Calls searched: RM_CompWorkedLottery countdown/menu and RM_WorkGiver_WorkLottery; no skill prefilter in automatic assignment.
Future specification only: trap gives a readable click/arming state; safe nearby escape and a qualified nearby miner can arrive before detonation, distant arrival may fail (ANSWERS_OWNER.md). Automatic worker selection filters Mining qualification. Preserve skill disarm and deepening risk.

Acceptance test: With shipped defaults on a fresh full Sump map, dig disarm contributes no active instances, offered actions, jobs, incidents, letters, effects or queued callbacks (state read, not a def-count), including after reload; the log is clean. Enable its clearly labelled Next version setting with required companion extras in the same group: execute its ordinary producer/action and observe the named state/effect present. Disable again mid-operation: no new effects or lost pawns/items; retained tar, life and ordinary work continue. Compatibility defs and seated animal/plant bodies remain loadable.

## T20: beast dormancy

Capability: Deep-tar set-piece places bulge; stock damage/construction wake, lottery relay and working deep-drill proximity emerge actual tar beast.
Why: Hidden wake causes launch the deferred catastrophe system, not ordinary wildlife or land.
Calls searched: RM_SumpTarBeastGenStep_Register -> shared placed-set-piece GenStep -> RM_BeastBulge; stock wake, BeastWakeRelay and BulgePumpWake; scanner and dread registration patches.
Gate GenStep producer, stock damage/construction wake, deep-dig relay and pump wake; scanner/dread consumers must not create or wake a hidden bulge.

Acceptance test: With shipped defaults on a fresh full Sump map, beast dormancy contributes no active instances, offered actions, jobs, incidents, letters, effects or queued callbacks (state read, not a def-count), including after reload; the log is clean. Enable its clearly labelled Next version setting with required companion extras in the same group: execute its ordinary producer/action and observe the named state/effect present. Disable again mid-operation: no new effects or lost pawns/items; retained tar, life and ordinary work continue. Compatibility defs and seated animal/plant bodies remain loadable.

## T21: beast station eater

Capability: Body size 9, slow pace, reachable dense-building selection, timed crushing bites, filth trail, stagger nearby pawns, mound/letter, satiation/timer and sink to new deep-tar bulge.
Why: A station-eating evacuation event is an additional system; no roster entry is evicted because this is a caused set-piece.
Calls searched: RM_TarBeast race/think tree -> EH RM_CompTarBeast and RM_CompStationEater; wake emits pawn, sinking creates RM_BeastBulge.
Gate eating, target selection, coating and sink/rebulge callbacks as well as spawning. No disappearing saved pawn: freeze with readable disabled sign or visible compatible migration.

Acceptance test: With shipped defaults on a fresh full Sump map, beast station eater contributes no active instances, offered actions, jobs, incidents, letters, effects or queued callbacks (state read, not a def-count), including after reload; the log is clean. Enable its clearly labelled Next version setting with required companion extras in the same group: execute its ordinary producer/action and observe the named state/effect present. Disable again mid-operation: no new effects or lost pawns/items; retained tar, life and ordinary work continue. Compatibility defs and seated animal/plant bodies remain loadable.

## T22: solvent weapon

Capability: Ordered solvent haul/pour, explicit danger confirmation, hiss/splash, pending wake record, permanent manhunter attempt/retry and letter; optional Ninefold deltas.
Why: Deliberately waking a manhunter is a weapon, not necessary for solvent cleaning. Keep solvent itself.
Calls searched: RM_BeastBulge CompProperties_BulgeSolventPour -> EH FloatMenuOptionProvider_PourSolvent/JobDriver_RM_PourSolvent and pending wake map component; Ninefold optional deltas.
Gate float-menu offer, haul/pour job, pending-wake execution, manhunter retry and god deltas. Retained weak-solvent cleaning must never enter the weapon path.

Acceptance test: With shipped defaults on a fresh full Sump map, solvent weapon contributes no active instances, offered actions, jobs, incidents, letters, effects or queued callbacks (state read, not a def-count), including after reload; the log is clean. Enable its clearly labelled Next version setting with required companion extras in the same group: execute its ordinary producer/action and observe the named state/effect present. Disable again mid-operation: no new effects or lost pawns/items; retained tar, life and ordinary work continue. Compatibility defs and seated animal/plant bodies remain loadable.

## T23: mouse tracks

Capability: Tameable mouse opts into dread-avoiding wander destinations and deposits tracks on shallow tar; bulge/awake beast register dread.
Why: Tracks and dread avoidance are a route-information system tied to hidden dangers. The mouse keeps ordinary movement and taming without those claims.
Calls searched: RM_SumpMouse comp -> EH RM_CompFilthTrail; custom think-tree RM_JobGiver_DreadAvoidWander -> DreadField plus SumpLivingMap.
Gate trail producer, dread-avoid think-tree and fresh-crust query together. Substitute ordinary animal wandering; mouse body, diet and native tar crossing remain.

Acceptance test: With shipped defaults on a fresh full Sump map, mouse tracks contributes no active instances, offered actions, jobs, incidents, letters, effects or queued callbacks (state read, not a def-count), including after reload; the log is clean. Enable its clearly labelled Next version setting with required companion extras in the same group: execute its ordinary producer/action and observe the named state/effect present. Disable again mid-operation: no new effects or lost pawns/items; retained tar, life and ordinary work continue. Compatibility defs and seated animal/plant bodies remain loadable.

## T24: gaslight chemistry

Capability: Bitumen plus weak solvent crafts stackable tar gas at machining bench behind research; own resource, not a Helixien pipe-network implementation.
Why: Collectable gas and its research/fuel production add a separate industry. Keep solvent recovery without bottled gas.
Calls searched: RM_TarGas recipeMaker consumes bitumen+weak solvent; RM_GaslightChemistry gate; scrub byproduct produces gas independently.
Gate gas recipeMaker and gaslight research, but do NOT gate TarRendering used by retained pitch/solvent chains. Recoverable scrub gas has a separate producer ticket.

Acceptance test: With shipped defaults on a fresh full Sump map, gaslight chemistry contributes no active instances, offered actions, jobs, incidents, letters, effects or queued callbacks (state read, not a def-count), including after reload; the log is clean. Enable its clearly labelled Next version setting with required companion extras in the same group: execute its ordinary producer/action and observe the named state/effect present. Disable again mid-operation: no new effects or lost pawns/items; retained tar, life and ordinary work continue. Compatibility defs and seated animal/plant bodies remain loadable.

## T25: warbling lamp

Capability: Fueled/flickable lamp, warm hue/radius pulses and room-beauty reward via shared warbling-glow comp.
Why: A bespoke pulse/beauty/fuel lamp is not necessary for dusk to be readable; ordinary lamps supply light.
Calls searched: RM_GaslightLamp refuel/glower/warbling comps read tar gas; vault graphic reuse references lamp texture, not lamp runtime.
Gate build/refuel/beauty/pulse behaviour and gas research offers. Vault texture reuse is code/data coupling only; keep texture addressable without enabling a lamp.

Acceptance test: With shipped defaults on a fresh full Sump map, warbling lamp contributes no active instances, offered actions, jobs, incidents, letters, effects or queued callbacks (state read, not a def-count), including after reload; the log is clean. Enable its clearly labelled Next version setting with required companion extras in the same group: execute its ordinary producer/action and observe the named state/effect present. Disable again mid-operation: no new effects or lost pawns/items; retained tar, life and ordinary work continue. Compatibility defs and seated animal/plant bodies remain loadable.

## T26: living map

Capability: Shared hourly diff queues soffeth rings, delays mouse dread on fresh RM_TarGlass and migrates mirrelin; settings and saved responder queues exist.
Why: Delayed plant rings and fresh-crust mouse reroutes add changing ecological clues. Static habitat and normal growth remain whole without this queue.
Calls searched: EH map-component autoinstantiation -> BiomeCarriesSumpFlora -> terrain diff/queued ring/crust tasks; DreadField calls IsFreshCrust.
Gate scan, ring/crust queue execution and dread consumer. Preserve old-save state safely; retaining soffeth/mirrelin roster bodies must not silently re-enable via BiomeCarriesSumpFlora.

Acceptance test: With shipped defaults on a fresh full Sump map, living map contributes no active instances, offered actions, jobs, incidents, letters, effects or queued callbacks (state read, not a def-count), including after reload; the log is clean. Enable its clearly labelled Next version setting with required companion extras in the same group: execute its ordinary producer/action and observe the named state/effect present. Disable again mid-operation: no new effects or lost pawns/items; retained tar, life and ordinary work continue. Compatibility defs and seated animal/plant bodies remain loadable.

## T27: tar sealed food

Capability: Optional ColdStorage vat and bills seal meat/fish/eggs/produce with bitumen; 30-day pitch aging, bad-cook ruin chance, sealing failures and preserved-taste data; independent of shelf vault.
Why: Food sealing, cooking failure and pitch aging duplicate a preservation progression beyond the chosen signature.
Calls searched: RM_TarSealingVat plus recipes/products -> ColdStorageGateExtension, Sealed/aging and product hazard engine; tarSealEnabled setting.
Gate the complete Sump-specific producer, offered player action, scheduled job/incident/letter and consumer callbacks; leave shared engine code/defs in the tree. Keep all acquisition/research links behind the same effective gate.

Acceptance test: With shipped defaults on a fresh full Sump map, tar sealed food contributes no active instances, offered actions, jobs, incidents, letters, effects or queued callbacks (state read, not a def-count), including after reload; the log is clean. Enable its clearly labelled Next version setting with required companion extras in the same group: execute its ordinary producer/action and observe the named state/effect present. Disable again mid-operation: no new effects or lost pawns/items; retained tar, life and ordinary work continue. Compatibility defs and seated animal/plant bodies remain loadable.

## T28: acoustic payload

Capability: Optional AcousticScanner patch identifies dormant bulge, still hunter, brood and hidden caves, with Sump-specific readings.
Why: Scanner-specific hidden readings are an optional instrument for deferred hazards, not the player warning retained tar exposure needs.
Calls searched: Patches/RM_AcousticPayload_TheSump.xml adds AcousticScanner target payloads for bulge, still hunter, brood/caves; scanner def discovery.
Gate Sump-specific payload injection and target registration, without disabling AcousticScanner or independent neighbouring data.

Acceptance test: With shipped defaults on a fresh full Sump map, acoustic payload contributes no active instances, offered actions, jobs, incidents, letters, effects or queued callbacks (state read, not a def-count), including after reload; the log is clean. Enable its clearly labelled Next version setting with required companion extras in the same group: execute its ordinary producer/action and observe the named state/effect present. Disable again mid-operation: no new effects or lost pawns/items; retained tar, life and ordinary work continue. Compatibility defs and seated animal/plant bodies remain loadable.

## T29: arrival letter

Capability: Biome extension gives first-arrival surface-reading advice; Utinni patch supplies campaign voice.
Why: Recommend retiring this arrival letter: it teaches absent mouse/crust/gas tells and ordinary inspect text can teach the retained tar cost. Until decided, keep the letter gated off, with corrected text before any opt-in.
Calls searched: RM_TheSump arrival extension -> EH biome-arrival notifier; campaign BiomeArrivalLetters_TheSump.xml replaces prose.
Gate EH notifier and both RM/campaign prose replacements; use honest inspect text for tarred/terrain/solvent instead. Do not teach disabled clue systems on arrival.

Acceptance test: With shipped defaults on a fresh full Sump map, arrival letter contributes no active instances, offered actions, jobs, incidents, letters, effects or queued callbacks (state read, not a def-count), including after reload; the log is clean. Enable its clearly labelled Next version setting with required companion extras in the same group: execute its ordinary producer/action and observe the named state/effect present. Disable again mid-operation: no new effects or lost pawns/items; retained tar, life and ordinary work continue. Compatibility defs and seated animal/plant bodies remain loadable.

## T30: false floor behaviour

Capability: Pallick body is built; false-floor collapse and mouse avoidance specifically over pallick are absent in inspected src.
Why: Pallick collapse is a separate hidden trap. Keep its roster body as harmless crust cover with honest text until this opts in.
Calls searched: No current consumer found by named-symbol search in source/defs and read-only HEAD blobs; earlier inventory search_scope records the promised behaviour separately from its present body.
Future specification only: a pallick skin fails into tar with recoverable mire, never lethal alone; genuine mouse-avoidance evidence and readable changing state must ship together. Harmless body remains ordinary life now.

Acceptance test: Before future activation, a reviewed situation/transition specification covers the producer, no-trigger control, save/reload, death/despawn, disable and player-readable failure; current default state read shows the promised extra absent. Acceptance is the spec, not an assertion that the unbuilt mechanic works.

## T31: species ecology

Capability: Custom thrummel mound/guard radius/queen ends hive; dredgel dig-attraction; moving skarrid dread are not wired onto current native bodies.
Why: Mounds, guarded radii, dig attraction and moving dread are bespoke ecosystems beyond ordinary diets/combat/products.
Calls searched: No current consumer found by named-symbol search in source/defs and read-only HEAD blobs; earlier inventory search_scope records the promised behaviour separately from its present body.
Future specification only: specify mound/guard/queen transitions, attraction to actual active digging, and moving skarrid dread separately before enabling. Ordinary broodmother butcher seepwax is NOT contingent on building these systems.

Acceptance test: Before future activation, a reviewed situation/transition specification covers the producer, no-trigger control, save/reload, death/despawn, disable and player-readable failure; current default state read shows the promised extra absent. Acceptance is the spec, not an assertion that the unbuilt mechanic works.

## T32: indicator placement

Capability: Initial soffeth gas-seep and tolleth rich-find placement, reliably cooled-ground-only mirrelin/pallick and margin-only flora are not implemented by these plant defs.
Why: Gas/treasure/false-floor indication needs deferred underlying states. Ordinary tar-margin, pool and glass habitats are a separate kept requirement.
Calls searched: No current consumer found by named-symbol search in source/defs and read-only HEAD blobs; earlier inventory search_scope records the promised behaviour separately from its present body.
Future specification only: tie each gas/treasure/false-floor tell to a saved actual source, invalidate it when source changes, and distinguish stale tracks. No clue may claim certainty about an absent source.

Acceptance test: Before future activation, a reviewed situation/transition specification covers the producer, no-trigger control, save/reload, death/despawn, disable and player-readable failure; current default state read shows the promised extra absent. Acceptance is the spec, not an assertion that the unbuilt mechanic works.

## T33: prewake warning

Capability: Ordinary disturbance's day-ahead room-sized bubble/ring warning not located; instant solvent weapon is deliberately separate.
Why: The warning is indispensable WHEN the beast returns, but no beast runs in this version. Preserve day-ahead warning and evacuation constraints then.
Calls searched: No current consumer found by named-symbol search in source/defs and read-only HEAD blobs; earlier inventory search_scope records the promised behaviour separately from its present body.
Future specification only: ordinary waking must warn before emergence with localized rising ground/bubble plus persistent message; use the already recorded day-ahead ruling, allow people and selected stores out, lose buildings. Solvent weapon remains deliberately instant and separate. Do not replace that ruling with a new shorter delay.

Acceptance test: Before future activation, a reviewed situation/transition specification covers the producer, no-trigger control, save/reload, death/despawn, disable and player-readable failure; current default state read shows the promised extra absent. Acceptance is the spec, not an assertion that the unbuilt mechanic works.

## T34: natural flame discovery

Capability: Natural seep flames plus first-flame/geyser encounter discovery and first-tar technology trigger not located; current gaslight/rendering are ordinary research rows.
Why: Discovery-triggered technology and seep flames are a progression system. Existing manual research covers retained rendering.
Calls searched: No current consumer found by named-symbol search in source/defs and read-only HEAD blobs; earlier inventory search_scope records the promised behaviour separately from its present body.
Future specification only: keep first natural flame/geyser discovery separate from ordinary TarRendering research, with saved once-only progression and no literal natural flame producer in the current version.

Acceptance test: Before future activation, a reviewed situation/transition specification covers the producer, no-trigger control, save/reload, death/despawn, disable and player-readable failure; current default state read shows the promised extra absent. Acceptance is the spec, not an assertion that the unbuilt mechanic works.

## T35: special archive finds

Capability: Lore-specific bones/hides/casings and live ancient-machine/Assailant dig-wake outcomes not authored in current Sump lottery; existing draw-joint is real.
Why: Ancient finds and exceptional live excavation outcomes belong to the deferred archive system, with partial-remains bans intact.
Calls searched: No current consumer found by named-symbol search in source/defs and read-only HEAD blobs; earlier inventory search_scope records the promised behaviour separately from its present body.
Future specification only: preserve no whole Assailant/Rakatan, traps more likely than exceptional partial remains; no living ordinary ancient fauna. Wreckage owns wreck loot, Bones ordinary remains; do not duplicate engines.

Acceptance test: Before future activation, a reviewed situation/transition specification covers the producer, no-trigger control, save/reload, death/despawn, disable and player-readable failure; current default state read shows the promised extra absent. Acceptance is the spec, not an assertion that the unbuilt mechanic works.

## T36: moat wall integration

Capability: Current actual fuse-post path has no TarBlaze consumer establishing promised impassable long-burning smoke wall and column.
Why: Impassable long-burning smoke wall belongs to the deferred military moat; support code alone is not its implementation.
Calls searched: No current consumer found by named-symbol search in source/defs and read-only HEAD blobs; earlier inventory search_scope records the promised behaviour separately from its present body.
Future specification only: real impassable smoke/flame with spent ground, explicit duration, and gate-aware front. The existing fuse post starts vanilla Fire and does not establish this promise. No claim of a smoke wall on that evidence.

Acceptance test: Before future activation, a reviewed situation/transition specification covers the producer, no-trigger control, save/reload, death/despawn, disable and player-readable failure; current default state read shows the promised extra absent. Acceptance is the spec, not an assertion that the unbuilt mechanic works.

## T37: nine rites v2

Capability: The Sinking and Mob'Unloo effigy rite are deferred outside v1 by explicit owner retarget; no current Sump effect implementation found.
Why: The Sinking and effigy rite were already moved by the owner. This is an acknowledgement, never a renewed request or waiver.
Calls searched: No current consumer found by named-symbol search in source/defs and read-only HEAD blobs; earlier inventory search_scope records the promised behaviour separately from its present body.
Already owner-deferred; preserve the Sinking/effigy idea without implementation work or renewed waiver request. Holy Flame on the neighbouring idol is expressly outside this ticket.

Acceptance test: Before future activation, a reviewed situation/transition specification covers the producer, no-trigger control, save/reload, death/despawn, disable and player-readable failure; current default state read shows the promised extra absent. Acceptance is the spec, not an assertion that the unbuilt mechanic works.

## T38: inhabited future

Capability: Campaign faction weighting, expedition ruins, attempted refineries and moisture farmers belong to the Inhabited pass; no installed Sump-specific injection chain verified.
Why: Junker ruins, refinery attempts and faction injections are campaign inhabited content, not ordinary ground/life/tar maintenance.
Calls searched: No current consumer found by named-symbol search in source/defs and read-only HEAD blobs; earlier inventory search_scope records the promised behaviour separately from its present body.
Future specification only: find installed campaign injections before asserting absence; no new settlement, faction, world placement or alternative planet. Existing fixed-world stations are not removed.

Acceptance test: Before future activation, a reviewed situation/transition specification covers the producer, no-trigger control, save/reload, death/despawn, disable and player-readable failure; current default state read shows the promised extra absent. Acceptance is the spec, not an assertion that the unbuilt mechanic works.

## T39: titan passage neighbour

Capability: Ledger-only native/visiting giant question exists; dormant tar beast set-piece is not automatically a HugeThings passage candidate.
Why: A visiting giant is additional encounter content. Existing HugeThings behaviour is not redesigned or inferred from the tar beast.
Calls searched: No current consumer found by named-symbol search in source/defs and read-only HEAD blobs; earlier inventory search_scope records the promised behaviour separately from its present body.
Future specification only: inspect HugeThings seated passage data before proposing an encounter. Do not equate the dormant tar beast with a migrating giant or change its evacuation fiction.

Acceptance test: Before future activation, a reviewed situation/transition specification covers the producer, no-trigger control, save/reload, death/despawn, disable and player-readable failure; current default state read shows the promised extra absent. Acceptance is the spec, not an assertion that the unbuilt mechanic works.

## T40: routine cleaning

Capability: Automatic supplied worker cleanup with no repeated medical-bill selection
Why: Without this, repeated exposure makes the owner's chosen routine into repeated player clicks.
Calls searched: No automatic cleanup consumer found; existing surgery bill is manual.
Specify a repeatable routine using player-set work priorities and an enable/reserve policy. At a clean reachable work spot an available helper/pawn physically reserves and consumes accessible weak solvent, clears carried tar as well as RM_Tarred, and finishes without surgery injury. Abort/death/unreachability releases reservations; no map-wide teleport of solvent. With no solvent, stop requesting it, show the shortage and permit slow clean-ground recovery. Do not require a per-pawn medical bill. Existing recipe does not provide this automation.

Acceptance test: Ordinary work with tar-exposed workers consumes reachable reserved solvent once, clears both carried tar and hediff, survives interruption/death/reload without duplicate use, needs no repeated player bill and reports shortage without an error/retry storm; the same healthy pawn on ordinary clean ground consumes none. State read plus negative controls; forty-colonist routine completes alongside food and route work.

## T41: ordinary habitats

Capability: Tar-margin plants, pool film and harmless pale crust on walkable glass; no truth-claims about deferred hazards
Why: Without this ordinary habitat, land reads as a fertile grassland with plants sprinkled anywhere, against the frozen chemotroph margin ruling.
Calls searched: Current ordinary wildPlants placement and deferred EH SumpLivingMap; no initial margin gate located.
Add initial/regrowth habitat consumers using actual tar/solid-glass adjacency: margin plants on eligible dry cells within 1-3 cells of tar; Velloch only on tar; Mirrelin on walkable cooled sheets; harmless Pallick on solid sheets while its trap is off. Dorvel is the player-sown exception on eligible worked ground; no grow lights required. Never use the deferred living-map queue or claim these plants locate gas/loot.

Acceptance test: Enumerate every retained wild plant habitat on initial and regrown terrain across tar/glass/margin boundaries; no wrong-habitat spawn. Sown dorvel grows in actual dusk without a lamp where temperature permits. Deferred clue/false-floor behaviours stay absent and descriptions make no such claims. Compare against an actual map terrain/plant read before trusting the generator.

## T42: gas byproduct

Capability: Collectable gas emitted by successful pawn scrubbing
Why: Collectable fuel is deferred industry; recovery must finish without granting or loading a lamp.
Calls searched: RM_ScrubTarred calls the byproduct worker; independent of gas recipe research.
Gate RM_ScrubTarred bottled-gas output independently of recovery success. Default cure may show a harmless dissipating reaction; it creates no fuel Thing. Keep chemical lore, not an active deferred industry.

Acceptance test: With shipped defaults on a fresh full Sump map, gas byproduct contributes no active instances, offered actions, jobs, incidents, letters, effects or queued callbacks (state read, not a def-count), including after reload; the log is clean. Enable its clearly labelled Next version setting with required companion extras in the same group: execute its ordinary producer/action and observe the named state/effect present. Disable again mid-operation: no new effects or lost pawns/items; retained tar, life and ordinary work continue. Compatibility defs and seated animal/plant bodies remain loadable.

## T43: Retained ground and tracking seam

Move/generalize the actual shallow-tar generated-filth and acceptance consumer into the RM dependency path using FlowWorks-owned definitions. Surface masks must admit natural/pawn filth but not Terrain when generatedFilth is set. Add no parallel fluid engine. Correct sand/lush-grass presentation and assure a connected starting build area outside deep tar; no worldgen capability. Ordinary tar descriptions name the oily reek (the typed “stinking” experience), without adding an odor simulation or hazard.

Acceptance test: All-DLC composed post-patch data resolves without Utinni; ordinary pawn walking shallow tar acquires and deposits tar on an accepting floor, deep tar remains visibly unwalkable, glasswalk rejects new deposits, and an absent-filth control stays clean. Old campaign patches cannot double-add fields. Read actual map geometry and log; tar description conveys the oily reek without teaching deferred clues or inventing smell penalties; no tile-count finding.

## T44: Native movement and actual flyer evidence

Implement the required basic mouse/stilt tar-crossing contract independently of dread/trails; do not change animal roster membership. Check real flight state and use the standing whole-body directional animation requirement; do not invent a sprite path or count. Existing MaxFlightTime is a built stat, missing movement proof/flipbook binding remains an implementation gap.

Acceptance test: State traces show mouse shallow-tar crossing without colonist mire and skellarn ground/flight transitions over tar, including downed and cooldown. No pawn vanishes. FlightTracker deterministic read is the instrument; any visual flight look requires the owner present. No unattended flight captures.

## T45: Settings and disable recovery

Retained controls: dry-dusk presentation, tar coating/exposure, glasswalk offer and auto solvent cleaning; keep density timing labels. Gate all deferred Sump producers locally, never by globally disabling a neighbour. All-off clears local penalties/reservations safely, preserves animals/items/terrain and ordinary jobs; settings reset returns shipped defaults. Remove active worldgen UI.

Acceptance test: Read local effective gates and consumer states after toggle, save/reload and reset, both new map and existing dirty worker. No frozen hediff penalty on all-off, no carried Thing loss, no ordinary-life eviction, no global neighbouring setting change; deferred actions stay absent by default, log clean.

## T46: Situation and causal-state instrument

Build Situation walk and Route geometry as specified in models.md; extend functional tests to collect actual carried filth, exposure, hediff, path cells/ticks, labour/resource reservations, terrain, plant profiles, flight and settings. Existing direct proof hooks stay checks and require safe restoration.

Acceptance test: Every declared situation class has a reproducible fixture, expected causal contrast and outcome or UNMEASURED reason; inject absent tracking, retained-filth cure, wrong habitat, disabled flight and enabled-extra mutants and detect the corresponding bar failure. Calibration/reload identity checks pass before model readings are believed.

## T47: Whole-map and resource instruments

Build Whole map and Solvent queue as specified in models.md first when their unknown meetings are reached. Capture full default settings, all dependency profiles and ordinary actions with no special weather/feature locks; add exception-safe disposable-map restore.

Acceptance test: Matched actual game intervals meet the specified calibration agreement, season trace and mid-save continuation are compared, main action orders reverse, and mutations producing land conversion, no growth, perpetual caking, stock duplication and retry storms are all detected. An uncalibrated or unrun model reports UNMEASURED, never PASS.

## T48: Source/proof census reconciliation

Retarget current functional coverage to these experience bars after review/application, preserving old def/quantity checks and deferred-extra tests as checks. Sparse external files were read via HEAD blobs. No old tree leaves exist; historical first-script criteria are not imported bars.

Acceptance test: New coverage names all retained experiences and the whole run, every extra gate has an off/on check, and no test claims all deferred defs must be absent from the database. Current runtime/source/settings fingerprints accompany future proof. No previous historical pass becomes current by copying it.

## T49: Composed plant-growth integration

Read actual ExplosiveGrowth profiles for all seated chemotrophs with the engine enabled. The source default classifier sees our wild natives but no explicit Sump rows were found in its base roster; resolve the data classification through its existing extension/roster API, respecting the frozen no-sun flora rule. No custom growth engine or invented watering exception.

Acceptance test: With shared growth enabled at shipped defaults, actual dusk/positive-temperature plants progress without artificial light, temperature stop remains normal, and resolved archetype/top/soak settings are read. A sun-dependent or burst-spreading misclassification is detected before any whole-map model is trusted; correct data through the existing API and repeat only affected readings.

## T50: Native hydration binding

Ordinary life, not an extra. The standing ruling in biome_rulings.md (2026-11-01) covers every biome's native environmental liquid. FlowWorks RM_ThirstUtility already supplies NativeHere/HomeWater and a nativeWater terrain extension; no matching tar binding was found in RM_Tar.xml or the inspected foreign-terrain patches at HEAD. The generated native-water audit infers liquids from biome fertility terrain or names containing the biome name, so its lack of a Sump row is an instrument coverage gap, not permission to omit tar. Use the engine's existing data/API for native hydration and correct its audit input to include actual local liquid terrains; do not redesign thirst, add fresh-water terrain or make tar potable for humanlikes.

Acceptance test: With shared thirst on at defaults, hungry/thirsty wild and tame seated native animals beside reachable shallow/deep-tar shores satisfy hydration through a real ordinary action without human liquid penalties or dehydration; source and need delta are read before/after reload. The same liquid remains unavailable as normal potable water to a colonist. The instrument enumerates Sump's actual tar pools rather than reading only terrainsByFertility, and an absent nativeWater binding mutant fails the native-life reading.

## T51: Finite carried-water provisioning proof

Needed by the supplied-colony whole run and native-life humanlike control. Existing FlowWorks RM_Bottle_FreshWater and RM_Barrel_FreshWater are the named supply; their humanlike ingestion/partial-container jobs exist. No Sump water source or new drink job is commissioned. Read-only callers searched: JobDriver_FillBottle -> TryDebitTerrain/MakeContainer; JobGiver_RM_Drink -> vanilla Ingest or RM_DrinkFromContainer; container drawnUnits is saved; JobGiver_RM_AnimalDrink searches terrain only. Shared thirstEnabled and animalsGetThirst default on (RM_ThirstSettings.cs). Animal terrain-only drinking is an owner ruling, thirst_bottles_design_2026-10-16.md §2 OQ-5 and §3, not an implementation gap we may override.

Specify and record an actual legal fresh-water source outside the Sump on the fixed world, ordinary filling and caravan transport, source/container identities and debit, available carry mass/trips, route access and losses. Do not guess a tile or guarantee a trader. Humanlikes drink this cargo at the Sump without spilling it into water terrain. A run starting from a provisioned disposable save may reuse a recorded fill/transport trace; authoring the fixture is not proof that water was obtainable. If no legal accessible source/transport can be demonstrated, report the supplied-colony range UNMEASURED and the concrete conflict; do not conjure stock or disable thirst.

For the declared 60-day-or-longer horizon, compute a conservative finite cargo budget from the actual colonist count and resolved RM_ThirstMath: sum maximum per-day fall × LitresPerFullNeed × run days over supported heat/work factors; add recorded sip-rounding waste, container deterioration/destruction and a declared contingency reserve. Record actual capacities using RM_ContainerMaterials.UnitsIn, subtract saved drawnUnits and include bottles packed in inventory. Extend the budget for any longer run. Cargo must physically fit real storage/transport; no infinite stack, automatic refill or local source. A starting expedition stock can cover the whole finite horizon, but indefinite settlement requires additional player-arranged imports and their costs.

Sustained imported non-native livestock is excluded, not quietly supplied: tar-only land plus the ruled terrain-only animal job leaves no legal drinking source. Include an isolated negative boundary trace showing readable dehydration and no unexplained disappearance; do not make that unsupported animal survive by an exemption. Seated tame natives remain positive tar-hydration arms under T50. Never insert a pond or an animal container adapter to satisfy this ticket.

Acceptance test: On the complete default Sump with shared thirst enabled, a recorded ordinary fill/transport trace pays for the named bottle/barrel cargo at an actual off-site source. A finite measured budget covers the declared whole-run duration for the supported colonist counts, with reachable home/work stock and actual ordinary drink/haul jobs; container debits and human need deltas agree through mid-run reload and changed work order. Remaining litres reconcile exactly with consumption/losses and no surface-water cell or unrecorded refill appears. In a separate inaccessible/empty-cargo control, humanlikes cannot hydrate from tar, and the reading detects impending depletion or dehydration rather than passing a hidden source. Seated natives still hydrate at tar; a non-native import remains visibly unsupported under the unchanged animal rule. Log clean. Any missing source/transport/capacity evidence is UNMEASURED, never PASS.
