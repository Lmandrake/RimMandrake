# 1. What the plan gets wrong or misses

## Incident queue, storyteller, and map events

- `enableStoryteller=false` is not a general event freeze. It does not stop:
  - already queued incidents;
  - quest parts and site/map-parent logic;
  - map components and condition components;
  - pawn/lord logic;
  - mod-specific tickers that directly call incident workers;
  - forced debug incidents.
- `IncidentQueue.Clear()` is global and destructive. It may remove expected delayed incidents for another map, quest, or later component. Add queue inspection and selective removal before using it routinely.
- Clearing the queue once is racy: a quest or mod can enqueue another incident on the next tick.
- `threatScale=0` and `allowBigThreats=false` do not suppress forced incidents, site defenders, quest raids, infestations, manhunters, or direct pawn spawning.
- The E4 resident-faction attack may originate from map-parent/site generation or lord logic, not the storyteller queue.
- `game_condition end` is not necessarily durable. Permanent, quest-owned, site-owned, or mod-maintained conditions may be recreated immediately.
- `ForceWeather` is itself a game condition. `lock_weather("Clear")` must declare that condition expected and later remove precisely the condition it created.
- `rain_suppress` plus forced clear weather is redundant unless a test later releases the weather lock.
- Debug settings and difficulty are process/game-global, not safely map-scoped. Running against a human save or multiple maps is hazardous.
- The restoration design is incorrect: it says settings are restored from a baseline captured after `prepare_bland_map` changed them. Capture a pre-mutation transaction record first.

## Raids, hostility, predators, and manhunters

- `isPlayer` or faction `"player"` does not mean colonist. It may include livestock, player mechs, slaves, or other player-faction pawns. The census needs `isColonist`, `isSlave`, `isPrisoner`, race category, and map ownership.
- `HostileTo(Faction.OfPlayer)` is not a sufficient threat predicate:
  - predator hunting is target-specific and may not make the animal generally faction-hostile;
  - berserk player pawns can be dangerous without belonging to a hostile faction;
  - neutral quest pawns can have hostile jobs or duties;
  - dormant threats can be faction-hostile without currently attacking.
- Proximity plus a later Bite/Scratch is not a `predator_hunting` detector. It is delayed attribution with many false positives.
- Predator selection depends on hunger, reachable prey, prey body size/combat power, reservations, food availability, and the actual `PredatorHunt` job target.
- Manhunter state must come from mental state or attack job, not localized letter text.
- Raids have phases: queued, announced, skyfallers/transport pods, spawning, lord assembly, assault, flee, and reinforcement. A pawn census observes only some phases.
- Drop-pod raiders can be inside holders and absent from spawned-pawn lists. A 600-tick grace period is not enough for every arrival mode.
- Raids are not the only hostile threat: infestations, mech clusters, dormant mechs, hives, hostile shuttles, siege equipment, quest assaults, and berserk colonists need coverage.
- “Hostile more than 40 cells away and not moving” cannot be computed from the proposed snapshot. It needs position history or `curJob`/movement state.
- Killing current hostiles does not end their lord, siege, hive, spawner, transport pod, or scheduled reinforcements. “Kill anyone hostile again” needs a quiescence operation, not a one-shot census.
- Using `Bomb 99999` is unsafe: it can damage nearby pawns and items, ignite fires, destroy gear, and manufacture the surprise being diagnosed.
- Destroying `categories=Item` at a corpse cell can erase dropped apparel, weapons, test objects, and unrelated stacks. Dispose of exact IDs only.
- Killing neutral strangers can alter goodwill, produce thoughts or letters, and break quests. Prefer scoped despawn on a disposable map, with exact exclusions.

## Mood, thoughts, needs, and mental states

- “Lower `colonistMoodOffset`” has the sign backwards. A higher positive offset improves mood.
- Mood is not restored by filling Food/Rest/Joy. It also reflects:
  - memories and situational thoughts;
  - pain and health;
  - expectations;
  - beauty, room, outdoors and comfort;
  - ideology/precepts/roles;
  - genes, traits, psychic effects, drugs and withdrawal;
  - recreation variety and chemical needs.
