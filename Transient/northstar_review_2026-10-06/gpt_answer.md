# Northstar review

**My leading hypothesis: Northstar’s main bottleneck is producing durable, attributable evidence—not running RimWorld or writing more checks.** GSS demonstrates that dense validation can work. The broader programme repeatedly spends live time on invalid fixtures, stale deployments, broken instruments, and results that never reach the authoritative report.

This is a hypothesis list for testing. I reviewed all supplied files as inlined, without opening files from disk. Citations identify filenames plus sections, functions, or exact phrases. The implementations of `required_checks_report.py`, `modcheck.status`, and FlowWorks’ `validation_v2.py` were not supplied; conclusions about their internals remain hypotheses. Build costs below are estimates for one engineer familiar with this repository.

## 1. Diagnosis

### 1. The best checkouts and the lead metric appear to use disconnected evidence paths

Tonight’s measurement is a fact:

> `TOTAL proven 0 of 1543 required (owner bars 0 of 0)`

FlowWorks and GimmeSomeSlack are absent from the report. That does **not** establish that their mechanisms fail. It establishes that the reporting system does not currently account for the project’s two completed checkout efforts.

Specific evidence:

- Both walks prescribe a separate `modcheck.cli record ... --result ...` command after their custom proof runs.
- `proof_all.py` writes its own result JSON; it does not call `record_run`.
- `debug_process.md §1` explicitly records the earlier gap: “the driver does not record into `modcheck_status.json` today.”
- `required_checks_now.txt` includes `observed-not-in-manifest`, alongside stale deployment and unknown identity reasons.
- The report says **“0 more would be proven if the run’s deploy were recorded fresh.”** Deployment bookkeeping alone therefore cannot repair this snapshot.
- FOUNDRY’s `202610040745` handoff reported **28/1690**; tonight is **0/1543**. Neither the lost numerator nor the changed denominator is reconciled in the supplied evidence.

**Hypotheses to test:** custom result formats are not connected to required-check manifests; discovery misses nonstandard entry points; rename/composition identities are inconsistent; or proof files exist but their record commands were never successfully ingested. Several could coexist.

**Cheapest discriminator:** trace one GSS row from `proof_all` JSON → record command → status entry → required-check mapping → report contribution. Repeat for one FlowWorks row. Print every join key and rejection reason. Do this offline before spending another live minute.

The remedy is not to loosen taint rules. It is to make missing registration, missing identity, and failed behavior separately visible.

### 2. A run’s subject keeps changing while it is being tested

This is principally a **HARNESS/control-plane defect**.

FOUNDRY’s `202610040745` handoff names the cause directly:

> “stale deploys (builders rebuild DLLs after each deploy)”

Other evidence shows that the bridge lock does not protect the complete experiment:

- `lessons_extract.md`, `20260926`: agents respecting the bridge lock still race `ModsConfig.xml`.
- `20260927`: a worktree agent’s quicktest/restart overwrote a session whose holder correctly held the lock.
- `20260929`: restoring from the committed full-list snapshot reintroduced a load-order defect fixed only in the live config.
- `202610020551` handoff: prep deployed from a source tree approximately **304 commits behind**.
- `20260927` lesson: a stale deployed DLL failed silently because its expected startup self-test never printed.

`proof_all.py:p2_tier_and_startup_log()` records a repository `mod_hash`, running package IDs, and an assembly SHA. But the shown code does not compare the live assembly SHA to the expected deployment, bind a `.srchash`, or verify the complete expected tier.

**Consequence:** an honest assertion can describe the wrong build. More check depth cannot compensate.

**Cheapest discriminator:** deliberately deploy an older DLL while leaving current source in place. Preflight must refuse before site construction. Separately, attempt a mod-list swap from another session during a held run; it must be rejected by the same lifecycle lock.

### 3. Random fixtures and incomplete setup turn ordinary tests into investigations

This is mainly **SITE/HARNESS cost**, although a surprise can expose a real mod defect.

The time ledger measured **84.7 minutes—40% of the 210-minute pass—on runs failing their own bland-world setup gate**. Other examples recur:

- Fixed cells were unstandable; fixed zoom assumptions failed. Both were corrected in GSS’s densification work.
- `lessons_extract.md:20261005`: fewer than two free colonists makes SL4 UNMEASURED.
- `20261002`: `Session.sweep` killed test colonists using `Bomb 99999`.
- `20261003`: clearing ruins with RealFoW active caused an exception on every update.
- `20261001`: an unsettled generated map could be culled on save.
- FOUNDRY’s `202610040745` handoff reports unexplained cuts every approximately 120 ticks, affecting six mods.

GSS now prepares much more of its fixture explicitly, but it still selects available colonists and searches random terrain for parking cells. Those are avoidable sources of uncertainty.

**Hypothesis:** a fixture service with explicit prerequisites would eliminate much of the remaining UNMEASURED volume.

