# Instruments to specify before further building

These are specifications, not implementations or measurements. Build in the order below. Every real-game comparison is future work on disposable copies of the fixed world, with all kept mechanics on. No model produces planets, chooses a new world seed, or changes biome painting. Local floor geometry may be enumerated without generating another world. Model-only success is never a game PASS. Unknown dependencies are resolved before trusting a model of them.

## M1 - Situation and transition generator

Question: does an ordinary action sequence preserve access, identity, readable consequences and effective settings across every reachable regime?

Informs B1, B3-B8, R1, R4, R7-R9, R11; unknown persistence and rescue_state meetings. First to build because it also establishes whether the missing external contracts exist. Instrument tickets T40, T43-T48.

Inputs/range: enumerate the four named seas, RM versus campaign-enhanced configuration, beach versus floor, new/continued/day-100 saves, 150/250/325/400-square maps, 1/8/40 colonists, all kept gates default/on/off, optional extras default off. Actor states: healthy/downed/dead, wild/tame/native/visitor, spawned/carried/held/off-map, source map versus destination. Action transitions: arrival, unload, harvest, haul, current entry, surge begin/end, sink arrival, rescue start/interruption/death, safe carriage, departure, re-entry, save/load, feature flip; gardener swim/graze/patch/interruption, attempted injury/death/capture/transfer and map unload. Require the same living protected animal with actual completed work, not a flag or death followed by respawn. Enumerate boundary transitions exhaustively; group cosmetic species only after proving identical effective behaviour, not from similar names. Expand any failing group to all affected roster entries.

Assumptions: stable entity ids and actual Scribe/holder observations can be exported; dependencies expose their resolved activation. Keep reachability as an engine input. State graph reduction preserves predicates that bars read. Do not assume a roof is rescue, that a missing pawn is dead, or that a gate stops a running job.

Leaves out: final visual judgement, long-term ecology and frame rendering. It is a generator of test situations, not a simulated substitute for the engine.

Real-game calibration: T40 records ordinary action traces and actual Scribe reload from a saved copy. Match identity, holder ancestry, map/layer, condition state, job completion, signs, gardener protection, actual rim/light changes and effective gates exactly; event dispatch may differ only within one declared polling interval after the same input. Record that interval from resolved implementation, never guess it. Any different death, loss, damage eligibility or reachable destination invalidates the abstraction. Withhold at least transfer-during-carry and rescue-after-reload sequences from development.

Output: reachable-state/transition table, untested boundaries, shortest refusing action sequence per bar and event/state diffs for reload and reversed orders. Include unreachable-state explanations, not just coverage percentages.

Rough size: [guess] tens of thousands of reduced transition cases; basis is the product of actor, map, gate and action boundaries after reachability pruning. Do not generate the full pointless Cartesian product.

Trigger: build first, for the unknown persistence/rescue meetings and unresolved external adapters. Add a case whenever a first live failure exposes a new regime. Do not rerun a full fleet merely because a constant changes.

## M2 - Channel and landing geometry

Question: can reachable current layouts preserve ship arrival, bank work and rescue while the Scald floor also retains a route outside localized boiling pools?

Informs B1, B2, B4-B7, R1-R4, R6-R7; unknown floor_access and channel_field meetings. T41/T44 supply the instrument.

Inputs/range: actual local generator elevation/obstacle data, reservations, field grids and paths; Scald floor substrate and localized boiling-pool masks from B4/T45, with no beach-only margin. Include hull-to-bank and pool-to-retreat connectivity under the same obstacles and hull placements. Enumerate all eight directions, border/corner sources, sink cells, centre/margin/surge bands, overlapping braids, eddies, actual legal hull footprints/rotations and arrival clearances over 150/250/325/400-square maps. Exhaust local collision/boundary patterns; sample full-floor patterns deterministically with recorded local seeds only. Include walls/doors/arrest works, occupied basin cells, terrain replaced after field authoring, native versus visitor, float harness, loose items, settings extrema and every entry phase over scan/process intervals. Check the space between source and destination for diagonal/grab movements, not only destination standability. Sweep ordinary walking speed relative to registration so a brief crossing cannot escape the current entirely.

