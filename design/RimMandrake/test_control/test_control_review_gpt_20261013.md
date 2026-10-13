## 1. Recommendation: install a test-state monitor and a local run governor

**The measured gap justifies continuous observation now.** My earlier review tied cadence too closely to the question of pawn provenance. That was too narrow: colony survival, elapsed time, specimen decay, and UI blockage require continuous coverage even when every pawn’s origin is known.

Install three cooperating pieces:

| Piece | Responsibility |
|---|---|
| **Test-state monitor** | Record pawn vitals, hazards, clock changes, UI state, and the state of test actors/specimens throughout setup and execution. |
| **Local run governor** | Refuse unsafe operations, interrupt long stepping, latch disturbances, and capture evidence before cleanup. Runs inside the companion/harness; does not depend on Grafana or an agent noticing an alert. |
| **External telemetry** | Preserve history, display trends, notify the owner, and support diagnosis. Reuse the existing JSONL → VictoriaMetrics/SQLite → Grafana/RimPulse architecture. |

Keep `scene_report` as the detailed boundary/diagnostic interface. Reuse the built incident journal, origin observations, and action receipts. **They complement the monitor; they cannot replace it.** An incident journal misses starvation, ongoing combat, existing hives, and specimen decay.

The supplied records establish implementations and some measurements, but contain different deployment states. They do **not** establish which capabilities are working in today’s running game.

Confidence labels below:

- **V — VERIFIED-from-knowledge:** familiar existing Verse/RimWorld interface or established engineering behavior; **not verification against your installed assemblies**.
- **P — PLAUSIBLE:** a credible read or instrumentation route; exact binding, semantics, cost, or coverage needs local proof.
- **U — UNKNOWN:** requires source inspection or a specific adapter. No API name is asserted.

Official sources confirm DLC mechanics, not companion-hook coverage. None of the proposed tool names below should be treated as an existing deployed API.

### Observation rules

1. **Arm before site construction.** The destructive clock advance happened during setup; a monitor armed only around the final assertion would still miss it.
2. **Record both simulation and real time.** Every record needs game/load epoch, map identity, sequence, game tick, absolute/calendar tick where available, UTC, and monotonic time.
3. **Combine sampling with event latches.** A pawn can spawn, die, and disappear between samples. Death, damage, hazardous arrivals, and control violations need retained evidence.
4. **Stop locally.** A ten-day advance must be interruptible inside its execution loop. An external alarm after completion cannot protect the colony.
5. **Missing coverage is UNMEASURED.** Never substitute zero pawns, zero errors, or “no threats” for a failed read.

## 2. What to watch

### 2.1 Cadence and thresholds

These are proposed starting cadences, subject to overhead measurement:

| Code | Meaning |
|---|---|
| **E** | Event observation with sequence and tick; retain until the run ends. Verify each hook independently. |
| **T60** | Sample every 60 **processed simulation ticks**, plus setup/row/action boundaries. Approximately one simulated second at normal ticking; not one wall second. |
| **T250 / T600** | Slower tick sampling for less urgent state. |
| **W250** | Check every approximately 250 ms of monotonic wall time, including while paused. Read Unity/game objects on their owning thread. |
| **B** | Baseline and relevant mutation/row boundaries. |

Sampling deadlines must use actual processing progression, not simply “current tick is divisible by 60.” Clock reassignment can skip a deadline.

**“Far from bland” is an observation flag, not automatically a DISRUPTED verdict.** The thresholds below are defaults for quiet fixtures. A declared combat, disease, weather, or destruction test can expect them. Relevant hard safety constraints still apply.

### 2.2 Clock, execution, UI, and observer health

| Channel | What it detects | Cheap read / confidence | Cadence | Default flag |
|---|---|---|---|---|
| Game and calendar clocks | Excess elapsed time, direct clock reassignment, backward time, seasonal/daylight changes | **V:** `Find.TickManager.TicksGame`, `TicksAbs`. **P:** companion processed-tick counter and mutation receipts distinguish advancement from reassignment | E + every stepping chunk + W250 | Any unexplained discontinuity; any advance outside the action/row budget |
| Requested versus executed stepping | A requested short wait becoming a long simulation; partial execution hidden by a success response | **V:** harness receipts. **P:** count completed ordinary ticks in the controlled stepping loop | E | Executed ticks exceed request; missing completion receipt; rejected action nevertheless mutates state |
| Pause and speed | Unexpected pause, speed change, or ticking despite a claimed pause | **V:** tick manager `Paused` and `CurTimeSpeed`; compare with processed ticks | E/P + W250 | State differs from the action contract; tick progress contradicts reported pause |
| Tick/frame/bridge progress | Simulation stalled, UI progressing while ticks stop, blocked dispatch, long uninterruptible operation | **V:** reuse existing timings. **P:** separate frame, tick, dispatch-start, completion heartbeats | W250 | Deadline exceeded with no appropriate progress; distinguish paused, busy, queued, and stalled |
| Window stack | Stale dialogs, confirmation requests, choice letters, menus, mod windows | **V:** `Find.WindowStack`. **P:** read window types, age, blocking/pause flags and identity; exact properties verified locally | E + W250 | Unexpected blocking window; expected window exceeds its deadline |
| Interaction/UI context | Wrong map, world view, active targeting/designator, stale selection, focus/input capture | **V:** existing selection/designator infrastructure. **P:** context fingerprint; exact bindings depend on the tool | B + W250 when relevant | Action context differs from its prerequisite; UI-driven action loses required focus |
| Letters and transient messages | Colony-loss letter, threats, deaths, betrayals, quest deadlines, joiners, warnings | **V:** `Find.LetterStack`. **P:** insertion observation plus retained letter IDs/types/targets; separate message observation | E + T60 fallback | Unexpected actionable/threat/death letter; colony-loss indication immediately |
| Active alerts | Starvation, medical emergency, fire, power/food problems, entity containment issues | **P:** observe existing alert reports when evaluated, or modest-cadence reads. Exact alert interface requires verification | E/P + T250 | Newly active critical alert relevant to actors, specimen, or environment |
| Game/map/load lifecycle | Reload, game replacement, map removal, unexpected branch change | **V:** `Find.Maps`; **P:** lifecycle observations and fixture identity | E + B | Active row crosses an undeclared load/map/fixture boundary |
| Human or other-agent mutations | Dev actions, manual edits, concurrent bridge drivers, settings changes | **V:** bridge lease/action ledger. **P/U:** dev/UI mutations require additional coverage | E + B fingerprints | Mutation outside the owning run’s declared actions |
| Error/warning bursts | Broken tickers, repeated job failures, swallowed exceptions, log saturation | **V:** Unity’s `Application.logMessageReceivedThreaded`; supplied record establishes the logging-cap hazard. **P:** bounded fingerprints and logger-state read | E + W250 | New exception during a row; repeated error fingerprint; emission becomes suppressed |
| Observer/control health | Dropped rows, failed reads, expired arming, missing hooks, writer backlog, ineffective control | **V:** explicit status/sequence/TTL counters; **P:** per-capability runtime coverage | E + W250 | Required source fails, expires, becomes stale, overflows, or reports unavailable |