**Cheapest discriminator:** construct the same fixture repeatedly from a fixed seed or verified saved baseline. Assert exactly the needed pawn count, roles, terrain, settlement, roofs, needs, and incident state. Compare fixture fingerprints before running a mod check.

“Boring” must be scoped: suppress ambient incidents, while leaving the fire, injury, drowning, or job behavior under test operational.

### 4. Live time is dominated by invalid work, RPC overhead, and unnecessary simulated time

The supplied measurements contradict a blanket “loads are expensive” explanation.

`northstar_time_ledger_2026-10-01.md §2` measured:

| Cost | Minutes |
|---|---:|
| Setup-gated runs | 84.7 |
| Harness-lost/voided runs | 64.0 |
| Clean productive 13-suite run | 16.4 |
| Two minimal-list launches themselves | Approximately 1.2 |

Within valid execution:

- Antiquities waited **95,000 ticks**, even though its docstring acknowledges that a skilled reader finishes early.
- Antiquities and FlowWorks accounted for **94% of ticks and 91% of wall time** in the slow run.
- Each 600-tick sweep made approximately **17–20 calls**, with a measured median call latency of **48 ms**.
- The GSS settings-type discovery scanned all loaded assemblies on every call. The `20261004` lesson measured **0.74 s → 0.050 s** after caching; that one call had consumed **88% of a 2,640-second matrix run**.

These are **HARNESS economics**, not mod defects. The discovery fix is already banked; it should not be claimed again as future savings.

The 416→50 ticks/s collapse remains causally unresolved in the ledger. Later evidence says setting `RunInBackground=True` removed a focus dependency (`lessons_extract.md:20261003`), but that does not retrospectively separate focus, map count, and CPU cost in the original pass.

**Cheapest discriminator:** record step time, observation time, tick delta, map count, and background setting for every chunk. Then repeat the ledger’s small map-count/background A/B experiment.

### 5. Positive mechanism assertions still miss the player’s experience

This is a **CHECK defect** that permits real **MOD defects** to escape.

The strongest counterexample is already documented:

- `north_star_validation_spec.md`, “Why this exists”: Pits passed `expect_pawn_despawned`, while its render hook drew the occupant standing on a vanilla trap icon.
- `FlowWorks.md`, anti-guessing notes: state assertions passed while the channel borrowed a gravel texture.
- FOUNDRY’s `202610050845` GSS handoff:

> “Every defect this round came from the owner LOOKING at the review map, not from a check.”

Both supplied walks now say `state: DRAFT`. GSS has drafted visual expectations, but they do not yet supply binding automated experience proof.

There is also an observation effect:

- The debugging skill says camera movement repaints sections.
- `proof_all.py:install_no_shots()` deliberately preserves camera moves because graph rebuilding depends on camera-driven section regeneration.

That is sensible for exercising rendering, but it can conceal a failure to invalidate an already visible section.

**Hypothesis:** the current checks are stronger at proving internal state and forced refresh than ordinary player-visible updates.

**Cheapest discriminator:** keep the camera stationary, perform a conduit mutation, read dirty-section/mesh state, and capture without reframing. Only then move the camera and compare. A defect repaired by looking must be recorded as such.

### 6. “Basic checkout” is too easy to shrink without exposing the resulting claim

`debug_process.md §6b` excludes removal and mod-mod compatibility from a normal checkout. That ruling is clear.

FlowWorks’ current walk goes further: its on-request extension proof includes **“optional-feature chains”** covering doors, spikes, prison rooms, capture down, pumps, bottle revert, and other ordinary mechanics. The remaining-functionality inventory separately says substantial machinery is **BUILT, live verification owed**.

A settings toggle makes a feature optional to use; it does not automatically make it outside basic functional coverage.

Coverage declarations also drift:

- `debug_process.md §2.3` requires every must-be-true line to end in `→ chain.component` or `→ UNCOVERED`.
- FlowWorks has five must-be-true bullets without those arrows, despite a much larger shipped surface.
- GSS adds subsystem coverage, but broad lines such as M10 and M13 combine many behaviors and cite groups of rows in parentheses.
- GSS E4 says “no pump in FlowWorks yet,” while `flowworks_remaining_2026-10-05.md` records a built pump slice and machinery pass.

**Hypothesis:** the registry cannot reliably distinguish a complete checkout from a complete run of a narrowed selection.

**Cheapest discriminator:** enumerate shipped mechanics/settings against declared requirements and default-run membership. Every omitted ordinary feature must produce an explicit coverage gap. Keep compatibility/removal separately requested, as the owner ruled.

### 7. The shown collector still has paths to lost evidence and permissive completion

These are concrete **HARNESS review findings in the supplied `proof_all.py`**, requiring confirmation with focused tests:

