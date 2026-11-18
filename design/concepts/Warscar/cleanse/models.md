# Instruments specified, not built

Order below is the proposed build order. No model output in this proposal is a measurement of the game. Capture a real disposable map/save and its actual loaded fingerprints before calibration; use read-only exports, never an alternative planet or a worldgen seed sweep. All primary readings keep retained mechanics enabled, extras off and ordinary weather unlocked. A controlled input sequence is labelled and diagnoses transitions. W5/W9 require a complete cycle in the unforced shipped-weather season itself. An all-calm/all-wind season or other missing natural cycle cannot pass through replay. Inconclusive natural evidence stays UNMEASURED for a fresh unforced season, and repeated absence triggers threshold/weather diagnosis. Missing adapters, records or agreement mean UNMEASURED. Game-side tests and their offline counterpart are built together, under the existing rule.

## Situation and transition generator

Question: can the kept state machines and the default-off boundary survive every meaningful transition without silently reviving an extra or losing saved state?

Informs: W2, W4–W7, W9/W10; R2–R10; unknown save and defaults meetings, plus the wind argument. First build: small pure counter coverage already exists and can expose misplaced gates before an expensive map run.

Inputs/range: production RM_SettlingKernel, actual post-patch settings/defs/creation routes, native mask and ordinary surface classes; state tuples {idle, counting calm, falling, counting wind, lifting}, threshold values immediately below/equal/above actual shipped values and UI extrema, interruption/reset, fresh calm during lift, empty/full grid, roof/screen power edges, map identity changes. Pawn tuples {initially clean untreated wild, wild-scaria, incubating each stage, medically cured with saved exemption, independently reinfected, factioned clean, downed, dead, despawned}. Include treatment/retreat/arrival/death/save orderings. Native source tuples cross original mask membership with roof-only, player-floor-only, both, neither, pollution clean/polluted and coverage removal. Mark tuples cross eligible/noneligible humanlike, other-family mark, shallow/deep/floor-armed severity, active attributed episode, residency/departure/re-entry, save and master/feature/floor switches. Include fresh and migrated-save identities. Gun tuples cover master and feature switches on Warscar, an unrelated map at shipped defaults, and stale targets after transfer or load. Gate tuples include fresh default profile, each extra individually enabled with declared prerequisites, master off during every kept phase, re-enable, and existing saved content. Exhaustively enumerate small predicate classes and adjacent event permutations, then deterministic generated longer sequences. Do not enumerate a meaningless Cartesian product of every setting number.

Leaves out: rendering, hearing, pathfinding success and probabilities of real wind or food supply. Cannot declare W3/W4/W5/W8/W9/W10 passed. Mental-state roll eligibility is distinct from observing an actual scheduled episode. Existing kernels prove only the predicates they actually execute.

Calibration: capture game counters, condition registration, actual job offers, hidden buried list, all reachable build/recipe/research routes, extra output/letter/incident counts and both components' saved fields before/after the same sequence. Compare transitions/event identities exactly; a tolerance of at most one actual sampling interval is allowed for timestamp boundaries, documented from the production scheduler. No tolerance for duplicate registration, regenerated rewards, a hit on a dead pawn or a still-enabled extra. Break a gate deliberately in the test fixture to prove the detector refuses it. Cure cases compare actual hediff/job outcomes and saved native-reinfection exemption. Mark cases compare actual mood thoughts and episode cause, floor identity and departure stop, including an unrelated-state control. Renewal cases compare source writes and their eligible mask. Gun cases compare target/angle/draw/inspect entry paths on both maps.

Produces: coverage table by reachable predicate/transition, active-route matrix per gate, smallest failing sequence, before/after snapshots and attributed callbacks. Rough size [guess]: a small extension to the existing SelfTest plus an integration exporter, thousands to tens of thousands of short sequences. Engine-only branches require game trace replay, not invented stubs declared equivalent.

Decision changed: which missing gates/serialization fields/transition rules must be repaired, whether fresh fall must wait for lift, and whether mark reward gating preserves the retained mental cost and independent biome lookup, and whether treatment exemptions, shelter coverage and native-only tracking survive all transitions. It never votes to remove a necessary bar.

Build trigger: unknown save/defaults meetings already trigger it. Later trigger: an off/on or reload failure, or a threshold changed twice to chase a check.

## Whole-map season model

Question: does the complete retained system have a playable regime in which dust cycles, native contamination persists and ordinary life survives without a record or exposure flood?

Informs: W2, W3, W5–W10; R2–R6/R8–R10; unknown air and life meetings and the higher-order life/film/colony-work loop. The ground meeting already resolves pollution compatibility through native flora Any and covered renewal eligibility. Build after the generator establishes what actually runs.

