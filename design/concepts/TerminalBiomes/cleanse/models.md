# Instruments to specify before further building

These are specifications, not implementations or measurements. Build in the order below. Every real-game comparison is future work on disposable copies of the fixed world, with all kept mechanics on. No model produces planets, chooses a new world seed, or changes biome painting. Local floor geometry may be enumerated without generating another world. Model-only success is never a game PASS. Unknown dependencies are resolved before trusting a model of them.

## M1 - Situation and transition generator

Question: does an ordinary action sequence preserve access, identity, readable consequences and effective settings across every reachable regime?

Informs B1, B3-B8, R1, R4, R7-R9, R11 and R12; unknown persistence and rescue_state meetings, plus the floor_access probe. First to build because it also establishes whether the missing external contracts exist. Instrument tickets T40, T43-T48.

Inputs/range: enumerate the four named seas, RM versus campaign-enhanced configuration, beach versus floor, new/continued/day-100 saves, 150/250/325/400-square maps, 1/8/40 colonists, all kept gates default/on/off, optional extras default off. Actor states: healthy/downed/dead, wild/tame/native/visitor, spawned/carried/held/off-map, source map versus destination. Action transitions: arrival, unload, harvest, haul, current entry, surge begin/end, sink arrival, rescue start/interruption/death, safe carriage, departure, re-entry, save/load, feature flip; gardener swim/graze/patch/interruption, attempted injury/death/capture/transfer and map unload. Require the same living protected animal with actual completed work, not a flag or death followed by respawn. Enumerate boundary transitions exhaustively; group cosmetic species only after proving identical effective behaviour, not from similar names. Expand any failing group to all affected roster entries.

Well boundary check K11: stage the record just before each lifecycle transition and run the game’s normal update path, including reload and loss/restoration of eligible replacement ground. Compare the resulting stage, light, pending state and replacement site against ordinary T42 season events. Label staged fixtures as checks.

Floor access probe for M2: use ordinary ship departure, let game time pass with no crew on the floor, then return through DivingInteraction. Record map/parent and well ids, well ages and global tick before departure and after arrival, with a reload variant while away. Identify when the dependency retains, freezes, ages or recreates the floor. Compare ages against the observed persistence and dispatch rule. This probes the deployed contract while the B7 countdown is read on an occupied floor.

Assumptions: stable entity ids and actual Scribe/holder observations can be exported; dependencies expose their resolved activation. Keep reachability as an engine input. State graph reduction preserves predicates that bars read. Do not assume a roof is rescue, that a missing pawn is dead, or that a gate stops a running job.

Leaves out: final visual judgement, long-term ecology and frame rendering. It is a generator of test situations, not a simulated substitute for the engine.

Real-game calibration: T40 records ordinary action traces and actual Scribe reload from a saved copy. Match identity, holder ancestry, map/layer, condition state, job completion, signs, gardener protection, actual rim/light changes and effective gates exactly; event dispatch may differ only within one declared polling interval after the same input. Record that interval from resolved implementation, never guess it. Any different death, loss, damage eligibility or reachable destination invalidates the abstraction. Withhold at least transfer-during-carry and rescue-after-reload sequences from development.

Output: reachable-state/transition table, untested boundaries, shortest refusing action sequence per bar and event/state diffs for reload and reversed orders. Include unreachable-state explanations, not just coverage percentages.

Rough size: [guess] tens of thousands of reduced transition cases; basis is the product of actor, map, gate and action boundaries after reachability pruning. Do not generate the full pointless Cartesian product.

Trigger: build first, for the unknown persistence/rescue meetings and unresolved external adapters. Add a case whenever a first live failure exposes a new regime. Do not rerun a full fleet merely because a constant changes.

## M2 - Channel and landing geometry

Question: can reachable current layouts preserve ship arrival, bank work and rescue while the Scald floor also retains a route outside localized boiling pools?