| Code location | Finding |
|---|---|
| `Proof.block()` / `Proof.want()` | `--only core,aerial` also skips the `"preflight"` block. |
| `Proof.__init__()` | `--no-fresh-map` alone still gets `"mode": "live"`, despite being documented as debugging. |
| `main()` | Accepted offline reds do not automatically make the run diagnostic/partial. |
| `Proof.take()` | A missing result or empty row list adds no missing-evidence failure. |
| `main()` exit predicate | Only FAIL, UNMEASURED, and `aborted` cause failure; other unexpected/nonpassing statuses can exit zero. |
| `main()` artifact write | JSON is written after `P.run()` and restoration. An uncaught exception in determinism or `log_budget()` can lose accumulated evidence. |
| `p3_probes_and_site()` | `w.get("success") is not False` accepts a missing success field. A failed pawn-list call can look like an empty region. |
| `log_budget()` | No shown success/completeness check; a failed response can look like no errors, and `limit=1000` can omit earlier entries. |

A single socket and per-block exception rows are good improvements. But “the session goes on” is safe only if a failed block has not invalidated later blocks’ prerequisites.

**Cheapest discriminator:** use a fake bridge to inject missing fields, empty results, an unknown status, and a final log exception. The run must preserve its partial artifact and refuse certification.

### 8. Policy history has become executable guidance, and the incentives reward activity

The docs contain valuable lessons, but too much historical material remains indistinguishable from current instructions.

Examples:

- The debugging skill says minimal cold load is **22 seconds**, then later says a cold load costs **23–30 minutes** without consistently separating tiers.
- It forbids full-list quicktest categorically; CLAUDE’s September 27 excerpt reports it working after content fixes; a same-date lesson reports another ready-load path failing. These need exact environment/tool-version attribution.
- `north_star_validation_spec.md §10.4` permits model YES on open text. §§4, 5, 10.2, 11, and even §10.4’s final mitigation still preserve the opposite rule.
- `debug_process.md §2` mandates a `modcheck Suite`; the successful GSS proof is a custom orchestrator.
- The human-review doc says sheets live in `Transient/`; densification says they live in the mod’s `review/`; the GSS walk still points to `Transient/`.
- The spec says owner vision is **“the only bottleneck”**; the ledger and FOUNDRY’s 20-hour session demonstrate major harness and evidence bottlenecks.
- “Keep the bridge busy” is an activity metric. A setup-invalid run can maximize utilization while proving nothing.

**Hypothesis:** agents follow locally plausible but mutually incompatible fragments, then preserve the gap in a handoff.

**Cheapest discriminator:** give a fresh agent one small mod and only the proposed current checkout contract. Count the decisions that still require consulting historical prose.

## 2. Faster

Rank by **expected valid live minutes saved × eligible mods ÷ build hours**. Eligibility counts and present baselines are incomplete, so this is a provisional ordering, not a calculated ROI table. Historical losses are opportunities to prevent recurrence—not guaranteed savings on every run. Savings overlap and must not be added together.

| Rank | Strategy | Evidence and likely benefit | Estimated build cost |
|---:|---|---|---:|
| 1 | Preserve results continuously; reject invalid setup before expensive work | The ledger lost/voided 64 minutes and spent 84.7 minutes on setup-invalid runs. Applies across the shared runner. | 1–2 days |
| 2 | Freeze one verified deployment per run batch; lock deploy, config, launch, and bridge together | Repeated cross-session restarts and stale DLLs invalidate whole experiments. Broadest prevention benefit. | 2–4 days |
| 3 | Batch observations; cache discovery; use lightweight watches | Ledger estimates 5–7 minutes recoverable from sweeps. GSS already proves discovery caching’s importance. Shared across ticking suites. | 1–3 days |
| 4 | Replace worst-case waits with bounded `wait_until` and explicit tick budgets | Antiquities’ 95k wait; FlowWorks’ 799 excavation polls. Largest gains concentrated in long-job mods. | 0.5–2 days |
| 5 | Reuse verified results according to changed dependencies | Existing expensive proofs should not rerun for unrelated edits. Broad benefit after identity is reliable. | 2–4 days |
| 6 | Generalize GSS’s one-session, disjoint-site, shared save/load structure | Demonstrated approximately 30→10 minutes for GSS. Greatest benefit for mods with several proof scripts. | 2–4 days shared work |
| 7 | Run compatible mods in one warmed tier/load | Full loads cost approximately 15 minutes; minimal loads are cheap. Amortize full-list validation across many mods. | 1–3 days |
| 8 | Expand offline def/type/patch contract checks | Known startup defects have straightforward structural signatures. Avoid failed launches across content mods. | 2–5 days initially |
| 9 | Reuse verified saved fixtures and reset recipes | Avoid repeated worldgen/site construction and random fixtures. Benefit must be measured: clean quicktest creation can already be very cheap. | 2–4 days |
| 10 | Prototype a narrowly scoped engine-backed headless loader | Potentially broad, but Unity/static initialization may dominate implementation. Less certain ROI than the existing fixes. | 2-day feasibility spike; more if viable |

### Move computation offline, with explicit limits

**Def graph and assembly metadata.** Extend the existing patch validators to catch the defects the handoffs actually found:

