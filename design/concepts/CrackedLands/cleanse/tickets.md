# Implementation and instrument tickets — proposal only

No ticket is executed by this pass. Each built extra keeps its code, defs and assets. A next-version gate defaults off, is labelled “Next version”, survives persistence/reset, stops production and callbacks, and cannot invalidate a retained bar. All primary fresh-map acceptance below runs the **complete retained biome at shipped defaults**, natural sky/weather and no kept lock. Optional-on comparisons use disposable copies and explicit prerequisites; they are not first-version passing evidence. Read effective state and log deltas, not just menu labels. Existing saves retain old objects; release old jobs safely and finish/readably explain lifecycles, never destroy visiting pawns to enforce fresh-map absence.

## T1: Switch off the herald sequence without silencing the core warning

Callers: RM_MapComponent_CanyonFlood.Cfg/PlayHeraldBeat/RingChime/ChimeCell, RM_FloodKernel.Tick/MinArmLeadTicks, RM_TarruqHushPatch and RM_CanyonBeats.xml. Keep chimes/anchors, urgency and continuous water roar. Separate core anchor placement and chime spatial use from fiveBeatsEnabled: current false branch puts core sound on camera. Defer wind/pan-tick/hush messages and the Herald stage as a package; migrate legacy phase safely. Capture ordinary tarruq calls as the baseline. Bespoke audio was already waived by the October 3 vanilla-clips ruling; never refile that commission.

Acceptance test: Fresh default native map completes natural warning/water/recede with chimes and roar but no Herald events, pan tick/wind messages or call suppression; runtime phase/event reads and clean log prove absence. Enable the next-version sequence and observe its wind/tick/hush/chime/roar stages and call gate; default reset returns it off without shortening a pending core warning.

## T2: Switch off uttaqar reactive wound-stone

Callers: RM_MuttavaqUttaqar.xml race.hediffGiverSets -> RM_UttaqarPetrificationGivers -> stock bleeding giver and hediff. Separate the wound reaction from the ordinary predator body/stats and retain defs. Do not remove the race or its roster row. Existing wound effects need a documented expire/retain policy, not blanket pawn cleanup.

Acceptance test: Fresh default uttaqar can hunt, be tamed where normal rules permit and take a wound without gaining reactive wound-stone; inspect hediff state and a clean log. With the next-version gate on, a controlled bleeding wound grants the declared wound-stone effect. Baseline armour remains ordinary and is not mistaken for the reactive grant.

## T3: Switch off floodline salvage and stakes

Callers: RecedeAftermath.OnRecede -> SpawnSalvage/PlantStake, MapComponentTick expiry, Unclaimed and crew target/query helpers. Gate scatter, stakes, claim processing and announcements independently of retained irqit/qirra wet callbacks. A crew gate alone is insufficient. Leave ordinary Wreckage untouched. On old saves disable new production, release reservations and preserve legitimately recovered items; do not delete visitor pawns or player inventory.

Acceptance test: Fresh default map through flood/recede/dry has no flood-generated component/slag scatter, stake, claim record, claim job or salvage letter, with clean log; distinguish ordinary pre-existing wreck output by source IDs. With this gate on and crew off, scatter and stakes/claim records appear and an unclaimed test piece expires with its readable notice while recovered goods survive. Same map with gate off still has qirra/irqit and correct wet expiry.

## T4: Switch off rival claim crews and preserve their future race specification

Callers: OnRecede CrewComes -> crewArrivalTick -> SendCrew; RM_ClaimCrew lord/duties/job drivers; ClaimCrewProfile/Trader defs and Utinni substitution patch. No scheduled arrival, trader stock, props, faction-relation change or claim job may survive the off gate. Old crews receive a safe ordinary exit/release, not vanishing cleanup. Existing faction/trade/about-one-in-three choice is already ruled; do not ask it again. Later race default: physical recovery wins custody; a queued designation alone cannot protect the whole flood line forever. Interrupted work releases a temporary reservation; simultaneous arrival uses normal exclusive job reservation, and hostility depends on actual relations rather than an automatic raid.

