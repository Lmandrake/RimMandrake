## 1. Adjudication: accept the structural corrections, narrow both recommendations

**Recommendation:** repair validation isolation and detector expectations first, while adding a precise scene report and “what is this thing?” resolver. Add a small incident journal next. Build full pawn provenance only if measured, unresolved cases justify it.

**Player.log is insufficient, but that does not establish that a full recorder is the best first investment.** Identification, causal attribution, and test validity are three different problems.

Confidence labels throughout:

- **VERIFIED-from-knowledge:** established engineering, .NET, or Harmony behavior; not a claim that I inspected your installed game.
- **PLAUSIBLE:** supported by the supplied documents or general RimWorld behavior, but not independently verified against your exact 1.6 build and mod stack.
- **UNKNOWN:** requires engine-source inspection, companion-source inspection, or a live proof.

I have not accessed RimSage, the running game, the logs, the 82 summaries, or companion source. The supplied skills describe the available tools; they do not prove today’s deployed surface. All new tool names and schemas below are **proposals**.

| Disagreement / correction | Decision | Reason |
|---|---|---|
| Player.log answers neither arrivals nor provenance | **Accept, with narrower wording — PLAUSIBLE** | Both supplied scans support this. Reject “vanilla logs only warnings/errors”; the reviewer identifies raid debug logging. Even raid logging cannot explain every pawn or its art. |
| Evidence mainly supports control rather than provenance | **Mostly accept — PLAUSIBLE** | E3 already had an explanation; E5 is requested-versus-actual identity; E7 is a modal; E8 is faction setup. Those do not justify a generation recorder. |
| Only E1/E4 “need provenance” | **Too categorical** | They are the strongest unexplained-origin cases. Attribution could still help prevent E2 recurring. But the supplied evidence does not quantify that benefit. |
| E1 insects necessarily came from mapgen | **Reject — UNKNOWN** | Presence on a fresh map does not distinguish initial placement, hive production, scenario behavior, or an early event. |
| 24/82 is a leakage rate | **Reject** | Both documents acknowledge missing expectation data. The reviewer’s “up to ~8” is also not a verified contamination rate. Reclassify individual runs before quoting a replacement rate. |
| Preserve the whole context chain | **Accept** | `bridge → incident → helper` must retain bridge involvement and the immediate mechanism. However, the outermost *observed* frame is not necessarily the ultimate cause. |
| Thread-aware contexts; push inside the scheduled game operation | **Accept — PLAUSIBLE engine premise; VERIFIED engineering consequence** | A context established on the server thread does not automatically exist in a later main-thread lambda. Thread-local stacks also do not cross worker-task boundaries. |
| Use `Pawn.SpawnSetup`, not `MapPawns.RegisterPawn` | **Accept provisionally — PLAUSIBLE** | The reviewer’s cited registration behavior makes that hook unsuitable for arrivals. Verify the precise signature and patched behavior locally. |
| Separate arrival from transit | **Accept, but rename carefully** | “First observed spawn in this recording epoch” is provable. “First-ever arrival” is not, after a load, installation gap, or eviction. |
| Never use an ID watermark for arrivals | **Accept — VERIFIED-from-knowledge** | An existing pawn can arrive after the mark. Even perfectly increasing allocation IDs cannot solve this. |
| Defining mod determines expectedness | **Reject as a verdict rule** | A test mod can spawn an unintended pawn. Another mod can trigger vanilla content. Ownership is an investigative hint, not permission. |
| End active quests as part of a cheap freeze | **Reject as a default** | Ending a quest changes world state and can trigger consequences. Prefer a prepared quest-free fixture, or explicitly account for active quests. |
| Quiet controls cover every vanilla source except scenario/mod tickers | **Reject — UNKNOWN and visibly incomplete** | Births, hatching, existing hives, delayed transports, existing conditions, and DLC systems require separate consideration. |
| Generation tags cannot persist | **Reject the absolute statement** | They do not persist automatically. An external journal could preserve them without modifying saves, with careful save-branch identity. Do not build that complexity initially. |
| Report all missing tags as `PRE_LOAD` | **Reject** | Absence of a tag does not prove pre-load generation. Use `unknown`, with a specific coverage limitation. |
| `TryExecute` result tells whether execution occurred | **Reject** | Even the reviewer describes a successful early return without worker execution. Record outer-method outcome separately from observed effects and worker entry. |
| Empty-stack tagging is “free”; wild-spawner tick is “cold” | **Reject** | Hooks still execute. A tick method may be frequently called even when actual spawning is rare. Measure both frequency and overhead. |