- nonexistent enum literals such as `PlantPurpose.None`;
- fields under the wrong owner, such as `butcherProducts` inside `race`;
- unresolved classes, nonexistent `PatchOperationAddOrReplace`, and inactive-mod types;
- drug defs missing required comps;
- effective null `thingClass` after inheritance;
- unresolved cross-tier references and incorrect `MayRequire`;
- exact `PatchOperationFindMod` names, including composed-mod names and `Core`;
- source files omitted from explicit `.csproj` compile lists;
- duplicate/incompatible comps and settings-definition parity.

Use the pinned RimWorld and dependency assemblies to derive field/type/enum contracts. A grep alone is insufficient because inheritance, comments, patching, and custom def classes matter.

**Patch application.** Start with the existing `validate_patch.py` machinery, adding ordered application, match counts, pre/post graph diffs, and provenance for each changed field. Support the project’s actual custom patch classes incrementally. Compare its output to a live def census before claiming engine equivalence.

**C# tests.** Reference actual pinned game assemblies where feasible; use decompiled types to understand seams. Test extracted calculations and adapters that can run without Unity initialization. A stubbed `Map` proves behavior against that stub, not RimWorld’s region system.

**Fake games.** Keep the existing FlowWorks `fakegame.py`, GSS matrix fakegame, and MockBridge faults. They are cheap places for many generated cases. Do not build a general fake RimWorld first: start with the narrow contracts these mods exercise.

### Reuse warmed state without pretending RimWorld can simply fork

A verified save is the first useful snapshot mechanism here.

- Key it by game/DLC/mod-list/build identity and fixture recipe.
- Verify settlement, map count, pawns, terrain, settings, and incident state after loading.
- Reuse the one bland map rather than accumulating maps.
- Compare reset-by-recipe with reload-from-save for both cost and isolation.

A save does not necessarily reset static caches, settings, or unsaved companion state. Add reset hooks and verify them. Genuine process/VM snapshotting is a later experiment; no supplied evidence establishes that it is practical for this Windows/Unity setup.

### Batch simulation, not bridge clients

Keep one serialized bridge connection. The ledger explicitly associates side connections with mixed replies.

Several independent sites can run jobs simultaneously, with one tick advance satisfying their waits. Their tick cost can approach the longest wait rather than the sum of waits. This is only valid when:

- regions are separated by the mechanic’s actual reach;
- global settings/weather remain compatible;
- one site’s fire, explosions, power, or jobs cannot affect another;
- observers retain per-site expected outcomes.

Do not casually turn four global cable styles into simultaneous local variants—the human-review document correctly identifies that as a mod behavior change.

### Cache by dependency, not just by folder

A result should depend on the tested shipped files, referenced defs/assemblies, settings, fixture, harness, and requirement predicate.

Examples:

- Editing the review sheet should not rerun GSS geometry.
- Editing hose carry logic must rerun carry, its save/load branch, and dependent relay behavior.
- Editing `CordBuilder` must rerun generated geometry and live adapter sentinels.
- Editing the shared snapshot parser must invalidate all checks that consume it.
- Changing a composed biome assembly must invalidate its constituent features.

Cached evidence retains its original run identity. It must not be presented as newly observed.

## 3. Deeper

GSS and FlowWorks already have important ingredients: independent-language oracles, fake games, determinism checks, and offline mutations. The next step is systematic coverage of **sequences and failure classes**, rather than more hand-authored happy-path scenes.

| Strategy | Specific tests for this codebase | What it catches |
|---|---|---|
| Property-based testing | Generate GSS conduit graphs with gaps, rings, walls, multiple nets, and insertion/deletion sequences. Generate FlowWorks depth/fill/body graphs and debit/credit operations. Preserve and shrink failing seeds. | Cases omitted by the fixed scene catalogue. |
| Metamorphic testing | Translate a topology within valid bounds; reorder construction; rebuild incrementally versus freshly. Split/rejoin a conduit run. For isolated FlowWorks cells, compare equivalent total debits and transfers. | Coordinate, ordering, caching, and path-dependent errors. |
| Long-time invariants | Check liquid accounting with explicit rain/refill/burn terms; nonnegative stocks; valid depth/fill bounds; no illegal net edges; no orphan hose references; bounded queues/caches. | Slow leaks, accumulation, exhaustion, and delayed corruption. |
| Whole-graph save/load diffs | Capture world/map components, holders, jobs, target references, terrain layers, stocks, styles, links, and pending actions. Compare immediately after load, then compare equal-length continuations. | State omitted by current selected censuses. |
| Mutation testing | Disable a real job effect, make a command no-op while returning success, suppress mesh invalidation, drop a saved field, or weaken a predicate. Require the intended check to fail. | Checks that agree with themselves or never detect the actual defect. |
| Differential runs | GSS master switch/mod off versus on; FlowWorks engine/toggle off versus on. Check untouched vanilla overlay, terrain, jobs, and power behavior. | Harmony overreach and collateral changes. |
| Def-value fuzzing | Exercise zero, minimum, maximum, and malformed values for viscosity, cadence, capacity, range, depth, transition time, and conversion ratios. | Divide-by-zero, overflow, invalid clamps, and bad authored values. |
| Targeted interference sweeps | GSS power/render neighbors; FlowWorks + GSS pump; DBH thirst patch; VE adapters; RealFoW cleanup. Select pairs by shared Harmony targets and def dependencies. | Integration defects absent from minimal tiers. |
| Tick-time regressions | Measure engine tick cost for empty/control and populated scenes at increasing sizes, separately from bridge/render/watch time. | Mod performance regressions hidden by harness latency. |