Acceptance test: Fresh default flood cycles create no crew schedule, lord, pawn, trading session/stock, prop, incident or crew letter and no goodwill change; log clean. Enable crew plus T3 prerequisites, drive the production chance/event on an unclaimed scatter, and read actual visitor arrival/work/trade/exit; lowering actual relations invokes the hostile recovery state, not a raid. A designation without recovery cannot permanently settle all future-on claims; record interruption/custody and simultaneous-reservation outcomes.

## T5: Switch off repeated recede wreck rewards

Callers: RecedeAftermath.OnRecede -> TakeBackFloodWrecks/SpawnFloodWreck; RM_CanyonWreckHull/Speeder inherited defs remain needed by ordinary map field. Gate the special tracked-list spawner, repeated takeback and announcements, not the shared Wreckage family. Existing tracked wrecks become ordinary engine-owned wrecks or remain safely tracked until their declared end; no player-built object is reclassified by a stale reference.

Acceptance test: Fresh default state through repeated recedes has no recede-produced wreck IDs/list entries or reward/takeback message, clean log; ordinary initial field/deconstruction remains. Enable the next-version wreck gate on a map with a legal placement footprint and observe a recede-generated deconstructible wreck and its documented next-recede notice/removal. Source attribution prevents a map-start wreck from falsely proving the extra on.

## T6: Switch off fossil-strata seeding and decouple passive talus placement

Callers: fossil Register patch -> RM_GenStep_FossilStrata.Generate -> SeedMap; its seed path also calls ThreeHeightFlora.SeedClasps from seams. Retain map/def registration harmlessly gated, keep mineable defs resolvable, and give passive talus its ordinary natural-wall placement independent of fossil seams. Do not let a future-off seed call the special pry path.

Acceptance test: Fresh default native map has no generated fossil seam of any tier and no fossil-seed event, clean log, while natural-wall talus and retained flora/ledges still place legally. Enable this gate on a rock-face/deep-rock fixture and read seeded seams; retained passive talus does not depend on finding a seam. Seed density is a regression check, not a bar.

## T7: Switch off flood fossil recutting

Caller: RecedeFlood -> RM_FossilStrata.RecutAlong. Gate before any candidate replacement or announcement, independently of natural wet accounting. Keep rock geometry and refs intact; a debug force must report the extra is off rather than running behind the gate.

Acceptance test: Fresh default floods with wetted natural rock faces create no new fossil seams or recut event/state, clean log. With recutting on and a valid natural-rock candidate, a recede produces a new seam traceable to that flood; pre-existing ore/player walls remain unchanged. T6 may remain off for this contrast.

## T8: Switch off collectible fossil goods as an acquisition system

Callers: seam mineableThing, talus PlantCollected, trader stock eligibility via tradeTags, RM_FossilCase costList; scanner target strings are separately gated. A gate only in RecutAlong is insufficient. Keep defs and existing save items; suppress all new default acquisition channels, using a parse-safe def/settings gate or equivalent supported data filter rather than deleting definitions. Gate mining yields and natural/trade generation, not generic Bones butchery.

Acceptance test: Fresh default map/inventory/trader-source state after map creation, flood and ordinary mining contains no newly generated fossil impression/skeleton/deep-stratum collectible or fossil job/letter, clean log. Enable collectible goods and the appropriate seam source, mine it and read the real drop; enabling T10 permits its separately declared fossil drop. Existing items loaded from old saves remain valid and do not count as fresh default generation.

## T9: Switch off carvings and memories pending retirement decision

Recommendation: retire this extra; the owner decides. Callers: RM_MercyLedges.CarveLedge places carving before an else-if anchor; CompRM_MercyCarving.CompTickRare/inspect/readers gives memories. Gate carving placement, inscriptions/memory effects and related prompts. Place core chime anchors independently so no carving branch or occupied slot is a prerequisite for warning. Keep definitions/save reader references inert.

Acceptance test: Fresh default map has usable cliff-cut refuges and anchors but no carving object, reading memory, religious inscription prompt/job or carving letter; log clean. Enable the next-version carving gate and observe inspectable carving plus a single per-pawn reading memory under the retained future shape, with core anchors still present. Neither contrast changes flood exclusion/capacity.