- Writing the mood need directly is transient and will be recomputed.
- Clearing all bad memories would remove the mod behavior under test. Restoration must remove only post-baseline nuisance memories, preferably by exact thought instance/source.
- `RecoverFromState` does not guarantee stability. A hediff, ability, lord duty, low mood, or mod ticker can reapply the state next tick.
- Mental-break recovery may leave breaker state, cooldowns, jobs, drafted state, reservations, or social consequences behind.
- Disabling random mental states is not proof that social fights, ability-driven states, quest states, or mod-driven states are disabled.
- Chemical, hemogen, deathrest, psyfocus, mech energy, gene-specific, and modded needs are absent from `restore_needs`.

## Hediffs, healing, downing, and death

- Diffing only hediff defs misses:
  - severity growth;
  - the same hediff on a new body part;
  - multiple instances of one def;
  - immunity/tend-quality changes;
  - scars becoming painful;
  - bleeding changes without a new def.
- “Remove every injury/disease hediff” is not a safe heal-all operation. It can remove pregnancy, immunity, addictions, chronic conditions, mod state, implants represented as hediffs, and the subject of the test.
- Restoring missing parts can conflict with prosthetics and implants or create an anatomy different from the baseline.
- The correct target is a selected baseline delta, not generic perfect health.
- `bleedRate==0`, alive, and not downed is insufficient. Consciousness, moving, manipulation, pain, lethal severity, temperature injuries, and vital-part state also matter.
- Resurrection cannot undo death history: tales, records, relations, thoughts, ideology consequences, corpse handling, dropped equipment, lord membership, and other mod callbacks have already happened. Aborting after death is correct.
- Death letters and `colonistsKilled` do not establish cause. Capture incremental damage/hediff changes, instigator, weapon/damage def, combat log, environment, and prior downing.
- Relevant death causes include blood loss, destroyed vital parts, disease, toxins, starvation, temperature, roof collapse, explosion, fire, childbirth, surgery, execution, animal predation, social fights, and mod callbacks.
- The roughly 601-tick E1 cadence suggests a tick-interval mechanism but does not identify it. It could also reflect the harness’s observation cadence.
- `story_stats.colonistsKilled` is a global aggregate and cannot identify a pawn or map. Aggregate it with letters and pawn transitions into one event rather than emitting duplicate hits.

## Letters and alerts

- `arrivalTick > t0` loses letters created at exactly `t0`. Use a baseline multiset or stable letter identity/fingerprint plus arrival tick.
- Multiple letters can share label and arrival tick.
- Letters can be dismissed, archived, replaced by dialogs, or never generated because notification settings suppress them.
- Choice letters, quest letters, and modded letters may have richer fields than `RawText`.
- A death or raid can be silent; letters are corroboration, not the primary detector.
- LetterDef severity is not equivalent to event severity. A `NegativeEvent` may be harmless to the test, while a neutral-looking mod letter may announce destructive behavior.
- Alerts are recomputed state, not an event log. They may lag, disappear, localize differently, or be suppressed by UI state.
- Map attribution is mandatory in multi-map games. A letter lacking `mapId` should not be allowed to produce a map-local fatal result by itself.

## Fire, corpses, meat, and item fate

- Fire detection must distinguish newly created fire, baseline fire, fire attached to a pawn/thing, and fire that escaped an expected rect.
- A one-tick screenshot refresh can let fire spread, apply damage, detonate something, or kill a pawn. That is evidence mutation.
- Extinguishing every map fire can break a fire-related test even when the originating fire was expected.
- A corpse or meat stack can:
  - rot or dessicate;
  - be eaten directly;
  - be butchered or cooked;
  - merge or split stacks;
  - be hauled into storage;
  - enter inventory, a building, a transport pod, or caravan;
  - be destroyed by fire, explosion, roof collapse, deterioration, or a mod.
- A vanished ID is not a vanished quantity. RimWorld routinely destroys one stack ID during merging and creates/splits others.
- Nearby `Filth_*` is not proof of rot, and an “Ate” thought does not identify which ingredient was consumed.
- Forbidding does not stop rot, fire, explosions, stack merging, every animal, or every modded job.
- A sealed wall changes temperature, reachability, room thoughts, pathing, and sometimes the mechanism being tested.
- Item validation needs holder traversal and quantity/lineage tracking, not only map-cell searches.

## Pausing and ticking