### Treat matrix reduction as a tested hypothesis

The densification rule is excellent:

> “A row is cut only when another row … FAILS whenever it fails.”  
> — `northstar_densification_lessons.md`, “What was cut”

But the GSS topology×setting reduction relies on an additional assumption: settings do not introduce untested interactions in the **Verse adapter**, because those combinations are covered offline in the core.

“Every factor value runs once” does not establish that assumption. Pairwise coverage likewise does not detect every three-factor interaction.

Keep the reduced matrix as the default. Validate the reduction by:

1. comparing full and reduced runs on several fixed seeds;
2. injecting setting-dependent adapter faults;
3. recording which faults the reduced set misses;
4. retaining inexpensive targeted live pairs for those classes.

Do not describe the reduction as lossless until the relevant implication has been demonstrated.

### Separate a production defect from an instrument defect

FlowWorks’ O-LIVE-NEG MockBridge faults prove the observer responds to corrupted inputs. That is valuable, but it does not prove a real C# defect produces those inputs.

Use two mutation layers:

- **Instrument mutation:** missing fields, truncation, stale replies, incorrect success, empty lists.
- **Production mutation:** wrong conservation, stale meshes, broken job progression, dropped serialized state.

A never-red check has weak evidence. A check red only under a mock may still be blind to the production defect.

Keep the known Pit rejection and Gizka-facing counterexample as judge calibration fixtures. A fake judge comparing frame bytes verifies plumbing; it does not establish the visual model’s accuracy.

### Control randomness and time explicitly

Record world/map seed, scene seed, pawn-generation inputs, and action order. Where possible, isolate test RNG use from game RNG and restore its state.

- Deterministic jobs should use deliberately constructed pawns.
- Probabilistic mechanisms should use a declared batch and acceptance rule.
- Random quicktest colonist count must not determine whether SL4 can run.
- Flyers retain the owner’s deterministic `Pawn_FlightTracker` state-read rule; do not resume screenshot hunting.

FlowWorks’ zero-tick phase checks are valuable algorithm/adapter evidence. They should be paired with a small number of actual engine-cadence checks. `time_set_ticks` scrubs the clock; it cannot establish that a mechanism survived a simulated day.

### Make persistence about continuation, not just equality

GSS SL3 already has useful nonempty-before guards and covers several subsystems. SL4 additionally tests resumed behavior. Generalize that distinction:

- **Persistence equality:** expected saved state survives.
- **Reconstruction:** disposable geometry/cache state rebuilds correctly.
- **Continuation:** the same next actions produce equivalent outcomes after load.

Compare an uninterrupted branch with a saved/loaded branch after the same number of actual ticks. Normalize only documented unstable fields. Do not normalize unexpected missing state away.

The “save names no class of ours” rule is GSS-specific, with an explicit carried-job exception. FlowWorks legitimately owns serialized state; it needs a declared save schema, not namespace prohibition.

## 4. Trustworthy

### Make PASS require observation, completeness, and identity

A command acknowledgement is not its postcondition.

Examples:

- Spawn: resolve a new thing ID and verify type, count, position, and relevant comp.
- Tick step: independently read clock before/after.
- Setting change: read the setting back, then observe its effect.
- Job: verify start, progress, completion, and resulting state.
- Save: verify the new artifact, then its relevant contents.
- Screenshot: verify unique artifact, camera, frame/tick identity, and capture freshness.

The project has already paid for failures of every form above: paused `waitTicks`, stale screenshots, custom defs unsupported by the resolver, 64-item list truncation, and silent fallback to a vanilla mod list.

Use one strict result vocabulary:

| Status | Meaning for certification |
|---|---|
| PASS | Required observation succeeded with sufficient evidence. |
| FAIL | A valid observation contradicted the requirement. |
| UNMEASURED | The instrument or prerequisite could not settle it. |
| UNJUDGEABLE | Captured evidence cannot settle the experience claim. |
| SKIP | Declared inapplicable to this scope, with a machine-checkable reason. |
| NOT REACHED | Expected check never executed. |

Unknown statuses, missing required rows, duplicate IDs, and empty manifests must refuse certification. A required check cannot become covered merely by emitting SKIP.

An intentional compatibility-only SKIP is legitimate. A missing ordinary dependency is a coverage/setup failure.

