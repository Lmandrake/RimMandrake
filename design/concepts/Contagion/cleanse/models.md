# Instruments specified, not built or measured

Build in this order. Every item is a prediction/test instrument until its production adapter agrees with running-game state. The existing kernels and fake-game suite are useful seeds, not evidence that these models already exist. An exported save/state snapshot is input, never an alternative planet generator. No simulator generates a planet or retunes a shared engine autonomously. The ordinary full-map season still settles the whole bar; no credible offline model can certify the drawn tells, beam, readable remains or player recognition of a strange body.

## M1 Situation and transition generator

Question: can every retained state and transition execute without a skipped warning, stuck job, repeated notification, duplicated commit or dependence on a disabled extra?

Informs: all bars, especially forecast, native_response, body_change, arrest, tissue and season; R_clock, R_dive, R_touch, R_deck, R_arrest, R_batch, R_settings; unknown meetings sky-clock and jobs. It supplies M2/M3/M4 test inputs rather than duplicating their geometry/economy logic.

Assumptions: production transition/eligibility/arbitration functions can be called through small deterministic adapters; resolved defs and body trees are exported with fingerprints; state at each action boundary and random choice is observable. A reimplementation agreeing only with itself is not credible. Where Verse job machinery cannot execute offline, enumerate its cases and expected invariants here but require actual job-state traces for those cases; that subset cannot be “passed offline.”

Inputs/range: weather {Bloom, wet lull, tell, transition-to-Burn, Burn, transition-back}; due tick just before/on/after poll; old/new clock and tell flags across load; all setting edges one at a time then producer-affecting combinations; flesh humanlike/animal/mech; native shy/leaker/armoured; health/body eligibility, all production mutation cards and part classes, pre-onset warned with zero mutations, active progression and existing mutations through cap/exhaustion; job {idle, running, arrive, reserve fail, cancel, target/actor dies, loses weapon, loses reach, toggle}; extraction/injection/treatment/birth/ordinary-corpse-claim commit before/on/after reload; colonists {4,40}, natives {1,40,200}. Use full Cartesian enumeration for each interacting component and three-way intersections sky x job x exposure, job x setting x commit, death x claim x reload. Do not prune distinct failure branches merely because their results look alike.

Leaves out: renderer quality, true human response time, new worlds, unrelated quest/raid AI. It cannot prove a moving animal visibly flops; visual bar parts remain live.

Real-game calibration before belief: read actual persisted sky fields, TellsBegun, actual weather, job IDs/targets/reservations, applied hediff/gene effects, letters/messages and sample/host/output IDs from disposable saves at each transition. Capture natural continuous traces and paired save/reload branches, including treatment clearing the actual state on a naturally warned zero-mutation patient versus an untreated sheltered control retaining the warning, with a separate naturally exposed control reaching onset/first mutation, a real interrupted hold/injection and an exposed mutation. Agreement: exact class, identity, eligibility, state edge and message count; timestamps within the production poll interval only where ordering is preserved. A warning after harm, different commit identity or absent real cost is disagreement, not tolerated error. Fail adapters closed on unobservable state.

Produces: transition table and shortest failing action sequence per bar, explicit unobservable branches, negative-control traces and production-versus-prediction diff. Mutation rows show applied effect deltas, not metadata alone; batch rows show calculated pre-commit odds from the actual pool/count law.

Rough size [guess]: thousands to tens of thousands of bounded transition cases, not an exhaustive simulation of all RimWorld. Stop expanding redundant stat magnitudes after boundary classes cover the same decision. An engineer-sized adapter/test task, not a new game engine.

Decision changed: job priority/commit boundaries, notice latch persistence, settings gates, exposure state classification and whether an alleged offline bar must instead require a live state witness. Does not change the player's costly-crossing promise to fit broken jobs.

Trigger: first build after proposal adoption, because sky-clock/jobs meetings are unknown and several required behaviours are absent. Existing SelfTest Program, ContagionFuzz, RM_SkyKernel, RM_TouchedKernel and fake-game tests provide starting cases; production integration is still owed.

## M2 Coupled valley season

Question: do weather, shared growth/Rupture, ordinary births, death/reabsorption and colony work sustain repeated choices over a full season without runaway bodies/remains or an emptied/stalled valley?

Informs: season, place, native_response, unfinished_life, body_change, tissue, remains; R_clock, R_dive, R_life, R_death, R_engines, R_settings; unknown map-ecology meeting including the Rupture -> hosts/jellies -> buds -> remains -> work/route loop. This is the whole-mod model, not several isolated example scenes.

Assumptions: map-cell geometry and terrain/native initial state come from the actual disposable authored-world map; production growth/charge, birth eligibility, local cap, natural deadlines, lifespan and death/claim rules are called or faithfully event-stepped. All named shared engines use their shipped settings. Externally observed event rates may seed an exploratory approximation but never certify stability. One host-local cap is not a carrying-capacity model. Weather sampling preserves actual competition, transitions and covered-interval fractions.