- `step_game_ticks` while paused performs real simulation. Health, AI, turrets, explosions, conditions, jobs, and incident processing can all run.
- Some bridge mutations cause immediate state transitions without a tick; others schedule work for the next tick. Each tool needs measured semantics.
- Two equal `ticksGame` reads do not prove a durable pause. They can occur within the same rendered frame or while a modal temporarily blocks ticking.
- UI rendering, bridge work, long events, and Unity updates can proceed while simulation ticks are paused.
- A running game can advance between the “after” read of one verb and the “before” read of the next. Charge from a single global `last_seen_tick`, including every pre-call observation.
- A 600-tick sweep is detection, not prevention. Ten in-game seconds is enough for attacks, explosions, bleeding, ingestion, hauling, and fire spread.
- Helpers that step one tick are spending game time. “Helper time is not charged” contradicts the central rule. Charge it to an overhead ledger and the hard session cap.
- Save/load or map changes can make tick readings unavailable, discontinuous, or lower. The budget needs an explicit epoch reset; never interpret a negative delta as free time.

## Harness-level issues

- “Idempotent” is too strong for killing, resurrecting, closing dialogs, clearing incidents, or stepping ticks. Require convergence to a postcondition and record side effects.
- Default `heal_and_continue` is unsafe. Default should be `abort`; automatic recovery should be limited to explicitly declared nuisance classes before the component’s decisive observation.
- `PASS(INTERVENED)` should not count as GREEN. It is an invalidated or diagnostic completion.
- Expectations need lifetimes and scope. An expected raid during one phase must not suppress a second raid later.
- An expected entity still needs monitoring for unintended death, movement, damage, or escape. “Expected” must suppress only its presence alarm.
- There is a race between spawning a subject and calling `expect_presence`. Provide an atomic “expect this mutation’s result” context.
- `prepare_bland_map` before every chain can destroy intended cross-chain state. Either declare chains isolated or reload a pristine checkpoint.
- A dedicated disposable test save is substantially safer than attempting to sanitize an arbitrary live map.
- Full-map clear operations need a dry-run manifest and must refuse to act when protected pawns, holders, roof supports, quest objects, or unknown defs are present.

# 2. Additional detectors and helpers

## Detectors

| Name | What it reads | Fires when | False-positive risk |
|---|---|---|---|
| `pending_incident` | New queue-peek tool: incident def, fire tick, target/map, source | An unapproved incident targets the active map | Quest/world incidents may be legitimate; never infer solely from def |
| `threat_in_transit` | Skyfallers, drop pods, transport holders, shuttle contents, arrival mode | Hostile or unknown pawns are inbound but not spawned | Player cargo pods and friendly shuttles |
| `active_threat_source` | Lords, duties, hives, spawners, siege blueprints, mech-cluster activators | Killing pawns will not stop the threat | Dormant/expected encounter machinery |
| `aggressive_job` | G1 mental state, job def, job target, duty/lord | Any pawn is actively targeting a protected pawn or thing | Drafted combat and deliberate test attacks |
| `predator_targeting` | PredatorHunt job target, hunger, prey ID, reachability | A protected pawn/animal is the selected prey | Expected predator/prey tests |
| `expected_contract_broken` | Expected IDs/defs plus census and thing-fate | Expected subject died, despawned, changed faction, left rect, or lost required state | Deliberately transient subjects need deadlines/phases |
| `pawn_roster_transition` | Baseline colonist IDs plus map/world/holder state | Birth, join, kidnapping, caravan exit, disappearance, faction change | Tests intentionally adding/removing pawns |
| `health_progression` | Hediff instance, part, severity, bleed, immunity, tend quality, capacities | Existing harm worsens even though no new def appears | Disease/healing tests must declare expected trajectories |
| `lethal_exposure` | Outdoor/cell temperature, toxic/gas state, pawn safe range and hediffs | Protected pawn is approaching heat, cold, toxic, or gas injury | Temperature/condition tests |
| `recent_damage_source` | New companion ring buffer of damage events: victim, def, amount, instigator, weapon, tick | Protected pawn receives undeclared damage | Deliberate test damage must carry an action correlation ID |
| `tracked_item_job` | Pawn jobs, reservations and targets for tracked things | Haul, ingest, butcher, load, refuel, construct, or destroy job targets an item | Expected interaction tests |
| `tracked_quantity_changed` | Thing-fate, holders, stack lineage, total quantity by tracking tag | Quantity falls or changes holder unexpectedly | Recipes and intentional stack operations |
| `rot_risk` | CompRottable progress/stage, ambient temperature, holder, refrigeration/power | Tracked perishables will rot within the next budget window | Tests intentionally studying rot |
| `roof_or_collapse_risk` | Roof grid, support reachability, damaged supports, falling-roof things | Protected area is unsupported or collapse has begun | Mining/building tests |
| `map_context_changed` | Current map unique ID, tile, parent, biome, active-map ID | Calls or evidence moved to a different map | Intentional caravan/map-transition tests |
| `settings_drift` | Debug settings, difficulty, storyteller def, time speed | Another actor or tool changed the safety envelope | Human intervention or parallel harness |
| `long_event_or_transition` | Long-event state, loading screen, current program state, map availability | Reads are being taken during load/generation/transition | Brief harmless UI transitions |
| `evidence_truncated_or_stale` | Completeness flags, snapshot tick, map ID, call timestamps | Inputs belong to different ticks/maps or are incomplete | Slow full snapshots; treat as evidence invalidity, not game surprise |