### Bind the complete run identity

| Bound information | Required content |
|---|---|
| Subject | Stable package ID, feature/family membership, composed-mod mapping, resolved path. |
| Mod source | Content hash of shipped inputs, including dirty content; commit is context, not the sole identity. |
| Build | Each DLL SHA-256, source hash/`.srchash`, build inputs, and relevant dependency versions. |
| Deployment | Manifest of actual deployed files and hashes, checked against expected build. |
| Running game | Process/session ID, game version, loaded assembly identity, ordered active mod list, DLC fingerprint. |
| Harness | Hash/version of script, imported helpers, bridge server, companion DLL, schemas, observer, and judge. |
| Requirements | Manifest hash, stable check IDs, predicates, scope, and owner-bar validation hashes. |
| Fixture | Recipe/save hash, seed, map identity/count, settings, and prerequisite fingerprint. |
| Evidence | Actual tick ranges, timing, complete log interval, snapshots, images/text, and artifact hashes. |
| Completion | Executed/expected checks, interruptions, waivers, cleanup status, and collector receipt. |

Check identity at the start and end. Detect process/session replacement and deployment mutation during the run.

`.srchash` alone is insufficient: it must match source/build inputs and the loaded binary must match the deployed binary. XML/textures also need deployment identity.

Avoid making provenance depend on `python.exe` successfully running git on a UNC checkout; the supplied October 4 lesson shows that already produced unknown identity. Generate a portable build/deploy manifest before launching.

### Publish proof transactionally

The shared harness should:

1. Open a run record before connecting.
2. Persist each completed check and block.
3. Preserve partial evidence on exceptions.
4. Finalize an immutable result with an artifact digest.
5. Automatically call the authoritative record API.
6. Receive a receipt listing accepted checks and rejection reasons.

Notification, ledger annotation, or `emit_verify` failure must not destroy observations. **Failure to register must remain visible**, rather than being confused with mod failure.

Keep durable proof artifacts beyond `Transient/`’s 14-day shelf. They need not all be committed to git, but a long-lived status entry must resolve to retained evidence. Hand-editing a result must invalidate its recorded digest; the October 4 lesson shows why this cannot remain only a prose prohibition.

### Repair the metric without manufacturing a green

The report should list every census subject, including FlowWorks and GSS, with separate counts for:

- requirements declared;
- requirements mapped to checks;
- observed passes;
- current eligible proof;
- stale/unknown/not-reached evidence;
- owner experience bars: validated, draft, or absent.

A genuine **zero current proven** remains a valid answer. What must disappear is a silent zero caused by omitted subjects or failed joins.

Likewise, `owner bars 0 of 0` should explain whether there are no validated bars, discovery failed, or no bars were registered. The two supplied DRAFT walks help explain zero binding bars for those two mods; they do not explain every owner bar across the project.

Reconcile denominator changes and counts with stable check IDs. Taint reasons may overlap on the same checks; do not add them as independent populations.

### Make the final claim bounded

Use distinct conclusions:

- **Functional checkout passed on identified tier/build.**
- **Canonical-list checkout passed on identified build/list.**
- **Experience bars passed / pending / not defined.**
- **Requested extended concerns passed / not run.**

The owner permits agents to approve functional scripts. Preserve that autonomy. Do not make a DRAFT visual checklist erase valid mechanism evidence, or make a functional pass imply approved experience.

## 5. A standard checkout recipe

The reusable unit should be **a mod’s requirement manifest plus executable checks**, with the current `Suite`, custom proofs, and driver adapted to one result contract. GSS’s orchestration is a strong template; its monkeypatches and mod-specific assumptions should not become the general API.

### Minimal checkout template

| Phase | Required work and row kinds | Proposed budget |
|---|---|---:|
| 0. Declare | Intended behaviors, provenance, stable IDs, evidence type, dependencies, false-pass explanation, scope, tick budget. Coverage lint refuses omissions. | Offline |
| 1. Offline gate | Def/type/patch contracts, settings parity, pure C# tests, oracle comparisons, check mutations, fixture/layout validation. | Target ≤60 s for routine edits |
| 2. Identity/preflight | Verify deployed/running build, actual list, sentinel custom defs, startup log completeness, transport capabilities. | Target 10–30 s once warmed |
| 3. Fixture | Create/reset one verified map; provision exact pawns and disjoint sites; verify prerequisites. | Target 5–30 s; measure exceptions |
| 4. Behavior | Positive effect, important negative/refusal, toggle restoration, representative boundaries, real engine path. Batch compatible jobs. | Small mod: 1–3 live min |
| 5. Persistence | One save/load for mods owning relevant state; verify graph, reconstruction, and continuation. | Target 10–30 s when practical |
| 6. Experience | Automatically capture/judge applicable validated show/read bars; insufficient evidence is not PASS. | Separate capture/judge timing |
| 7. Session close | Complete log budget, final identity, expected-row reconciliation, cleanup, artifact finalization, automatic registration. | Target ≤10 s excluding judge |