Inputs/range: export actual full local maps at sides 200/250/300/400 and authored rectangles from the fixed planet, native substrate/terrain, roof/building/crater/ruin anchors, ordinary flora and actual animals, imported food and salvage/work orders. Replay unforced recorded shipped wind/weather and dose/cell-effect schedules for a 15-day season, continuing worst regimes to day 100. Classify each natural trace by whether it actually completes calm/fall/wind/finished-lift at defaults. A missing cycle is a stall, including a trace that never reaches the shipped thresholds. Replay under altered wind is diagnostic output only and cannot change that classification. Compare 3 and 40 colonists; ordinary harvest/hunt/clean/roof and reversed work orders; sparse/dense fauna, mostly open/heavily roofed colonies, no-cleaning and normal-cleaning routes. Use actual damage/immunity/ingestion/growth parameters as inputs, not bar constants. Include external active-screen geometry as a compatibility branch; do not require Warscar technology. Native renewal uses ordinary cell pollution only on saved native cells with neither player floor nor roof. Cross coverage/removal with cleanup and source inspection. Native crusts require resolved plant.pollution Any and clean/polluted establishment. Add the actual bare mark accrual/fade/floor, mood and mark-origin nightmare/job interruption ledger, departure/re-entry and other-family-mark cases. Include initially clean untreated wild grazers as inevitable-onset cases and cured exemptions as separate states.

Assumptions: spatial cell-effect scheduling and actual recorded arrivals/jobs are replayable. Initially bound unmodelled AI between observed high/low feeding/cleanup cases instead of forecasting invented pawn decisions. Coupled native renewal and wet-growth exclusion require production code/adapters before predictive use. Correlation in a replay is not causal evidence without source tagging.

Leaves out: new weather climatology, fictional isotope chemistry, travel between generated planets, exact fun or market-value optimisation. A simplified population equation is not trusted to predict unobserved AI.

Calibration: compare source-tagged health increments, film/record masks, forage biomass and actual consumption/death/arrival ledgers to uninterrupted game checkpoints through ordinary wind/calm and a full lift, plus the midway save branch. Compare native source writes against the exact uncovered selector, covered-clean controls against no native renewal, and ordinary pollution effects separately from airborne doses. Mark thought/episode/floor identities and departure stop must agree with observed traces. Actual low-frequency nightmare episodes require scheduled game observations, and a probability envelope alone cannot certify W10. Require exact discrete state/corpse/item accounting and event ordering; stochastic cell/feeding envelopes must contain held-out game checkpoints, with deviations too small to reverse flood/desert/stall classification. If an envelope covers both acceptable and failed regimes, calibration is inadequate: obtain finer game traces rather than invent a percentage tolerance. Hold out a distinct action ordering and the mature colony. No predicted equilibrium can substitute for W9's live season.

Produces: time series and spatial masks for dust/forage/exposure, attribution table by source, gate state at each checkpoint, worst case and uncertainty envelope per bar. Rough size [guess]: modest event replay/ledger simulator on exported maps, not a RimWorld clone; several full-map traces and targeted held-out checkpoints.

Decision changed: whether renewal cadence, ordinary ecological resistances, lichen replenishment, trace retention or transition scheduling needs tuning; whether a new implementation assumption should be replaced rather than weakening land or life. Natural-cycle absence changes shipped thresholds or scheduling and requires a fresh unforced season. Mental-work collapse changes mark tuning or scheduling while preserving the required mood/nightmare/floor experience. The source footprint and native flora tolerance remain the explicit R2 contract. Reject any proposed screen requirement as the cure for an unplayable default. Powerful future technology retains its broad scope.

Build trigger: unknown air/life meetings already trigger it. Rebuild when toxin/growth/capacity parameters are changed twice to move a check, or the first live combined failure produces a desert/flood/stall.

## Geometry and trace sweep

Question: do film, movement records, cleanup and the lifting frontier agree at every relevant cell/bearing/batch/load boundary?

Informs: W1's cheap layout rejection, W2 coverage boundaries, W6/W7, W8 case selection, W9; R1–R5/R8; unknown film meeting and saved-cursor uncertainty. Whole-season classification consumes its worst cases.

Inputs/range: production RM_TrackPool.SweepOrder, record/style/serialization code and actual surface-selection/erase adapters; map dimensions as above plus tiny synthetic rectangles for exhaustive order proofs, bearings 0..359 including axis/tie angles and float neighbours, all cell locations, batch sizes at first/middle/last boundary and game-shipped values. Empty/saturated pools, visible/invisible grounded walkers at actual body-size cutoffs, later overwrites, cleaned/eaten/replaced film, roofs/water/edifices and neighbour screen boundary/map identity. Replay both components' save/load during each boundary; move the same pawn through multiple batches, then death/despawn. Export defense facings/entrances to flag layouts with no common approaches; no model claim that a tidy angle plot looks like a last stand. Enumerate ancient-danger payload state and wake triggers to detect sealed/dormant live threats independently of sealed salvage. Sweep native mask/roof/player-floor overlap and last-cover removal to verify renewal eligibility geometry.

