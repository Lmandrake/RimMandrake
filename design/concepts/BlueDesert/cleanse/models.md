# Instruments to specify now, build later

These are designs, not simulation results or measurements of the running game. Ordering is build priority: enumerate the states, then expose the full-map loop before spending time tuning a postcard. Each calibration binds game version, assemblies/source, composed patched defs, settings, dependencies, save and geometry. A missing read is UNMEASURED, not zero or agreement. No model generates or edits a planet. Use captured local-map geometry and explicit scenario overlays only.

## Situation and lifecycle generator

Question: Does any reachable birth, death, ingestion, warming, work, storage, settings or reload transition bypass the retained experience?

Informs B2, B4–B8; R1–R4 and R6–R11; organics/native_triggers/conversion/departure meetings and the boundary conditions for every unknown meeting. This is the mandatory generator of situations, not a collection of hand-picked examples.

Inputs/range: enumerate inline and campaign-added native identities, plant/animal/corpse/wax/roe/refined native Chemfuel/consumer products, generated/newborn and juvenile/adult, healthy/damaged/downed/dead, native/foreign ingestion, mapped/held/caravan/container, spawn/despawn/transport/edge exit/map teardown; every attack family named by B5; cut/harvest/damage modes; cold→warm→warning→wick→blast and cool/off interruptions; split/merge at every reserve/progress stage; master, retained major toggles and each extra default-off/on in separate switch regressions. Sweep threshold neighbors using loaded values ± one tick/quantum, every plant Long-tick phase and ordinary tick/rare phase. Add adjacent transition pairs and three-event sequences (damage→death→butcher; warm→split→reload; nearly warned wax→refine→mix with imported Chemfuel→refuel→reload→warm internal unburned fuel; drift→burial→off; hauling→warm→map return). For long paths use reachability deduplication and explicit causal-state coverage, not all arbitrary switch combinations.

Leaves out: visual taste, engine timing/performance claims, population equilibrium and physics not represented by observed states. Optional future behavior is only an isolation arm, never necessary to a retained bar.

Assumptions: exported state is sufficient to distinguish progress, cause and identity; adapters implement documented Core callbacks. Before believing it, compare a real action trace for every distinct handler/transition equivalence class, including a newborn, generated corpse, held stack, split/merge and midpoint reload. Required agreement: identical classified transition, product identity, source causal event and saved hazard debt; exact integer events/tick ordering at callback boundaries, with temperature floats within exported reader resolution. For refining, compare native-source quantity, inherited wax safe limit and warning/ruin/wick debt through the ordinary BiofuelRefinery bill, interrupted work, mixing and actual fuel consumption. Include an unrelated imported-Chemfuel control. A missing callback or field invalidates that branch, not the game. Deliberately delete a charge/serialization/gate in a controlled later harness mutation and require the generated case to fail.

Output: transition graph and witness sequence per violated bar, unreachable-state ledger, coverage by cause rather than a “field count,” machine-readable rows with start/control/reset evidence. Size [guess]: tens of thousands of deduplicated cases, a small command-line runner plus trace adapter; existing RM_BlueKernel and fake-game suite are starting material, not validated substitutes for the callbacks.

Trigger: build immediately for T27 before accepting lifecycle fixes. Extend when a new source/consumer/handler is added or a bar's first live failure reveals an omitted state. Choice changed by output: fix the adapter/rule causing a bypass, or remove an extra dependency; never weaken the organic/flight/containment bar to match a fake-game model.

## Whole-season coupled map

Question: Can the living ice, native death charges, weather, resource work and cold hold coexist over a season without a self-erasing food web or permanent stall?

Informs B2–B8 and all retained rules, especially the ecology unknown meeting; provides temporal inputs to heat, weather and propagation unknowns. This is the mandatory whole-mod model.

Inputs/range: captured full maps of 200/250/300 cells per side with natural distributions, empty/ordinary/dense plant-prey initial states, site placements, local room/door network and colony sizes 1/12/40; 15 in-game days of actual-rate state updates. Cold ambient traces -60 to -19 C, interior heaters, ordinary weather rotations and consecutive storms; both B8 action orders, a repairable blackout and a local accidental ignition. Restart from a day-100 baseline and compare midpoint reload versus uninterrupted continuation. Use recorded random streams or explicit ensembles on these local inputs; never a world seed/biome placement sweep. Inventory every external action and every resource, death, departure, birth and spawn source.