These are targets to test, not bars to force checks under. Complex mods can legitimately retain a roughly **10-minute** core proof, as GSS does. Cold load time is recorded separately and amortized across a batch.

A first script may be shallow initially, as the process allows. Its result must say that coverage is partial until every declared ordinary behavior has evidence.

### Row kinds

Keep these distinct:

- **ENV:** deployment, list, runtime, transport.
- **SITE:** prerequisite/fixture validity.
- **BEHAVIOR:** actual intended effect.
- **NEGATIVE:** forbidden action/effect absent under an exercised trigger.
- **PROPERTY:** invariant/metamorphic relation.
- **PERSISTENCE:** saved state and resumed operation.
- **EXPERIENCE:** show/read bar.
- **LOG/PERF:** session health and measured budgets.

A consolidated row can contain multiple named assertions. Preserve their stable semantic IDs and individual evidence. Densification should reduce calls and presentation, without making the coverage denominator shrink merely because rows were merged.

### The shared harness must provide

- One lifecycle lock covering config/deploy/launch/map changes and driving.
- One connection with request IDs, late-reply quarantine, timeout semantics, and capability/version checks.
- Typed bridge adapters that distinguish unsupported, failed, truncated, absent, and successful responses.
- Fixture recipes for flat land, water, power, rooms, Deep maps, and exact pawn roles.
- Region allocation using effect reach; GSS already supplies the concrete R=5 and mast-range examples.
- Atomic/batched snapshots and bounded `wait_until`.
- Clock verification and per-step/per-observer timing.
- Complete incremental log collection.
- Save/graph capture, canonicalization, and continuation comparison.
- Unique, attributable image/text capture; capture without camera movement.
- Requirement discovery for families and composed/per-feature mods.
- Dependency-aware reuse of prior proof.
- Streaming evidence plus automatic authoritative recording.

Keep human galleries as optional presentation builders using the same recipes. They remain places to inspect and interact, with no agent-prefilled verdict.

## 6. Critique of the skill and docs

| Document/problem | Concrete edit |
|---|---|
| `debug_process.md` devotes substantial space to the lifted pause | Move the historical pause to an appendix. Keep one current sentence: every new mod ships with requirements and a checkout. |
| §2 requires `Suite`, while GSS uses custom orchestration | Specify the required manifest/result contract. Permit supported adapters for `Suite`, `proof_all`, and FlowWorks v2; prohibit divergent verdict semantics. |
| §2 asks for “one cheap state check per line” | Add: “The observation must establish the claimed behavior; def existence alone does not prove a job, render effect, or delivered text.” Require positive/negative and false-pass fields. |
| §2.3 coverage arrows are not followed by the supplied walks | Generate/lint stable requirement mappings. Broad prose can remain readable, but its constituent behaviors must map to semantic IDs. |
| §3 has “No clock” exploration and later a 20-minute consult trigger | State that exploration has no forced cutoff, while the no-new-evidence consult trigger still fires. Carry budgets for ordinary checkout execution separately. |
| §4 excludes performance/intermittent checks because no method exists | Replace the blanket boundary with evidence contracts: measured tick-time samples, seeded repeated runs, and explicit inconclusive outcomes. Retain human-only experience boundaries where ruled. |
| “A new assembly always goes alone” versus load batching | Clarify that the current rule applies to new-assembly attribution. Proposal: isolated startup smoke first, then batch subsequent proofs of the identified build. Do not silently reinterpret the ruling. |
| Bridge utilization is treated as throughput | Make it diagnostic. Lead with accepted current requirements per live minute, invalid-run minutes, and time to first actionable failure. |
| Validation spec’s open-text rules contradict §10.4 | Propagate the latest typed ruling—model YES may pass open text—through §§4, 5, 10.2, 11 and §10.4’s obsolete mitigation. Retain batch requirements and residual-risk disclosure. |
| Spec says “6 is the only bottleneck” and contains old inventories | Replace with generated dated status outputs. Move historical measurements to evidence notes. |
| Debugging skill mixes full/minimal timings | Use a small environment table: list fingerprint, launch path, measured readiness time, and date. Current context distinguishes roughly 22-second minimal from roughly 15-minute full load. |
| Full-list ready/quicktest warnings conflict across dates | Create a tested capability matrix by tool version and list fingerprint. State observed failures and their causes; avoid timeless “works”/“never works” claims from one session. |
| Skill §9 says one observation is usually enough; §4 requires batches | Scope the first to bounded visual inspection items. Functional certification follows the declared deterministic or probabilistic evidence contract. |
| Skill §8 makes repeated owner questions a default | Agents derive candidate observables and predictions from design/source. Ask only for missing intent; do not make every first checkout an interview. |
| Trimmed-tier GenStep/null-reference errors are called “NORMAL” | Classify them as known environment defects with bounded allowances. If they compromise setup or the tested surface, the run is invalid—not automatically clean. |
| Skill says clear the debug log before shooting | Distinguish closing/clearing the visible console from retaining the complete run log. Capture health must not discard evidence. |
| Human-review paths disagree | Standardize keeper sheets/assets under `review/`; scratch captures under `Transient/`. Update the walk and doc together. |
| CLAUDE contains large historical counts and hand-operated census warnings | Replace counts with commands. Turn recurring traps—64-item truncation, dict parsing, exact identity, stale logs—into shared typed APIs and regression fixtures. |
| GSS E4 and FlowWorks header/requirements lag shipped functionality | Reconcile pump/machinery state, dependencies, toggles, and default proof scope against the current inventory. |
| Whole-section owner hashing includes prose | Preserve the owner’s explicit ruling. Use state-independent prose inside hashed sections; keep changeable operational status outside. Do not revive declined bar-only hashing as an unapproved “fix.” |