Informs B1, B2, B4-B7, R1-R4, R6-R7; unknown floor_access and channel_field meetings. T41/T44 supply the geometry instrument. Use M1/T40’s departure and re-entry probe for the floor retention and aging part of floor_access.

Inputs/range: actual local generator elevation/obstacle data, reservations, field grids and paths; Scald floor substrate and localized boiling-pool masks from B4/T49, with no beach-only margin. Include the Scald hull-to-working-ground path and pool retreat connectivity under the same obstacles and hull placements. Enumerate all eight directions, border/corner sources, sink cells, centre/margin/surge bands, overlapping braids, eddies, actual legal hull footprints/rotations and arrival clearances over 150/250/325/400-square maps. Exhaust local collision/boundary patterns; sample full-floor patterns deterministically with recorded local seeds only. Include walls/doors/arrest works, occupied basin cells, terrain replaced after field authoring, native versus visitor, float harness, loose items, settings extrema and every entry phase over scan/process intervals. Check the space between source and destination for diagonal/grab movements, not only destination standability. Sweep ordinary walking speed relative to registration so a brief crossing cannot escape the current entirely.

Assumptions: exported movement and PathGrid predicates match the game, the ship reservation is the actual hull/access reservation rather than a hatch point, and the shared FlowWorks arrest seam is observable. Flow is directed topology, not fluid dynamics. Cycles and dead ends are witnesses to investigate, not automatically acceptable eddies.

Leaves out: full hydrodynamics, a new channel algorithm, art production, worldgen and numerical balance of forage. The instrument judges existing/generated field shapes and reports a failing region; it does not author a new planet.

Real-game calibration: compare lane, direction, bank, sink, terrain, reservation and arrest grids cell for cell on exported ordinary generated floors and withheld obstruction/crossing layouts. Compare actual pawn paths, first warning and displacements against replay within the resolved processing interval, while requiring exact blocked/unblocked, terminal-sink and map-ownership outcomes. A wall crossing, missed harmless centre traversal or hull overlap is never tolerated as timing noise. Bed art visibility requires B5’s live blind boundary sort (habitat identity remains B2); no grid or timing agreement proves that an invisible-water boundary is readable.

Output: overlaid maps of current, safe routes, reserved hull and garden sites; disconnected/unsafe placement classes; worst crossing phase and shortest failure trace per bar; Scald pool overlays, pool retreat and pool-free hull-to-working-ground routes or their blocking witnesses. Distinguish legitimate source-to-sink danger from an unavoidable trap.

Rough size: [guess] millions of cheap local edge predicates and hundreds of full-floor replays; basis is exhaustive small neighbourhoods combined with whole-map connectivity checks.

Trigger: current floor_access/channel_field unknowns require it before accepting the geometry. Also rebuild relevant sweeps after width, cadence, sink search or landing-clearance constants change twice to move a regression check.

## M3 - Whole sea season model

Question: with every kept mechanic running together, does a season remain a recognisable living habitat with workable visits instead of runaway growth, empty life, inaccessible banks or a stalled simulation?

Informs B3, B5, B7, B8, R3, R7-R9, R11; unknown native_ecology and throughput meetings. Uses M1 transitions, M2 geometry and M4/M5 calibrated contracts, not invented species ecology. T42 owns recording.

Inputs/range: actual resolved defaults, full 250-square maps for each sea, boundary floor sizes from M2, native rosters, predator/prey relations, reproduction/arrival/death, growth/harvest, liquid exposure, ordinary salvage, current/surge timing, temporary well sites, ship visit/action order and all DLC/dependency defaults. Run 15 game days and longer until an actual signature surge cycle occurs. Include continuation from day 100. Colony sizes 1/8/40, no harvest through repeated depletion of accessible patches, natural deaths and rescue disruptions, loaded/unloaded visitation. A second branch reverses harvest/haul/shelter/rescue order and a mid-season Scribe reload anchors another branch. Keep the crew working on the Twilight floor through natural well turnover at the R7 week-scale default. Observe new garden light with ordinary current, forage and predation running.