Do not call every alert’s potentially expensive report-generation logic every tick. Letters and alerts are useful summaries, but their absence cannot establish safety.

A modal window also does not necessarily block every bridge operation. Record whether it blocks ticking, input, a specific tool family, or bridge dispatch; do not collapse these into one boolean.

### 2.3 Pawn vitals: every spawned pawn, plus roster continuity

Start from **V:** `map.mapPawns.AllPawnsSpawned`.

That collection is **not a historical roster**. Dead pawns generally leave it; carried, contained, transported, cryptosleep, and other held pawns require additional coverage.

| Channel | What it detects | Cheap read / confidence | Cadence | Default flag |
|---|---|---|---|---|
| Presence and location | Arrival, departure, disappearance, map transfer, pawn near an anchor | **V:** spawned-pawn census, `thingIDNumber`, map and position. **P:** existing spawn/despawn observations with verified semantics | E + T60 | Unexpected arrival; tracked actor disappears; unplanned proximity or transfer |
| Alive/dead history | Death followed by corpse removal, destruction, resurrection, or transfer | **V:** `Pawn.Dead`, `Corpse.InnerPawn`. **P:** verified death paths plus retained roster/tombstones | E + T60 reconciliation | Any unapproved tracked-actor/sentinel death; unexpected resurrection |
| Downed and actor availability | Incapacitation, collapse, lack of usable workers | **V:** `Pawn.Downed`; **P:** actor-specific availability classification | E + T60 | Required actor becomes downed or unavailable; usable actor count falls below contract |
| Injury and health trend | Combat damage, deterioration, recovery, unnoticed harm | **V:** `pawn.health.summaryHealth.SummaryHealthPercent`; **P:** verified damage observations | E + T60 | Any new injury to a protected sentinel; illustrative warning: health drops ≥0.05 between samples |
| Bleeding and pain | Ongoing blood loss, pain shock, urgent treatment | **V:** `pawn.health.hediffSet.BleedRateTotal`, `PainTotal` | T60 + relevant E | New bleeding in a quiet fixture; actor pain exceeds its declared operating range |
| Hediffs and disease progression | Infection, starvation, toxic buildup, heatstroke, hypothermia, overdose, anesthetic/coma, unusual mod effects | **V:** `pawn.health.hediffSet.hediffs`. **P:** changed def/severity summaries, targeted detailed reads | T250 + damage/downing/row boundaries | New unapproved hediff; dangerous severity progression; expected recovery reverses |
| Critical capacities | Consciousness, movement, manipulation, breathing, or other capacity loss despite misleading overall health | **P:** health capacity tracker; exact calls and caching verified locally | T250 for actors; on health changes | Required capacity falls below the row’s prerequisite |
| Mood and break margin | Mood collapse, accumulating stress, imminent mental break | **V:** nullable `pawn.needs.mood.CurLevel`. **P:** read actual pawn-specific break thresholds | T60/T250 | Mood crosses its own break threshold; illustrative trend warning: drop ≥0.20 within 600 ticks |
| Mental state | Berserk, manhunter, panic, wandering, murderous behavior, social fights | **V:** `Pawn.InMentalState`, `MentalStateDef` | E/P + T60 | Any unexpected state on an actor; aggressive state on any pawn |
| Needs and dependencies | Hunger, exhaustion, recreation, chemical dependency, hemogen/deathrest-related needs where applicable | **V:** pawn needs tracker and nullable food/rest needs. **P/U:** DLC/mod-specific adapters | T250; T60 for vulnerable actors | Need crosses the relevant in-game danger threshold or violates actor prerequisites |
| Relationship and control | Recruitment, taming, enslavement, escape, betrayal, player pawn becoming dangerous | **V:** faction and `Faction.HostileTo` for faction diplomacy. **P:** guest/slave/control state and verified pawn-level hostility predicates | E/P + T60 | Unplanned control/faction change; player-controlled pawn becomes dangerous |
| Actual aggression | Predator targeting a colonist, friendly berserk pawn, combat underway, hostile turret targeting | **V:** `Pawn.CurJob`; **P:** target/verb/duty interpretation and actual damage evidence | T60 + combat E | Unapproved attack target involves actor/specimen; damage actually occurs |
| Job progress | Timeout caused by sleeping, drafting, combat, fleeing, hauling diversion, labor, ritual, or repeated job failure | **V:** current job identity. **P:** job-change/progress observations and targeted diagnostics | T60 for actors | No expected progress for the row’s deadline; repeated restart/failure; actor diverted |
| Work prerequisites | Forbidden target, restricted area, unavailable work type, skill/role restrictions, reservations, unreachable path | **P:** targeted reads at setup and on stalled progress; avoid continuous full path searches | B + stall E | A required prerequisite ceases to hold; actor cannot perform the asserted job |
| Reproduction and age changes | Birth, hatching, pregnancy/labor, age-stage changes, new children/animals | **V:** age tracker and observed pawn-set changes. **P:** pregnancy/hatching adapters; supplied build identifies some hooks | E + T600 | Unplanned new pawn, labor, or age-stage transition affecting a row |
| Held/off-map roster | Abduction, devouring, carrying, transport, containment, caravans, cryptosleep | **V:** `IThingHolder` infrastructure. **P/U:** bounded holder traversal and transport/world adapters | B + E + T600 | Required actor leaves monitored availability; disappearance cannot be resolved |
| Population viability | Zero living colonists, zero capable workers, missing medic/mechanitor/pilot | **V:** derived from tracked roster. **P:** role-specific capability checks | E + T60 | Expected population becomes zero; required role has no available pawn |