## T10: Switch off all talus mining mechanics together

Callers: RM_Plant_TalusClasp.TickLong -> TryPry; PlantCollected fossil drop (currently not governed by claspPryEnabled); RM_TalusClaspMiningPatch.Prefix/Postfix (currently governed by bonus amount, not the full feature gate); TryPry letter. Keep passive wall-rooted plant, placement/dieback and ordinary non-resource harvest handling. Remove the seam-required SeedClasps dependence via T6/T29.

Acceptance test: Fresh default mature clasps beside natural walls produce no seam replacement, mining bonus, fossil harvest or pry/cut letter under repeated production decision opportunities; mine/cut and compare source-attributed yields, with clean log. Enable this gate with T8 prerequisites and drive a valid production pry, mine beside a grown clasp and cut a qualifying clasp; the configured effects and rate-limited notification become observable. Debug bypass cannot count as the default-on proof.

## T11: Switch off the special zennaq filament commodity

Callers: RM_Zennaq.plant.harvestedThingDef -> RM_ZennaqFilament and any general trade/harvest source. Keep zennaq's roster, ordinary body, habitat and flammability; no lightning target code is restored. The future commodity is optional material flavour, not a required source of ordinary cloth/dye/food.

Acceptance test: Fresh default mature zennaq/cut/trade state produces no special filament item or commodity job/announcement, with clean log and ordinary plants retained. Enable the next-version commodity gate and harvest a mature plant to the declared filament product. No other core plant yield or existing roster member is removed by the toggle.

## T12: Switch off luqqim's glower while keeping the plant

Caller: RM_Luqqim.comps CompProperties_Glower; no C# gate exists. Use a safe loaded comp/behaviour gate so startup resets and save loads do not leave registered glow. Do not remove the wildPlants row or the ordinary minor harvest. It must not alter the shared Direct Sun/shade reader or become a workaround for Veqma eligibility.

Acceptance test: Fresh default native luqqim remains visible/selectable and harvestable but contributes no registered local glow/lighting utility, log clean; read glow-source registration rather than only daylight brightness. Enable its next-version light setting and read its emitted glow after update; off/on/reload unregisters/re-registers without duplicates and without changing geometric shade classification.

## T13: Switch off lithops metal/stone output pending retirement decision

Recommendation: retire metal-producing lithops, retaining its passive plant/def and existing memberships. Callers: RM_CrackedLands_DonorPorts.xml harvestedThingDef Steel and unguarded VEF.Plants.DualCropExtension. No kept behaviour needs VEF. Gate both outputs; merely disabling a callback after XML resolution is too late for an unavailable extension class. Use parse-safe mod guard/data with no default unresolved VEF type; do not redesign another framework.

Acceptance test: Fresh default composed RM load resolves retained donor-port defs without a VEF class error; harvesting a mature placed lithops produces no extra steel/secondary stone, no commodity job/letter and clean log. With the next-version gate on in its explicitly supported dependency configuration, actual harvest produces the declared outputs. No promise of a VEF-absent enabled configuration; an unavailable dependency is shown before enabling, with the default still load-safe.

## T14: Switch off wax-suit availability and specify later protection

Callers: RM_CrackWaxSuit generated tailoring recipe, menus/stock/loot; RM_WaxSuit.xml explicitly admits survival unwired. Retain apparel/assets/old-save wearability but suppress fresh default access, not just a nonexistent survival callback. Future boundary: works only on already accessible water terrain, no personal dive/planet-layer travel; breathing protection does not imply immunity to flood impact. Recipe/campaign discovery remain in their correct tiers, no RM reference to mandatory RUT-only ingredients.

Acceptance test: Fresh default map/menu/recipe/trader/incident state has no obtainable newly generated wax suit or suit craft job/letter, log clean; existing saved apparel still resolves. With the next-version gate on, the garment/recipe is available and craftable in its supported configuration. Survival effect remains explicitly unimplemented until its later spec/replay proves actual immersion protection; no false “fully functional” on test is recorded for wearability alone. Before that later version can ship, compare matched clothed/unclothed accessible-water exposure and verify no dive/travel action exists.