## Helpers

| Name | What it reads before acting | Action and verification | Mutation risk |
|---|---|---|---|
| `settings_transaction` | All debug, difficulty, storyteller, weather-lock and speed values before mutation | Restore exact pre-run values in `finally`; verify every field | Mods may change the same settings concurrently |
| `reload_bland_checkpoint` | Save ID, map ID, mod list/hash, active map | Reload a disposable pristine save and verify fingerprint | Resets tick epoch; cannot support cross-chain state |
| `remove_incidents_scoped` | Queue entries with target/source/fire tick | Remove only disallowed entries targeting this map | Requires a new selective queue tool; quest semantics can still be harmed |
| `quiesce_hostile_wave` | Inbound carriers, lords/spawners, hostile census, expected IDs | Neutralize exact sources and pawns, then verify no inbound source remains | Can invalidate raid/AI tests; bounded arrival ticks must be charged |
| `neutralize_exact_pawn` | Pawn ID, nearby protected things/pawns, holder/lord | Direct non-explosive kill/despawn; verify exact pawn state | Death callbacks, goodwill, loot, thoughts |
| `dispose_exact_things` | Exact corpse/item IDs and holder contents | Destroy only named IDs; verify unrelated cell contents unchanged | Corpse callbacks or references may still observe destruction |
| `stabilize_to_baseline` | Per-instance health/need/mental baseline and current delta | Reverse only approved post-baseline deltas; verify capacities and state | Never makes a post-death component valid |
| `stabilize_mind_inputs` | Current mental state, mood contributors, memories since t0, breaker state | End state and remove only allowlisted nuisance inputs | Can erase the mod’s intended thought or mental behavior |
| `protect_tracked_items` | Holder, reservation, jobs, forbidden state, temperature, stack identity | Cancel targeting jobs; use a tagged holder or controlled cell; verify fate | Protection changes accessibility and may invalidate interaction tests |
| `quarantine_bystanders` | Colonist jobs, zones, position, drafted state, current test requirements | Move/restrict non-subject pawns to a safe area; verify reachability separation | Breaks work, pathing, social, mood, and job tests |
| `clear_rect_safely` | Full manifest of pawns, holders, roofs, supports, quest objects, buildings and items | Refuse on unknown/protected entries; remove exact approved IDs | More conservative and slower than bulk clearing |
| `cancel_dangerous_jobs` | Current job, targets and reservations | Stop hauling, ingesting, attacking, firefighting, deconstruction, or loading | Job cancellation alters AI tests and can leave reservations |
| `restore_environment_transaction` | Conditions/weather/fire present before preparation, including source IDs | Remove only harness-created locks and restore prior state | Source-owned conditions may immediately return |
| `flush_inbound_bounded` | Pending arrivals and remaining diagnostic tick reserve | Step very small charged intervals while repeatedly neutralizing arrivals | Simulation itself can create new harm; never use after decisive evidence |
| `seal_test_subjects` | Subject IDs, room/holder properties, temperature and access rules | Place subjects in a purpose-built controlled enclosure; verify membership | Appropriate only when isolation is not part of the behavior under test |

Companion gaps should therefore add at least: selective incident-queue inspection/removal, damage-event history, holder/stack lineage, colonist-role fields, active lord/duty data, and map identity.

# 3. Better build order