**Health percentage is a trend, not a survival guarantee.** Critical organ/capacity loss, disease, and unusual hediffs can matter more than that scalar.

**Do not treat absence as death.** A pawn may have boarded a shuttle, transferred maps, entered a holder, or been abducted. Conversely, do not let a pawn’s departure from `AllPawnsSpawned` erase a recorded death.

“Alive colonists = 0” needs two scopes:

- **Map availability:** no suitable actor remains on this map.
- **Game/fixture survival:** no living expected colonist remains anywhere in the monitored roster.

A legitimate gravship or caravan transfer must not produce a false colony-loss alarm.

For rollups, keep **role**, **race/type**, and **relationship/threat** separate. “Colonist, hostile, neutral, animal, mech” are overlapping categories: an animal can be hostile, and a player mech can be friendly.

### 2.4 Threats, environment, resources, and specimen integrity

| Channel | What it detects | Cheap read / confidence | Cadence | Default flag |
|---|---|---|---|---|
| Incident attempts and outcomes | Raids, traders, clusters, disease, weather events, other incident-driven changes | **V:** supplied build verifies `IncidentWorker.TryExecute`. Reuse journal; successful outer return is not proof of effects | E | Unexpected attempt/effect; permitted incident produces effects outside its bounds |
| Pending incidents | Delayed events surviving storyteller-off | **P:** storyteller/incident queue inspection; exact queue binding verified locally | B + T250 | Unapproved pending event overlaps the row’s interval |
| Quest state and deadlines | Scheduled attacks, arrivals, betrayal, weather, lending, failure consequences | **P:** quest-manager inventory/state and selected quest-part adapters; **U:** universal part scheduling inspection | E + T250/B | Unexpected quest activation/state change; relevant deadline or signal during the row |
| Pending deliveries and groups | Drop pods, shuttles, visitors, caravans, refugees, reinforcements | **P/U:** transport/group adapters plus held contents and arrival observations | E + T250/B | Unapproved delivery is pending or arrives; required actor departs |
| Hostile structures and dormant threats | Turrets, mortars, mech assemblers, reinforcement beacons, ancient dangers | **V:** thing-lister infrastructure. **P:** verified def/component classification and armed/dormant state | E + T250/B | New unapproved threat structure, even with zero active hostile pawns |
| Hives and spawners | Infestations, continuing insect production, eggs/cocoons, mod pawn factories | **P:** indexed structure census and selected component state; supplied hooks cover some producers | E + T250 | New hive/spawner; unapproved production; dormant threat activates |
| Active game conditions | Toxic fallout, volcanic winter, heat/cold waves, eclipse, solar flare, psychic effects, DLC conditions | **V:** `map.gameConditionManager.ActiveConditions`. **P:** include relevant world-level conditions and source identities | E/P + T60 | Unapproved condition starts, changes intensity, or fails to end |
| Weather and illumination | Lightning/fire risk, rain washing effects, visibility, solar power, sunlight-dependent behavior | **V:** `map.weatherManager.curWeather`. **P:** relevant weather parameters and existing glow/environment reads | E/P + T250 | Weather/light leaves the declared range; transition affects actor or specimen |
| Temperature/exposure | Indoor overheating, outdoor extremes, freezer loss, lethal exposure | **V:** `GenTemperature.GetTemperatureForCell`. **P:** cached actor/specimen/room samples | T60 at critical cells; T250 elsewhere | Temperature leaves the relevant pawn/item tolerance; fast adverse trend |
| Fire | Fires spreading to actors, structures, crops, ash/filth test area | **P:** indexed fire census and verified spawn/extinguish observations | E + T60 | Any unapproved fire in fixture; fire enters critical region |
| Explosions and falling hazards | Roof collapse, meteorites, lightning impacts, shells, traps, explosive chains | **P:** verified effect/damage/destruction paths; indexed active hazards | E + T60 relevant checks | Unapproved impact/damage in scope; dangerous projectile aimed into scope |
| Gas and contamination | Tox gas, smoke, rot-related exposure, dangerous custom gases | **P:** relevant map-grid reads at actor/specimen cells; exact grid APIs verified locally | T60/T250 | Exposure violates contract; dangerous gas enters work/test region |
| Power, fuel, and breakdowns | Life support, freezer, heater, bench, turret, or shield outage | **V:** thing/component reads. **P:** targeted power-network/fuel/breakdown state | E/P + T250 | Required infrastructure goes offline or below reserve |
| Food and care runway | Starvation, no usable food, no medicine, inability to rescue/tend | **P:** targeted usable-stock and actor-need reads; accurate accessibility accounting costs more | B + T600 | Supplies/needs cannot cover the permitted advance horizon |
| Terrain, roof, doors, and access | Destroyed paths, sealed rooms, flooding, freezing water, roof changes | **V:** existing map grids. **P:** region fingerprints and mutation adapters | E/P + T250/B | Access/support/exposure prerequisite changes |
| Plants and ecology | Blight, crop death, predator pressure, breeding, wildlife changes | **P:** indexed population/plant summaries; detailed reads only when relevant | T600 + E | Unexpected loss or ecological hazard affecting the row |
| Test object lifecycle | Ash decays, filth washes away, food rots, corpse vanishes, plant grows, HP changes | **V:** thing identity, spawned/destroyed state, HP. **P/U:** component-specific age, rot, decay, despawn causes | B + T60 for critical specimens | Subject disappears, ages beyond contract, or changes before measurement |
| Resource competition | Traders, visitors, animals, or other pawns consume, reserve, move, or use test resources | **P:** targeted reservation/job/inventory/stack deltas | E/P + T60/T250 | Required input is removed, claimed, consumed, or relocated |
| Faction relations | Hostility flips, retaliation, goodwill effects, betrayal | **V:** faction relationship reads. **P:** relation-change observation | E/P + B/T600 | Relevant relation departs from fixture contract |
| Settings and content identity | Difficulty, storyteller, mod settings, loaded-content/build changes | **V:** existing content identity and action ledger. **P:** selected settings fingerprint | B + known mutation E | Relevant configuration changes mid-run |

