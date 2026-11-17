# Cauldron instruments, in build order

These instruments are specified, not built or run. No output is a measurement of the game until the stated calibration agrees. The first instrument generates situations for the others; no model makes scenery/readability or enjoyment a numerical verdict. Names below are the exact references used by bars.json. Rough sizes are Designer estimates, not observed performance. All game calibration is later work on disposable copies with all kept mechanics on, all DLC/providers and actual defaults, weather unlocked, next-version extras off. No world generation, bridge use or deployment occurs in this proposal.

## Situation generator

Question: Which reachable combinations and transitions can falsify the retained experiences, including turning a feature off and loading an unfinished action?

Informs: all bars; R_scope, R_world, R_warning, R_protect, R_health, R_research, R_fluids, R_life, R_settings and R_evidence. It covers the argued hush_flight meeting with job/flight-tracker state reads; suush flight visuals require an owner-present sitting and no images of flight are captured. It supplies cases to all six unknown meetings (weather_cycle, ecology, exposure, gas_geometry, fluid_stock, colony_work); it does not settle their dynamics alone.

Inputs/range: parse the resolved Cauldron roster/settings and shared services, not XML `<li>` counts. Enumerate the actual weather states and every allowed transition; vent stable/leaking, capped/uncapped, active/saved-suppressed/recovering; exposed/roofed/fully sealed/partial gear; native/non-native/immune, factions, live/downed/dead; animal diet/flight/product/binding states, including hush eligibility × Wait_MaintainPosture × grounded/takeoff/airborne/landing/cooldown tracker states and pre/during/post-falter reloads; growth below/at/above harvest eligibility; research blocked/doing/done; liquid identity and empty/partial/full/incompatible stores; power/fuel/output shortages; jobs queued/working/interrupted/completed; setting now/restart/local-map boundaries. Include before/after save and both task orders. Pairwise covering arrays are only a first filter: explicitly enumerate weather × cap × protection × population, tank capacity × batch completion × save, and gas topology × flame-front limit × reload. Provider-complete RM-only and campaign-extended compositions are separate contexts, never DLC-absent variants. Local geometry snapshots come from the intended fixed world, not generated planets.

Leaves out: new species, world distribution, art variant counts and arbitrary other mods; no presumption that all Cartesian products are reachable. Document unreachable combinations using a transition precondition, not by silently omitting failures.

Game agreement before belief: export actual settings, resolved types/rosters and a known ordinary action from each state/transition class. Generated predicates must agree exactly with an independent engine state reader for identity, eligibility and action completion, including a deliberately ineligible control. For hush × flight, calibrate against the same suush’s job, position and Pawn_FlightTracker before, during and after falter, plus a non-falter control; verify airborne positional hold, no hush-forced landing, unchanged flight-budget/cooldown rules and ordinary AI resumption. A wait-job label without flight state cannot calibrate hover. Do not judge flight visually unattended. Wrong/missing candidate/state/log reads must refuse. A false eligible or false unreachable case blocks trusting that generator branch. State reads are independent of strings printed by the component under test; a formatted expected value is not a second instrument.

Produces: stable case manifests, precondition proofs, case-to-bar/rule coverage, contrasting controls, durable checkpoint/recovery instructions, and the smallest counterexample per failed bar. It records actual actor IDs, ticks, hashes and log completeness. Source-only cases are labelled source checks, not runtime passes.

Rough size: hundreds to a few thousand small cases plus focused multi-way products; approximately 2–4 implementation days including exports and fixture recovery. The small shape parser already exists, but the actual state generator/observer does not.

Build trigger: first, before acceptance staging, because every unknown meeting needs controlled situations and the existing observer/recovery work is incomplete (T34). Rebuild the affected case set when a new state, roster provider, setting application point or transition is added.

## Gas geometry and save walk

Question: Can any allowed emission, drift or ignition path cross sealed geometry or lose a connected combustible front at a save boundary?

Informs: gas_chain, protection, chemical_work and whole; R_gas, R_local, R_protect and R_fluids; unknown gas_geometry. It also supplies actual plume extent/ignition traces to weather_cycle and colony_work.

Inputs/range: use RM_VentGasCells/RM_VentGasKernel but drive the actual adapter semantics from RM_VentGas.cs, including AddGas overflow and the live Fire neighbour scan, not just kernel diffusion. Exhaust all 3x3 blocker masks and orientation transforms, then tiled corners/doors/edges on 5x5 and longer chained ground/water fixtures. Sweep byte densities 0..255, threshold neighbours, all eight drift bearings, open/closed/changing door passability, roof/vacuum flags, capped/uncapped emission, bank/suppression-related output, wind zero through the configured maximum, disconnected/branched/looped/continuous clouds and clear corridors 1..5 cells. Save immediately before/after a burn scan, during the scan budget spillover, after fuel-less Fire deletion and during shared displacement; instigator live, dead, despawned and null. Include gas overflow near sealed diagonal corners, a path overlooked by isolated drift tests. Tag distinguishable other-gas bytes.