Assumptions: exported movement and PathGrid predicates match the game, the ship reservation is the actual hull/access reservation rather than a hatch point, and the shared FlowWorks arrest seam is observable. Flow is directed topology, not fluid dynamics. Cycles and dead ends are witnesses to investigate, not automatically acceptable eddies.

Leaves out: full hydrodynamics, a new channel algorithm, art production, worldgen and numerical balance of forage. The instrument judges existing/generated field shapes and reports a failing region; it does not author a new planet.

Real-game calibration: compare lane, direction, bank, sink, terrain, reservation and arrest grids cell for cell on exported ordinary generated floors and withheld obstruction/crossing layouts. Compare actual pawn paths, first warning and displacements against replay within the resolved processing interval, while requiring exact blocked/unblocked, terminal-sink and map-ownership outcomes. A wall crossing, missed harmless centre traversal or hull overlap is never tolerated as timing noise. Bed art visibility requires B5’s live blind boundary sort (habitat identity remains B2); no grid or timing agreement proves that an invisible-water boundary is readable.

Output: overlaid maps of current, safe routes, reserved hull and garden sites; disconnected/unsafe placement classes; worst crossing phase and shortest failure trace per bar; Scald pool overlays and a non-contact hull-to-bank/retreat path, or its blocking witness. Distinguish legitimate source-to-sink danger from an unavoidable trap.

Rough size: [guess] millions of cheap local edge predicates and hundreds of full-floor replays; basis is exhaustive small neighbourhoods combined with whole-map connectivity checks.

Trigger: current floor_access/channel_field unknowns require it before accepting the geometry. Also rebuild relevant sweeps after width, cadence, sink search or landing-clearance constants change twice to move a regression check.

## M3 - Whole sea season model

Question: with every kept mechanic running together, does a season remain a recognisable living habitat with workable visits instead of runaway growth, empty life, inaccessible banks or a stalled simulation?

Informs B3, B5, B7, B8, R3, R7-R9, R11; unknown native_ecology and throughput meetings. Uses M1 transitions, M2 geometry and M4/M5 calibrated contracts, not invented species ecology. T42 owns recording.

Inputs/range: actual resolved defaults, full 250-square maps for each sea, boundary floor sizes from M2, native rosters, predator/prey relations, reproduction/arrival/death, growth/harvest, liquid exposure, ordinary salvage, current/surge timing, temporary well sites, ship visit/action order and all DLC/dependency defaults. Run 15 game days and longer until an actual signature surge cycle occurs; include continuation from day 100. Colony sizes 1/8/40, no harvest through repeated depletion of accessible patches, natural deaths and rescue disruptions, loaded/unloaded visitation. A second branch reverses harvest/haul/shelter/rescue order; a mid-season actual Scribe reload anchors another branch. Years-scale well expiry uses the separate real-tick branch below; it is never relabelled as a short-season natural turnover.

Assumptions: event and spatial budgets come from real records. Preserve competition for ground/light/food, not independent averages that hide a three-way collapse. Rendering may be omitted; simulation ticks, RNG, jobs, pathing, health, hunger/thirst and all timing order remain real. If those cannot be preserved in an offline surrogate, use it only to rank risks and use a headless game trace for the bar.

Leaves out: enjoyment, final art, universal colony self-sufficiency, unshipped extras, alternate planets, real-fluid simulation and faction town economics.

Real-game calibration: record full-map start/mid/end state plus event times from ordinary runs with every kept gate exported. Require exact conservation of tracked pawn/item identities including births, death/remains and holders; exact topology and gate state; exact qualitative bar decisions and event causes. For aggregate growth/population/exposure forecasts, compare a model envelope to withheld real traces. A prediction outside that envelope, or an envelope spanning both acceptable and collapsed regimes, is insufficient: refine it or use the real trace. No unvalidated percentage tolerance certifies the game.