Watch **effect state as well as source events**. A mod can create fire, a hostile pawn, or a condition without calling an incident worker.

The ash failure deserves a dedicated principle: **test specimens have prerequisites and lifetimes just as test workers do.** Sampling the right def after its intended state has decayed is not a valid measurement.

### 2.5 DLC-specific additions

All five DLCs remain loaded. Control their unrelated active mechanisms through fixtures and narrow gates, rather than unloading them.

| DLC / channel | Detects | Cheap read / confidence | Cadence | Default flag |
|---|---|---|---|---|
| **Royalty: cluster lifecycle** | Dormant cluster, activation, assembler production, reinforcements, turret/mortar threat | **P:** indexed cluster structures, relevant components, pawn/incident observations; exact cluster grouping interface **U** | E + T60/T250 | Unapproved cluster/activation/production; threat capable of affecting scope |
| Royalty: problem causers | Psychic droner/harmer, weather effects, sun blocking, EMI or other remotely sustained conditions | **P:** condition list plus source-building/world-site adapters | E + T250 | Relevant condition or source appears/changes |
| Royalty: psychic state | Psychic drone mood effects, neural heat, psycast-induced aggression, skip relocation, neuroquake aftermath | **V:** mood/hediff/location observations. **P/U:** ability and psychic-resource adapters | E + T60/T250 | Unexpected psychic effect, relocation, capacity loss, or resource depletion |
| Royalty: permits and obligations | Trooper/labor arrivals, orbital strikes, bestowers, hospitality/lending, noble work restrictions | **P:** action/quest receipts, group arrivals, role/work prerequisites | E + B/T250 | Unapproved helper/strike/departure; actor becomes unavailable |
| **Ideology: rituals and gatherings** | Actors diverted; injury, sacrifice, recruitment, goodwill or mood outcomes | **P:** current jobs/group state and ritual outcome adapter; exact interface **U** | E + T250 | Unapproved ritual or outcome; required actor diverted |
| Ideology: belief/role changes | Conversion, crisis, role assignment, work prohibitions, precept-related mood | **P:** pawn ideology/role trackers; mood and work checks | E/P + T600/B | Relevant role/belief/work prerequisite changes |
| Ideology: slavery/prisoners | Rebellion, escape, suppression loss, prisoner aggression/recruitment | **P:** guest/slave trackers, mental state, control and availability | E + T60/T250 | Unapproved rebellion/escape/control change |
| Ideology: facilities and linked beings | Biosculpting absence, neural-supercharger effects, dryad production/link changes | **P/U:** selected component/holder adapters; pawn and hediff deltas | E + T250/B | Actor enters an unavailable state; unexpected linked pawn/effect |
| **Biotech: pregnancy/children/vats** | Labor, birth, growth-vat transitions, childhood stage/work eligibility changes | **P:** pregnancy/age/holder adapters and existing birth observations | E + T250/T600 | Unplanned birth/labor/stage transition; actor eligibility changes |
| Biotech: genes and dependencies | Metabolic hunger changes, drug dependency, genetic sickness, xenogerm effects, unusual tolerances | **P:** gene/need/hediff trackers; exact specialized fields **U** | B + T250/T600 | Dependency/health deadline crossed; declared tolerance or metabolism changes |
| Biotech: sanguophage states | Hemogen shortage, deathrest, forced rest, special injury/death behavior | **P/U:** needs/genes/hediffs and actor availability; verify exact state semantics | E + T250 | Required actor enters unavailable state or violates resource prerequisite |
| Biotech: mech control | Energy depletion, mechanitor loss, bandwidth/control change, gestation, boss summons | **P/U:** mechanitor/mech trackers and relevant components; generic actor/arrival observations | E + T250 | Required mech unavailable/uncontrolled; unapproved gestation or boss encounter |
| Biotech: pollution | Wastepack decay/burning, tox gas, toxic buildup, polluted terrain, cocoon emergence | **P:** wastepack state, pollution/gas cells, hediff and structure deltas; specialized APIs **U** | E + T250/T600 | New relevant exposure/pollution; dangerous wastepack transition or cocoon emergence |
| **Anomaly: escalation** | Monolith progression, anomaly activation, endgame/darkness changes | **P/U:** relevant game component, conditions, quests, and structure state | E + T250/B | Undeclared activation/escalation affecting the row |
| Anomaly: entities and attacks | Sightstealers, revenants, shamblers, fleshbeasts, devourers, nociosphere and other entity threats | **P:** pawn/effect observations and def-specific adapters. Hidden/invisible coverage **U** until proved | E + T60 | Unapproved entity/effect; abduction, swallowing, hypnosis, incapacitation |
| Anomaly: containment | Escape attempts, broken containment, held entity changing state | **P/U:** containment holders/buildings and strength/state adapter | E + T250 | Escape-risk threshold crossed; containment fails |
| Anomaly: covert pawn changes | Metalhorror infection/evidence, cube obsession, inhumanization, duplication, unnatural-corpse behavior | **P/U:** selected hidden-state/hediff/component adapters plus public evidence events | E + T250/B | Unapproved relevant state/evidence; actor identity or behavior changes |
| Anomaly: spreading hazards/pocket maps | Flesh growth, pit gates, obelisk transport/mutation, unnatural darkness, blood rain, cult rituals | **P/U:** conditions, region fingerprints, ritual/entity adapters, map/roster transitions | E + T60/T250 | Unapproved spread, transport, mutation, ritual, or environmental hazard |
| **Odyssey: gravship/shuttle transit** | Launch, landing, map transfer, held passengers, stranded actors/specimens | **P/U:** verified transport/gravship adapters plus map and roster transitions | E + B/T60 | Undeclared transit; expected passenger/specimen fails to arrive |
| Odyssey: vacuum/life support | Breach, oxygen/life-support failure, unsafe apparel/exposure, power loss | **P/U:** room/environment and equipment adapters; power/health fallback | E + T60 | Actor’s enclosure/equipment becomes unsafe; required life support fails |
| Odyssey: dynamic terrain/weather | Floods, lava, freezing/melting water, thin ice, volcanic impacts; severe visibility/movement/weather changes | **P/U:** targeted terrain/weather/hazard adapters and exposure observations | E + T60/T250 | Hazard reaches scope; access/support/visibility prerequisite changes |
| Odyssey: destinations/endgame | Temporary map expiry, dangerous landmarks, orbital encounters, mechhive progression, drones | **P/U:** map/site/quest and encounter adapters; general threat census | E + B/T250 | Map expiry overlaps row; unapproved encounter/progression or drone arrival |