## T15: Switch off the canyon Acoustic Scanner payload

Caller: RM_AcousticPayload_CrackedLands.xml FindMod -> AddModExtension -> independent scanner pulse. Add a real per-payload next-version gate; FindMod is not a setting. Retain scanner engine and unrelated payloads. Deferred veqma/prospecting targets must ultimately read real site data, not plant presence as a fabricated water measurement.

Acceptance test: Fresh default canyon with scanner dependency loaded has no canyon-specific water/fossil/pan/cave targets or prose/letters from this extension, clean log; unrelated scanner service still runs. Enable the payload setting and read its target/quiet-text extension and scanner output on a prepared real target. Mark present proxy-water readings as provisional until T17, never accept them as truthful survey data.

## T16: Switch off the newer decorative fossil case pending retirement decision

Recommendation: retire the case as redundant decoration, independently of the already retired slab/mount. Caller: RM_FossilCase.xml Furniture designationCategory, fossil skeleton costList and minification; generic ship-contribution tooling sees the def. No core mechanic calls it. Gate new build-menu, recipe/trade/loot production but retain the definition and old-save instances. Do not restore earlier display defs.

Acceptance test: Fresh default state has no obtainable case, build designator/craft job or case notification and clean log, even when fossil defs remain loaded. Enable its next-version gate with a test skeleton in inventory and observe the normal build designator and completed case. A debug-spawned case alone is not an availability test.

## T17: Specify the next-version hidden-water visit loop

Promised, not found built: cell-specific water score, dynamic truthful veqma blush, finite prospect job, sell-or-dig survey and flood-refilled slow cistern. Sources: mechanics item §2 and cast bible. FlowWorks drilling is a different built mapwide nonrefilling reserve; existing Cistern/temperature/farm template names are not evidence this loop exists. Default future shape: choose a promising site from honest tells, spend finite work there, report a truthful find or explicit dry result; successful survey identifies this map/site and is consumed once by sell or dig. Water stock/debit/refill goes through FlowWorks. No new wax-loss model. Keep old approval and tier boundaries; no first-version survey bar.

Acceptance test: With defaults on a fresh map there is no survey job/item/cistern-discovery letter or dynamic water claim. Future enabled implementation must distinguish matched wet and dry sites, complete within one visit without waiting for repeated floods, prevent duplicate sale/dig use, produce a real slowly yielding/refilling FlowWorks source and preserve site/item identity after save/reload and leaving/return. Until implemented record the on comparison as unmeasured, not “present”.

## T18: Isolate deferred Swale integration and enforce the campaign discovery lock

Built neighbour: FlowWorks/Source/Swale/RM_Swale.cs; its own ordinary fed/capped enrichment remains untouched. Missing local integration and WorldComponent discovery flag are admitted by the header; no current lock caller was found. Move automatic canyon refill/survey unlock with the survey loop. The current campaign must gate new Swale availability until discovery, even if that discovery belongs to next version; free RM FlowWorks buildability stays normal. Pre-existing legitimate unlock state is preserved, never revoked on an old save. Do not add a new “ignore lock” acceptance knob.

Acceptance test: Fresh default campaign has no canyon-issued Swale unlock, automatic cistern/refill job or discovery letter and cannot newly build the locked Swale; ordinary free-tier FlowWorks can still build its normal Swale, with clean logs. With next-version discovery integration on and T17 implemented, a completed first survey unlocks once at world scope, persists across map change/reload and permits a normal fed Swale; unpaid/failed survey does not. Without T17, the positive discovery comparison is unmeasured, never faked by a direct flag setter. The built external normal Swale is the separately observable present-on service, not evidence of implemented canyon integration.

## T19: Specify a later muttavaq walking-weir adapter

Promised trail edits not found; RM_CompPanSleeper only owns dormancy and XML calls hydraulics unbuilt. Future spec must state finite trail cells, permitted FlowWorks driver operation, water/depth budget, owner/refusal rules and how a giant's repeated path cannot terraform the reach. Default is off; ordinary wading, neutral behaviour, wake and dry sealing remain. No hydrology engine is designed here.

