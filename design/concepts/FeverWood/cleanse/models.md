# Instruments specified, not built

These are predictions until calibrated against the actual game. Existing production kernels and mock selftests are useful components, not measurements of gameplay. Build order below follows the unresolved meetings in bars.json. Every run records input fingerprints, range coverage, unsupported states and smallest counterexamples. A missing export or absent integration yields unknown, never zero. Tickets name implementation; this pass creates no executable models.

## Situations and water transitions

Question: can the actual water authorities, local memory, rescue obligations and save/settings transitions produce the promised outcomes together?

Informs: shore, memory, response, warning and whole; R_AUTHORITY, R_RESCUE, R_MEMORY, R_RELIEF, R_SCHEDULE, R_WARNING, R_SCOPE, R_SETTINGS and R_PROOF. Settles the water, rescue and save unknown meetings; supplies transition inputs to the geometry and timing models.

Assumptions: pool topology and pawn IDs are exported independently; game tick order, damage/death callback order and enabled service precedence are known; a setting-off transition is an explicit action, not equivalent to combat relief. Use production kernel functions where available, but adapters and saves are tested separately.

Inputs/range: enumerate active/absent/defeated adult; local/map quiet boundaries; neutral/angered pools; ordinary, sentinel and eye presence; no-free-cell/partial/free spawn capacity; eligible native/non-native, player/tame/wild, dead/downed/carried/despawned/world-transferred victims; repeated snare and simultaneous victim events; blocked/successful deposit; below/at/above withdrawal and rescue deadlines; fatal eye/porter callbacks; save/load and disable/re-enable at each pending transition. Include connected pools merging/splitting only under terrain edits the loaded game allows. Group states only when eligibility, timer, owner and terminal effects are identical; retain a witness for every group. Generate each bar’s rejecting cases as mutation controls.

Leaves out: path-time prediction (geometry model), rendered audio masking and hush (the separate Test Pilot PCM capture/comparison), unsupported campaign/provider implementation not actually loaded, intentional captive/gift/chemical behavior with extras off. It still checks those dormant callbacks cannot influence the core. No new engine or planet generator.

Real-game calibration before belief: T_OBSERVE exports actual pool masks/IDs, thing IDs, effective reasons, deadlines, pressure, relief and transactions before/after the identical event sequence; compare to saved records across reload. Require exact target membership, terminal outcomes and once-only ledger entries, plus exact absolute deadlines and counters at the recorded game tick. Exempt only documented rounding at a known scheduler boundary, bounded by one observed owning-service scan interval; never permit it to change success versus expiry. A transition-order disagreement invalidates the model until its assumptions or implementation are repaired.

Produces: a state-transition table and minimal failing event sequence per bar, dead/cyclic obligations, unauthorized extra-to-core calls, and a coverage manifest of enumerated equivalence regions. Checks are generated from the bar pictures, not a duplicate of implementation outputs. Counterexamples retain seeds, order and initial exports.

Rough size: [guess] a small production-kernel harness with hundreds of representative state classes and thousands of event sequences; pairwise reduction followed by targeted three-way expansion, approximately two to four developer days including adapters. Do not explode arbitrary irrelevant flags into meaningless combinatorics.

Trigger: build first because water/rescue/save meetings are unknown and current Tenant serialization/authority demonstrably differs from the proposed contract; also rebuild when an owning timer/gate changes twice to satisfy a regression check. Ticket: T_MODEL_SITUATIONS.

## Land and rescue geometry

Question: throughout legal local-map placements, can useful branch work and an alongside companion coexist with pool-scaled reach and ordinary foundations?

Informs: land, work, shore, life and whole; R_TERRAIN, R_HEIGHT, R_REACH, R_RESCUE, R_LIFE and R_SUN. Settles terrain/routes unknown meetings and the geometry part of rescue; supplies work-distance distributions to the season model.

Assumptions: exported terrain affordances, solid edifices, roofs/tree shade, path costs and pawn movement/pickup work match the actual loaded game. Plan-view height only; no independent climbing graph. The proposed r(A) is an attackable initial rule, not a measured reach law or a bar.