1. **Choose safety semantics first.**
   - Default surprise policy: `abort`.
   - Intervened results do not count GREEN.
   - Run only in a disposable dedicated save.
   - Define map, chain, component, expectation, and tick-epoch scopes.

2. **Investigate E1 before suppressing it.**
   - Reproduce the 601-tick deaths on a disposable map.
   - Capture per-tick health progression, damage source, mod callbacks/logs, and the responsible map.
   - Turn the result into a fixture.

3. **Run a minimal live contract probe.**
   - Measure letter/map shapes, fire lookup, pawn roles, manhunter hostility, paused damage, queue behavior, condition ending, screenshot freshness, and call latency.
   - Record exact bridge versions and raw responses.

4. **Build the central clock gate and pause guard.**
   - One wrapper owns every tick-moving call.
   - Maintain one global `last_seen_tick`.
   - Reject raw step/unpause/order calls without a tick lease.
   - Include overhead and diagnostic ticks in a hard session ledger.
   - Test tick truncation, overshoot, stalls, save/load epochs, and disconnects.

5. **Build the supervisory watchdog.**
   - A `threading.Timer` flag is insufficient for a blocked bridge call.
   - Use a separate supervisor capable of timing out/killing the worker and independently requesting pause when possible.

6. **Define snapshot/event contracts and fixtures.**
   - Include snapshot tick, map ID, completeness, schema version, and source call.
   - Normalize letters, pawn identities, hediff instances, and event fingerprints.
   - Aggregate corroborating signals into one event.

7. **Build the minimal fake from measured contracts.**
   - Start with clock, map identity, pawn census, letters, queue, fire, and screenshots.
   - Model holders, stack replacement, inbound raids, and worsening hediff severity before expanding breadth.

8. **Implement the critical pure detectors.**
   - Evidence validity/truncation first.
   - Then death, downing/health progression, aggressive jobs, inbound threats, fire, item fate, modal/transition, and clock drift.
   - Add expectation lifetimes and atomic expected-mutation registration.

9. **Implement evidence capture before repair helpers.**
   - Persist the triggering snapshot and sidecar first.
   - Make image capture optional and non-blocking.
   - Do not step a tick merely to refresh a screenshot until proven safe.

10. **Implement transactional, exact-ID helpers.**
    - Settings transaction, scoped incident removal, exact pawn neutralization, exact disposal, baseline stabilization, and safe rect clear.
    - Do not begin with explosive killing, bulk item destruction, or blanket healing.

11. **Implement bland-map setup as verification-first.**
    - Prefer checkpoint reload.
    - Capture pre-mutation state before changing settings.
    - Produce a dry-run manifest.
    - Refuse unknown hazards instead of trying to erase them.

12. **Add companion tools in risk order.**
    - Queue peek/remove and map-aware letters.
    - Pawn census/job/lord/predator target.
    - Thing fate/holders/stack lineage.
    - Damage-event history.
    - Baseline-aware health restoration.
    - Bulk exclusions last.

13. **Pilot one short suite in abort-only mode.**
    - No automatic healing.
    - Compare detector results with human observation and game logs.
    - Measure snapshot cost and safe sweep interval.

14. **Run self-inflicted threat cases and screenshot tests.**
    - Include simultaneous events, same-tick letters, drop-pod delay, stack merge, rot, berserk colonist, and existing-heddiff severity growth.

15. **Integrate progressively.**
    - Short suites first, then RED suites, then long-clock suites.
    - Replace 95,000-tick waits with mechanism-specific debug advancement where possible.

16. **Add Jev last, in shadow mode.**
    - Jev should consume stable normalized artifacts, not compensate for missing bridge state.

# 4. Novel Jev uses, ranked

These are additional to unknown-def harm, failure routing, surprise cause, letter triage, log triage, and before/after attribution.

## 1. Vacuous-test and assertion-alignment lint

High value because it catches tests that perform setup but never observe the claimed behavior.

- Type: `choice`
- State: `{test_intent, stimulus_summary, observed_assertion}`
- Choices: `directly_tests`, `reasonable_proxy`, `setup_only`, `tests_different_claim`, `not_stated`
- Exact question: **“How does `observed_assertion` relate to the behavior claimed in `test_intent` after `stimulus_summary`?”**
- Guard type: `noul`
- Guard state: `{observed_assertion}` only
- Exact guard: **“Does `observed_assertion` describe a value or state read back from the game after an action, rather than only an action that was requested?”**
- Use: review flag only; never converts a result to PASS.