Acceptance test: Default fresh map has no muttavaq-sourced depth/fill writes while wet giants move, clean log. Later enabled adapter must emit traceable bounded engine-owned edits on legal trail cells, honour refusals and preserve floors/old edits across reload; remove the giant mid-action to test cleanup. Until its budget and API contract are supplied there is no truthful positive hydraulic test.

## T20: Specify later unique fossil identity

Raw deep-stratum item exists; per-instance names/one-off identity do not. Default later shape: identity generated once per recovered unique, saved on the item and carried unchanged through stacking prohibition, sale and map transfer; no new quest campaign is implied. Moves with T6–T8, not an excuse to restore retired mounts.

Acceptance test: Default fresh map produces no named unique fossil or associated quest/letter and log clean. Future enabled collectible recovery produces a persistent individually named piece distinct from the static common deep-stratum def; split/merge/sell/save/transfer does not reroll or duplicate its identity. Until implemented positive case unmeasured.

## T21: Bound the later titan-passage cast request

Current composed passage availability unknown; historical inventory names CRACKEDLANDS_TITAN_POPULATE_CRACKS_UNSHAKEN. Read HugeThings' effective supported pool before calling anything missing. Ordinary muttavaq/uttaqar are not evidence of a T2+ passing giant. Future requirement must name a local population/encounter experience and fit the stopped-evictions law; no new species or tier is invented on this pass.

Acceptance test: none, no specific cast/population contract or current effective passage pool has been established; a count of local giants could not distinguish success. First output is a read-only effective-pool/consumer report and a later experience definition. This unknown is outside retained bars, not an owner question.

## T22a: Keep campaign toll-gap integration off for this version

Built outside this mod: StructureInjectionsRUT/Defs/GenStepDefs_Batch3.xml and Templates/toll_gap.txt; construction is not an active canyon visitor/economy contract. Gate only the Cracked Lands encounter integration/registration; do not delete the global template or change frozen world placement. If the canonical fixed save already contains such a site, report it as external existing scenery rather than destroy or repaint it. No new resident Hutt faction or automatic extortion is inferred.

Acceptance test: Fresh default canyon creates no new toll site/buildings/jobs/letters/incidents by this integration and log clean. With its next-version gate on and an explicitly designated local site fixture, the existing template can appear through its actual injector; later visit/negotiation behaviour remains unmeasured until specified. Reading a template file alone does not count as a live toll encounter.

## T22b: Define bloom-market economics only in a later version

Promise: mechanics item §6 post-bloom trade-caravan bias and price factors; implementing canyon consumer not found. Later spec must tie a finite market response to an actual bloom, preserve faction/visitor residency rules and leave base commodity price renormalization free. Default off; not a kept wet-window payoff.

Acceptance test: Default fresh canyon has no bloom-market job/letter/incident/price modifier and clean log. Positive enabled acceptance: none until an explicit later trade trigger and persistence/expiry contract exists; no built-on behaviour is claimed.

## T23: Build the retained canyon landform, front and real refuge contract

Required spec: definition.md “Local landform” and “running contract”. Present implementation is random-seed capped BFS, roof immunity, generic refuge flags and cliff pockets using temporary map-generation elevation. Supply saved bed/bank/station/access data alongside local canyon layout, generate matching marks/anchors/pockets, and connect natural and external ArmFlood to the same front. This is local map work, never planet generation. Invalid layout is a readable defect, not a silent patch fallback. Farmer templates are sited only on upper ground; no new colony faction generator. Natural map acceptance contains no dev control supplier.

Acceptance test: M1 outputs validated against native runtime cell/contact/path data, then B1–B4/B7 primary ranges: complete open cross sections at bends and roofs, upper-bank controls dry, high refuges genuinely reachable, 40 mobile colonists with prompt recall clear ordinary accessible work sites while slow freight has a risk, visitors/trained animals seek and release without colonist job takeover. Save mid-front and resume; missing/invalid layout is reported. No world score/paint/generator runs.

## T24: Build ownership-aware temporary wetness and safe recede