Leaves out: full vanilla fire damage balance, explosion physics and human visual judgement; use ExplosiveKnockback events/outputs as a dependency, not a rival solver. A contained combustion front does not imply no blast damage outside it. A moving door may legitimately change connectivity at that tick.

Game agreement before belief: export passability/door state, densities, burn-front pending cells/tags, live Fires, smoke deltas and knockback source/destination events from actual natural-emission and controlled single-ignition cases. With an exported random sequence and update order, every visited cell's change and pending-front identity must match exactly at scan checkpoints, including save continuation. Validate wall tests against actual GasCanMoveTo, not a guessed solid-wall flag. Any forbidden crossing or lost active front in the game invalidates a model pass; if deterministic RNG replay cannot be obtained, retain a reachability over-approximation, validate every asserted permitted/forbidden edge, and use live cases for chronology. Never label centroid agreement as topology agreement.

Produces: reachable burn maps, crossing arrows, saved-versus-uninterrupted front differences, original-instigator audit, worst case per gas/protection bar and a reduced failing geometry.

Rough size: thousands of local topologies and transition cases, then a handful of full-map replays; 2–3 implementation days building on existing kernel fuzz. Source shows an unsaved front and unguarded neighbour offers; that is a risk, not a measured failure of this candidate.

Build trigger: unknown gas_geometry is immediate (T31/T35); also first live gas-chain failure, any change to passability, overflow, scan budget, ignition neighbourhood or front serialization. A twice-retuned gas constant triggers the coupled-season model as well.

## Coupled season and work model

Question: With the complete default system, is there a regime in which useful protected work is replaced by gas flooding, ecological collapse, persistent illness or a resource/job stall?

Informs: whole and every contributing bar; R_weather, R_warning, R_local, R_gas, R_health, R_fluids, R_life, R_forestry and R_settings. Settles candidates for unknown weather_cycle, ecology and colony_work; consumes gas_geometry, exposure and fluid_stock results rather than assuming those resolved.

Inputs/range: full local 200x200, 250x250 and 325x325 maps with actual intended-site terrain, obstacles and roster snapshots; supplied flat/hill/mountain and warm/cold terminator-tail contexts actually available. Run 15-day seasons plus a continuation to day 100, 3/40-colonist starts, finite declared arrival/established supplies, both action orders and a halfway save/reload. Use actual weather transition/output/dose cadence, vent density/recovery/capping, gas sweeps/ignition/smoke, native feeding/drinking, growth/regrowth, harvest removal, predator consumption, animal births/deaths and VEF fission. Shared-neighbour behaviours remain active in calibration. Expose shortages in water, cartridges, medicine, safe work access and food rather than auto-refilling. Sweep plausible initial stocks, uncapped source layouts, weather histories and labour availability; these are local saved-state scenarios, never alternative planet generation. Tuning sweeps include current configured bounds and candidate changes, recorded as predictions.

Assumptions: exact cell gas and component clocks use calibrated kernels/adapters. Food-chain and colony labour use bounded rates measured from normal jobs and lifecycle traces, not an invented perfect AI scheduler. Persistently injured workers change available labour. Explicitly retain correlations (bloom raises dose and source output together; low food reduces work; refinery blockage increases backlog). Where real shared-creature AI or births cannot be credibly reproduced, use measured event replay and conservative lower/upper trajectories; identify that branch as requiring a live season, not a simulation-certified pass.

Leaves out: subjective enjoyment, unmodelled raids as a colony survival guarantee, a market-profit target and all next-version extras. Vanilla incidents may be replayed as exogenous events; their actual Cauldron interactions stay in the live record.

Game agreement before belief: calibrate on ordinary full-map intervals containing a natural complete weather transition, actual source emission, protection changes, harvesting, conversion and animal lifecycle events, followed by a held-out interval. Exact subsystem conservation/state transitions must agree exactly with the trace. For stochastic ecology/work approximations, compute 95% predictive intervals from independent measured intervals and require held-out trajectories of population, food/water, pending jobs and exposed-worker harm to remain inside those intervals at all declared checkpoints, without systematic directional residuals. Intervals broad enough to contain both safe routine and collapse cannot decide the question: tighten the model or retain live-only evidence. The whole bar still requires an actual season and live readability; no statistical percentage becomes its bar.

Produces: time-series plots of gas extent/connectedness, active fronts/fires, protected/unprotected dose, usable food/water/reagent, fuel, tree/animal population, job backlog and labour; stock-flow graph; worst regimes for each bar. Name a flood (connected gas continually invading normal work routes), desert/collapse (ordinary habitat/food chain ceases to sustain living encounters), stall (supplied reachable work stays uncompleted), and recurring attributable errors separately. Identify whether the smallest fix is timing/rate, accessibility, source layout or an extra scope cut; never relax a sourced health or gas outcome to balance a chart.

Rough size: several dozen bounding regimes over full cell maps, with short exact subsystem replays and coarser ecological intervals; 4–7 implementation days. This is the most expensive model and is built after trustworthy situation and gas traces.

Build trigger: immediate unknown weather_cycle/ecology/colony_work (T36); first whole live failure; any emission/exposure/collector/growth/population constant changed twice to rescue a check. Also required before declaring that the two main action orders are equivalent enough for livelihood.