The short current skill should contain the recipe, result semantics, lifecycle ownership, and links to relevant traps. Historical incidents belong in searchable references. Repetition has not prevented recurrence; executable guardrails are now the higher-value form of memory.

## 7. Top 10 actions

Ordered for overall improvement in trustworthy checkout throughput.

| # | What | Why / evidence | Estimated build cost | Cheapest test proving it worked |
|---:|---|---|---:|---|
| **1** | Reconcile GSS and FlowWorks with the required-check registry; add a report-accounting selftest | Tonight omits both and reports 0/1543. `observed-not-in-manifest` and “0 more if fresh” show multiple failed joins. | **1–2 days** | Trace one real result from each mod through every join. Both appear with explicit accepted/rejected reasons. A fresh valid synthetic run contributes; a stale one does not. |
| **2** | Enforce build/deploy/runtime identity and one lifecycle lock | Stale rebuilds and cross-session config/restart races repeatedly invalidate runs. | **2–4 days** | Load an old DLL against current source: refusal before site work. Attempt a concurrent config swap: rejection while the lease is held. |
| **3** | Make collectors durable and strictly validate completion | Ledger lost 64 minutes; `proof_all.py` writes late, accepts absent rows, and has inconsistent debug/status semantics. | **1–2 days** | Inject a final-log exception, an empty block, unknown status, accepted-red gate, and skipped preflight. Each preserves evidence and cannot certify a full checkout. |
| **4** | Build deterministic shared fixtures with exact prerequisite checks | Setup-invalid runs consumed 84.7 minutes; SL4 depends on random free-colonist count. | **2–4 days** | Rebuild/load a fixed fixture repeatedly. Two carry pawns and the same map fingerprint exist every time; deliberately missing one refuses setup immediately. |
| **5** | Add chunk/RPC profiling, batched snapshots, and adaptive observation | 17–20 calls per 600 ticks; discovery previously consumed 88% of a matrix run. | **1–3 days** | Replay one fixed wait before/after. Actual tick delta and fault detection stay equivalent; calls and observer wall time fall. A cached settings lookup stays fast on a large list. |
| **6** | Replace Antiquities’ fixed wait and FlowWorks’ dense polling with bounded waits | 95k fixed ticks and 799 excavation polls dominate useful execution. | **0.5–2 days** | Fast completion returns early; slow legitimate completion stays valid; a stuck job fails at its budget with last state and real tick delta. |
| **7** | Reconcile shipped behavior with default checkout scope, starting with FlowWorks | Ordinary pump/bottle/prison/door mechanics sit behind on-request extensions; settings parity and stale pump prose expose drift. | **1–2 days audit; 2–5 days initial wiring** | Disable one shipped mechanic. The default checkout fails its semantic requirement. Removal/compatibility remain separately requested. |
| **8** | Extract GSS session orchestration and add dependency-aware proof reuse | GSS demonstrated 15→1 invocations, seven→one save, approximately 30→10 minutes. Folder-based staleness also reruns unrelated work. | **3–5 days** | Convert a second multi-script mod without copying orchestration. Then edit only its review text: behavior proof remains reusable; edit a consumed helper: affected proof becomes stale. |
| **9** | Add a mutation/property/persistence pilot for GSS and FlowWorks | Known geometry/load regressions provide red cases; reduced matrices depend on untested adapter-independence assumptions. | **3–5 days initially** | Each of a small named set of real faults is killed by the intended check: no-op job, cross-net edge, stale visible mesh, lost carry state, and liquid accounting error. Preserve a shrunk seeded failure. |
| **10** | Publish a short current checkout skill; automate the highest-frequency doc traps | Contradictory read authority, launch guidance, paths, and counts keep returning through handoffs. | **1–2 days** | A fresh agent completes one small mod checkout with the short contract; an offline linter rejects contradictory state/path declarations and missing coverage mappings. |

The first experiment should be **an offline trace of the two completed checkouts into the lead metric**. It will distinguish missing discovery, missing registration, incompatible result schemas, and genuinely ineligible evidence before Northstar spends another live session trying to increase a number it cannot yet account for.