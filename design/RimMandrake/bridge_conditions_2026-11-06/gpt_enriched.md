# Bridge conditions — enriched design review

## 1. Assessment and scope

The central direction is sound. Keep proof orchestration and verdict policy in Python, reuse `safe_advance`, and evaluate bounded condition trees near the simulation tick.

The draft substantially understates the remaining work. This needs a defined observation model, temporal semantics, execution ownership, and reliable result delivery before it becomes trustworthy test infrastructure.

This review treats the inlined inventory, measurements, and repository references as supplied evidence. Engine-specific claims, including the flyer decompilation claims, still require verification against the deployed game and mod versions. Defaults proposed below are design recommendations.

### What needs correcting immediately

1. **“Only the glue” is misleading.** A temporal evaluator with persistent watchers, reflection adapters, actions, budgets, and lifecycle handling is a small runtime. Its correctness contract is the main engineering task.

2. **Per-tick sampling does not observe every event.** A job can start and finish inside one tick. A value can change twice between evaluations. End-of-tick sampling observes end-of-tick states. Event instrumentation is needed for complete transition histories.

3. **A transition bracket does not recover missed transitions.** Sampling false at tick 100 and true at tick 110 establishes an endpoint change. It cannot establish that exactly one transition occurred, or detect a true–false pulse entirely inside that interval.

4. **Probe failure and temporal incompleteness are different.** An unreadable temperature and an unfinished “fills within 600 ticks” obligation require different handling.

5. **Several examples establish weaker facts than their surrounding claims.**
   - Nearby toxic terrain does not establish that the pawn contacted it.
   - An adjacent water source snapshot does not identify which source caused flooding.
   - A stable cached value does not establish that the cache refreshed.
   - A cell-position threshold gives a simulation crossing time, with the limitations of that position representation.

6. **Actions can change the result being measured.** Repeatedly setting temperature, needs, or flight state creates a controlled intervention. Those results need an intervention record.

7. **The offline twin can drift.** Shared vectors and differential testing reduce that risk. They cannot make drift impossible.

8. **The polling census supports prioritization, not causation.** The supplied UNMEASURED rate does not establish how many failures these primitives would prevent.

---

## 2. Define the observation contract first

### 2.1 Separate observations, conditions, monitors, and runners

Use four explicit concepts.

| Concept | Responsibility |
|---|---|
| Probe | Read a typed observation with availability and provenance |
| Condition | Evaluate a proposition using those observations |
| Temporal monitor | Maintain history, baselines, deadlines, and obligations |
| Runner | Schedule evaluation, advance or observe the game, arbitrate stops, and retain results |

A public API can still feel like three layers. Internally, temporal state must have a clear owner.

### 2.2 Give observations a consistent type

Replace the mixed boolean/string `ok` field with a tagged status.

```json
{
  "value": 0.43,
  "status": "ok",
  "observedAt": {
    "epoch": 12,
    "tick": 41002,
    "phase": "post_tick"
  },
  "subject": {
    "gameId": "g7",
    "mapId": "m2",
    "thingId": "Human123"
  },
  "sourceUpdatedAt": null
}
```

Useful statuses include the following.

| Status | Meaning |
|---|---|
| `ok` | A valid value, including zero, false, or a schema-permitted null |
| `missing` | The referenced entity or member could not be resolved |
| `despawned` | The entity exists but lacks a spawned-map context |
| `destroyed` | Destruction is positively known |
| `oob` | A spatial target falls outside its permitted bounds |
| `unsupported` | The installed engine/mod version lacks this capability |
| `error` | The read threw or returned an invalid value |
| `stale` | The observation exceeds an explicitly required freshness bound |
| `gap` | Required historical observations or events were lost |

Death, destruction, despawn, unloading, and leaving the selected map must remain distinguishable.

`thing.exists` should return a known false when nonexistence is established. A position probe for that same subject may be unavailable. Tests should express expected disappearance through lifecycle probes.

### 2.3 Specify the evaluation point

Document and verify the complete ordering.

1. Apply explicitly scheduled pre-tick interventions.
2. Execute one simulation tick.
3. Establish the post-tick observation point.
4. Read due probes, once per shared observation context.
5. Update active temporal monitors.
6. Collect condition events and safety triggers.
7. Freeze event evidence.
8. Arbitrate stopping before another tick starts.
9. Queue deferred frame work and result serialization.

Use one observation dispatcher. Calling the evaluator from both `SA.Frame` and a `DoSingleTick` postfix risks double evaluation, duplicate event counts, and shortened timers.