## Liquid ledger and interruption walk

Question: Does real chemistry and accepted stock survive every ordinary transfer, blockage, interrupted conversion and reload without silent loss or duplication?

Informs: pool_use, chemical_work, timber's resource accounting and whole; R_fluids, R_local, R_research and R_settings; unknown fluid_stock.

Inputs/range: resolved intended pool terrain/liquid/fluid registry bindings, including ToxicWater compatibility forms; normal bottle/bucket/barrel and pump/tank paths; material/gate compatibility. Tap bank empty/fractional/full, tank capacity 0/just-below/exactly/above a delivered bank unit, incompatible contents and multiple touching tanks around all footprint orientations; normal converter power/fuel/input/output permutations. Enumerate each action boundary, destruction, setting change, save/load and repeated work; ordinary research with rig off and opt-in discovery as a separate extra-gate check. Use actual 200-litre bank-unit -> decilitre conversion and actual loaded recipe ratios, never guessed production yields. Account for byproducts, accepted volumes, explicit discards and ordinary harvested item stock.

Leaves out: a redesigned fluid solver, gas density physics, pricing/profit and optional upgraded-machine fuel bonuses. Undocumented loss is a failure to explain, not an invented evaporation term.

Game agreement before belief: read independent source and destination components, ingredient/fuel consumption, product identities and explicit spill/destruction events before/after actual normal transfers/conversions and interrupts. Integer unit volumes and identity must agree exactly; bounded fractional tap-bank arithmetic uses the implementation's float tolerance, recorded once as a check. Every conservation residual must be explained by a real measured event. An empty source or debug-spawned output cannot calibrate the path. Match at least a blocked-to-resumed route and a reloaded incomplete delivery before trusting the state machine.

Produces: directed identity/stock graph, per-event ledger and residual, unreachable/blocked-state table, reduced counterexample at a transfer boundary, and a decision to repair a binding, gate, transaction ordering or UI explanation.

Rough size: hundreds of short deterministic state walks, 1–2 implementation days plus actual calibration (T32/T37).

Build trigger: unknown fluid_stock; first site-pool identity mismatch, cartridge use while blocked, volume residual or saved duplicate output. Re-run affected cases after recipe ratio or bank-unit changes; this does not create new bars.

## Exposure and treatment state walk

Question: Do the combined ambient/contact hazards, protection changes and medical actions have the promised lasting outcomes across real pawn states?

Informs: warning, protection, lasting_cost, pool_use, living_cast and whole; R_warning, R_protect, R_health, R_local and R_life; unknown exposure, with health/save_state arguments checked as transitions.

Inputs/range: exported species/part anatomy, immunity flags, faction, native membership, final loaded VacuumResistance/ToxicEnvironmentResistance below/at/above 1.0 from gear-only, gene/hediff/race-only and mixed sources (including no apparel), separate ToxicResistance, roof state, weather/transition/dose cadence and near/far/capped source weight. Cross these with existing load zero/hidden/visible stages, exposed/sheltered/gear-removed states, ordinary treatment/unavailable/successful/failed/interrupted advanced purge, travel and reload. Acid includes genuine facial disfigurement and sensory part damage/loss branches across normal healing and extraordinary repair. Enumerate chance outcomes to establish possibility, then match witnesses against real runtime actions; no statistical frequency bar is invented. Death removes a subject from work through a readable lifecycle, never marks it cured. Include changing protection inside a dose interval and a warning save immediately before first dose.

Leaves out: new scars/art, a bespoke health engine, tuning the rate of disfigurement, promises of guaranteed sensory injury per hit, all-off magical cure and exceptions to vanilla extraordinary healing. A generic finite random batch that happens to show no permanent case cannot prove impossibility.

Game agreement before belief: both ambient adapters must agree exactly with R_protect’s shared complete-seal predicate, including full non-gear ToxicEnvironmentResistance and full VacuumResistance; full ToxicResistance alone is checked separately, not mistaken for the seal. Actual caused damage and dose events must match exposed/protected eligibility and severity/part/capacity changes exactly on the exported tick sequence. Completed medical jobs, real MedicineUltratech consumption, low-trace bill eligibility, failed/interrupted accounting and serialized condition/part state must match exactly. Validate with actual bloom and supported acid sources, never debug-added injuries, and follow ordinary comparison wounds to recovery. If the game offers no causal part/damage read, implement the observer before trusting the model; an inspect label is insufficient.

Produces: transition tables and earliest harm time, missing-treatment edges, protected-state counterexamples, source-attributed lasting-injury witnesses and worst duty-route exposure histories. Output decides whether to fix eligibility, warning clock, sealing, decay/treatment or part injury implementation; it cannot change the owner’s lasting-cost choice.

Rough size: a few hundred eligibility classes and bounded treatment/part transitions, 2–3 implementation days reusing vanilla state and the existing kernels (T28–T30/T37).

Build trigger: unknown exposure; immediate implementation gaps in decay and full sealing; first misleading protected-health pass, inaccessible saved trace or untraceable permanent injury. A twice-changed exposure constant also triggers the whole model rather than another isolated healthy scene.