Output: time-series of active life, accessible forage, safe-bank reach, carried/rescued actors, eligible well ground and processing work; causal maps and worst sequence per bar. Label observed values and model forecasts separately. Classify flood as repeated hazards removing the usable visit route; desert as disappearance of viable native life; stall as tasks/transitions that never complete; error storm as recurring errors replacing ordinary progress.

Rough size: [guess] a handful of full-map season traces plus replay branches per declared regime; basis is shared 250-square spatial grids and a finite action schedule. In addition, reserve a continuously simulated full Twilight floor from initialization through a natural well’s waning, closure and replacement. Its minimum extra work is T = max(0, L - A) + P actual simulation ticks, with L the selected well’s recorded initial lifespan, A its initial age and P the observed replacement wait; round up to real update boundaries and include the real reload. L and A are exported from resolved shipped defaults, P cannot be guessed from a prose year. Report T and the elapsed simulation ticks, separate from the season budget. CPU time and checkpoint storage are unknown until the adapter measures throughput; there is no assertion that years are cheap. Record a short real-tick throughput sample before reserving that workload, and change recording/rendering overhead if necessary, never the clock.

Tick-aged save provenance: T42 captures a fresh normally initialized floor, source-save digest, all well ids/ages/lifespans, global tick, RNG and resolved mod/settings fingerprint. Keep that floor loaded with every kept system active. Advance the real game using all actual simulation ticks, skipping rendering only under B8’s compression contract; do not write ages/stages/lifespans/due times, jump game ticks, change lifetime settings or call forced-advance hooks. Automatically record clock/event checkpoints and actual Scribe save digests chained to the initial record. Save when normal MapComponent aging first enters waning; follow through natural closure, pending replacement and opening at a real eligible site, with a genuine mid-branch reload. Compare recorded age increments to executed age-dispatch intervals and original deadlines, not just a matching inspect string. A missing initial record, checkpoint discontinuity, edited age, shortened lifetime or forced event disqualifies the near-boundary save. M1 may still use explicitly staged states to explore transitions, but they cannot certify natural years-scale aging or satisfy this provenance. Calibrate the recorder against known edited-age, skipped-tick and frozen-clock mutants; it must refuse all of them. This branch supplies B7’s later-visit evidence; B7’s ordinary visit only claims tending and inspectable remaining life.

Trigger: build after M1/M2 establish credible adapters; the current whole-system unknowns already trigger it. The separate tick-aged branch is mandatory before passing B7’s later-visit lifecycle claim; a season trace alone is insufficient. Any first whole-bar live failure or twice-retuned growth/current/light constant reopens the affected forecast.

## M4 - Liquid and native physiology replay

Question: does liquid/layer classification charge visitors for the real hazard while keeping natives viable and Scald body water undrinkable?

Informs B3, B4, B6-B8, R4-R8; unknown liquid_exposure meeting, using T40/T43/T45; gardener protection is a declared species exception rather than proof that visitors are immune.

Inputs/range: resolve all named Scald liquid/margin bindings and B4’s beach/floor contact masks, Grey brine, Chill fuel/ice and Twilight fields; air temperature, native/visitor, flesh/mech, age/life stage, equipment, roof/shade geometry, inside/outside oxygenated hull, wet/dry, moving/carried, ordinary drinking/feeding and safe versus unsafe rescue. Sweep terrain/layer transitions, first and sustained contact, still/steam beach state, calm floor, temperature/protection UI extrema and actual native comfort/growth boundaries. Beach retreat is dry shore or the nonpotable cool margin; floor retreat is nonboiling hot substrate or the hull. Export localized boiling-pool cells, verify no beach-only margin on the floor and no contact burn from ordinary floor submersion, and prove a non-contact hull-to-bank route remains. Compare sun at identical geometry, not different biome presets.

Assumptions: the shared engines supply actual damage, temperature, water and atmosphere predicates. Model them from observed reads, without creating a private heat system. Shared dehydration/air code is unavailable in this checkout, so formulae are unknown until resolved.