Required spec: definition.md temporary benefit, per-cell source/expiry, exact accepted-soak handoff and terrain owner rules. Reuse ThreeHeightFlora wetUntil where suitable but do not mistake it for built fertility restoration. Align fertile benefit/qirra/irqit nursery clocks; preserve shade ordinary soil without permanent open rich ground. FlowWorks remains sole depth/fill owner; version/source comparisons prevent stale prior-fill restore undoing a pump or player edit. Missing dependable edit ownership is an integration gap to resolve through the supported API, not permission to overwrite.

Acceptance test: T26 state capture distinguishes wet natural ground, dry shaded soil, dry exposed substrate, built surfaces and D=1..4 engine cells through onset/recede/expiry. Same/disjoint/overlap rewet, independent water and edits before/after reload give source-correct expiry, accepted growth soak and preserved work. Exact API outcomes and source records support B5/B7; no fallback terrain writes on Refused/NotOwned engine cells. M2/M3 calibration precedes trust in their predictions.

## T25: Implement and expose real flood impact and immersion danger

Current DamagePawnsInCells/WallHitAmount is one light hit with downed/low-health exclusions. Build a thin contact adapter to existing applicable hazard/vanilla services; if none can supply ordinary-terrain immersion, specify that narrow missing service with the same causal inputs and state reads before implementing. Do not redesign shared hazards or force a personal diving system. Source defines contact/late entry/flight/nonbreather boundaries, damage causes and readable death. Kill probability/damage stats remain tunable and not bars. Update old harmless-hit settings/descriptions.

Acceptance test: Actual engine matched-body replays cover B4 range: front impact, later immersion danger, rescue, vulnerable/downed subjects, landing and true-airborne controls, nonbreather distinction and explicit trait protections. Exposed breathing pawns can die from attributable flood consequences without certain scripted death; timely high-ground controls avoid those causes, corpses/remaining state are readable. Counted damage requests without real injury/exposure are unmeasured. Full default run never switches damage off.

## T26: Build the missing bar readers and model calibration harness

Existing validation.py/northstar_plan.py plain-map fixtures and compressed ArmSoon are regression support, not native acceptance; several required chains are UNMEASURED. Implement M1–M4 with independent oracles and calibration export, a situation replayer, per-cell source/owner/contact reads, per-entity life/flight/cause reads, effective-settings/dependency fingerprint and continuous seasonal capture. Provide ordinary-playback/look records for B1/B2/B6/B8; a counter cannot supply these. Capture a full native map's natural sky/scheduling with retained mechanics effective, mid-water real save/reload and reordered tasks, then extension to day-100 history. No accidental edits to canonical saves. Fixtures restore captured settings/map/time/faction state, not merely defaults; discard the test copy to restore terrain/pawns.

Acceptance test: Each bar's stated primary/control starting conditions are asserted and its cheapest plausible false pass is demonstrably distinguishable; exporter mismatch, missing class, inaudible capture or stale fingerprint reads UNMEASURED. M1–M4 calibration agreement is recorded before model output is called evidence. A whole native trace includes every cycle transition, actual duration/expiry, all kept default feature activity, reload and second order; optional jobs/letters absent, no weather/terminal locks, reset restores the snapshot. The one whole bar B8 remains human-and-state judged.

## T27: Make retained animal lifecycles continuous and readable

Fix RecedeAftermath's aggregate cohortDieTick/append behaviour by nursery-owned deadlines. Trace capture/carry/world exit/carrier death/map loss as actual lifecycle transitions; no exported irqit immortality or silent disposal. Preserve pan identity, visually readable sealed state and wake/dry guards; ordinary sleep is not a vanished/replaced pawn. The current WaterNear terrain-only check must consume the retained wet-source/expiry truth as well: retreating water must not start dry sealing while the pan’s ground still belongs to the wet interval. Independent real water keeps its own wet cause; a flood on another part of the map must not postpone this pan’s dry transition. Expose inspectable expiry/state to normal players, not DevMode only. Keep corpse/butchery/Bones consumers active. Existing spawn caps are checks, not permission for a visually empty hatch.