Inputs/range: local authored maps 150..400 cells per side, boundary samples and actual used sizes; the current complete bole count/radius, spacing, edge margin and causeway pass width/length/bearing/turn distributions parsed from defs. Enumerate translated/rotated compact, long, concave, diagonal-touching, bottleneck and overlapping pool/route situations; all neighbour bearings and every legal within-profile size, with witnesses at every reach, foundation and path boundary. Sweep all valid worker/companion/target cells within each representative exported map, loads/speeds/pickup times from actual current pawn stats and route congestion from initial through 40-colonist layouts. Use exact shortest-path or game-equivalent path costs, with walls/doors/raised terrain distinctions. Include zero/free/partial limb placement capacity and pool-edge occupancy; generated routes may not overwrite pools, trunks or unsupported ground. If a supported actual fixed-world map lies outside the declared interval, extend before claiming coverage.

Leaves out: random hostility frequency, human art interpretation, arbitrary modded map sizes not used or declared supported, player-created impossible enclosures and unsupported vertical layers. It is a local geometry enumerator reading fixed-world maps, not a worldgen sweep.

Real-game calibration before belief: T_LAND independently exports final terrain, buildings and affordances after the actual existing placement steps; compare the model mask/allowed foundation/path connectivity exactly. On selected shortest, diagonal, bottleneck, obstructed, laden and 40-pawn congested routes compare actual normal job path and carry-start tick. Require exact traversability/buildability/strike membership and agreement of the pre-seizure Show water reach UI’s displayed cells/status with that membership; inspect the actual ordinary-zoom capture independently so an invisible or stale overlay is not certified by the same radius export; movement-plus-pickup predictions must lie within the independently measured scheduler/work uncertainty, declared before comparison. Any error which changes nearby rescue success or crosses a reach boundary invalidates the relevant region. Tree-shade classifications must agree with the shared Direct Sun read, without a local substitute.

Produces: overlays of useful work circuits, supported construction, danger envelopes and rescue slack, a table of uncovered/counterexample geometry regions, and worst placement/bearing/size per affected bar. Report usable route components, not an attractive average. Output changes whether to adjust the reach curve, land placement overlap/spacing or the job fixture, never whether to add magic height immunity.

Rough size: [guess] one grid/path adapter plus enumerator, two to five developer days; thousands of local boundary witnesses with exhaustive per-cell sweeps on representative final maps. Use symmetry classes and preserve edge cases instead of pretending random examples enumerate all geometry.

Trigger: terrain/routes unknown now; later a normal route/rescue failure or the reach/placement constants changed twice. Ticket: T_MODEL_GEOMETRY.

## Crown and encounter timing

Question: do living-call overlap, finite limb presence and encounter scheduling leave a readable warning and reachable eye opportunity without permanent hush?

Informs: warning, shore, response and whole; R_WARNING, R_REACH, R_SCHEDULE, R_AUTHORITY and R_SCOPE. The geometry model supplies the boundary mask; this model checks inspection status across quiet/defeat and warning transitions, while T_WARNING reads the actual rendered sign. Settles the warning unknown meeting and checks the season’s escalation/hush tails.

Assumptions: individual birds have independent identifiable emitters, actual call duration/interval distributions and positions; named hush reasons are the only veto; encounter scheduling uses the production unit and cadence. No synthesized chorus-level stat. The separate Test Pilot T_WARNING mixed-PCM analysis decides masking/hush against C_SOUND; emitter timing alone cannot.

Inputs/range: absent/sparse/crowded wild and tame flock; staggered calls at legal positions and listener at flock/home/shore; overlapping sentinel and shared warning reasons through spawn, linger, retreat, fatal removal, map switch and reload. Scheduler opportunities at no pool, insufficient and qualifying pool sizes/pressure; capacities full/free, ordinary opportunities, quiet expiry and permanent defeat. Read exact configured MTB/check unit, ordinary/eye weights/chance, cap, linger and call ranges. Use normal bounds plus immediate-boundary and long-run day-100 states. Compare live traffic with no-player-action control; do not force the sky clear or turn growth off.

Leaves out: subjective annoyance, artistic sound quality and unsupported campaign triggers. Actual audio masking/hush is read separately through T_WARNING capture/comparison, not inferred from this timing model. No guarantee that rare events occur in a particular season, nor a hidden mercy timer or maturity gate.

Real-game calibration before belief: T_WARNING/T_WATER exports emitter start/stop, reason add/remove, actual tick/RNG outcome, spawn/withdrawal, capacity and eye-eligibility logs. Require exact reason lifetimes, pre-seizure inspection status and spawn eligibility at deterministic replay ticks; statistical call/emergence waiting-time distribution must cover runtime observations in predeclared 95% prediction bands with no unaccounted indefinitely-held reason. Then the Test Pilot running T_WARNING captures actual rendered output as lossless PCM for matched living-flock absent/present and warning inactive/active replays at unchanged camera/bed/mixer volumes. Retain raw streams and synchronized events, compare call-band loudness to the matched bed and check actual work-bed hush/restoration under C_SOUND, with machinery/weather as an independent reference. Missing/uncalibrated capture is unknown; source-event counts and detectable-but-masked calls cannot pass. Failure of audible separation changes sound mix/call scheduling, not the source of the calls or the warning bar.