Assumptions: actual production callback and selection code is exercised, extracted behind a narrow adapter if necessary; an independently rewritten sorting algorithm is only an oracle, not production proof. Surface loss must reach existing grid erase API without a private new grid.

Leaves out: perceptual visibility, actual toxic damage application and real pathfinding. Front dose ledger checks calls/identities; W5 calibrates their game effect. It cannot approve a screenshot or claim flyers leave ground prints while airborne.

Calibration: compare game step cell/time/bearing/style and erase callback order exactly on a natural filmed path, an invisible path, a roach-cleaned path and a full diagonal-front passage; compare record/film arrays plus both cursors before/after a saved midpoint. Require exact identity/mask agreement, allowing only documented sample tick offsets, with no missing/double visited cell or duplicate front hit. Independently query ahead and behind the front. Compare rendered selected sample paths at play zoom under W8 before treating direction metadata as a visual witness.

Produces: overlay masks, advance-order maps, route/record diffs, boundary coverage table and minimized failing geometry. Rough size [guess]: small production-kernel harness with spatial fixture adapter; millions of cheap cell cases are plausible, actual runs state their measured counts.

Decision changed: repair cleanup coupling, shared sweep restore or source gate; keep seeded bearing instead of inventing a wind-direction engine; align existing defenses if geometry really fails. A missing grid is a missing dependency, not authority to accept instant wiping.

Build trigger: unknown film meeting now; first local stale-print/reload-repeat/edge failure later.

## Food-web and onset ledger

Question: do the retained feeding and disease routes work without erasing bodies, starving the native web or turning a readable grazer warning into an unavoidable ambush?

Informs: W3/W4/W9/W10, W2/W6 interactions; R2/R4/R6/R7/R10; unknown life meeting. This is a conservation/transition model with real AI traces, not a speculative ecosystem simulation.

Inputs/range: resolved actual roster, diet and ingest/weapon routes, reachable food and native forage areas; ordinary spawn/arrival/death/taming; actual shipped hunger/growth/immunity parameters. Enumerate corpse state/body/gear/quest-item classes, hungry/fed, fresh/frozen/rotting/desiccated, 0/3/40 colonists, sparse/dense native habitat, before/after cure/tame/death/reload, initially clean/infected wild chatrak and saved medical exemptions. Include mark-caused work/sleep interruptions alongside ordinary breaks, shelter coverage and departure, so the body/food ledger sees their indirect effects. Onset branch uses production stage transitions and measured path lengths/travel times for able workers 1..12 cells away, with reachable escape and blocked/open circling. Test cure before and after arming; distinguish vanilla aggression from delayed scaria onset.

Assumptions: nutrition and carried-item conservation hold between attributed imports/consumption; actual job reachability is observed. For unobserved AI regimes report unknown rather than assuming the animal chooses ideal food. The builder must not mistake appearance or def foodType for successful feeding.

Leaves out: exact balance/yield requirements, a colony fed wholly by the biome, perfect safety for trapped/downed workers and new cross-biome casting. Ordinary attack/taming feasibility remains game evidence.

Calibration: compare actual ingest target/job completion, food-need change, weapon cause and corpse/gear/remains IDs; exact item conservation and source identity. Onset matches actual severity/first-attack order and successful retreat/cure outcome in an uninterrupted and a restored branch. Timing tolerance is the observed scheduler interval, never enough to change retreat pass/fail. Validate the normal pallbearer final-ingest path explicitly: Bones butchery output is irrelevant there.

Produces: food/remains flow ledger, unreachable-food cases, native-occupancy bounds, warning/retreat timing map, minimal bad transition. Rough size [guess]: small ledger analyzer with a table of game feeding/attack traces and a production onset harness.

Decision changed: fix false forage or missing leftovers, ordinary native food viability/eligibility, cue/onset sequencing or residual incubation cleanup. Do not add permanent morale auras, take away a roster species or nerf a future broad technology to make this model pass.

Build trigger: unknown life meeting now; first invisible body loss, population desert, untreated wild-grazer failure to turn, cured-animal rearming, mark-induced work collapse or failed open-path retreat later.

No credible offline instrument is specified for “the sound and picture remain understandable together.” W1/W8 and the whole bar retain their live looks/listens. T23 defines those observations; arithmetic sound density is a check only.