Assumptions: growth, food demand, predation target selection, native release, heat and weather clocks can be replayed or bounded by observed game transitions. Use exported engine traces rather than inventing a replacement hunting probability. Where Core AI cannot be credibly replayed, keep it as recorded input and report conditional results, then require multiple actual full-map traces before claiming stability. This is the main limitation: an offline ecology with guessed AI is not credible evidence of autonomous stability.

Leaves out: artistic judgment and raid/storyteller outcomes beyond explicitly injected challenge inputs. It does not guarantee survival under deliberate global heating. It never rescues the colony or repopulates for convenience.

Calibration: against the same save's real snapshots, compare cold no-challenge growth/feeding, natural predation episodes, storm accumulation/erosion, a controlled chain and a blackout before trusting a season forecast. Agreement good enough: exact event identities and mass ledger for deterministic replay, same causal connected destruction region for recorded initiators; population/temperature series must remain inside an explicitly reported envelope derived from repeated same-state game traces, with no contradictory stall, extinction, or warning ordering. No arbitrary percentage tolerance can conceal a different classification. If the game falls outside the envelope, the model is uncalibrated and the bar remains unmeasured.

Output: time series of food/plant/animal/cargo/ice state, causal blast maps, longest work stalls, leave/death explanations and worst witness per bar; report flood (unbounded reseeding/products), desert (routine ecological extinction), stall (no work/repair path), and error storm (recurring exceptions) separately. Size [guess]: medium runner/trace exporter, captured-map batches and stored seasonal histories; no new game engine.

Trigger: first substantive instrument after the generator, before accepting any density/blast/growth tuning. Rebuild after a constant is changed twice to move a check, or the first B8 live failure. Choice changed: attack R2/R3/R6 implementation/timing/propagation rules and existing ecology tuning first, not the player's whole-bar promise. If no feasible regime remains, report that conflict on owner pages.

## Thermal reserve ledger

Question: Can loose ice alone keep a prepared closed hold cold far beyond an ordinary cooling repair while preserving finite heat and water accounting?

Informs B3/B4/B6–B8; R1–R4, R9–R11; heat unknown meeting and conversions. Inputs: loaded item mass, heat-exchange rate and phase reserve, real room heat coefficients, roofs, room sizes 9/36/144 cells, open/closed/traffic doors, 0/ordinary/40-colonist traffic, ambient -60 through +40 C, heater and cooler rates, loose-ice reserves 0 through loaded stack limits, multiple stacks, held/container transitions and ordinary conversion routes. Sweep reserve exhaustion, warming, notification, ruin/wick thresholds and load/split/merge immediately either side of every transition. Include actual ordinary cooler faults, healthy available workers, reachable materials and worker route/repair durations from drift/fog path traces. Compare full prepared reserves in closed rooms under declared ordinary positive heat loads. Continue unrepaired arms well beyond the matched repair completion. Partial/empty reserves, open-door bursts and excessive heat remain stress witnesses. Include cold-wax/refined-native-Chemfuel product states at the loaded safe limit, currently -1 C from RM_ColdWax.xml, and warm bill interruptions.

Assumptions: sensible/latent accounting can be translated into the same energy units as vanilla room heat. Do not import laboratory water constants directly into arbitrary Core units without calibration. Cooling is limited by finite exchange and reserve, rather than setting room temperature. Melt output represents the same consumed water mass; re-freezing, if a shared consumer supports it, requires accounted heat removal.

Leaves out: molecular thermodynamics, unbounded outdoor climate control, invented ship engine physics and clinical survival. A sealed but unmapped container needs a documented retained-state contract; absent such data its branch is UNMEASURED.

Calibration: real matched enclosed rooms with positive measured heat input and no working cooler/rack; log air temperature, ice mass/residual reserve, phase, door events and organic warning progress. Compare ice/no-ice, closed/traffic doors, partial/full reserve and a save/reload/split case. Require heat/mass balance within exported quantization, same warning/ice-exhaustion ordering, and temperature trajectories within a measured tick/reader-resolution envelope; a colder initial room or active cooler invalidates comparison. Actual ordinary repair must finish while the prepared hold remains cold with substantial reserve. Its matched unpowered arm must continue cold holding far beyond that completion under the same heat input. Merely beating repair fails B6. Report trajectories through eventual finite reserve exhaustion and inherited warnings on refined native fuel. Never assert a fixed duration from the old rack's coldPerBlock.

Output: paired temperature/reserve/progress curves, energy and mass closure table, feasible prepared-reserve/repair regimes and counterexamples. Size [guess]: small numerical ledger with a game-trace adapter, dozens of deterministic trajectories per room class.