## 2. Expected-set overbreadth auditor

Prevents expectations from hiding the very environmental or mod defect the layer is meant to reveal.

- Type: `choice`
- State: `{test_intent, detector, exemption, phase}`
- Choices: `necessary_subject`, `narrow_fixture`, `overbroad_hides_related_harm`, `unrelated_exemption`, `not_stated`
- Exact question: **“Why is `exemption` appropriate or inappropriate for `detector` during this test phase?”**
- Guard type: `noul`
- Guard state: `{exemption}` only
- Exact guard: **“Could this exemption match events or entities other than one explicitly identified test subject, definition, or bounded area?”**
- Use: lint/review. It never edits expectations automatically.

## 3. Semantic oracle for narrative and localization checks

Useful when a test requires a letter, description, thought, quest text, or translated label to convey a specific meaning, not an exact string.

- Type: `choice`
- State: `{required_meaning, observed_text}`
- Choices: `entails`, `contradicts`, `related_but_incomplete`, `unrelated`, `not_stated`
- Exact question: **“What is the semantic relationship between `observed_text` and `required_meaning`?”**
- Guard type: `noul`
- Guard state: `{observed_text}` only
- Exact guard: **“Does `observed_text` state an in-game event, consequence, requirement, or action rather than only a name or flavour phrase?”**
- Use: shadow oracle beside exact structural checks; never sole proof of PASS.

## 4. Pairwise duplicate-failure clustering

- Type: `noul`
- Question: “Do these two normalized failure records describe the same underlying defect despite different names or values?”
- Value: reduces repeated human triage across seeds, mods, and suites.
- Guard: code requires matching operation family or evidence field before asking Jev.

## 5. Failure-evidence quality gate

- Type: `score`
- Question: “How sufficient is this record for a developer to reproduce and distinguish the failure cause?”
- Value: flags findings missing an observed/expected pair, subject identity, phase, or causal evidence.
- Use: report-quality warning, not result routing.

## 6. Metamorphic-run interpretation

- Type: `choice`
- Question: “Is this normalized difference between two seeded runs expected variation, contract-relevant variation, or evidence of state leakage?”
- Value: separates harmless RimWorld randomness from cross-run contamination.
- Code computes all diffs; Jev sees no counts or raw snapshots.

## 7. Test-intent decomposition

- Type: `choice`
- Question: “Which single behavior category does this mod claim primarily require testing?”
- Choices can include `spawn`, `combat`, `health`, `thought`, `incident`, `item_transformation`, `persistence`, `ui_only`, `not_stated`.
- Value: proposes reviewable coverage tags from About/XML descriptions.

## 8. Tool-mutation risk lint

- Type: `choice`
- Question: “From this tool description, is the mutation local/reversible, local/irreversible, global/reversible, global/irreversible, or unclear?”
- Value: catches new bridge tools that should not be allowed inside ordinary components.
- Must be reviewed once per tool/version and cached.

## 9. Save-contamination explanation

- Type: `choice`
- Question: “Does this compact baseline anomaly most plausibly reflect intended fixture state, previous-test residue, ordinary colony state, or an unknown source?”
- Value: helps humans decide whether to repair or discard a checkpoint.
- It must not authorize cleanup.

## 10. Report headline generation from structured facts

- Type: `choice`, followed by a fixed template rather than free text
- Question: “Which fixed diagnostic headline best represents this evidence?”
- Value: produces consistent, terse report summaries without allowing Jev to invent causes.

For every use: calibrate per question/version, cache immutable judgments, log the exact reduced state, and send disagreement or low-confidence cases to review. None should pause, heal, suppress, pass, or mutate the game.

# 5. Tick-budget and surprise-screenshot failure modes