Acceptance test: M2 cases replayed in real engine show same/overlap/disjoint nursery wetting, local dry death with corpse/aggregate notice, predation, tame, inventory carry and exit/reload without deadline reset or duplication. A wet pan wakes; a dry eligible wild one seals with identity intact; owned/downed/drafted/mental ones do not force-seal. B6 look sees wet movement and later dry signs. M3 reconciles corpse/material/population history under full defaults.

## T28: Apply standing-ruling and settings corrections without adding gameplay

Retain all definitions and restore naming/tier/dependency hygiene for unified Biomes. Inert the legacy planet placement worker/rarity UI as prohibited functionality; **recommend retirement**, never park worldgen in next version or expose a new enable switch. No planet generation is an acceptance action. Correct lowSun/heatKind/heatOffsetC and roof-exposure arrival prose to the shared Direct Sun rule. Full internal rename is already authorised (historical record scope s_renaming points to October 21); preserve canonical references via the existing migration tooling, do not repeat the earlier approval question. This pass changes no saves.

Add persisted effective controls for retained major features, including Peakstorm weather as well as bias, safe master/disable/re-enable transitions and independent default-off extra gates. Keep search/reset/groups/now-versus-new-local-map labels and unsupported existing cross-biome labels. A base/campaign roster must remain visible with special behaviour off; the existing startup flora gate must not be reused to evict passive plants. Optional VEF references must be parse-safe at default load. Dependency declarations/build composition must match the shipped composed target, not stale standalone description. No DLC-absent matrix and no new art approval hold.

Acceptance test: Fresh default and all-off native loads are clean and settings/effective states/persistence/scope labels agree; all kept defaults effective together and T1–T22 extras off. Disable in warning/water/wet stops new harm/production and performs safe ownership-aware cleanup without vanishing living things; re-enable/reload after idle grants a full warning. Static/effective-def reads show no eligible biome-world score or insertion control, no per-biome heat fields, correct tier refs and canonical rename mapping; forbidden worldgen is never re-enabled for a test. Existing refs still resolve. Retirement deletion awaits owner decision.

## T29: Keep ordinary land/life whole after decoupling extras

Retain every current roster member, and fix invented RM ownership/base coverage without an eviction or reliance on canon to fill a free-tier hole. Current WildAnimals patch replaces the base fauna; preserve all effective members while repairing tier ownership/membership. Read and annotate existing multi-homing; do not duplicate a neighbour's species to fill another hole. Preserve real flyer behaviour, walking woolamander, ordinary predation/taming limits, harvest/calls. Keep passive talus natural-wall siting when fossil seeding is off; keep zennaq/luqqim/lithops plants when special output/light is off. Apply Nabbuq's admitted shade law; Veqma keeps its def glow law plus actual shared shade. Until discovery exists, remove false dynamic water promises from ordinary plant/arrival prose. Preserve existing accepted art; a readable pan state is functional presentation, not a new taste gate.

Acceptance test: Effective base/campaign roster memberships are compared before/after with no lost member; all ordinary supply/predation/call roles function and retained fliers have actual flight jobs. Fresh default maps show natural-wall clasps without fossil seams, ordinary unlit luqqim, flammable zennaq without filament and passive donor plants without extra metals; logs clean. M4 shade calibration plus invalid-placement/dieback cases align ordinary shade flora with shared geometry. Whole B6/B8 remains active with growth terminals and no reward extras.

## T30: Bound later uttaqar rock disguise without importing a donor framework

The race XML explicitly flags a donor rock-camouflage/emergence cousin as skipped because its behaviour requires compiled EmergingAnimals classes. Current ordinary uttaqar has no such attachment. Future scope, if pursued: readable rock-to-animal state with persistent identity and an actual emergence sign; no silent pawn spawn/despawn and no duplication of muttavaq's pan role. Keep it off; do not treat the donor header as evidence of a built comp or a reason to add a dependency now.

Acceptance test: Default fresh uttaqar has no rock-emergence job/object/event/letter and no donor-class error, while normal crag life persists. A positive enabled test cannot be claimed until a later state/identity contract and implementation exist; then replay rock/awake/damaged/dead/reload states and account for one persistent pawn. No live-first-version bar depends on this deferred effect.