Trigger: T30 before implementing/accepting T17; also first unexpected reserve or blackout bar failure. Choice changed: exchange/reserve representation and R4 assumptions, routing/storage layout guidance, or a shared consumer adapter. Never solve it by bringing the superseded rack back into B6.

## Containment geometry sweep

Question: Can real fuel geometry and ordinary work leave an actually reachable retreat that interrupts the chain under the intended ignition range?

Informs B4–B8, R1–R3/R6/R10/R11, propagation unknown meeting and routes/ecology meetings. Inputs: loaded blast radii, heat/fire propagation and LOS behavior, captured terrain/rooms, every plant/body/product footprint and supported blast origin, each gap at radius/cell-rounding boundaries, wall/door/edge/corner rotations, full-map components and local worker routes. Include animals moving into gaps, dying prey, carried/dropped stacks, fog/drift path costs and naturally regrowing cells. Compare prepared/unprepared copies with same initiator and work demand; sweep all legal translations/rotations of small motifs, plus full captured layouts rather than only a row of plants.

Assumptions: the actual engine's blast/heat reach can be exported/replayed; a radius-only graph without LOS, heat and secondary sources is insufficient. Treat animal motion traces as inputs or worst-case reachable bridges, not invented static guarantees. Pre-ignition warning latency and worker response come from calibrated traces.

Leaves out: global balance and artistic readability. Worst-case reachable bridges diagnose a failed preparation boundary, not an obligation to survive every conceivable animal invasion of a gap.

Calibration: actual game ignition traces for empty gap, obstacle corner, body/wax bridge, overlapping blasts, map edge and room heat leak at threshold placements. Require exact membership and causal order of damaged/ignited nodes for deterministic motifs, plus no false “safe retreat” predictions in real worker trips. Differences at threshold mean an invalid geometry rule/reader, not permission to round the bar away.

Output: annotated fuel/heat graphs, maps of causal components and reachable exits, smallest failing geometry per bar and feasible preparation regimes. Size [guess]: small-to-medium enumerator, thousands of local motifs plus full-map graph cases.

Trigger: T29 after generator traces, before claiming B4; first live blast crossing an asserted safe route or second spacing/radius adjustment. Choice changed: R2 propagation implementation, R6 growth/route assumptions and declared containment advice; preserve the meaning of useful extraction and a reachable retreat.

## Drift and route geometry

Question: Does the existing sand-grid/weather mechanism actually make deep obstructing ice deposits against representative structures and then release the routes?

Informs B1/B3/B4/B6/B8, R4/R5/R9/R10, weather unknown meeting and routes/heat meetings. Inputs: actual SandGrid accumulation/erosion rules, weather durations/rates, captured maps of 200/250/300 cells, all structure rotations and edge/interior locations, wall/door/hull/courtyard configurations, roof/open path cells, weather transitions including consecutive storms and fog-shot origin/target ranges around current loaded cap. Sweep grid noise phases present on captured maps, not alternate planets.

Assumptions: vanilla patchiness is not secretly windward collision accumulation. Depth and path-cost reads are available and actual pathfinders can be exercised. Blue-white presentation is a separate local-material concern, checked by B1, never inferred from numerical depth.

Leaves out: a new fluid/wind simulator, future vehicle burial jobs, custom global weather engine and aesthetic approval.

Calibration: match real game depth grids/path costs at storm start, established buildup, stop and erosion, plus real colonist path times and shot-range predicate. Require exact cell class (obstructing/not) and depth/path values within reader precision; compare routes with identical topology and pawn state. Require a pile burying a representative wall/door/hull approach so ordinary passage needs clearing or erosion. A thin film with slight slowing fails B3. RM_IceSandDrift.moveSpeedMultiplier itself slows travel with no deposit. Compare post-storm deposited paths before erosion or equal-weather deposited/deposit-free twins, using the same pawn, load, topology and roof state, and require ordinary use to recover after clearing. Read fog slowdown separately on deposit-free routes before/during/after fog. Global averages, overlays and in-storm trip times alone cannot establish deposited obstruction. If vanilla never produces that picture, state that no demonstrated compliant mechanism exists; do not invent a favorable offline model.

Output: depth/path maps over time, blocked/alternate routes, worst repair travel and fog shooting cases, explicit adequacy finding for vanilla SandGrid. Size [guess]: small captured-grid replay and path-query harness; no independent aerodynamic model.

Trigger: T31 before signing off deep drift, or B3's first live failure; repeats only if weather/depth/path rules change. Choice changed: R5 choice of existing mechanism/configuration, or a narrowly scoped engine dependency request if it is demonstrably inadequate. The owner's deep-drift requirement itself is unchanged.