Royalty’s clusters include factories, reinforcement beacons, turrets, and condition-producing structures; counting active mechs alone misses much of their risk. [Official Royalty description](https://store.steampowered.com/app/1149640/RimWorld__Royalty/).

Ideology rituals can alter mood, recruits, and goodwill, while roles can restrict work. [Ludeon’s roles and rituals description](https://ludeon.com/blog/2021/07/ideology-adds-social-roles-and-rituals/). Biotech wastepacks can deteriorate into pollution or release tox gas when damaged, and pollution interacts with dormant insect cocoons. [Ludeon’s pollution description](https://ludeon.com/blog/2022/10/biotech-preview-2-combat-mechanoids-pollution-and-super-mechanoid-bosses/).

Anomaly explicitly includes covert infection, obsession, containment, duplication, transport, and threats beyond ordinary visible combat. [Official Anomaly description](https://store.steampowered.com/app/2380740/RimWorld__Anomaly/). Odyssey adds flooding, lava, freezing water, and consequential weather, while orbital survival requires airtight protection and life support. [Ludeon’s terrain/weather description](https://ludeon.com/blog/2025/06/odyssey-preview-1-map-features-landmarks-and-biomes/), [gravships and space](https://ludeon.com/blog/2025/06/odyssey-preview-2-gravships-and-space/).

**Hidden-state visibility must be declared.** Internal diagnostics may observe a concealed infection; a player-equivalent integration test should not let the driving agent use information a player would lack. Record privileged evidence separately from agent-visible observations.

### 2.6 Covering 600 mods without pretending this is a complete source inventory

Add a cheap baseline capability inventory:

- **V:** enumerate loaded incident, condition, weather, hediff, mental-state, and relevant thing definitions through `DefDatabase<T>`.
- Record active condition defs, relevant components/runtime types, held populations, pending mechanisms, and defining packages.
- Permit source-specific adapters with stable IDs, switches, coverage declarations, and measured costs.
- Report an unfamiliar active mechanism as **unclassified**, while continuing to watch its observable effects.

Definition ownership is an investigative clue. It neither proves causation nor makes an effect expected.

There is no finite vanilla hook list that intercepts every direct mutation arbitrary mod code can perform. The monitor’s stronger claim is: **the row’s required state and relevant effects were covered**, with explicit gaps.

### 2.7 Storage and implementation

**Record every spawned pawn’s cheap vitals in bounded structured history. Put aggregates in VictoriaMetrics.**

| Destination | Suggested content |
|---|---|
| Raw JSONL / capped flight recorder | Per-pawn samples/deltas, arrivals/departures/deaths, conditions, windows, action receipts, disturbances, coverage |
| SQLite | Indexed pawn/event history, row intervals, evidence references, verdicts, control interventions |
| VictoriaMetrics | Counts by bounded categories, minimum actor health/mood margin, bleeding/downed counts, threat/fire counts, modal age, clock discontinuities, observer health |
| RimPulse | Latched critical disturbances, stalled runs, coverage failure; links to the row/evidence |

Avoid putting pawn ID, job target, letter text, quest ID, or run ID on every long-lived metric series. Keep them in records and event links.

Additional requirements:

- Include **membership events and death tombstones**, not merely current counts.
- Mood/food/rest absent on a pawn are **not applicable**, never zero.
- Preserve max severity and transition events between rollup exports.
- Do not interpolate per-pawn history across a clock discontinuity or coverage gap.
- Copy bounded scalar data before background serialization; writer threads never traverse game objects.
- Avoid routine stack traces, renderer initialization, full pathfinding, and full-map cell scans.
- Contain observer exceptions, preserve game exceptions, and expose observer faults.
- Verify Harmony postconditions: a postfix alone does not prove the original operation ran.
- Measure the whole observer cost, including Harmony dispatch, scanning, allocations, serialization, and writer backlog.

Use the supplied telemetry skill’s per-source switches, unavailable-state rules, and decommission ledger. The existing mandatory overhead gate still applies to broader always-on deployment.

## 3. What else to install: prevention and control, ranked

Costs are relative engineering estimates. Compatibility with the mod stack can dominate them.

| Rank | Installation | Value / cost | Risk to test validity: what it could hide |
|---:|---|---|---|
| **1** | **Safe time-advance interface** | Very high / medium | Bounded ordinary stepping has low distortion. Calendar rewriting or selective ticking has high distortion |
| **2** | **Row governor with local tripwires** | Very high / medium | Stopping limits the observable sequence; retain evidence and mark incomplete criteria UNMEASURED |
| **3** | **Known disposable fixtures and reload between rows** | Very high / low–medium | Clean fixtures omit messy campaign interactions; declare that scope |
| **4** | **Actor/specimen prerequisite gate** | Very high / low | Narrow prerequisites reduce integration coverage; they prevent meaningless timeouts and stale samples |
| **5** | **Scoped quiet-world profile** | High / medium | Suppresses storyteller-dependent pacing and interactions; preserve mechanisms under test |
| **6** | **Modal broker with explicit handlers** | High / medium | Automatically choosing or dismissing consequential dialogs can hide broken flows |
| **7** | **Mutation lease and operation budgets** | High / low–medium | Minimal behavior distortion; can expose previously unnoticed owner/agent concurrency |
| **8** | **Verified incident/delivery gates** | High / medium–high | Suppression changes quest/event outcomes; direct mod effects remain possible |
| **9** | **Checkpoint/reload around destructive rows** | High / medium–high | Save/load itself changes lifecycle and may not restore unsaved static/mod state |
| **10** | **Environmental fixture presets** | High / low–medium | Fixed weather, temperature, power, and relations hide environmental compatibility defects |
| **11** | **Ordinary witness pawns and reference specimens** | Medium–high / low–medium | Witnesses change population, wealth, pathing, social interactions, and targeting |
| **12** | **Visitor quarantine/removal policy** | Medium / medium | Removal changes reservations, social effects, threat targets, and subsequent behavior |
| **13** | **Synthetic job executor / dedicated worker** | Medium / medium | Directly forcing work bypasses scheduling, priorities, travel, reservations, and needs |
| **14** | **Immortal or auto-maintained support colonists** | Medium / medium | Hides health, damage, starvation, rescue, death-trigger, and mood interactions |
| **15** | **Faction-relation pins** | Medium / low–medium | Hides retaliation, betrayal, diplomacy, and relation-dependent behavior |
| **16** | **Quest/scenario suppression adapters** | Medium / high for comprehensive coverage | Can silently skip signals, deadlines, rewards, or consequences |
| **17** | **Deterministic event schedules and paired runs** | Medium / medium–high | Scripted schedules omit natural timing interactions; matching seeds does not ensure replay |
| **18** | **Spatial quarantine or freeze fields** | Limited / high | Can break movement, targeting, projectiles, heat, power, and cross-boundary effects |
| **19** | **General component/pawn/world freeze** | Poor default / very high | Often freezes the implementation being tested; global clocks may keep advancing |

### 3.1 Safe time advance: the most valuable control

Expose three distinct operations:

| Operation | Policy |
|---|---|
| **Advance ordinary simulation by N ticks** | Budgeted, interruptible, checks tripwires between small chunks |
| **Initialize a fixture’s date/time** | Allowed during fixture creation before introducing actors and age-sensitive specimens; receipt and baseline required |
| **Reassign live game/calendar time** | Refused by default during validation; narrowly declared temporal tests only |

A ten-day advance is approximately **600,000 ordinary ticks**. It is a substantial simulation run, with hunger, weather, combat, quests, health, and decay opportunities—not a lighting adjustment.

We do not yet know whether the supplied “warp” executed ticks, reassigned clocks, or combined mechanisms. Record that distinction explicitly.

A safe advance should require:

- Current epoch/map and a fresh prerequisite report.
- Actor IDs, critical specimen IDs, and expected population.
- Maximum total elapsed ticks, including setup.
- Permitted condition/weather/arrival changes.
- Healthy required monitor coverage.
- An interruptible execution path and cancellation deadline.

Start with chunks no larger than **60 ticks**, tightened for hazardous tests. Urgent event latches can request interruption earlier. This reduces response latency; it does not guarantee that a lethal event cannot complete within one tick.

**Setting pause is insufficient if a forced stepping loop ignores pause.** The loop itself must check cancellation.

For “mid-summer noon,” prefer a prepared fixture initialized at that time. Introduce the ash and pawns afterward. Do not advance a populated, perishable fixture merely to obtain lighting.

### 3.2 The row governor

Use a local state machine:

```text
PRECHECK → ARMED → EXECUTING → CHECKING → COMPLETE
                     │
                     └→ DISTURBANCE_LATCHED → CAPTURE → STOP/RECOVER
```

The latch should:

- Stop additional mutations and interrupt eligible stepping.
- Request pause where appropriate.
- Preserve the first trigger and later consequences.
- Capture actors, specimens, threats, clocks, conditions, windows, recent events, and coverage.
- Return a structured disturbance result rather than allowing a job timeout to masquerade as a mod failure.

Critical triggers include required actor death/downing, dangerous attack, specimen loss, forbidden time operation, unexpected map change, blocked modal deadline, and required observation failure.

**The governor must remain useful while external telemetry ingestion is unavailable.**

### 3.3 Modal handling

Install a **modal broker**, not “close every dialog.”

| Window class | Handling |
|---|---|
| Explicitly expected test window | Validate identity/content/state; use the declared handler |
| Known harmless acknowledgement | Capture evidence, then dismiss through an approved handler |
| Choice, confirmation, quest, trade, save/load, or destructive dialog | Stop dependent actions; explicit workflow required |
| Unknown mod window | Capture type/identity and block dependent execution |
| Reappearing window | Escalate repeated blockage; never create an infinite dismiss loop |

Acknowledging the colony-loss letter does not recover the colony or restore row validity.

### 3.4 Isolation, protection, and rollback

A sandbox should be a **named profile composed of narrow controls**, with read-back and intervention receipts. Storyteller-off is one control; it does not stop existing threats, quests, deliveries, disease, needs, hives, or arbitrary mod tickers.

Use ordinary protected support pawns where possible: safe housing, adequate supplies, controlled jobs, and explicit actor selection. Make immortality or auto-healing opt-in and exclude it from damage/health/needs/death validation. Record attempted harm before any repair.

For rollback, prefer **save checkpoint plus verified reload** over an ambitious in-memory undo system. Reload does not necessarily reset static fields, external files, outstanding work, or unsaved mod state. Revalidate the fixture afterward; restart the process when the reproduction contract requires it. Telemetry remains historical evidence and must not be rolled back.

Honor the owner’s existing visitor decision: **capture → remove/quarantine → continue unless disruption is evidenced or relevant validity becomes unknowable**. Removal itself gets an action receipt. It does not erase prior damage, consumed resources, or altered jobs.

## 4. Feeding observations into CLEAN / DISRUPTED / INDETERMINATE

Keep two independent dimensions:

```text
criterionResult = PASS | FAIL | UNMEASURED
rowValidity     = CLEAN | DISRUPTED | INDETERMINATE
```

| Validity | Meaning |
|---|---|
| **CLEAN** | Required coverage exists; prerequisites and declared environment held; no evidenced disturbance invalidated the measurement |
| **DISRUPTED** | A disturbance demonstrably changed a required actor, specimen, resource, timing assumption, or environment |
| **INDETERMINATE** | Required coverage or prerequisites cannot be established, or a plausible relevant disturbance cannot be resolved |

A global “far from bland” alert should carry a separate severity. Expected combat can be severe and still CLEAN.

### 4.1 Each row needs a compact contract

Declare before execution:

| Contract field | Example |
|---|---|
| Scope | Map, region, setup-through-measurement interval |
| Required actors | Pawn IDs; alive, available, capable of assigned work |
| Critical specimens | Thing IDs; permissible age/state/HP/location |
| Time budget | Setup and measurement budgets; no live clock reassignment |
| Expected transitions | Specific spawn, injury, condition, letter, modal, or job change |
| Bounds | IDs/types, count, target, region, magnitude, timing |
| Protected invariants | Support pawn survives; reference ash remains; bench powered |
| Required coverage | Pawn monitor, clock ledger, specimen reads, UI watch |
| Permitted controls | Storyteller gate, fixed weather; no auto-heal on subjects |

Expectation matching should be **field-specific and bounded**. An expected spawn must not also authorize an unexpected attack, faction change, or extra twenty pawns.

Never permit everything owned by the mod under test. Its accidental extra pawn or condition is exactly the regression the harness may need to detect.

### 4.2 Example verdicts

| Observation | Result |
|---|---|
| Mod intentionally spawns a hostile test subject; declared targets and boundaries hold | Expected; may remain CLEAN |
| Expected subject unexpectedly kills a protected support pawn | Contract violation; criterion may FAIL and validity is DISRUPTED |
| Mech attack downs the worker; worker-job assertion times out | DISRUPTED; timeout does not establish a mod defect |
| Unrelated visitor appears, is removed, and no relevant effect occurred under covered scope | Record anomaly/intervention; may remain CLEAN |
| Visitor consumed the required ingredient or injured the actor | DISRUPTED |
| Unknown pawn origin, but its identity/effects match the declared contract | Origin uncertainty alone does not prevent CLEAN |
| Relevant interval loses pawn/clock coverage | INDETERMINATE |
| Ash disappears during unapproved elapsed time before sampling | DISRUPTED; failed ash criterion is not established |
| Ash fails to persist in a clean, declared lifetime test | Criterion FAIL; validity CLEAN |
| Expected destructive test kills its subject | Expected; may remain CLEAN |
| Unexpected modal blocks execution before the operation completes | DISRUPTED if blockage is established; completion-dependent criterion UNMEASURED |
| Game reloads midway through a row | INDETERMINATE unless explicitly part of the row protocol |

Preserve demonstrated defects even when the row is also disrupted. Do not let validity become a mechanism for discarding inconvenient failures.

For attribution, **“this event preceded the failure” is weaker than “this event changed the actor/specimen required by the assertion.”** Prefer direct damage, availability, resource, and lifecycle evidence over temporal coincidence.

Publish a north-star success only when required criteria pass **and** row validity is CLEAN. Store the first disturbance tick and evidence references with every non-clean verdict.

## 5. Minimal first build that catches the measured failures

Build **six channel groups and two controls**, reusing the existing awareness and telemetry infrastructure.

| Channel group | Minimum contents |
|---|---|
| **1. Pawn census/vitals** | Every spawned pawn: ID/map, alive/downed, health, bleeding, mood if applicable, mental state, faction/threat; retained deaths and required-actor roster |
| **2. Threat changes** | Pawn arrivals/aggression plus new dormant mech/hostile structures; reuse incident journal |
| **3. Clock/action ledger** | Requested/executed ticks, game/calendar clocks, discontinuities, epoch, pause/speed |
| **4. UI/notifications** | Blocking-window type/age; new letters including colony-loss; wall-time coverage while paused |
| **5. Critical subjects** | Required worker availability/job progress; specimen identity, existence, age/state where observable |
| **6. Coverage heartbeat** | Arm state, TTL, sampling/event gaps, failed reads, dropped records, governor availability |

The two controls:

1. **Safe advance gate:** refuse live time reassignment and over-budget advances; ordinary stepping is chunked and interruptible.
2. **Row governor:** latch relevant threats/actor loss/specimen loss/modal blockage, stop dependent execution, capture evidence, and emit a non-clean verdict.

This would address the supplied cases:

- **Ten-day advance:** refused before mutation. If an uncontrolled route still changes time, the ledger latches it; pawn and specimen records expose its effects.
- **Mech wipeout:** threat changes interrupt the worker wait; injury/downing/death establishes disruption.
- **Stale modal:** wall-time UI watch detects blockage while ticks are paused and prevents later actions from silently cascading.

Do not make safe stepping conditional on deploying full provenance. It needs current state and control coverage, not an explanation of every pawn’s creation.

### Required acceptance proofs

| Injected case | Required result |
|---|---|
| Request 600,000 ticks on populated/perishable fixture | Refused before clocks, actors, or specimens change |
| Direct game-clock or calendar-clock reassignment | Distinct discontinuity detected; active row cannot certify CLEAN |
| Pawn dies and corpse disappears before next sample | Death remains in event history and required roster |
| Dormant cluster with turret/assembler but no active attacking pawn | Threat detected before relying on a hostile-pawn count |
| Raid during one long bridge stepping call | Call interrupts locally; external alert is supplementary |
| Worker becomes downed during job wait | DISRUPTED; no ordinary mod FAIL from timeout |
| Ash disappears before final read | Subject-state violation identified; false FAIL blocked |
| Modal appears while paused | Wall-time detection works; dependent actions stop |
| Expected mod hostile/injury plus unintended extra effect | Expected transition accepted; extra effect still flagged |
| Actor legitimately transfers maps | Transfer distinguished from death; row scope evaluated correctly |
| Monitor expiry, read failure, queue overflow, or unavailable source | Coverage failure prevents CLEAN |
| Hook skipped/replaced, observer throws, or game reloads | No invented event; fault/epoch boundary visible; game exception behavior preserved |

Measure both the 23-mod tier and full list. Compare armed/off repeated workloads, including busy pawn maps, arrivals, health changes, paused UI, and long stepping. Each source keeps its own measured cost and removal switch. An unexercised hook remains **UNMEASURED**, not “free.”

## 6. Four decisions for the owner

1. **Default validation environment:** use isolated fixtures for mechanism rows and a separate integration suite? **Recommended: yes**, with all five DLCs loaded in both.
2. **Time policy:** refuse live clock reassignment and multi-day fast-forward in ordinary validation, using prepared seasonal/daylight fixtures instead? **Recommended: yes**; temporal tests receive explicit exceptions.
3. **Recovery after evidenced disruption:** stop, capture, and reload by default, with continued diagnostic execution explicitly selected? **Recommended: yes**. Harmless visitors retain the existing record/remove policy.
4. **Pawn protection:** ordinary support pawns with survival tripwires, or immortal/auto-maintained support pawns? **Recommended: ordinary by default**, with labeled protection only for suites whose assertions do not depend on health, needs, damage, or death.