A postfix also needs verified ordering against other patches. Its name alone does not establish that every relevant mod mutation has completed.

Include `epoch`, tick, phase, and event sequence in records. Sequence numbers establish ordering among multiple events in the same tick.

### 2.4 Distinguish simulation, frame, and wall clocks

| Clock | Appropriate uses |
|---|---|
| Simulation ticks | Gameplay deadlines, durations, rates, and temporal conditions |
| Render/update frames | Lifecycle readiness, deferred rendering, and frame-dependent state |
| Monotonic wall time | Transport deadlines, leases, watchdogs, and performance measurements |

A tick watcher cannot finish loading a map while ticks are unavailable. `await_lifecycle` needs frame/lifecycle servicing and a wall-time deadline.

---

## 3. Repair the logic and temporal semantics

### 3.1 Keep three-valued logic for unavailable observations

Strong Kleene logic is appropriate for ordinary conditions.

| Expression | Result |
|---|---|
| `false AND unknown` | false |
| `true AND unknown` | unknown |
| `true OR unknown` | true |
| `false OR unknown` | unknown |
| `NOT unknown` | unknown |

Define whether `on_unknown` applies to the root result, every declared required probe, or selected nodes. The current draft leaves these policies conflated.

Recommended behavior follows two rules.

- Validate every required binding at arm time.
- During execution, preserve child observation errors in diagnostics even when Boolean logic determines the root result.

An explicitly optional or guarded probe can have different availability requirements. This must be declared.

### 3.2 Give temporal monitors progress and coverage

A temporal monitor should expose separate fields for its progress and evidence quality.

```json
{
  "progress": "pending",
  "coverage": "complete",
  "deadlineTick": 41600,
  "unavailableNodes": []
}
```

Recommended progress values are `pending`, `satisfied`, and `violated`. Coverage can be `complete`, `sampled`, or `incomplete`.

“Within 600 ticks” remains pending before its deadline. It has no instrument failure merely because the future has not happened.

Likewise, an invariant can remain unviolated during an open-ended watch. It becomes satisfied for a bounded interval only when that interval closes with adequate coverage.