One additional safety correction: **a postfix can run when another Harmony prefix skipped the original**. Therefore a recorder cannot treat its postfix as proof that generation, spawning, or incident execution happened. Harmony documents both this behavior and `__runOriginal`; test against your pinned 2.4.2 installation. [Harmony 2 execution flow](https://harmony.pardeike.net/v2/articles/execution.html), [injected values](https://harmony.pardeike.net/v2/articles/patching-injections.html).

## 2. “Quiet world first”: right for isolated validation, wrong as a universal freeze

**Yes, with a test-specific profile and verified baseline.** Establish isolation before measuring behavior. Introduce the scene report at the same time so suppression failures are visible.

Use two declared profiles:

- **Isolated:** suppress unrelated scheduling and environmental variation; explicitly enable mechanisms needed by the test.
- **Integration:** retain specified game systems and evaluate their interactions.

A passing isolated test supports only its declared environment. It cannot establish that the mechanic works with quests, natural raids, wildlife replenishment, or layer transitions.

The following covers every family requested and several additional ones. **It is not an exhaustive inventory of arbitrary code in 600 mods.** Exact interception APIs not already supplied are **UNKNOWN**; I deliberately do not invent them.

**Table confidence:** mechanisms and controls are **PLAUSIBLE** unless explicitly marked otherwise. Each proposed suppression needs source verification and a live negative-control proof.

| Source / mechanism | Relationship to storyteller | Suppress or constrain | Detect in harness | Effect on validity |
|---|---|---|---|---|
| Storyteller-scheduled incidents | Normal storyteller path | Existing `storyteller_off`; clear queue; verify settings read-back | Incident journal, queue checks, pawn/condition/letter deltas | Disables threat pacing, quest offers, and other storyteller-dependent behavior |
| Already queued incidents | Reviewer says queue can continue with storyteller disabled | Clear at setup; detect newly queued entries throughout run | Queue snapshots plus incident journal | Invalidates tests of delayed incidents or queue behavior |
| Active quests and quest parts | Can execute independently after acceptance | Prefer fixture with no unrelated active quests; retain explicit test quest IDs | Quest inventory and state changes; incident/spawn/transport observations | Ending quests is destructive setup, potentially with callbacks; suppressing parts invalidates quest integration |
| Scenario parts | Initial creation and recurring actions can bypass storyteller | Inspect fixture scenario; remove unrelated scheduled parts when constructing fixture | Record scenario inventory and scheduled actions; journal actual effects | Changes startup population and recurring scenario behavior |
| Existing game conditions | May tick independently and create effects/pawns | Start without unrelated conditions; retain expected conditions | Condition identity/state deltas; effects and arrivals | Removing weather/biome conditions can disable the mechanic under test |
| Map components, thing components, world/game components | Direct ticking code can bypass incidents | Only targeted, documented switches; do not freeze components generally | Pawn/state deltas; source-specific instrumentation if needed | High risk: often the actual implementation under test |
| Mod tickers, jobs, hediffs, abilities and callbacks | Arbitrary direct effects | Mod-specific opt-out or controlled fixture; otherwise observe | Deltas plus targeted hooks; incident journal alone misses them | General suppression can make a broken mechanic appear correct |
| Wild animal replenishment | Supplied source claim: independent map spawner | Armed, map-scoped block of verified replenish path; allow deliberate test spawning | Generation/spawn observations and count changes | Changes ecology, predator targets, population caps, and replacement behavior |
| Herd/manhunter migrations and packs | Often incident-driven; direct/mod paths remain possible | Disable scheduler and unrelated queue entries; expect explicit injections | Incident records; pawn arrival and mental-state records | Threat suppression can remove precisely the hostility behavior being tested |
| Trader/visitor groups, trade ships | Often incidents or quests; mods can schedule directly | Scheduler/quest controls; remove pending unrelated arrivals in fixture | Group arrivals, letters, transport state and trade-ship state | Disables trade/visitor interactions; not all arrivals are map pawns |
| Infestation incidents | Can be incident-driven | Suppress unrelated scheduling; preserve intentional infestation tests | Incident record and new hive/pawn observations | Changes threat and underground ecology |
| Existing hives / pawn-spawning structures | Continued production need not be an incident | Hive-free fixture, or targeted suppression of verified production mechanism | Track structures and their pawn production separately | Removing hives changes combat, reproduction, and biome behavior |
| Faction relations and retaliatory behavior | Relations are state, not themselves an incident scheduler | Set only relations required by fixture; audit reactive quest/DLC/mod systems | Relation changes, group arrival, actual targets, incident records | Peaceful relations or threat scaling invalidate hostility and raid tests |
| Drop pods, shuttles, transporters and other pending arrivals | Delivery can occur long after incident/quest/tool call | Remove unrelated pending deliveries during fixture construction; retain expected delivery IDs | Track contents and delivery/arrival transitions | Cancelling transport invalidates arrival mechanics; a queue clear may miss these |
| Existing caravans and world-pawn arrivals | Existing pawns can enter without new generation | Controlled world fixture; avoid unrelated travel | Pawn-set changes across maps and world/held states | Affects caravan, trade, recruitment, and travel tests |
| Pregnancy, births, egg hatching, reproduction | Biological/component paths can bypass incidents | Start without unrelated pregnancies/eggs/breeders; targeted opt-out only where valid | Parent/egg observations and child spawn records | Disabling reproduction invalidates reproduction and downstream ecology tests |
| Recruitment, taming, emancipation and faction changes | Often changes an existing pawn, not arrival | Constrain jobs and interactions if unrelated | Same-ID faction/guest/control-state delta | Must not count as a newly arrived pawn; affects social/control tests |
| Animals joining, wanderers, refugees and other joiners | Commonly incidents or quests; may reuse existing pawns | Scheduler/quest controls plus explicit expectations | Arrival and faction/guest transitions | Blanket non-player filtering misses unexpected player-faction joiners |
| Weather transitions | Not every transition is an incident | Controlled weather only for tests that permit it; exact freeze facility **UNKNOWN** | Weather observations, conditions, damage and environmental effects | Changes visibility, movement, fire, power and temperature behavior |
| Disease and health progression | Disease onset may be incident-driven; existing/direct effects persist | Existing `random_events_off` where applicable; clean fixture; preserve tested health mechanisms | Hediff/state deltas and damage log | Disabling health events invalidates health/biome/disease tests |
| Mental breaks, manhunter state, social fights | Pawn-state processes can bypass storyteller | Existing random-mental-state control; controlled needs/stress; retain intended state | Mental state, jobs, targets and damage changes | Suppression invalidates stress, behavior and aggression tests |
| Mapgen, ancient dangers, landmarks and mutators | Initial population predates run scheduling | Build known fixture; audit initial pawns, structures and dormant threats | Full baseline, including dormant and held entities where supported | Stripping initial inhabitants can invalidate biome/mapgen tests |
| Gravship, layer, pocket-map and destination events | Movement and destination setup may bypass storyteller | Pin maps/layers and disallow unrelated travel only in isolated tests | Map creation/removal; same-pawn transitions; held/transit state | Invalidates flight/layer tests; exact 1.6/DLC/mod funnels **UNKNOWN** |
| Anomaly or other DLC-specific systems | May combine incidents, conditions, hidden pawn state and components | Inventory active systems in fixture; targeted controls only | State/health/structure changes, emergence, conditions and damage | Disabling these systems prevents meaningful compatibility testing |
| Dev actions, bridge tools and owner intervention | Direct mutation bypasses storyteller | Serialize authorized mutations; record action receipts | Mutation ledger and before/after observations | An authorized action is still contaminating if outside this test’s contract |
| Fires, explosions, destruction and existing hostile behavior | Often no new pawn and no incident | Remove unrelated hazards at fixture setup; constrain only permitted behavior | Damage/kill logs, condition changes, structure state and modal sweep | Pawn-only awareness cannot establish world cleanliness |

Two practical requirements:

1. **Read back suppression state and record what was actually suppressed.** A configured flag is not proof that every path obeyed it.
2. **Restore settings, not imaginary world history.** A settings transaction cannot undo a quest ending, suppressed birth, deleted hive, missed weather transition, or destroyed pawn. Reload an expendable fixture between runs when necessary.

`DebugSettings.logRaidInfo` is a useful supplementary breadcrumb **if its supplied source claim is verified**. It is observation, not suppression, and is neither a complete incident journal nor a pawn-origin ledger.

## 3. Minimal robust provenance: separate creation, generation/reuse, delivery and observation

“Why is this pawn here?” can mean:

- What is it?
- Who initiated the operation?
- Was it newly created or an existing world pawn reused?
- What generated or selected it?
- What delivered it to this map?
- Why is it hostile now?

**One `origin` string cannot answer all six.**

### Comparison

All implementation estimates below are **PLAUSIBLE design judgments**, not measured costs.

| Approach | What it can establish | Principal failures | Cost / hot-path risk |
|---|---|---|---|
| **(a) Generation hook + context chain** | Observed generating/selecting operation; preserves context until deferred delivery if tag retained | Existing pawn reuse; recursive relative generation; quest generation long before arrival; load/tag eviction; uninstrumented helpers; worker handoffs; replacement prefixes | Highest coverage potential, but generation can be frequent during worldgen. Keep writes bounded and cheap; no routine stack traces |
| **(b) `SpawnSetup` observation** | Observed map spawn, map/cell, load flag, current delivery context | Does not recover earlier generation cause; repeated spawns/transit; pending tags absent; partial/skipped execution; specialized mod paths | Relatively small observer; safer arrival signal than registry membership, provisionally |
| **(c) Incident journal + before/after pawn diff** | Incident invocation/outcome; pawns visible before and after synchronous operation | Deferred drop pods/fly-ins; despawned pawns; held pawns; nested calls; unrelated effects during operation; reused IDs | Journal cheap relative to full provenance; full-map diff per incident adds scans and allocation |
| **(d) Periodic pawn-set snapshots + heuristics** | First observation between samples; changed faction/state/map membership | Misses spawn-and-disappear between samples; cannot establish cause; returning caravans look newly observed; similar events overlap | No Harmony needed; cost proportional to scope and cadence; heuristic classifier must remain explicitly uncertain |
| **(e) Precise scene report only** | Current identity, state, threat, location, letter association, art/def information | No historical explanation for silent arrivals; no brief-event history | Lowest risk and likely substantial value; atomic companion read improves consistency |

**For identification:** start with **(e)**.

**For run monitoring:** combine **(d)** with existing damage, condition, letter and modal detectors.

**For a small historical breadcrumb:** add the incident journal portion of **(c)**.

**For reliable deferred attribution:** use **(a)+(b)**, plus explicit action receipts and selected delivery contexts. Neither hook alone is sufficient.

### Proposed provenance record

```text
pawnKey = recordingEpoch + pawnId

generationObservation:
  sequence, tick?, contextChain, requestSummary,
  reuseStatus = new | reused | unknown

spawnObservation:
  sequence, tick?, mapId, cell, respawningAfterLoad,
  classification = firstObservedSpawn | observedRespawn | mapTransfer | unknown

bridgeAction:
  actionId, runId?, tool, requestedKind?, returnedPawnIds, readBackKinds

attribution:
  observedInitiator, generationMechanism, deliveryMechanism,
  evidenceIds, confidence, coverageLimitations
```

`tick?` is intentional: startup/mapgen may occur before normal run timing is usable. A recorder sequence and recording epoch are required.

The chain must preserve, for example:

```text
bridge action A17 → incident I9 → pawn-generation operation
```

But also preserve distinct stages:

```text
quest offered → pawn generated
quest signal later → transporter delivery → pawn spawned
```

A `GiveQuest` generation tag does not by itself explain which later quest signal delivered the pawn.

### Required implementation constraints

- **Thread-local synchronous contexts:** viable for synchronous nesting. Explicit immutable tokens are needed across scheduled lambdas, worker handoffs, queues and deferred callbacks. `[ThreadStatic]` alone does not propagate causality.
- **Game/load epochs:** every operation captures its epoch. Late work from an old game cannot append to the new game’s state.
- **Robust scope cleanup:** save an initialized scope token, depth and epoch; unwind only that scope; tolerate skipped prefixes and missing state. Cleanup must be idempotent.
- **Preserve game exceptions:** contain recorder failures, expose a health fault, and let the original game exception propagate. Do not “protect the game” by swallowing its exception. Harmony supports observing exceptions with a `void` finalizer. [Harmony finalizer documentation](https://harmony.pardeike.net/v2/articles/patching-finalizer.html).
- **Postcondition checks:** a skipped generation method may return a mod-supplied pawn; a skipped spawn method may still have been emulated. Record what was observed rather than assuming the vanilla body ran.
- **Bounded retention:** cap event records, pending tags, context lengths, stack hints and writer queues. Report evictions and gaps. A `ConditionalWeakTable` is GC-friendly but does **not** guarantee a fixed memory bound.
- **No game objects on writer threads:** copy bounded scalar records on the producing thread; serialize those records elsewhere.
- **No universal stack attribution:** a stack frame identifies executing code, not necessarily the initiating mod or intended mechanism.
- **No unconditional overwrite on reuse:** a new generation request for an existing pawn is another observation, not a replacement for its historical creation record.
- **Early installation must be proven:** a companion loaded by the bridge may install too late for initial mapgen. The startup path is **UNKNOWN** until checked.

### Claims that must remain unknown

| Evidence | Allowed statement | Forbidden upgrade |
|---|---|---|
| Pawn already present when recording starts | “Present at baseline; origin unknown” | “Mapgen pawn” |
| Missing generation tag after load | “Generation provenance unavailable across load” | “Generated before load” |
| Raid-style lord/job | “Currently organized for assault” | “Created by a storyteller raid” |
| Letter look-target association | “Associated with this letter” | “This letter/incident created it” |
| New pawn observed near an incident | “Appeared in this interval; possible association” | “Caused by incident X” |
| Vanilla pawn kind/texture | “Uses vanilla definition/asset” | “Vanilla initiated its arrival” |
| Foreign assembly on stack | “This assembly participated” | “This mod caused the pawn” |
| Bridge context around generation | “Generated/selected during our operation” | “Newly created and intentionally spawned by us” |
| Pawn appears after mark with old ID | “Newly observed on this map” | “Newly created” |
| No event rows | “No retained observations” | “No arrivals occurred” |

For the incident journal, initially record:

```text
called, outerBodyRan, returnedResult, exceptionObserved,
workerEntered = true | false | unknown,
observedEffects, contextChain, coverage
```

`__runOriginal` concerns the patched outer method. It does not establish that the outer method reached `TryExecuteWorker`. Unless worker entry is instrumented or a branch is independently established, leave `workerEntered=unknown`.

## 4. First-look schema and one-call creature resolver

**This may deliver most of the owner-facing value.** The owner’s immediate question is often identity and visual ownership, not historical generation provenance.

### Proposed `jawa/scene_report`

First implement a batched Python report over existing reads. Label its acquisition interval. Move to a companion tool when atomicity, call count, or missing fields justify it.

| Group | Required fields |
|---|---|
| Identity and timing | `schemaVersion`, `reportId`, `runId`, game/load/recording epochs, map ID, tick start/end, paused state, atomic/non-atomic acquisition |
| Scope | Included maps; spawned/dormant/held coverage; exclusions; truncation; collection failures |
| Baseline/diff | Baseline report ID; added/removed IDs; same-ID map/faction/state changes; missing interval warning |
| Environment | Active conditions/weather; relevant quests; pending incidents/deliveries where supported; active suppression profile |
| Recorder health | Installed hooks individually; installation epoch/tick; latest sequence; retained interval; overflow/eviction/fault counts |
| Pawn identity | Canonical bridge ID plus namespace-specific aliases, name/label, pawn kind def, race/thing def, runtime type |
| Position | Map/layer, spawned or held state, cell, distance to anchor and distance metric |
| Control/state | Faction, player control, guest/prisoner/slave status, alive/dead/downed/dormant, mental state |
| Threat | Separate fields below; current job, target, lord job/duty where available |
| Evidence | Letter associations; bridge receipt; generation/spawn observations; attribution confidence |
| Test evaluation | Matching expectation rule; unexpected observation; relevant effect on test |

**Do not hide dormant pawns or held threats behind “every pawn on the map.”** Verify what the underlying pawn collection actually includes. Report limitations explicitly.

### “Hostile” must be decomposed

| Field | Meaning |
|---|---|
| `factionRelationToPlayer` | Diplomacy between factions; null faction is not automatically neutral |
| `engineHostileToPlayer` | Result of the verified engine predicate, with its exact semantics documented |
| `mentalState` / `aggressionReason` | Manhunter, berserk or other state capable of overriding ordinary diplomacy |
| `currentTarget` | Observed enemy/prey/job target, distinguished by target type |
| `capabilityState` | Dead, downed, dormant, contained or active |
| `threatAssessment` | Derived summary with explicit reasons, uncertainty and scope |

A player-faction berserk pawn can threaten colonists. A hostile-faction dormant mech can be an inactive threat. A factionless predator can attack without belonging to an enemy faction.

“Distance to anchor” is a proximity measure, not proof of reachability or attack capability.

### Show our involvement without a false binary

Use:

```text
ourInvolvement =
  confirmedDirectSpawn
  confirmedIndirectAction
  correlatedOnly
  unknown

expectation =
  expected
  unexpected
  unresolved
```

These are independent. A deliberately fired raid can be `confirmedIndirectAction + expected`. An accidental extra pawn from our spawn tool can be `confirmedDirectSpawn + unexpected`.

### Proposed `jawa/thing_explain`

Accept exactly one selector:

- Canonical thing ID.
- Current selection.
- Hover target captured at a specified UI frame.
- Name with explicit map/scope.
- Cell, returning candidates if multiple things occupy it.

**Never silently choose between ambiguous names, selections or stacked things.** Hover resolution may require UI-specific support; the exact API is **UNKNOWN**. Prefer an explicit ID when available.

Return a compact answer first:

```text
“What is it?”
  label, pawnKindDef, race/thingDef, runtime type
  definition-owning packages
  faction/state/threat reasons
  our involvement and test expectation
  attribution evidence or “unknown”
```

Then return optional diagnostic detail:

```text
“What supplies its appearance?”
  configured graphics/variant information
  currently resolved render layers, if observable
  logical texture paths
  candidate or confirmed supplying packages
  recolors, shaders, overlays and runtime replacements
  asset-resolution confidence and limitations
```

The requested chain needs refinement:

```text
PawnKindDef → race ThingDef → appearance selection → texture lookup
```

It is **not generally**:

```text
one defName → one modContentPack → one texture
```

Important distinctions:

- **PLAUSIBLE:** `def.modContentPack` identifies the definition’s owning content pack.
- It does not identify every XML patch contributor, runtime patch, or asset override.
- Pawn appearance may involve kind-specific variants, life stages, body/head graphics, genes, apparel, render layers and custom renderers.
- A configured texture path is not proof of the file currently supplying the visible texture.
- Load-order-based candidate resolution is useful, but label it `candidate` unless actual resolution was observed.
- If the renderer exposes only an atlas/material texture, recovering the original asset path may require extra instrumentation; that is **UNKNOWN**.

Avoid forcing graphic initialization or traversing expensive lazy properties just to explain the creature. The resolver should report existing observations and known configuration first.

Acceptance must include a mod that overrides another mod’s texture path: the resolver must either name the actual provider correctly or report ambiguity. Naming the definition owner as the texture supplier fails.

## 5. Contamination: an expectation violation affecting the test, not “foreign origin”

Use **two separate dimensions**:

```text
criterionResult = PASS | FAIL | UNPROVEN
runValidity     = CLEAN | CONTAMINATED | INDETERMINATE
```

Publish a validation pass only when required criteria pass and validity is clean for the declared scope. Preserve a demonstrated defect even if the run was also contaminated.

| Observation | Verdict |
|---|---|
| Unexpected pawn appears but remains outside a narrowly scoped cosmetic test | Record anomaly; contamination depends on the contract |
| Unexpected pawn attacks, changes targets, competes for resources, blocks movement or changes subject behavior | `CONTAMINATED` |
| Unexpected raid during a declared closed-world run | `CONTAMINATED`, even if nothing was damaged |
| Mod under test produces an extra unapproved pawn | Contract violation; possibly criterion `FAIL`; never auto-allow because of mod ownership |
| Expected mod letter/condition occurs within declared bounds | Expected |
| Same expected letter/condition occurs too often or with wrong targets | Violation |
| Unknown origin, but exact pawn/effect is explicitly expected | May remain valid; provenance is unnecessary unless it is itself a criterion |
| Unknown arrival in a closed-world run | `CONTAMINATED` if the unexpected arrival is confirmed |
| Required recorder interval lost, baseline absent, or suppression state unverifiable | `INDETERMINATE`; cannot certify cleanliness |
| Unexpected player-faction joiner | Evaluate exactly like other arrivals; “non-player pawn” is insufficient |
| Recorder silence without proven coverage | Not evidence of a clean run |

### Per-test expectation contract

Declare before execution:

```yaml
scope:
  maps: [fixture-map]
  region: whole-map
  interval: after-setup-through-final-check

profile: isolated

baseline:
  pawnIds: [...]
  allowedConditions: [...]
  allowedPendingDeliveries: [...]

expectedTransitions:
  - actionId: spawn-subjects
    actualPawnCount: 3
    actualKinds: [expected-kind]
  - mechanism: mechanic-under-test
    pawnKinds: [expected-output-kind]
    count: {min: 0, max: 2}
    region: test-area
    factionConstraint: expected-faction
    timeWindow: declared-window

forbiddenEffects:
  - unrelated-arrival
  - damage-to-control-pawn
  - unexpected-modal
```

Mechanism constraints must use evidence the instrument can actually supply. If it cannot observe a mechanism, say so and use observable count/location/state constraints.

Do not automatically add observed pawns to the allowlist. Expectations learned during exploration belong in a reviewed contract for a subsequent run.

**Mod ownership can narrow investigation and reduce presentation noise. It must not suppress contract violations.** Letter categories likewise are not incident identity; a threat-category letter does not prove a raid arrived.

## 6. Exact first-look protocol and enforcement

Place this in the existing “look before you theorise” workflow rather than creating a competing rule.

1. **Establish identity and timing.** Confirm current game/load epoch, map, tick, pause state and deployed companion surface. Acquire the bridge lease before driving it.
2. **Capture the scene before modifying evidence.** Obtain the scene report and relevant conditions, letters, queue and pending-delivery observations. Record acquisition gaps.
3. **Resolve the subject exactly.** Use its canonical ID or an unambiguous selection. Read actual kind, race/def, faction and state; do not substitute the requested spawn kind.
4. **Check the action ledger and test contract.** Determine whether the pawn/effect was expected and whether our direct or indirect operation is confirmed.
5. **State observed facts and uncertainty.** Distinguish identity, current aggression, letter association, generation evidence and delivery evidence. Say “origin unknown” where necessary.
6. **Check validity before continuing.** If unexpected state can affect the criterion, capture damage/modal/condition evidence and mark validity contaminated or indeterminate.
7. **Only then form and test a hypothesis.** Choose the smallest distinguishing probe, read back its actual result, and capture a new scene at the boundary. Do not delete unexplained evidence before capture.

Enforcement strength:

| Mechanism | Value / limitation |
|---|---|
| Skill paragraph | Helpful reminder; weak enforcement alone |
| Automatically capture baseline before timed harness stages | Strong; removes reliance on agent memory |
| Action receipts containing requested and actual IDs/kinds | Strong; fixes E5 directly |
| Harness requires report ID, expectation contract and coverage status before publishing PASS | Strongest practical gate |
| Report footer states unresolved observations and coverage gaps | Keeps uncertainty visible |
| Report lint rejects attribution claims without evidence IDs | Useful if claims are structured; prose lint is unreliable |
| Gate long stepping or destructive cleanup on a fresh scene token in validation mode | Useful where it fits the harness; refresh after relevant mutations |
| Owner override | Record explicit override and scope; do not silently certify the overridden interval |

Freshness should depend on epoch, map, mutations and elapsed simulation ticks. A screenshot or census from before a spawn is stale even if only seconds old.

## 7. Ranking, phased plan, acceptance tests and decommission test

Costs are **planning estimates**, including source checks and proofs; the 600-mod compatibility surface can dominate them.

### Options ranked

| Rank | Option | Scope | Approximate cost | Main risk |
|---:|---|---|---|---|
| 1 | **O5: expectation and detector repair** | Exact IDs/kinds; bounded per-test expectations; meaningful validity status | 1–3 days | Overbroad allowlists conceal regressions |
| 2 | **O1: precise scene report + resolver** | Batched report first; atomic companion read and art explanation where necessary | Report: 1–2 days; robust asset explanation: several additional days | Incomplete collections; confusing definition ownership with rendered asset ownership |
| 3 | **O3-control: scoped quiet profile** | Existing controls, fixture audit, verified wildlife control if needed | 1–3 days for initial profile; exhaustive audit **UNKNOWN** | Observer effects; destructive cleanup masquerading as restoration |
| 4 | **O0: first-look enforcement** | Skill edit plus automatic baseline/report gates | Text: hours; enforcement included above | Ritual compliance without fresh evidence |
| 5 | **O3-lite: incident journal** | Calls, outcomes, context and coverage; no promised pawn causality | 1–3 days | False `executed` claims; bypasses and deferred effects |
| 6 | **O2: scoped generation + spawn provenance** | Thread-aware context chain, action receipts, bounded tags, arrival observations | Roughly 1–2 weeks including hard cases | Lifecycle, retention, skipped hooks, load gaps and causal overclaiming |
| 7 | **O4: blanket quest/component/ticker freeze** | Broad suspension | Open-ended | Changes the implementation being validated; reject as a general feature |

Ranking expresses expected value, not strict implementation order. Quiet setup is established before a validation interval; reporting is needed to verify it.

### Phase 1 — Make observations and verdicts trustworthy

- Repair detector output and per-test expectations.
- Add requested-versus-actual action receipts.
- Build the batched first-look report.
- Audit quiet fixtures; apply existing controls with read-back.
- Add the protocol and automatic baseline gate.

**Acceptance tests:**

| Test | Required result; defect-sensitive condition |
|---|---|
| Spawn-kind substitution | Independent map read shows actual substituted kind; response and receipt expose mismatch. A tool repeating its requested kind fails |
| Expected mod condition plus unexpected condition from the same mod | First accepted, second rejected. A package-wide allowlist fails |
| Unexpected pawn joins player faction | Detected despite being player-faction. Non-player-only filtering fails |
| Stranger near anchor | Reports exact ID/kind/faction/state and evidence links. Count-only output fails |
| Same pawn recruited or tamed | Reports state change, not arrival |
| Old-ID pawn enters after baseline | Set diff detects it. ID-watermark implementation fails |
| Empty map/letters, null targets, ambiguous name | Valid empty result or explicit ambiguity; no crash or silent selection |
| Dormant and held pawn fixture | Reports them or declares exclusion. An unqualified “complete” report fails |
| Required observation read fails | Validity becomes indeterminate; no fallback to clean |

### Phase 2 — One-call identity and incident breadcrumbs

- Add atomic `scene_report` if batched reads are insufficient.
- Add `thing_explain`.
- Add the incident journal with honest outcome fields.
- Add targeted wildlife suppression only if observed leakage warrants it.

**Acceptance tests:**

| Test | Required result |
|---|---|
| Incident called but fails | Journal records call and failure; no “incident fired” assertion |
| Successful outer return without worker execution | Does not claim worker execution merely from return value |
| Another Harmony prefix skips incident/spawn operation | No invented effects or provenance; scope remains balanced |
| Scenario/direct incident while storyteller disabled | Journal sees the actual path if covered; harness reports the violation |
| Delayed delivery already pending at run start | Baseline detects it or declares the blind spot; storyteller-off alone cannot certify isolation |
| Wildlife suppression | Verified unrelated replenish opportunity is blocked; explicit test spawning still works; release restores the gate |
| Multi-layer creature with overridden texture | Resolver separates definition owners and asset providers; unresolved provider is labelled unknown |
| Selected/hovered object disappears or map changes | Resolver refuses stale identity rather than explaining another object |

### Phase 3 — Full recorder only after a measured gap remains

Instrument verified generation and spawn paths, then add contexts for the specific remaining sources: hives, births, hatching, breeders, quests or layer transitions. Avoid speculative hooks for everything.

**Acceptance tests:**

| Test | Required result |
|---|---|
| Our forced raid | Keeps bridge action and incident chain; expectation contract still evaluated |
| Mapgen wildlife using shared wild-spawner helper | Keeps mapgen and helper context; does not collapse to one origin |
| Deferred drop-pod raid and deferred wild fly-in | Generation association survives until observed delivery |
| Actual asynchronous first-map generation | Recorded without requiring the first bridge call; worker path exercised |
| Cross-thread scheduled operation | Explicit token preserves association, or report marks missing association; thread-local assumption fails |
| Returning caravan / map-layer transfer | Old ID observed correctly; creation and transit distinguished |
| Existing world pawn reused by generation | No false “newly created” claim or destructive historical overwrite |
| Quest offer, save/load, later arrival | Explicit provenance gap unless persistence is deliberately implemented; no invented `PRE_LOAD` attribution |
| Nested scopes, skipped prefix, exceptions, recorder failure | Scope restored; game exceptions preserved; recorder fault visible |
| Ring/tag/writer overflow | Bounds respected, losses counted, affected interval not certified clean |
| New game while old writer has pending records | No cross-game contamination or sequence confusion |
| Spawn bypassing generation hook | Arrival observed with unknown generation cause |
| Known unexpected arrival injected mid-run | Contaminated even when initiated by our bridge |
| Mod-under-test emits an unintended extra pawn | Violation preserved despite package ownership |

For all phases:

- Use independent map/state observations as the oracle, not the recorder testing itself.
- Deliberately reintroduce each targeted defect and confirm the acceptance test fails.
- A control spawn proves one route works; it does not establish all-route coverage.
- Compare recorder enabled/disabled using controlled repeated workloads. Measure allocations, frame/tick timing and bounded-memory behavior; do not assume exact replay determinism across this mod stack.

### Cadence and arming

Keep **on-demand boundary reports** as the primary interface.

If provenance becomes worthwhile:

- Tiny in-memory hooks may remain installed in the dev companion **after proving startup timing and overhead**.
- Disk output and periodic reporting remain armed with TTL.
- Sample on declared simulation-tick boundaries; do not claim intermediate completeness.
- Paused games need no repeated identical census.
- Define what happens at TTL expiry during a required validation interval: recording can stop, but cleanliness cannot be certified beyond retained coverage.

### Decommission test

After Phase 2, evaluate a fixed cohort—for example, **30 runs covering historically problematic suites plus several owner identification sessions**.

Measure:

- Confirmed unrelated contamination per run.
- Detector false positives per run.
- Time and tool calls to answer “what is that?”
- Unexplained arrivals after first-look reporting.
- Time lost to unresolved provenance specifically.
- Journal/report faults and gaps.
- Recorder overhead and maintenance cost.

**Proposed decision rule:** do not build Phase 3 unless unresolved provenance repeatedly changes the next debugging action or blocks validation. One important reproducible case can justify a targeted observer; repeated low-value mysteries do not justify a universal recorder.

If Phase 3 is built, keep it only if its confirmed causal answers materially reduce diagnosis time or prevent wasted runs. If disabling it leaves that performance unchanged, remove the hooks and writer while retaining scene reporting, action receipts, expectations and first-look enforcement.

## 8. Four genuine owner decisions

1. **What validity claim should north-star runs make?** Isolated mechanism correctness, realistic integration behavior, or separate suites for both? This determines which suppressions are legitimate.
2. **How should ambiguous disturbances be handled?** Abort/reload immediately, or finish collecting evidence while withholding PASS? This affects cost and diagnostic value.
3. **Is always-installed in-memory observation acceptable in the dev companion, with disk recording armed?** Otherwise initial-map provenance will often remain unavailable.
4. **Must provenance survive save/load and branched saves?** If yes, approve a separate external-journal identity design; if no, make load a declared provenance boundary and preserve unknowns honestly.