Inputs/range: real 250x250/325x325 maps and 150x150 stress fixture; canopy sparse/ordinary/dense, host clusters separated/overlapping, reachable/blocked refuge network, native density and plant regrowth current defs plus measured state; 4/40 workers with normal schedules; naturally elapsed 15-day season and extension to day 100; clock/duration endpoints and at least several ordinary RNG traces; before/after saved reload and alternative action orders. Sweep zero baseline remaining hosts versus clustered high producer states that the game can actually reach; include the game's Rupture births of Bloody Mess and zhool and guarded VEF asexual fission of zhool/bulloo, not just the local Unfinished spawner. Annotate configured frequency/rate endpoints as sensitivity runs rather than default passing requirements.

Leaves out: settlement strategy optimization, unexplained constant “kills per day,” world hydrology, world generation, new shared-engine rules and unrelated raid victory. Predation/pathing not credibly modeled must be calibrated as event envelopes from real traces and marked as a limit. If interactions depend on emergent pathfinding beyond the envelope, use real season runs instead of pretending the simulator settles them.

Real-game calibration before belief: export baseline and regularly sampled event ledger from unrestricted natural ticks, including every producer ID (local budding, Rupture, VEF fission and wildlife arrival), birth/death/remain transition, Rupture charge reset, weather interval, crop/tree changes, completed/queued/cancelled jobs, body costs and batch commits. Record default settings and fingerprints throughout. Agreement: deterministic deadlines/claims/order exact up to their documented polls; birth/death/population/charge distributions over repeated traces fit observed ranges without systematic residual producer or missing sink. A practical initial calibration tolerance [guess] is cumulative cohort/population error within a fifth over each weather segment, but no acceptance follows from that number: any disagreement that changes flood/desert/stall classification invalidates belief. Confirm worst forecast regimes with actual game runs; never label simulation output measured game state.

Produces: cell maps of cover, host/plant/remain density; population and work time series by producer/cause; worst case per bar; accumulation and extinction witnesses; reload/order invariant diff; explicit unmodeled dependency list. Distinguish water flooding from biological “flood” in the bar.

Rough size [guess]: tens of scenarios and hundreds of producer/timing sensitivity runs on a cell/event model; days of naturally ticked game trace may be needed to calibrate, even if offline runs are cheap. No new engine-level ecology framework.

Decision changed: whether local budding needs scheduling/fairness work, whether remains lifetime/claims need tuning, which actual map/regime to run first, or whether a shared-engine conflict must be returned to that engine with a concrete witness. It cannot change a standing engine rule or disable Rupture to make Contagion pass.

Trigger: build immediately after M1's adapter skeleton because map-ecology is unknown. Also reopen when a growth/birth/lifespan/cap constant has been changed twice to move a check, or the first unrestricted season floods/empties/stalls.

## M3 Refuge geometry and crossing envelope

Question: does the same shared exposure geometry guide shelter and pressure while leaving a useful, costly ordinary crossing window under combined UV, ambient heat, Direct Sun and touched exposure?

Informs: refuge, crossing, forecast, native_response, body_change, season; R_shade, R_dash, R_dive, R_clock, R_touch; unknown shelter-geometry and pawn-health meetings. Geometry and timing are connected: a correct shadow map alone cannot establish survival. This model is an offline prefilter; refuge remains live-only because drawn-shadow agreement and actual refuge path/job execution require the running game. T-water-cover is an explicit shared-owner dependency: today's ShadeAt/ExposureAt has no water term, so a model using the current service must report that water-cover witness as failed, not synthesize a local exception.

Assumptions: use production shade/exposure and cover functions, current grid invalidation, path costs, weather factor and actual health update law; snapshot actual world-tile solar geometry, not biome prose or a normal day/night guess. A formula of canopy circles inferred from sprites cannot replace the shared service. Compare the predicates actually consulted by Pressure() and the sky-derived touched-dose code, cell by cell against the shared grid, with consumer-call witnesses; an unused correct grid does not pass. It can bound ordinary route/health cases, not predict all combat and equipment mods.

Inputs/range: all legal bearings by 5-degree sample plus exact footprint-edge configurations, elevations 5/30/60/90 degrees; production crown/growth/rock/roof/structure footprints, map boundary/fog/water transitions and place/remove/cut/load events. Sweep reachable 8-20 open-cell routes and equivalent slow/loaded/door travel durations, distant 60-100-cell work parties, 80-120 percent ordinary mobility, ambient 25/32/45 C and 57 C extreme controls, ordinary apparel and shared parasol coverage; start-of-Burn phases, shortest/longest configured Burn, near both sides of pressure polls. Enumerate actual weather sun-factor levels and all candidate shelter states including sealed rooms. Numbers delimit cases and may change with calibration; no stat, route length or survival percentage becomes a bar.

Leaves out: new living-canopy predicates/Rawshade, water purification, raids, incapacitated rescue guarantee, future day/night-world support. None of these omissions authorizes a second local shade rule. Armour and injuries outside calibrated classes produce an “unmodeled” result.