| Failure mode | Consequence | Required mitigation |
|---|---|---|
| Game runs between call brackets | Unattributed ticks escape accounting | Charge from one global last-seen tick at every observation |
| A raw bridge/session call bypasses `TestContext` | Unlimited stepping or unpause | Central session wrapper; deny tick movers without a lease |
| Bridge call hangs | Timer flag is never checked | Separate supervisor/process with hard IPC timeout |
| Pause request hangs or connection dies | Runner cannot provide its promised pause guarantee | Report pause as unverified; attempt independent connection; terminate disposable game if authorized |
| Two equal tick reads falsely “verify” pause | Game resumes immediately afterward | Verify time speed/pause state and resample across render boundaries |
| Step overshoots requested ticks | Budget exceeded before code can intervene | Treat actual delta as authoritative; reserve margin; record overshoot as bridge defect |
| Step returns success with zero/partial movement | Infinite retry or premature success | Bounded retries and explicit stall failure |
| Save/load resets the tick clock | Negative or enormous false delta | Start a new clock epoch with save/map identity |
| World screen has no readable tick | Budget cannot be enforced | Refuse tick-moving operations until an authoritative clock exists |
| Helper/screenshot ticks are “free” | Real game time exceeds the cap | Separate component and overhead ledgers under one hard session cap |
| Budget is exhausted before evidence capture | Screenshot protocol cannot take its refresh tick | Pause first; capture without stepping; maintain a small diagnostic reserve only if unavoidable |
| Screenshot refresh tick causes harm | Evidence changes or a pawn dies | Prefer render synchronization without simulation; otherwise record pre/post snapshots |
| Sweep interval is too large | Threat harms subjects before detection | Use job/queue/inbound detectors; shorten intervals around hazards |
| Sweep interval is too small | Bridge overhead dominates and may induce timeouts | Measure cost; use event-specific tiers rather than one fixed cadence |
| Snapshot calls span different ticks | Internally inconsistent evidence | Pause before full snapshots; stamp every read and reject mixed-map/mixed-epoch data |
| Tripwire snapshot lacks health details | Escalated full snapshot misses the initial wound state | Keep a small health/damage-event ring buffer |
| Surprise detector remains true | Screenshot storm every chunk | Stable event fingerprints, deduplication, cooldown, and first/last capture |
| Several surprises occur together | First helper erases evidence for the rest | Freeze one shared pre-intervention snapshot and capture all hits before acting |
| Screenshot cleanup closes the causal modal | Evidence is destroyed before capture | Record window metadata and optionally capture UI-as-is before closing anything |
| Closing a choice dialog has gameplay effects | Capture procedure mutates the test | Never auto-close non-debug choice dialogs; abort with metadata |
| Camera points at another map or invalid cell | Misleading image | Verify active map and focus bounds before framing |
| Filename/path is rewritten by the tool | The verifier stats the wrong file | Discover the actual returned path and require run-local ownership |
| File is still being written | Size/hash verification is flaky | Wait for stable size with a short wall-clock poll |
| Fixed 0.5 MB threshold rejects valid PNGs | Simple or compressed frames falsely fail | Validate PNG structure, dimensions, decode success, and minimum nonuniformity instead |
| MD5 matches a legitimate unchanged frame | False stale-image alarm | Include requested camera/map metadata and compare decoded pixels only when freshness is in doubt |
| A stale frame is re-encoded | Different hash incorrectly appears fresh | Verify render/frame identifier if available; retain the state sidecar as authoritative |
| System screenshot captures other windows or monitors | Privacy leak and irrelevant evidence | Disable by default; require explicit opt-in and crop to a verified game window |
| Disk full or sidecar write fails | Evidence is lost after mutation | Persist sidecar atomically before helpers; abort if mandatory evidence cannot be written |
| `drain_log` consumes earlier context | Sidecar lacks the causal messages | Maintain a harness-side ring buffer; draining must not be the only copy |
| Surprise capture itself triggers detectors | Recursive captures and budget consumption | Mark a capture phase; collect secondary hits without recursively capturing |
| Static budget extraction misses loops/branches | Cap is wrong before execution | Require explicit component caps; use AST analysis only as lint |
| Concurrent human or harness client advances time | Budget charges unexplained ticks | Exclusive session lease; classify external advancement as fatal contamination |
| Restoring storyteller between chains permits a tick | New incident queues in the gap | Keep the safety transaction for the whole isolated run or reload the checkpoint |
| Screenshot succeeds but state is already gone | Human sees aftermath, not cause | Treat structured damage/job/queue history as primary evidence; image is supplementary |

Recommended defaults: dedicated checkpoint per isolated chain, storyteller suppression plus selective queue control, `abort` on surprise, no GREEN after intervention, and no screenshot-induced simulation tick unless a live probe proves it necessary and safe.