Runtime-verification work explicitly distinguishes definitive satisfaction, definitive violation, and inconclusive finite observations. Borrow that distinction while retaining separate probe-error diagnostics. [Bauer, Leucker, and Schallhart, *Runtime Verification for LTL and TLTL*](https://christian.schallhart.net/publications/2011--tosem--runtime-verification-for-ltl-and-tltl.pdf)

### 3.3 Clarify the existing operators

| Draft operator | Required correction |
|---|---|
| `changed(p)` | Distinguish “differs from arm baseline” from “differs from previous observation.” A return to the baseline demonstrates the difference. |
| `delta(p)` | Specify baseline capture, numeric types, counter resets, and overflow behavior. |
| `rate(p)` | Divide by elapsed ticks. Define the estimator and minimum history. |
| `settled(p, quiet=N)` | State the tolerance and observed fields. Sampled stability cannot establish continuous stability. |
| `edge(c)` | Define arm behavior and recovery after unknown observations. A new valid value after an unknown gap should establish a baseline by default. |
| `stays(c,N)` | Define elapsed duration and endpoints. If a true streak begins at tick `t`, an elapsed duration of `N` completes at `t+N`. |
| `within(c,N)` | Specify whether arm is included, check the deadline tick before expiring, and make violation terminal. |
| `seq[...]` | Specify stage activation, same-tick advancement, stage-local baselines, captured subjects, and deadlines. |
| `count(edge(c),n)` | Define reset, overlap, window, and gap behavior. Completeness depends on observation coverage. |
| `after(c,N)` | Separate a delayed trigger from evaluating another condition at the delayed tick. |
| `while(guard,c)` | Guard false currently creates UNKNOWN and therefore stops under the default policy. Add an explicit inactive state and reset/pause policy. |
| `for_each` | Define membership changes and aggregation. Returning subjects that hit is distinct from requiring every subject to hit. |
| `never(c)` | Treat a hit as violation. Avoid returning immediate success when it is placed inside `advance_until`. |

Stateful children must receive their scheduled updates even when a parent Boolean expression could short-circuit. Otherwise tree ordering changes temporal behavior.

### 3.4 Add a bounded temporal vocabulary

| Primitive | Purpose |
|---|---|
| `eventually(c, within=N)` | Reach a condition within a bounded interval |
| `always(c, for=N)` | Maintain a condition throughout a bounded interval |
| `until(a,b,within=N)` | Maintain `a` until `b` occurs |
| `responds_to(a,b,within=N)` | Create an obligation after a trigger |
| `at_offset(trigger,N,check)` | Evaluate a check at a specified delay |
| `once(c)` / `since(a,b)` | Useful bounded-history conditions |
| `count_events(source,filter,window=N)` | Count source events without reconstructing them from levels |
| `duration_where(c,window=N)` | Measure total qualifying duration |
| `duty_cycle(c,window=N)` | Measure the fraction of an interval satisfying a condition |
| `stable(p,epsilon,for=N)` | Numeric stability with explicit tolerance |
| `hysteresis(p,low,high)` | Maintain threshold state without chatter |
| `capture(name,p)` | Bind a subject or value at a stage transition |
| `at_least(k,conditions)` | Quorum conditions |
| `require_observed(trigger)` | Prevent vacuous success when a required stimulus never occurred |

For response obligations, specify whether repeated triggers create independent obligations, replace an existing one, or coalesce. Bound the number of outstanding obligations.

Implement a useful bounded subset first. MTL monitoring literature provides the vocabulary and explains why temporal nesting, future obligations, and retained history need deliberate resource bounds. [Ho, Ouaknine, and Worrell, *Online Monitoring of Metric Temporal Logic*](https://www.cs.ox.ac.uk/people/hsi-ming.ho/monitoring-full.pdf)

### 3.5 Make sampling guarantees honest

Every result should describe its coverage.

- Requested and achieved cadence.
- Actual evaluation ticks or a compact schedule description.
- Source-event completeness, where available.
- Maximum observation gap.
- Whether transitions may have been missed.

For `every=1`, call `hitTick` the first qualifying post-tick observation. That is an exact observation tick. It does not identify an intra-tick transition instant.

For `every>1`, a bracket can describe an observed endpoint change. Pulse counts, sequence order, and continuous `stays` claims require stronger evidence.

Mixed-cadence trees also need a policy. Prefer synchronized fresh inputs for correctness conditions. Explicit sample-and-hold inputs should carry age and freshness limits.

---

## 4. Expand the primitive catalogue

### 4.1 Missing probes

| Area | Additions and rationale |
|---|---|
| Entity lifecycle | Destroyed, spawned, map membership, holder chain, carried state, container contents, world-pawn/caravan membership |
| Jobs | Job instance identity, targets, start/end events, completion reason, interrupted state, toil transitions |
| Movement | Destination, path status, arrival, next path cell, progress along a declared axis, teleport detection |
| Work and ownership | Reservations, forbidden state, designated work, bill progress, work remaining, resource requirements |
| Items | Stack count, inventory membership, equipment/apparel membership, quality, durability, deterioration |
| Health | Damage/death events, bleeding, tending, immunity, hediff addition/removal |
| Networks | Connectivity, powered state, power deficit, battery charge, breakdown, flick state |
| Environment | Room identity, outdoors exposure, wetness/fluid identity, pressure or flow where supported |
| Events | Spawn/despawn, job start/end, terrain change, relevant mod pulses, map transitions |
| Instrument health | Adapter version, capability availability, last evaluation, ring retention, dropped rows, source freshness |
| Lifecycle readiness | Game identity, target-map readiness, long-event state, bridge servicing, target resolution |
| Collections | Stable IDs, membership changes, selection cardinality, and membership-generation identity |

Job and movement events would directly address short-lived behavior that state polling cannot reliably capture. Add event sources only at verified engine seams.

### 4.2 Missing value operations

Conditions need modest expression support.

- Arithmetic, absolute difference, distance, and vector projection.
- Approximate equality with absolute and relative tolerance.
- Set membership, subset, equality, and difference.
- Explicit null handling.
- Deterministic ordering for collections and `argmax` ties.
- Circular intervals for time of day, including midnight.
- Finite-number checks for NaN and infinity.

Document units. Temperature, fill fraction, depth level, ticks, seconds, and distance must be distinguishable in schemas.

### 4.3 Tighten spatial and collection semantics

Specify all of the following.

- Map coordinates versus offsets from a moving subject.
- Whether rectangle endpoints are inclusive.
- Whether out-of-bounds cells cause refusal or explicit clipping.
- Whether moving selections retain the same cells or recompute membership.
- Frozen versus dynamic subject membership.
- What happens when members enter, leave, die, or transfer maps.
- Minimum selection cardinality.

Mathematically, `all([])` is true and `any([])` is false. Tests often need `require_nonempty` so a missing subject set cannot produce a misleading pass.

For dynamic collections, preserve per-subject monitor state by stable identity.

### 4.4 Treat adapters as executable dependencies

A reflection recipe can invoke arbitrary code. A getter can allocate, mutate caches, consume RNG, or throw.

Each adapter should declare its signature, supported versions, units, availability rules, expected cost, thread affinity, and side-effect expectations. Include adapter identity and version in evidence.

Keep arbitrary `static.call` as an explicit diagnostic extension. A minimum cadence of ten ticks provides no bound on its duration.

---

## 5. Expand runners and actions without building a second test framework

### 5.1 Runner modes

| Mode | Behavior |
|---|---|
| `eval_now` | Read and evaluate without advancing |
| `advance_until` | Own stepping until a condition satisfies or another terminal cause occurs |
| `observe_until` | Watch externally driven play without owning the stepper |
| `observe_for` | Observe a bounded interval and return its monitor verdicts |
| `advance_for` | Run exactly a bounded tick count while maintaining watches and samples |
| `race` | Stop when any named outcome resolves, preserving simultaneous outcomes |
| `wait_all` | Continue until all required goals satisfy, preserving each hit |
| `record_window` | Retain bounded pre-trigger and post-trigger history |
| `await_lifecycle` | Wait through loading or readiness transitions using frame servicing |
| `dry_run` | Validate bindings, capabilities, estimated resources, and canonical form |

`race` and `wait_all` can initially be Python builders over a single underlying run specification.

Warm-up should be a declared phase. Record when it ends and when measurement baselines are captured.

### 5.2 Add atomic arm–stimulate–observe

A common test requires this ordering.

1. Arm event capture.
2. Capture baselines.
3. Perform one stimulus.
4. Observe its consequences.

Separate bridge calls leave a race between arming and stimulus. Provide a bounded request that performs those steps on the game thread.

Use existing bridge actions through a constrained action interface. Keep proof-level branching in Python.

### 5.3 Separate action classes

| Action class | Examples |
|---|---|
| Evidence | Snapshot named probes, freeze event payloads, retain a trace window |
| Run control | Stop, request pause, cancel a run, disable an owned watch |
| Scheduled stimulus | Perform a declared existing action at arm or a tick offset |
| Intervention | Maintain a temperature, need level, or other supported controlled value |
| Cleanup | Release owned resources and attempt declared restoration |

Every intervention needs an owner, lifetime, phase, schedule, failure policy, and action history.

Prefer scheduled reapplication at a declared cadence. “Every tick” should require an explicit need.

Two holds writing the same property must conflict visibly. Restoration also needs care because game behavior may have legitimately changed the property while the hold was active.

An action that partially succeeds must report that fact. Cleanup should be attempted and recorded, with any remaining mutation identified.

### 5.4 Use one terminal result with independent evidence

Keep execution outcome, condition verdict, coverage, and safety findings separate.

```json
{
  "runId": "r42",
  "state": "stopped",
  "primaryReason": "vitals",
  "condition": {
    "progress": "satisfied",
    "hitTick": 41002
  },
  "stopTick": 41002,
  "coverage": "complete",
  "triggers": [
    {"kind": "cond", "tick": 41002},
    {"kind": "pawn_downed", "tick": 41002}
  ],
  "executedTicks": 82,
  "cleanupComplete": true
}
```

Python decides whether that combination means PASS, FAIL, or UNMEASURED.

The draft’s comment “the condition IS the verdict” should be removed. A condition hit is evidence that Python interprets alongside coverage and safety outcomes.

---

## 6. Failure modes and operational edge cases

### 6.1 Required handling

| Failure mode | Required behavior |
|---|---|
| Already true at arm | A level condition can satisfy with zero executed ticks. An edge establishes its initial baseline. |
| False–true–false between samples | Report the limits of sampled coverage. Use complete source events when occurrence matters. |
| Multiple transitions in one tick | Preserve source-event order and sequence when instrumented. State samples cannot recover it. |
| Unknown between known values | Break continuity by default. Do not count a clean edge or continuous true streak across the gap. |
| Cached values | Expose source freshness where possible. Unchanged observations alone cannot prove refresh. |
| Despawn | Preserve entity identity and distinguish unavailable map context from destruction. |
| Map selection changes | Pin spatial probes to an explicit map. UI selection must not silently retarget them. |
| Subject transfers maps | Follow only when requested. Record the transition and rebind map-dependent context. |
| Map removed or unloaded | Abort scoped monitors or follow a declared lifecycle policy. Preserve terminal evidence. |
| Save/load or game replacement | Change epoch, terminate live runs, release bindings, and retain results for retrieval. |
| Tick jumps backward or forward | Invalidate affected temporal history. Require explicit rearming. |
| Ring overflow | Return a gap and lost-sequence range. Invalidate completeness-dependent verdicts. |
| Background log messages | Preserve source timing/thread metadata and dispatch timing. Avoid invented exact simulation timestamps. |
| Probe/action exception | Isolate the failure, record diagnostics, and apply the run’s explicit policy. |
| Reentrant or duplicate tick callbacks | Reject or deduplicate observations using an execution identity and phase. |
| Client disconnect | Expire an owned lease or apply a declared autonomous-run policy. |
| Conflicting clients | Permit one stepper owner and explicit compatible observers. |
| Cancel races with completion | Make cancellation idempotent and preserve the actual terminal ordering. |
| Game stops servicing frames | Detect the wall-time stall externally. An in-game tick condition cannot resolve it. |
| Evidence buffer fills | Apply declared retention or stop policy and expose lost coverage. |

### 6.2 Save/load policy

For the first version, terminate live runs on load and require explicit rearming.

Transparent monitor persistence would need serialization of baselines, hysteresis state, active sequence stages, pending response obligations, event cursors, and subject bindings. That is a separate capability.

A saved replay specification is easier to support. Store the tree and provenance, then arm a fresh run after loading.

### 6.3 Watcher ownership and leaks

Python `finally` cleanup is insufficient because processes crash and commands can be killed.

Require the following.

- Owner/session ID and run-scoped resource IDs.
- Wall-time leases renewed by the owner.
- Limits on watchers, nodes, subjects, history, rows, and retained bytes.
- Cleanup on completion, cancellation, lease expiry, load, and menu transitions.
- Idempotent release.
- Bounded retention of terminal results.
- Ownership information in `watch_list`.

Replace ordinary harness `watch_clear(all)` with owner-scoped cleanup. Global clearing can remove another test’s or the owner’s watches.

A warning about an orphan watcher does not resolve the leak.

### 6.4 Vitals stop-latch interaction

Keep the existing safety restrictions. Tighten the integration.

1. Associate condition triggers with a run ID and latch cursor.
2. Check for applicable existing safety stops before beginning another tick.
3. Collect all relevant causes observed at the stopping point.
4. Give safety causes precedence over a success-only terminal classification.
5. Preserve the condition hit even when safety takes precedence.
6. Require explicit acknowledgement before any recovery-and-resume path.

A per-tick condition hook does not improve the detection cadence of vitals checks that still run per chunk. Report safety observation latency separately.

Do not pass an `advance_until` interruption through automatic benign recovery without deciding whether its temporal history remains valid. A recovery mutation or observation gap can invalidate an ordering or continuity claim.

### 6.5 The 540-second command limit

Model three independent limits.

| Limit | Effect |
|---|---|
| Simulation tick ceiling | Bounds game advancement |
| Run wall-time ceiling or lease | Bounds background execution |
| Client command deadline | Bounds one external invocation |

Returning `running` before 540 seconds solves only the third limit.

Prefer a prompt `start` response with a durable run ID, bounded status calls, and separately paged evidence. Add the following guarantees.

- An idempotency key prevents a lost start response from causing duplicate execution.
- Reattachment uses the existing run ID.
- Status polling cannot reset simulation deadlines.
- Resuming preserves the original cumulative tick budget.
- Terminal results remain available after a lost response.
- Each external invocation leaves margin for transport, retries, and serialization.
- Long Python supervisors checkpoint and yield before their own command deadline.

Continuing in-game after a caller disappears should require an explicit bounded policy. Lease expiry should stop owned advancement and release owned interventions.

---

## 7. Cost, determinism, and evidence integrity

### 7.1 Replace the provisional cost budget

A default allowance of 0.5 ms per tick is substantial.

- At 60 ticks/s, it consumes 30 ms of evaluator CPU time per second.
- At 3,000 ticks/s, it would demand 1.5 seconds of evaluator CPU time per second.
- Across 1.2 million ticks, it permits 600 seconds of evaluation work.

Measure overhead against the intended burst throughput. Use both per-evaluation limits and aggregate frame/run budgets.

The current node and rectangle caps are insufficient. Cap total expanded subjects, total cells across probes, temporal history, pending obligations, and retained bytes.

### 7.2 Define what budgets can enforce

A stopwatch detects an expensive synchronous getter after it returns. It cannot safely interrupt arbitrary mod code on the game thread.

Therefore the implementation should do the following.

- Admit cheap verified probes to strict per-tick runs.
- Treat arbitrary calls as unbounded extensions.
- Check budgets between operations.
- Disable or stop after an overrun.
- Report the actual overrun and resulting coverage.

Automatic cadence degradation changes semantics and can make outcomes wall-time-dependent. Allow it for explicitly exploratory sampling. Correctness runs should stop when they lose their promised cadence.

### 7.3 Share reads without hiding state

Read each shared probe once per observation context. Keep monitor-specific state separate.

Do not let `changed`, `delta`, or sequence baselines become shared merely because their underlying probe is shared.

“No allocation per evaluation” can be a target for a warmed, fixed-size core. Qualify it around event recording, strings, variable-length collections, reflection, and serialization. Measure steady-state and event-hit paths separately.

### 7.4 Determinism needs provenance

The same save and tree are insufficient provenance for a deterministic replay.

Retain the following.

- Save hash and initial epoch/tick.
- Game, bridge, mod, settings, and adapter versions.
- Canonical tree and evaluator-semantics version.
- Subject bindings and collection ordering.
- Stimuli and intervention history.
- Cadence, gaps, and budget decisions.
- Relevant RNG and external-input controls.

Probes should avoid RNG consumption and gameplay mutation. Stat calculations and mod getters need verification against that expectation.

Compare instrumented and uninstrumented runs as well as repeated instrumented runs. A monitor that perturbs the result can reproduce its own perturbation consistently.

### 7.5 Preserve useful failure evidence

Add a bounded pre-trigger ring so a failure retains its lead-up.

Each terminal result should include the last relevant values, active temporal stage, pending obligations, observation gaps, simultaneous triggers, and first diagnostic failure.

Freeze evidence at the observation point. A deferred snapshot or screenshot must carry its own capture tick/frame.

---

## 8. Flyer frame recording needs a narrower claim

### 8.1 What is wrong in the draft

**A texture-path trace cannot establish what appeared on screen.** It may establish which animation state a verified selector would choose from the observed state.

The assertion that the displayed frame is a pure function readable identically while paused is too broad. It requires verification of render preparation, cached state, visibility behavior, custom render nodes, worker overrides, and patch ordering.

Further problems include the following.

- A pawn can have multiple relevant render nodes and layers.
- A selected graphic state may resolve through directional variants, masks, atlases, bundles, and mod overrides.
- `drawPos` can itself depend on render/update preparation.
- Multiple simulation ticks may occur between rendered frames.
- Facing need not equal movement direction during turns, stationary periods, forced rotation, or custom animation.
- West mirroring is an implementation-specific claim.
- `durationTicks = (count+1)*ticksPerFrame` alone does not establish the final frame’s behavior.
- Logging only changes in `[state, animation, keyIndex, rotation]` loses intermediate trajectory information.
- Raw sprite dimensions beside a human PNG do not establish in-game scale.
- A GIF needs a declared playback clock and explicit treatment of gaps.

### 8.2 Split the capability into three evidence products

| Product | What it can establish |
|---|---|
| Asset audit | Expected assets resolve under verified definitions and content precedence |
| Tick-state trace | Observed flight state, animation identity, animation time, facing, and verified selector outputs |
| Rendered-output evidence | What the rendering pipeline actually produced |

The existing standing ruling constrains rendered capture. The proposed deliverables should therefore be named an **asset contact sheet** and **reconstructed animation**, with their evidence limits stated.

### 8.3 Improve the recorder schema

Record these fields where they are available through verified reads.

- Game/mod version and pawn identity.
- Simulation tick, observation phase, and animation start identity.
- Flight state and animation time.
- Relevant render-node identity.
- Selected graphic state and resolved asset identity.
- Facing, mirroring, and available transforms.
- Logical position.
- Render-position value with freshness/provenance.
- Availability, gaps, and adapter version.

Record trajectory and animation-state changes as separate channels. Run-length encoding can preserve frame dwell, while periodic position rows preserve movement.

### 8.4 Preserve the joint-session gate

`jointSession=true` is a caller assertion. It cannot establish owner presence.

Use the established session-control mechanism if one exists. Otherwise require explicit owner confirmation for the bounded live run and retain that confirmation with the run record.

Offline validation can establish parsing, asset enumeration, trace encoding, and reconstruction. It cannot establish live animation selection or clearing on landing.

The flyer ticket should begin with verifying the proposed observation seam. Its acceptance criteria must distinguish asset coverage, selector behavior, and visual appearance.

---

## 9. Prior art and what to borrow

### 9.1 Unity Test Framework and `WaitUntil`

`UnityTest` supports coroutine-style Play Mode tests that yield control back to the framework. Unity documents a specific frame phase for `WaitUntil` predicate evaluation. Borrow cooperative execution, explicit observation phases, and resumable orchestration. Keep RimWorld simulation-tick deadlines explicit because Unity frame and time behavior belongs to a different clock domain. [UnityTest documentation](https://docs.unity3d.com/Packages/com.unity.test-framework@1.4/manual/course/unitytest-attribute.html), [Unity WaitUntil documentation](https://docs.unity3d.com/6000.0/Documentation/ScriptReference/WaitUntil.html)

### 9.2 Minecraft GameTest

Java GameTest’s `succeedWhen` checks assertions each tick until success or timeout. Its exact-tick variant distinguishes eventual success from timing correctness. Bedrock’s sequence API separately exposes waits, delays, repeated actions, and terminal success/failure. Borrow bounded runs, fixture-backed scenes, sequence-stage diagnostics, and exact-tick assertions. Keep Java and Bedrock API details distinct in implementation references. [Forge GameTest documentation](https://github.com/MinecraftForge/Documentation/blob/1.21.x/docs/misc/gametest.md), [Microsoft GameTestSequence documentation](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server-gametest/gametestsequence?view=minecraft-bedrock-experimental)

### 9.3 Factorio test frameworks

Community framework FUnit provides setup/teardown hooks, tick-delayed continuation, event-triggered continuation with optional timeout, JSON reporting, and separate failed/error results. Manis TestFramework documents an explicit determinism policy. Borrow event waits, lifecycle cleanup, machine-readable evidence, and reproducibility requirements. These are community examples with different scopes. [FUnit documentation](https://mods.factorio.com/mod/funit), [Manis TestFramework](https://github.com/suumani/Manis_TestFramework)

### 9.4 Godot GUT

GUT’s `wait_until` repeatedly evaluates a callable with a maximum wait. `watch_signals` records emissions for later assertions, and its signal-wait helper installs watching automatically. Borrow arm-before-action observation, explicit timeout results, signal arguments, and occurrence counts. Its separate idle-frame, physics-frame, and time waits also reinforce the need for clock-specific APIs. [GUT awaiting documentation](https://github.com/bitwes/Gut/blob/main/documentation/docs/Awaiting.md), [GUT test API](https://gut.readthedocs.io/en/v9.7.0/class_ref/class_guttest.html)

### 9.5 Unreal Automation latent commands

Unreal latent commands retain state across frames. Their `Update()` returns completion status so the framework can revisit unfinished work. Borrow cooperative bounded work, persistent command state, and ordered continuation. Loading and other frame-dependent tasks belong in this kind of servicing path. [Unreal Automation Technical Guide](https://dev.epicgames.com/documentation/unreal-engine/automation-technical-guide?application_version=5.3)

### 9.6 Playwright and Selenium

Playwright combines actionability checks with auto-retrying assertions. Borrow declarative prerequisites, re-resolution policies, and diagnostics that identify which prerequisite remains unmet. Selenium documents explicit waits and warns that combining implicit and explicit waits creates unpredictable timeout behavior. Use one propagated deadline and keep probes free of hidden waits. [Playwright auto-waiting](https://playwright.dev/docs/next/actionability), [Playwright assertions](https://playwright.dev/docs/test-assertions), [Selenium waiting strategies](https://www.selenium.dev/documentation/en/webdriver/waits/)

### 9.7 LTL/MTL runtime verification

Borrow definitive versus pending verdicts, bounded eventually/always/until, explicit trace semantics, and monitor state machines. Use a small bounded language initially. An online monitor must know when it has enough evidence to resolve a property, and when retained history or missing observations prevent resolution. [Runtime Verification for LTL and TLTL](https://christian.schallhart.net/publications/2011--tosem--runtime-verification-for-ltl-and-tltl.pdf), [Online Monitoring of Metric Temporal Logic](https://www.cs.ox.ac.uk/people/hsi-ming.ho/monitoring-full.pdf)

### 9.8 Property testing

Hypothesis stateful testing generates action sequences and checks invariants after steps. Borrow generated temporal traces for evaluator testing, shrinking of failing traces, and reproducible action histories. Apply those techniques offline first, then to selected bounded live scenarios whose fixtures can be reset reliably. [Hypothesis stateful testing](https://hypothesis.readthedocs.io/en/latest/stateful.html)

---

## 10. Revise the ticket split

### 10.1 Problems with the proposed split

- `CONDEVAL_BUILD_COMPILED_TREES` is too large. P1–P34 spans basic fields, arbitrary mod calls, temporal state, rendering, and performance instrumentation.
- The Python API arrives too late for the first end-to-end proof.
- Lifecycle handling, ownership, idempotency, retained results, and event gaps have no clear ticket owner.
- Sampling and event watching share storage concerns but have different completeness semantics.
- `await_lifecycle` belongs outside the poll-loop migration ticket.
- Ten migrations are too many before validating the execution contract.
- Flyer seam discovery, offline asset checking, reconstruction, and joint-session validation are bundled together.
- Acceptance bars emphasize feature presence more than false-pass prevention.

### 10.2 Proposed tickets and acceptance bars

The following names are suggestions and have not been namechecked.

| Ticket | Scope | Acceptance bar |
|---|---|---|
| `COND_CONTRACT_AND_VECTORS` | Schema, types, clocks, temporal semantics, coverage, result model | Executable boundary vectors cover arm behavior, unknowns, deadlines, gaps, and empty sets |
| `COND_ADVANCE_MINIMAL_SLICE` | Minimal C# probes, comparison/all/any/not, per-tick integration, minimal Python wrapper | One water-fill proof completes through the normal API with correct tick count and safety handling |
| `COND_RUN_LIFECYCLE` | Ownership, idempotent start, status, cancellation, lease, retained results | Lost responses and retries create one run, preserve results, and leak no resources |
| `COND_TEMPORAL_MONITORS` | Edges, stability, bounded temporal operators, sequence state | Python/C# differential tests agree on generated traces and boundary cases |
| `COND_EVENT_SOURCES` | Existing ring integration, subject filters, gaps, selected new hooks | Short events are observed through complete sources, overflow invalidates affected claims |
| `COND_SAMPLER_AND_TRACE_WINDOWS` | Sampling, change logs, pre/post-trigger history, paging | Retention is bounded and coverage loss is explicit |
| `COND_ADAPTER_CAPABILITIES` | Verified FlowWorks adapter first, capability/version metadata | Missing or incompatible mods produce named availability failures |
| `COND_LIFECYCLE_READY` | Frame-serviced readiness and Python helper | Covers loading, menu, missing map, cancellation, and wall-time timeout |
| `COND_ACTIONS_AND_HOLDS` | Atomic stimulus, scheduling, intervention ownership, cleanup | Conflicts, partial failure, and residual mutations are reported |
| `COND_INVARIANTS_AND_MIGRATIONS` | Opt-in invariant packs and three representative migrations | Each migration demonstrates preserved verdicts and improved evidence/call counts |
| `COND_FIELD_SNAPSHOTS` | Typed grids, provenance, spatial diff | Map and shape mismatches are rejected and source ticks are retained |
| `FLYER_SELECTOR_DISCOVERY` | Verify animation/asset observation seams | Claims are documented against the deployed versions |
| `FLYER_OFFLINE_RECONSTRUCTION` | Asset audit, trace decoding, contact sheet, animation | Missing assets, gaps, dwell, and provenance are visible |
| `FLYER_JOINT_VALIDATION` | Bounded owner-present live validation | Live selector claims are checked and limitations recorded |

Budget admission and aggregate resource limits belong in the initial slice. Arbitrary reflection and arbitrary actions can follow later.

### 10.3 First migrations

Choose three cases that exercise distinct guarantees.

1. **Water fill** tests a cheap level condition and round-trip reduction.
2. **Short job lifecycle** tests event completeness and subject identity.
3. **A bounded invariant during staging** tests violation handling, safety interaction, and pre-trigger evidence.

Measure bridge calls, wall time, executed ticks, evaluator overhead, observation coverage, and cleanup.

### 10.4 Required regression cases

The shared suite should include at least these cases.

- True at arm and `max_ticks=0`.
- Success exactly on the deadline.
- Safety stop and condition hit on the same tick.
- A pulse entirely between samples.
- Multiple source events in one tick.
- Unknown in the middle of a true streak.
- Entity despawn, transfer, destruction, and map removal.
- Save/load and tick discontinuity.
- Ring overflow and evidence truncation.
- Duplicate start after a lost response.
- Cancel/complete races.
- Lease expiry with an active intervention.
- Shared probes with independent monitor baselines.
- Stateful children beneath Boolean short-circuit opportunities.
- Slow getters and lost cadence.
- Empty and changing subject collections.

## 11. Recommended first delivery

Build one trustworthy path from Python through `safe_advance` to a retained terminal result.

That first delivery should include a small typed probe set, basic conditions, per-tick observation, safety arbitration, bounded sampling, run ownership, retry-safe transport, and explicit coverage. It should prove the water-fill case and survive cancellation, load, disconnect, and deadline boundaries.

The broader catalogue can then grow around a tested execution contract.