Assumptions: event and spatial budgets come from real records. Preserve competition for ground/light/food, not independent averages that hide a three-way collapse. Rendering may be omitted; simulation ticks, RNG, jobs, pathing, health, hunger/thirst and all timing order remain real. If those cannot be preserved in an offline surrogate, use it only to rank risks and use a headless game trace for the bar.

Leaves out: enjoyment, final art, universal colony self-sufficiency, unshipped extras, alternate planets, real-fluid simulation and faction town economics.

Real-game calibration: record full-map start/mid/end state plus event times from ordinary runs with every kept gate exported. Require exact conservation of tracked pawn/item identities including births, death/remains and holders; exact topology and gate state; exact qualitative bar decisions and event causes. For aggregate growth/population/exposure forecasts, compare a model envelope to withheld real traces. A prediction outside that envelope, or an envelope spanning both acceptable and collapsed regimes, is insufficient: refine it or use the real trace. No unvalidated percentage tolerance certifies the game.

Output: time-series of active life, accessible forage, safe-bank reach, carried/rescued actors, eligible well ground and processing work; causal maps and worst sequence per bar. Label observed values and model forecasts separately. Classify flood as repeated hazards removing the usable visit route; desert as disappearance of viable native life; stall as tasks/transitions that never complete; error storm as recurring errors replacing ordinary progress.

Rough size: [guess] a handful of full-map season traces plus replay branches per declared regime. The estimate uses shared 250-square grids and a finite action schedule. Record throughput so the T42 recorder can budget the actual tick workload.

Twilight season evidence: T42 records the normally initialized floor’s map and well ids, initial ages and lifespans, RNG, resolved mod/settings fingerprint and global tick. Trace real age-dispatch ticks, natural waning, closure, pending replacement and opening, with a mid-season Scribe reload. Use the record to link the new site, its light and its reachability to natural expiry under unchanged lifetimes. A missing initial record, clock discontinuity or forced advance invalidates the natural turnover reading. Calibrate against edited-age, skipped-tick and frozen-clock controls. M1 stages boundary cases independently for K11.

Trigger: build after M1/M2 establish credible adapters. The current whole-system unknowns already trigger it. Any first whole-bar live failure or twice-retuned growth/current/light constant reopens the affected forecast.

## M4 - Liquid and native physiology replay

Question: does liquid/layer classification charge visitors for the real hazard while keeping natives viable and Scald body water undrinkable?

Informs B3, B4, B6-B8, R4-R8; unknown liquid_exposure meeting, using T40/T43/T45; gardener protection is a declared species exception rather than proof that visitors are immune.

Inputs/range: resolve all named Scald liquid/margin bindings and B4’s beach/floor contact masks, Grey brine, Chill fuel/ice and Twilight fields; air temperature, native/visitor, flesh/mech, age/life stage, equipment, roof/shade geometry, inside/outside oxygenated hull, wet/dry, moving/carried, ordinary drinking/feeding and safe versus unsafe rescue. Sweep terrain/layer transitions, first and sustained contact, still/steam beach state, calm floor, temperature/protection UI extrema and actual native comfort/growth boundaries. Beach retreat is dry shore or the nonpotable cool margin; floor retreat is nonboiling hot substrate or the hull. Export localized boiling-pool cells, verify no beach-only margin on the floor and no contact burn from ordinary floor submersion, and prove a pool-free route from the hull to Scald working ground. Compare sun at identical geometry, not different biome presets.

Assumptions: the shared engines supply actual damage, temperature, water and atmosphere predicates. Model them from observed reads, without creating a private heat system. Shared dehydration/air code is unavailable in this checkout, so formulae are unknown until resolved.

Leaves out: new protective gear, a replacement physiology engine and the deferred Scald exposure clock. If an engine cannot export reliable health/job causes, no credible pure offline physiology model exists: collect real traces instead of guessing.