Produces: emitter/reason timeline, probability-of-opportunity curves across declared play horizons, worst hush episode and counterexample trace. Shows the decision between modifying linger/cap/call spacing/eligibility and adding unwarranted protection. No numerical probability becomes a bar.

Rough size: [guess] small timeline/state harness plus production-clock sampling, one to three developer days. Existing RM_PoolKernel/SelfTest helpers cover only parts and cannot certify emitter wiring or actual scheduler units.

Trigger: warning meeting unknown now; also permanent silence, unreachable eye, first captured-audio comparison failure or a call/linger/MTB constant changed twice. Ticket: T_MODEL_TIMING.
## Coupled colony season

Question: with all kept systems running, does ordinary branch-colony provisioning continue across water interruptions, shared growth, fear and population turnover?

Informs: whole, work, life, memory, response and land; all rules, especially R_NECTAR, R_SCHEDULE, R_RELIEF and R_SCOPE. Settles ecology/economy unknown meetings and feeds back possible terrain, route and warning regime failures. It consumes the validated situations and geometry models rather than assuming those conflicts away.

Assumptions: fixed exported map, actual normal job throughput, growth/aging/spoilage, diet and wild-population rules, local fear recovery, water opportunities and casualty accounting. Commodity conversion uses only present ordinary harvest/gather/butchery; no tank, treatment, wreck income, synthetic food supply or rite. Global growth tops remain the owning engine’s behavior, including silent/nonlethal giant handling; surface reroute/glut extras are absent.

Inputs/range: full-map 15-game-day season and paired day-100 continuation; initial through 40 colonists, their real associated animal populations, hungry/sated starting cohorts, sparse/dense plants at valid terrain, mature and beginning crown gardens, herd exposure/shelter and local threats, actual unlocked clear/fog/overcast/dry-thunderstorm distribution at authored climate. Sweep all supported map/plant/growth defaults and their exposed normal tuning bounds from loaded defs; use the geometry model’s worst cases and explicit reach thresholds. Vary companion allocation, shore-before-harvest versus harvest-before-shore, attack/no-attack of porter, relief/defeat histories and ordinary raid timing. Independent RNG streams and fixed replay seeds separate task-order effects from random weather differences. Record low/high pressure tails, not just a mean. Ranges outside readable supported service bounds stay unknown.

Leaves out: prediction of player enjoyment, bespoke raid/lure/hive/chemical/captive economies, real-time rendering performance and campaign events with unavailable source. Pure discrete-event approximations cannot certify actual RimWorld reservation/death/save callbacks; those require the calibration trace. No credible offline model alone can prove the full whole bar; it narrows the runtime experiments.

Real-game calibration before belief: T_SEASON takes hourly and event-boundary independent grid/population/stock/job/water ledgers on a full map with all kept defaults. Compare production, eaten/spoiled resources, losses, completed trips and pending obligations over a day and then a season. Conserved resources and deterministic transitions must reconcile exactly apart from explicitly recorded game rounding. For stochastic aggregates require the actual measurements inside precomputed 95% prediction intervals over replicate seeds, with no systematic drift in plant cover, food availability or completed work; choose replicate count from variance, not a passed screenshot. A wrong sign of resource/population trend or a model missing any actual flood, depletion or job stall invalidates it even if means agree. Extend through day 100 before claiming long-run stability.

Produces: map overlays/time series of food stock and habitat, completed/blocked work, herd calm, animal hunger/thirst/loss, water attacks/relief, reward backlog, hush duty and colony response capacity; worst regime and bar-linked counterexample with actual versus predicted results. Output changes rates, caps, spawn/placement rules or job costs. These are engineering retunes, not new bar thresholds.

Rough size: [guess] moderate coupled event simulation with measured runtime throughput inputs, three to seven developer days; retain a real-game tick-preserving runner for validation. Wall-clock compression may remove rendering/waits, never needs, weather, growth, RNG events, jobs or damage ticks.

Trigger: ecology/economy unknown now, any first whole-bar failure, or a production/growth/pressure constant changed twice to move a check. Ticket: T_MODEL_SEASON.