Real-game calibration before belief: export shared grid/version and cell exposure after real roof/tree/cover changes; compare the actual Pressure() and touched-dose consumer predicates to it, not just the grid to itself; compare chosen shelter to real path reach and actual location. Put equivalent pawns in an off-trunk shadow, on the trunk cell and in adjacent open ground and read actual Burn damage events and sky-derived touched dose, separating contact dose. The trunk receives only the protection its real cast shade provides. Compare drawn shade with the protected cells. For healthy pawn probes read UV dose and applied damage, vanilla Heatstroke/felt temperature, touched progression, consciousness/work ability and real traversal ticks. Agreement: cell classification and reachable status exact at declared grid update, selected route causally valid, travel within a poll of the actual path, effect signs/classification exact; magnitude residual must stay below any boundary that changes conscious arrival or inability to work. No tolerance hides a trunk-shadow disagreement. Calibrate exposed and sheltered, charged and interrupted paths with all retained effects on, not zero-damage state.

Produces: exposure/route overlays, invalid refuge witnesses and critical geometry changes; crossing cost versus residence time and arrival phase; smallest risky route/health combination and no-valid-window report. It must be able to say no normal route can satisfy both costly crossing and grave long stay.

Rough size [guess]: thousands of cell/geometry snapshots and tens of thousands of cheap route/health trajectories. Existing shade grid is reused, never recreated as a second geometry engine.

Decision changed: integration with shared shade, candidate fairness/invalidation and combined pressure tuning; if a useful window cannot exist under standing rules, report the actual conflict instead of guessing a safe distance. Any new engine change requires its own owner path.

Trigger: first geometry/health work after M1/M2 scaffolding, because current exact-tree predicate and per-biome heat fields conflict and both meetings are unknown. Reopen on first live crossing/refuge failure or a constant changed twice to fix opposite health checks.

## M4 Body and tissue ownership walk

Question: can each ordinary genome sample, host and corpse/remnant have a single readable saved lifecycle through competing extraction, birth, death, surgery, ordinary decay/destruction and butchery events?

Informs: remains, unfinished_life, tissue, arrest, season; R_death, R_batch, R_identity, R_settings, R_engines; unknown remains meeting and transaction risks in the argued tissue-identity meeting.

Assumptions: stable production identity/provenance is exported, actual job commit callbacks can be invoked/observed, deterministic placement outcomes are available; race-specific death workers, Bones and vanilla corpse owners are represented by their actual callbacks, not a proposed generic dissolve routine. Physical travel for ordinary corpse handling uses M3 reachability and actual job witnesses. Pure ownership conservation can be tested offline; readability of death/remains still requires live captures. Detailed Bodyprints and bespoke eater travel are off, not inputs needed by this first-version model.

Inputs/range: every retained native death class, Unfinished unraveling, birth without acid, combat with acid, outgoing Blisterfloat husk; original/corpse-or-bodily-remnant/claimed/butchered/decayed/destroyed states; reserved/transported/butchered/burning remains. Ordinary samples normal donor alive/dead/absent/renamed, body-part pool targets, injection failure and interruption, healthy/premature/departed-map/blocked-birth completion. Inject save/load, setting off/on, map unload and duplicate callback delivery immediately before/on/after each commit. Sweep ordinary remnant cleanup against observed readability and death loads from M2, not an arbitrary permanent filth count; no extra return-trip print lifetime is commissioned.

Leaves out: Bodyprint skin/print phases, timed fade, bespoke eater journey/consumption, final Bodyprint sampling and its deferred Draftprint consumer, Helix Draftprint values/contracts, all Grown Limbs/removal including natural arms/legs, custom organs or player-colonist corpse transformations. Vanilla surgery failure remains a valid outcome; it must not grant false matching feedback. Shared-engine ownership policies are inputs; the model does not rewrite Bones or acid mechanics.

Real-game calibration before belief: save/read original source ID and actual generated remnant/output/sample IDs, damage/death cause, donor ID, job reservation/arrival/commit, actual deleted source and generated outputs. Observe a natural death and its readable corpse/remnant, ordinary butchery/fire/decay, uninterrupted ordinary birth, premature acid death, real matched/nonmatched surgery and save forks. Agreement: exact ownership transitions and no double-spent source; death/claim event order exact within declared timing; disappearance has a named visible successor/cause. An item placement failure losing an entitlement or a duplicate branch is a model or implementation failure, never accepted drift.

Produces: state/ownership diagrams and tabulated adversarial sequences, conservation ledger of biological source/outputs, duplicate/loss counterexamples, shortest death/butcher/destruction conflict, ordinary-remnant accumulation witnesses and explicit readable-death checkpoints.

Rough size [guess]: a small finite ownership graph with thousands of interleavings across a handful of actual death/job classes; it does not need a whole-game simulator.

Decision changed: when to consume source items/hosts, what state saves and pauses, how readable death signs resolve without deferred Bodyprint phases/eater/sampling/trade, and which adapter needs a single-claim guard. If lifetime and accumulation requirements conflict, M2/M4 expose that region before a new cleanup constant is invented.

Trigger: build when completing readable native death signs and ordinary placement safety; the remains meeting is already unknown. Reopen on first lost/duplicated object, inconsistent reload or repeated opposing lifetime tweaks.