Real-game calibration: matched wet/dry visitor/native observations at identical air temperature and sun, with damage source, thirst change, completed drink jobs, oxygen and rescue inputs recorded. Exact match on cell/layer hazard eligibility, absence of contact burns on ordinary hot floor substrate, beach-only margin placement, drinking denial, native-water use and recovery direction; continuous severity/temperature deltas must agree to the exported precision over the recorded tick window. Any difference in survival class invalidates the surrogate.

Output: material/layer/actor decision matrix, cause-separated exposure curves and minimal counterexample to any false native immunity or potable margin.

Rough size: [guess] hundreds of eligibility cases plus short time traces; basis is finite material/actor/gear boundary combinations.

Trigger: the liquid_exposure unknown and known native-thirst/margin contradictions require it before physiological proof; expand on the first contradictory live state.

## M5 - Light habitat and food-chain model

Question: can temporary wells, moving natural light, current exclusions, native plant habitat and harvest/predation leave a viable Twilight garden without any deferred light economy?

Informs B2, B3, B7, B8, R7-R8 and R12; unknown twilight_light meeting. T40/T42/T43/T46 provide real state; T47’s deferred holdings provide no kept input.

Inputs/range: exported effective GlowGrid/LightLedger contributions, native plant growth limits and habitat, natural glowers, well stages and finite ages at the R7 cadence, site search/pending replacement, current and ship reservations, and the actual animal’s grazing and patching jobs. Sweep clear and overgrown rims, elapsed standing time around the K12 interval, the reduced radius, restored light and overlapping columns. Campaign occupancy is excluded, with its setting off in both base and enhanced loads. Sweep opening/standing/waning/closed/pending states, no eligible replacement, site destruction, gardener injury/removal attempts (refused in this version), tending interruption, save/load and map transfer, normal and depleted native food chains, no/8/40 colonists. Include plants formerly seeded by the extra callbacks: their ordinary placement cannot disappear when those callbacks are stubbed out.

Assumptions: actual local light, not vanilla sky glow alone, controls native growth. A well’s destruction must not erase a neighbour’s contribution. The gardener is a real spawned protected animal, not a narrative flag or off-map surrogate. R12 applies the rim factor to only the affected well’s current-stage radius. A graze removes that factor while the age/expiry schedule proceeds independently. Patching seals spent openings without requiring an optional event. Lifetimes/densities are inputs read from resolved defaults, never passing targets.

Leaves out: suulk, graze debt, cages, sun-spheres, rent, charts, lid-dark crisis, reactive flora charge/wilt and pane hazards. No campaign habitation or roof-collapse/death branch. No promise to model a full food web from prose alone; absent dietary data is an instrument gap.

Real-game calibration: compare exported effective light eligibility maps and well states exactly before and after a true Scribe reload and natural stage boundary. Compare plant growth/harvest and predator/prey persistence against M3’s withheld envelope procedure. At the same well stage, verify K12’s radius reduction at overgrowth and restoration on a completed graze, with neighbouring contributions and the expiry schedule unchanged. Verify natural closure drops that well’s light and a completed patch seals its spent rim. Interrupted-job controls must leave the intended rim work undone. Same-id protection survives attempted damage/removal and reload, not death plus replacement. Natural stage-boundary calibration uses M3’s season record. No inhabitant is required. If sky-growth bypasses local light, revise the adapter before trusting model growth.

Output: eligible-growth/site maps through the lifecycle, failure witnesses for blackouts or no replacement, native food-flow table, and the worst current/light/garden overlap. It changes the choice of well siting/growth rules first, not the bars or the kept roster.

Rough size: [guess] several full-floor light grids per boundary state plus a sparse population graph; basis is reuse of M2/M3 exports.

Trigger: the twilight_light unknown already requires it. Build before declaring the extra decoupling complete; revisit if a site/growth constant is changed twice or the first garden blackout occurs.