Leaves out: new protective gear, a replacement physiology engine and the deferred Scald exposure clock. If an engine cannot export reliable health/job causes, no credible pure offline physiology model exists: collect real traces instead of guessing.

Real-game calibration: matched wet/dry visitor/native observations at identical air temperature and sun, with damage source, thirst change, completed drink jobs, oxygen and rescue inputs recorded. Exact match on cell/layer hazard eligibility, absence of contact burns on ordinary hot floor substrate, beach-only margin placement, drinking denial, native-water use and recovery direction; continuous severity/temperature deltas must agree to the exported precision over the recorded tick window. Any difference in survival class invalidates the surrogate.

Output: material/layer/actor decision matrix, cause-separated exposure curves and minimal counterexample to any false native immunity or potable margin.

Rough size: [guess] hundreds of eligibility cases plus short time traces; basis is finite material/actor/gear boundary combinations.

Trigger: the liquid_exposure unknown and known native-thirst/margin contradictions require it before physiological proof; expand on the first contradictory live state.

## M5 - Light habitat and food-chain model

Question: can temporary wells, moving natural light, current exclusions, native plant habitat and harvest/predation leave a viable Twilight garden without any deferred light economy?

Informs B2, B3, B7, B8, R7-R8; unknown twilight_light meeting. T40/T42/T43/T46 provide real state; T47’s deferred holdings provide no kept input.

Inputs/range: exported effective GlowGrid/LightLedger contributions, native plant growth limits and habitat, natural glowers, well stages and finite years-scale ages, site search/pending replacement, current and ship reservations, the actual animal’s rim-grazing/patching jobs and corresponding cover/light changes. Campaign occupancy is excluded, with its setting off in both base and enhanced loads. Sweep opening/standing/waning/closed/pending states, overlapping columns, no eligible replacement, site destruction, gardener injury/removal attempts (refused in this version), tending interruption, save/load and map transfer, normal and depleted native food chains, no/8/40 colonists. Include plants formerly seeded by the extra callbacks: their ordinary placement cannot disappear when those callbacks are stubbed out.

Assumptions: actual local light, not vanilla sky glow alone, controls native growth. A well’s destruction must not erase a neighbour’s contribution. The gardener is a real spawned protected animal, not a narrative flag or off-map surrogate. Rim work preserves an opening’s existing light footprint until its natural expiry; it cannot reset age or make the well permanent. Patching seals spent openings without requiring an optional event. Lifetimes/densities are inputs read from resolved defaults, never passing targets.

Leaves out: suulk, graze debt, cages, sun-spheres, rent, charts, lid-dark crisis, reactive flora charge/wilt and pane hazards. No campaign habitation or roof-collapse/death branch. No promise to model a full food web from prose alone; absent dietary data is an instrument gap.

Real-game calibration: compare exported effective light eligibility maps and well states exactly before/after a true Scribe reload and natural stage boundary; compare actual plant growth/harvest and predator/prey persistence over observed intervals against M3’s withheld envelope procedure. Verify actual animal graze/patch completion and associated rim/light changes; interrupted-job controls must prevent those changes. Same-id protection survives attempted damage/removal and reload, not death plus replacement. Natural stage-boundary calibration uses M3’s tick-aged record and rejects unprovenanceable boundary saves. No inhabitant is required. If sky-growth bypasses local light, revise the adapter before trusting model growth.

Output: eligible-growth/site maps through the lifecycle, failure witnesses for blackouts or no replacement, native food-flow table, and the worst current/light/garden overlap. It changes the choice of well siting/growth rules first, not the bars or the kept roster.

Rough size: [guess] several full-floor light grids per boundary state plus a sparse population graph; basis is reuse of M2/M3 exports.

Trigger: the twilight_light unknown already requires it. Build before declaring the extra decoupling complete; revisit if a site/growth constant is changed twice or the first garden blackout occurs.
