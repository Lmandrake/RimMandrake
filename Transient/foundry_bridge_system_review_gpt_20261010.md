## 1. Architecture critique

**I would not spend the next full-list cold load on the current orchestration unchanged.** The immediate blockers are the intended mod list, deployed artifact identity, known recorder safety defects, false readiness, unprotected saves, and mutations whose outcomes become unknown after a timeout.

The main architectural problem is that **authorization, actual execution, and evidence are not joined**. Each has several competing records, and none is authoritative at the moment a mutation executes.

Evidence labels used below:

- **VERIFIED-from-knowledge [V]:** an established runtime/protocol property, or a logical consequence of the supplied design. This does **not** mean I inspected your implementation.
- **PLAUSIBLE [P]:** a credible failure mechanism requiring a reproduction or source inspection.
- **UNKNOWN [U]:** installed-server behavior, undocumented implementation, or unavailable evidence.
- **Reported:** a measurement or incident stated in the inlined documents; accepted as supplied evidence, not independently remeasured.

All new interfaces and manifest fields below are **proposed**, not existing RBS APIs or flags.

### 1.1 The important architectural failures

| Boundary | Critique | Redesign |
|---|---|---|
| Seat → driver process | A seat is an attribution label, not an exclusive execution identity. Parent, subagent, and abandoned child can all be “FOUNDRY.” [V] | Identify each driver by host boot, PID, process creation time, and random session ID. Explicitly transfer exclusive authority between processes. |
| Ledger → execution | Taking the lease does not prevent another client from submitting calls, changing ModsConfig, deploying, or restarting. [V] | One Windows authority controls RPC submission, configuration transactions, deployment, and lifecycle operations. |
| Lease expiry → queued work | Revoking a lease does not revoke a mutation already queued inside RBS. [V] | Check a monotonically increasing authority generation **at execution**, including between chunks of long operations. |
| Client → server | Client conventions cannot protect calls made through another client, Lua, nested tool calls, or upstream built-ins. [V] | Enforce capabilities at the common server dispatch boundary. A companion-only check protects only companion tools. |
| Socket → game readiness | Listener, token, authenticated session, working dispatcher, loaded map, and valid fixture are different facts. [V] | Publish separate readiness stages. Give `UP` one documented meaning and require stronger readiness for mutations. |
| Filesystem → deployed process | Source stamps, deployed hashes, and runtime-loaded assemblies are different identities. [V] | Join build input, deployed bytes, loaded module identity, running mod order, and script bundle in one run manifest. |
| Timeout → outcome | A client timeout establishes loss of timely observation. It does not establish cancellation or failure. [V] | Record an indeterminate mutation; reconcile through an execution receipt or postcondition before issuing dependent work. |
| Game → observability | The game can fail before the companion exists. The companion can itself cause failure. [V] | Keep an independent Windows startup/process/log witness. Diagnostic availability must survive companion failure. |
| Test profile → campaign | Save names and colony names are weak safety boundaries. A misidentified campaign can satisfy them. [V] | Campaign defaults to read-only; tests require an explicitly authorized fixture and expiring capabilities. Stronger option: campaign runs without RBS. |
| Build → deployment | Per-file atomic replacement does not make a multi-DLL/XML release atomic. [V] | Stage a complete release, validate its manifest, activate while DOWN, and retain a rollback release. |

**Central recommendation:** introduce a small Windows supervisor/broker. Its first version need not understand every tool. It must own:

1. Exclusive driver identity and handoff.
2. The single game process identity.
3. Immutable run bundles.
4. Launch/readiness checks.
5. Configuration/deployment transactions.
6. Mutation admission, receipts, and outcome uncertainty.

Keep the git ledger as the **audit trail and human-facing projection**, not the distributed locking primitive. A shared JSON file on drvfs plus later-event-wins reconciliation cannot supply mutual exclusion. [V]

The broker becomes a deliberate single point of control, but its failure mode should be useful: **deny new mutations; preserve independent diagnostics; allow a recorded owner override**. That is better than several distributed components silently allowing contradictory actions.

### 1.2 Threading and runtime assumptions

**Unity access must be main-thread confined.** Unity explicitly documents that its APIs are not thread-safe and that release builds may omit checks that would catch misuse. “It corrupts rather than throwing” is too absolute; crashes, exceptions, stale state, or apparent success are all possible. [Unity documentation](https://docs.unity3d.com/2022.3/Documentation/Manual/overview-of-dot-net-in-unity.html)

The confinement rule must cover more than obvious setters:

- Reads of mutable game collections.
- Enumeration, serialization, and deferred LINQ evaluation.
- Object resolution and property getters.
- Constructors, static initialization, and startup census.
- Continuations after `await`.
- Background heartbeat snapshots.
- Receipt construction that traverses game objects.

**Copy a bounded immutable snapshot on the main thread; serialize and write that snapshot elsewhere.** Returning a game object from `InvokeAsync` and serializing it later defeats the boundary.

The server concurrency model remains **UNKNOWN**. The two-driver wedge does not establish whether RBS uses a global queue, per-session serialization, a dispatcher bottleneck, or a deadlock. Until measured, permit **one game-bound operation at a time**, including read-only observers. “Read-only” does not mean “cannot contend.”

### 1.3 Versioning and modularity

Pin a tested **bridge dependency closure**, not merely the SDK:

- RBS assemblies and companion SDK.
- Lib.GAB/Gabp.Runtime.
- Harmony.
- Relevant game assemblies.
- Companion and its hard dependencies.

Automatically rebuilding against a newly downloaded SDK is **not compatibility testing**. It can compile successfully and still change semantics, startup, attention behavior, or dispatch.

Separate the companion into:

- A small dependency-light diagnostic/core bundle.
- Passive instrumentation.
- Test mutations.
- Mod-specific adapters.

Do not make diagnostics depend on five optional mod DLLs. Avoid a module initializer that installs unrelated features as one indivisible startup operation.

### 1.4 Windows/WSL and deployment

Keep Windows authoritative for Windows process identity, file identity, clock measurements, and deployment hashes. WSL submits intent and receives structured results.

Use an immutable Windows run directory containing the exact script, client, schemas, and manifest. Run it using an absolute interpreter path. The five-minute mirror should be a convenience export, **not executable release infrastructure**.

WSL loopback failure is a property of your reported NAT setup, not a universal WSL limitation. Microsoft documents Windows↔WSL localhost access in mirrored mode. Changing networking is optional; it does not solve authority, provenance, or retries. [Microsoft WSL networking](https://learn.microsoft.com/windows/wsl/networking)

---

## 2. Ranked and extended problem list

### 2.1 Merge the existing predictions into failure families

`A-Pn` refers to architecture predictions; `D-n` to debugging predictions.

| Priority | Consolidated family | Existing predictions merged | Why it ranks here |
|---:|---|---|---|
| 1 | Campaign/keeper persistence damage | A-P20, P21, P26, P41; D-24, 25 | Irreplaceable work can be changed while the tool reports success. |
| 2 | False identity and false readiness | A-P9–13, P22, P33; D-2, 9, 21, 34 | Invalidates an entire run or sends mutations to the wrong process/game. |
| 3 | Multiple drivers and surviving work | A-P3, P4, P28–31; D-12, 23, 31 | Corrupts attribution and can leave simulation or queued mutations running. |
| 4 | Uncertain mutation outcome and duplicate execution | A-P16; silent-success family | A timeout encourages precisely the retry that makes the state worse. |
| 5 | Content/load killers and effective-def drift | A-P13–15; D-7, 13, 18 | Repeated historical cold-load loss; the durasteel family belongs here. |
| 6 | Recorder/Harmony startup and hot-path hazards | A-P19, P41; D-3, 4, 6, 33 | Instrumentation can break the system it is intended to explain. |
| 7 | Deploy/dependency/version skew | A-P1, P5–8, P32, P42; D-9, 14, 32, 34 | Both loud failure and convincing stale passes. |
| 8 | Spoiled fixtures and hidden interference | D-8, 10, 17, 24, 29 | High reported UNMEASURED rate; CLEAN can overstate coverage. |
| 9 | Broken evidence production and acceptance | A-P25, P35, P36; D-5, 16, 19, 28 | Defects become green because the check or record is blind. |
| 10 | Misdiagnosed hangs and conflicting deadlines | A-P12, P15, P17, P23; D-15, 26, 27 | Healthy loads and menus get killed; real failures wait too long. |
| 11 | Host resource/lifecycle failures | A-P24, P26, P27, P32, P34; D-11, 22, 30 | Windows, WSL, disk, memory, sleep, and clocks disrupt otherwise correct runs. |
| 12 | Attention/protocol policy drift | A-P2, P35; D-14 | Important, but direct-mode gating is unresolved rather than established. |
| 13 | Unsafe legacy escape hatches | A-P18, P37–40, P43 | Cheap to remove; client-only bans are insufficient. |
| 14 | Evidence retention and archival races | A-P25, P44; D-28, 32 | Removes the evidence needed to explain the other failures. |

The debugging document’s numerical probabilities are **planning guesses**, not measured probabilities. Its history is also selected incident evidence, not a denominator of all runs. Use it to prioritize recurring mechanisms; do not infer population failure rates.

### 2.2 Problems missing or materially underspecified

The following are additional mechanisms, not just renamed existing rows.

| ID / label | Trigger | Symptom | Who it fools | Cheap guard |
|---|---|---|---|---|
| N01 [V] **Partial-frame timeout** | Timeout after reading part of a header/body; parser discards partial state | Next response starts mid-frame; desync or incorrect length | Client treating `abandoned` IDs as a complete fix | Preserve parser state, or close the connection and mark the operation indeterminate. Never restart parsing mid-frame. |
| N02 [V] **Byte/character length confusion** | Unicode arguments, names, or response text | Truncated JSON or framing desync | ASCII-only selftests | Frame UTF-8 **bytes**; test multibyte text at every split position. |
| N03 [P] **Unbounded framing input** | Huge/negative/conflicting lengths, unterminated headers, malformed JSON | Allocation spike, blocking, crash | “Loopback is trusted” | Header/body bounds, strict lengths, EOF handling, explicit protocol failure. |
| N04 [V] **Timeout extended forever by traffic** | Each event/read resets a socket timeout | Call exceeds its intended deadline indefinitely | Runner heartbeat that remains alive | An absolute monotonic operation deadline independent of individual reads. |
| N05 [V] **Operation ID unavailable when needed** | Response carrying the server ID is lost | Cannot identify the mutation to poll | Proposed “just poll OperationId” recovery | Client-generated command ID accepted before execution; maintain correlation independently of the final response. |
| N06 [V] **Client death leaves server work alive** | `os._exit`, socket close, parent termination, WSL loss | Spawn/tick/save continues after runner is DEAD | Supervisor treating process exit as cancellation | Track server work separately; cancellation acknowledgment and per-chunk fences. |
| N07 [V] **Lease takeover does not fence old work** | Old operation waits in dispatcher; new holder acquires lease | Old mutation executes during the new holder’s run | Both correctly leased drivers | Authority generation checked immediately before mutation. |
| N08 [V] **Read/write ordering after timeout** | Timed-out mutation followed by a getter | Getter returns pre-mutation state; late mutation occurs afterward | Read-back discipline | Fence dependent calls until outcome is terminal or explicitly unresolved. |
| N09 [P] **Same client object used concurrently** | Shared `RimBridge` object accessed by threads/tasks | IDs, receive buffer, and events race | “One request in flight” assumption | Enforce single caller with a lock or reject concurrent use. |
| N10 [V] **Unbounded event/abandoned-ID storage** | Long session, many timeouts or subscriptions | Memory growth and GC pressure | TPS investigation blaming gameplay | Bounded event queue, overflow counters, bounded retired-ID lifetime, connection reset policy. |
| N11 [V] **Pagination hides incomplete evidence** | Caller reads only first page or joins pages while game changes | Missing defs/pawns interpreted as absent | Inventory and detector checks | Explicit completion token/count; snapshot identity across pages; incomplete means unavailable. |
| N12 [V] **Set equality hides load-order drift** | Same package IDs, different order | Different XML winner/Harmony behavior | GREEN-FULL set comparison | Compare ordered identities and content, not only set/count. |
| N13 [P] **Duplicate package/assembly identity** | Local and Workshop copies, duplicate DLL names, stale folders | Wrong assembly/def provider wins | Inventory reporting the intended package ID | Resolve selected roots and assembly identities; report duplicates and actual loaded locations. |
| N14 [V] **Patch succeeds but semantic target is absent** | Conditional/FindMod returns success, inherited list, full-def replacement later | Clean log; intended change absent | `validate_patch` and launch gate | Replay effective XML in order; record match counts and assert resulting semantic fields. |
| N15 [P] **Null-def cost entry after patches** | Renamed/missing material, retired `MayRequire`, bad inheritance, later replacement | Load-time NRE or generator failure; possible ModsConfig recovery | Authors checking raw XML only | Effective-def cross-reference lint with writer provenance; §3. |
| N16 [P] **Shared build staging collision** | Two clones build into the same `_rmbuild` location | Mixed inputs, overwritten outputs, wrong DLL copied back | Source stamp tied to only one project | Unique build directory per build ID; hash input/output manifest; serialize deployment. |
| N17 [V] **Multi-file release tearing** | Individual DLL/XML copies succeed until interruption | New DLL plus old sibling/schema/defs | “Atomic DLL deploy” | Release transaction with complete staged manifest and rollback. |
| N18 [V] **Snapshot changes after pre-flight** | Steam, mirror timer, deploy, or settings writer runs between checks and launch | Pre-flight passes an environment that no longer exists | GO verdict | Recheck the manifest immediately before launch and after startup; invalidate on drift. |
| N19 [P] **Type initializer poisoning** | Startup initialization throws | Persistent type-initialization failure for the process; unrelated tools unavailable | Retry logic expecting recovery | Tiny nonthrowing bootstrap; independent feature initialization/status; injected-failure test. |
| N20 [V] **Await/thread-context escape** | Game state accessed after an await outside dispatcher scope | Races, collection-modified errors, stale references | Code review seeing an earlier `InvokeAsync` | Resolve and snapshot inside each main-thread scope; assert thread identity at access boundaries. |
| N21 [V] **Patching the base virtual method misses overrides** | Incident worker overrides `TryExecute` without calling base | Journal has no incident row for a real arrival | “Any route through TryExecute” claim | Enumerate actual implementation targets; test an overriding worker; declare coverage gaps. |
| N22 [V] **Thread-static provenance lost or leaked** | Await/thread switch, queued parms reuse, nested exception | Wrong or missing origin chain | Origin explanations | Explicit command/context IDs; token-checked stack cleanup; epoch-scoped queued associations. |
| N23 [P] **Cross-thread snapshot/lock deadlock** | Main hook waits on writer lock; writer calls game/Unity or waits for main | Main thread wedges; observer looks healthy | Instrumentation health checks | No game API on writers; no main-thread waits for writer; immutable snapshots and bounded handoff. |
| N24 [V] **Count-bounded rings retain large graphs** | Ring stores Pawn/Map/IncidentParms/Exception objects | Old games remain reachable across reloads | “Bounded ring” memory claim | Store scalar IDs/bounded text; test retained memory after repeated load/unload. |
| N25 [V] **Native job lifetime guarded by ticks** | Array freed after “60 ticks” while worker still uses it | Native crash under slower or differently scheduled jobs | Fix accepted because crash stopped once | Dependency completion/lifetime ownership; elapsed ticks cannot prove a job has finished. |
| N26 [P] **Late patching/inlining changes coverage** | Hook installed after target was JITted/inlined; overload changed | Installation reports success, counters remain incomplete | Patch inventory | Exact signature/implementation census plus execution canaries on the installed runtime. |
| N27 [V] **Whole-Game replacement without tick reversal** | Load another save with equal/higher tick count | Clock ledger and provenance join two games | Negative-delta epoch detector | Epoch from actual Game identity/load lifecycle, never tick reversal alone. |
| N28 [V] **Object IDs reused across games/maps** | Cached pawn/map target survives reload | Mutation reaches wrong object or invalid reference | Valid-looking IDs | Every target carries process session + Game epoch + map identity. |
| N29 [V] **Size-only save protection** | Wrong keeper overwritten with same-length contents | Wrapper reports no keeper size change | Save safety test | Hash protected files; inspect all changed files; protect writes before execution. |
| N30 [P] **Autosave defeats “we never save”** | Campaign unpaused during a test; mod/vanilla autosave fires | Persistent consequences despite avoiding `save_game` | Owner safety assumption | Test-only save environment and save-write policy covering automatic/mod-driven saves. |
| N31 [V] **Save success is not reloadability** | Well-formed XML contains invalid refs/serialization state | Save exists, later load fails or loses entities | NEW-file proof | Parse plus disposable reload and state invariants; keep original fixture immutable. |
| N32 [P] **Path escape or unintended destination** | Output/save path contains traversal, UNC path, reserved name, or reparse-point escape | Writes outside run directory or blocks on a network share | “Export-only” tool classification | Canonical path confinement, allowed roots, bounded file sizes; refuse ambiguous destinations. |
| N33 [V] **Loopback token authorizes arbitrary code effects** | Same-user process reads current log token and calls static invocation/scripting | Files, processes, saves, or game state changed | “Localhost means safe” | Remove arbitrary execution; separate RPC authentication from mutation capabilities; restrict token-bearing files. |
| N34 [P] **Credential exposure becomes live exposure** | Token or raw log copied to telemetry/private Git while game still runs | Another local client can reuse credential | Claim that archived tokens are always obsolete | Redact at collection/export; never store the token in provenance. |
| N35 [P] **Observer lock or scheduler failure** | Stale lock, hung collector, overlapping scheduled starts, wrong account/session/interpreter | Task says Ready; collection is absent or stale | Scheduler query as installation proof | Identity-aware singleton lock; completion freshness and source statuses; injected stale-lock test. |
| N36 [V] **Two observers duplicate findings or race JSONL writes** | Watchdog and scheduled observer append same incident concurrently | Duplicates, malformed/interleaved rows, conflicting lifecycle | Reconstruction reader | One finding writer or coordinated append; stable incident ID and reader deduplication. |
| N37 [P] **Heartbeat-age retention deletes live evidence** | Sleep, blocked disk, suspended process, clock jump | Active session appears stale and is pruned | “Heartbeat is a lease” retention | Check process identity and sleep state; quarantine uncertain bundles instead of deleting. |
| N38 [P] **Archive hash does not identify copied bytes** | Player.log changes during hash/copy | Archive filename hash differs from actual archive content | Forensic joins | Copy to a new artifact, then hash that artifact; preserve file identity and capture interval. |
| N39 [P] **Host presentation/power failure** | GPU reset, driver update, display/RDP change, thermal throttling, power saver | Rendering failure or slower frame cadence with responsive simulation | TPS blame on a mod | Record host/power/display/driver changes; use process/thread and simulation evidence separately. |
| N40 [P] **Memory/commit/pagefile exhaustion** | WSL + game + build + dump compete; pagefile capped | Huge stalls or allocation failure despite available-looking RAM | Heap-only metrics | Track system commit headroom, private bytes, native memory context, and competing processes. |
| N41 [V] **Same artifact, different settings/fixture** | Mod settings, difficulty, speed boost, save, seed state differ | Apparently comparable tests disagree | Commit/mod digest comparison | Fingerprint settings and fixture; declare uncontrolled variables. |
| N42 [V] **Visitor removal itself perturbs the test** | Removing pawn also affects lord, inventory, reservations, factions, RNG | Later criterion changes after visitor “clean-up” | CLEAN-with-note interpretation | Record intervention and affected dependencies; criterion-specific eligibility. |
| N43 [V] **Cleanliness sample races mutation** | Ten-read scene report spans ticks or a long operation | Internally inconsistent scene | “Not atomic” disclaimer overlooked | Pause/fence test game; include epoch/tick bounds; invalidate on identity change or excessive interval. |
| N44 [V] **Acceptance report hides missing checks** | Empty result, DRAFT counted passing, broad waiver, vacuous mock | Global GREEN while required evidence is absent | Owner/reviewer | Required check IDs and expected counts; missing/waived/unknown cannot satisfy acceptance. |

**Protocol basis:** TCP returns available bytes, not application messages; receive fragmentation is normal. Python also documents that a timeout from `sendall` does not identify how much was transmitted. These are transport facts, not rare edge conditions. [Winsock `recv`](https://learn.microsoft.com/windows/win32/api/winsock/nf-winsock-recv), [Python sockets](https://docs.python.org/3/library/socket.html)

### 2.3 Corrections to proposed fixes

Several existing fixes are too weak:

- **“Touch the shared lock on every call”** does not make acquisition atomic, stop same-seat concurrency, or fence old work.
- **“Skip watchdog probes during a long call”** needs a bounded reservation and independent liveness. A stuck runner must not suppress probes forever.
- **“Count matches FULL.LATEST”** misses wrong IDs, order, content, and a stale FULL.LATEST.
- **“Rebuild automatically after SDK change”** removes one binary mismatch while silently adopting untested behavior.
- **“Call `get_operation` after timeout”** is insufficient if the operation ID arrived only in the lost response.
- **“Campaign name deny-list”** fails on unknown, renamed, unsaved, or newly created games.
- **“Regenerate schemas from `[Tool]` regex”** can find names, but does not reliably reproduce compiled parameter types, defaults, conditional compilation, or aliases.
- **“Allow-list every window as modal”** confuses harmless overlays with blocking windows.
- **“Add broad Defender exclusions”** is not a cheap default fix. First measure interference and record exclusions; avoid excluding script/build trees indiscriminately.
- **“Install LocalDumps”** is not proof of dump collection. Windows documents limitations for applications with custom crash reporting. Verify actual capture. [WER documentation](https://learn.microsoft.com/en-us/windows/win32/wer/collecting-user-mode-dumps)

---

## 3. Exact pre-flight

Use **one implementation of checks**, callable by every existing runner, plus a standalone launcher entry point. Do not create a third independently maintained definition of readiness.

The stated “under one minute” target is achievable for **cached incremental checks**. It is not honest for a first full content hash, complete patch replay, builds, and all selftests across 551 mods.

### 3.1 Required inputs

A launch request must specify:

- Purpose: campaign, diagnostic menu, test fixture, or owner review.
- Intended **ordered** mod manifest.
- Immutable release/build manifest.
- Script/suite bundle and required capabilities.
- Fixture/save identity.
- Recorder configuration.
- Expected milestones and hypothesis-separating failure strings.
- Deadline policy.
- Driver identity and authority generation.

**Do not infer the intended FULL list from the currently deployed list.** The reported 67-versus-551 mismatch and 14 extra IDs need reconciliation against an explicit shipping manifest. “Every `mandrake.*` mod” is also insufficient: some are optional, retired, or composed members.

### 3.2 Ordered offline checks

Costs are approximate engineering estimates; hash/replay costs depend on disk and cache.

| Order | Check and exact pass condition | Cost | False-positive / uncertainty handling |
|---:|---|---:|---|
| O01 | Validate launch request schema; purpose, intended list, fixture, and decision strings are nonempty and internally consistent. | <1 s | Intent cannot be inferred. Missing intent is a real refusal. |
| O02 | Enumerate Windows game and driver identities. Refuse multiple RimWorld processes. For a cold launch, prove the previous process exited. For an existing session, take the separate attach path. | 1–3 s | Process-probe failure is UNKNOWN, not DOWN. Never use log age as the fallback proof of absence. |
| O03 | Acquire exclusive lifecycle/configuration authority atomically. Record boot ID, process creation time, driver session, purpose, and generation. | <1 s | Authority-store failure denies automation mutations; explicit recorded owner recovery remains available. |
| O04 | Check absolute Windows interpreter/build-tool paths, expected versions, accessible directories, and correct Windows user/SaveData location. | 1–3 s | An unavailable optional build tool need not block a launch of an already verified release. |
| O05 | Check C:/D: free space, system commit headroom, writable recorder directories, and expected observer health. Inspect declared competing workloads and update/reboot state. | 1–3 s | Use workload-based headroom; a fixed “X GB” cannot cover saves plus full dumps. |
| O06 | Establish Windows/WSL clock offset and uncertainty; record host boot and sleep/resume boundary. | <1 s | Large skew blocks precise cross-host joins, not automatically a harmless menu launch. |
| O07 | Parse actual ModsConfig through Windows. Exact ordered IDs equal intent; all IDs resolve to selected deployed roots; DLC/camera requirements satisfied; duplicates and composed-member IDs absent. | 1–5 s | Case/canonicalization follows verified game behavior; do not invent normalization rules. |
| O08 | Resolve dependency closure and order constraints from the deployed metadata. Verify package IDs, referenced sibling DLLs, and selected local/Workshop copies. | 1–5 s cached | Missing optional dependencies are allowed only when the compiled bundle does not require them. |
| O09 | Compare release closure: game/RBS/Harmony/SDK hashes, mod DLLs, XML, About metadata, textures, settings, and companion. No unexplained deploy delta. | 2–10 s cached; initial scan longer | `.srchash` supplements byte hashes; it does not replace them. |
| O10 | Check Steam/Workshop drift since approved release. Any changed dependency loses compatibility/comparability approval. Recheck immediately before launch. | 1–5 s cached | “Version unchanged” does not prove content unchanged. |
| O11 | Run effective-def/data-patch lint, including cost entries and known load killers. Required semantic postconditions pass. | 5–60+ s | Unsupported custom patch operations report UNKNOWN for affected outputs; never silently skip. |
| O12 | Run compiled-metadata tool census: names/aliases unique; expected build profile; retired/forbidden exports absent; parameter schemas complete; assembly references resolvable. | 1–10 s | A shrink from GM to campaign is intentional and must be represented by the expected profile. |
| O13 | Lint the exact script bundle against that schema. Reject prohibited discovery, direct unsafe saves, unbounded outputs, and mutations without outcome handling/target identity. | 1–5 s | Dynamic calls require declared capabilities and runtime validation. |
| O14 | Run required targeted selftests and mock harness checks. Verify expected test IDs/counts, nonvacuity, fault paths, and production-file linkage. | Seconds–minutes | Mocks prove harness mechanics, not Mono/Harmony compatibility. |
| O15 | Apply workload compatibility gate: RealFoW/bland-map recipe, recorder safety status, fixture mod match, review-map rules. | <1 s | Known unsafe combination is blocked; removing RealFoW means the run is a different manifest. |
| O16 | Preserve immutable configuration backup, fixture/keeper hashes and recoverable copies, previous logs, and outstanding-run status. | Seconds; save copies longer | A backup must be readable and outside the imminent overwrite path. |
| O17 | Freeze run bundle and manifest. Rehash activated release and ModsConfig; verify observer/task settings. | 1–5 s | Any change after O09 invalidates the earlier checks. |
| O18 | Produce signed-off-by-tool GO record listing every required check and evidence reference. Start observer before Steam launch. | <1 s | No blanket “allow unmeasured.” Waived checks remain unmet acceptance requirements. |

A write probe tests only the designated recorder/output directory. Do not probe protected saves by overwriting them.

**Illustrative orchestration pseudocode—proposed functions, not commands available today:**

```text
request = validate_explicit_intent()
identities = measure_windows_identities()

if request.is_cold_launch:
    require_zero_game_processes(identities)
else:
    return attach_preflight(request, identities)

authority = acquire_exclusive_authority(request.driver)

for check in O04..O15:
    result = check(request)
    record(result)
    stop_if_required_not_pass(result)

preserve_config_logs_and_protected_saves()
bundle = freeze_exact_inputs()
require_manifest_unchanged(bundle)

start_declared_external_observer()
launch_through_steam_once()
follow_exact_new_game_process()
run_live_preflight(bundle, authority)
```

### 3.3 The `costList` / null-def lint class

**Do not just search for the word `Durasteel`.** Test the invariant that the engine will later consume.

1. **Resolve the actual selected mod roots and load order.**
2. Parse XML with source paths and line provenance.
3. Apply supported patch operations in order, recording:
   - Match count.
   - Target identities.
   - Values before/after.
   - Operation/mod that last wrote each value.
4. Resolve inheritance using the verified RimWorld semantics, including list replacement/merge rules. Report unsupported behavior.
5. Build a typed definition symbol table.
6. Validate every effective cost entry:
   - Material key resolves to a surviving `ThingDef`.
   - Entry is not empty or null-producing.
   - Count parses and satisfies the applicable engine/domain constraint.
   - Required material survives conditional loading.
   - Parent/child patching has not left a stale inherited material.
7. Extend the same typed-reference checks to recipe ingredients, race references, comps, worker classes, extensions, factions, and other known load-killer fields.
8. Run specific rules for reported incidents:
   - Inert top-level `<Operation MayRequire>`.
   - Retired/composed package IDs in requirements.
   - Invalid enum values.
   - Missing required types.
   - Drug/comp inconsistency.
   - PawnKind/race inconsistency.
   - Faction naming requirements.
   - Concrete reflection leaves such as Alert subclasses.
9. Emit a useful finding, for example:

```text
FAIL effective ThingDef ExampleBuilding.costList:
  material ExampleDurasteel does not resolve
  inherited from ParentBuilding
  last written by ModX / Patches/Costs.xml / operation 4
  requirement names retired package ID ExampleOldPackage
  downstream consumer may dereference a null ThingDef
```

That is illustrative output, not a diagnosis of the actual durasteel crash. Its exact source and stack are **UNKNOWN** from the supplied material.

**Acceptance fixtures must include** a raw-valid definition made invalid by a later patch, an inherited bad entry, a renamed material, an absent conditional dependency, and a later full-def replacement. A raw-XML-only checker must fail these acceptance tests.

An offline emulator cannot completely reproduce arbitrary mod C# definition mutation. Add a **read-only resolved-def audit after startup**, before map creation. Any entry unresolved at that point blocks the map/load workload. This is the final protection against dynamic generators and runtime removers.

### 3.4 First five live minutes

Interpret this as **five minutes after authenticated transport becomes available**, not five minutes after Steam launch. Your companion cannot inspect the first fifteen minutes before it exists.

| Order/time | Check | Required evidence |
|---|---|---|
| L01 / launch onward | Track exactly one new RimWorld process, executable path, creation time, and process handle. | A Steam command exiting successfully is not the launch receipt. |
| L02 / launch onward | Follow the current log by file identity/generation. Token and listener belong to that process. | Require current-run evidence; truncation alone is neither necessary nor sufficient. |
| L03 / 0–30 s after transport | Authenticate; collect live protocol/server capabilities and live tool schemas. | No silent fallback that conceals an incompatible handshake. |
| L04 / 0–60 s | Verify loaded companion/dependency identities against manifest; inspect registration/install errors. | Runtime module identity plus deployment manifest, not an init-line grep alone. |
| L05 / 0–60 s | Compare actual running **ordered** mods and selected content with intent. | ModsConfig is checked again separately as the next-load configuration. |
| L06 / continuously | Parse current-run load failures, resets, ConfigErrors, missing types/refs, first exceptions, and logging suppression. | New required failures block readiness; previously allowed errors need exact, justified signatures. |
| L07 / 30–90 s | Verify main-thread dispatcher progress repeatedly and Run in background state. | Several successful bounded round trips and fresh progress samples while the game remains unfocused. No focus healing. |
| L08 / 30–90 s | Verify recorder startup, switches, install health, writer health, and observer configuration. | Off, unsupported, and failed are distinct. No-client autostart acceptance is tested separately. |
| L09 / before map operation | Run resolved-def invariant audit, including cost entries. | Full expected scope/count; capped/incomplete enumeration cannot pass. |
| L10 / fixture entry | Load/create only the authorized test fixture. Establish new Game epoch, map identity, home/colonist state, required settings, and save identity. | Menu readiness is not map readiness. Campaign cannot enter this branch. |
| L11 / next 30–60 s | Verify pause, named colony where required, windows, quiet profile, baseline population, and no outstanding old mutations. | Closing windows and removing visitors are recorded interventions, not read-only checks. |
| L12 / before suite | Write baseline scene/evidence; confirm suite capabilities, fresh heartbeat, and unchanged manifest. | Unknown observations remain unknown. |
| L13 / by five-minute boundary | Issue scoped MUTATION_READY receipt, or explicit refusal/pending state. | No required check missing; no open uncertain mutation; no known startup defect hidden by settling. |

Use the reported 40-second settle as a **minimum observation opportunity**, not proof. Repeat the zombie/map checks at the end of settling and before each suite.

A long fixture load may exceed five minutes. Report **pending fixture load**, not “bridge failed” and not GO.

---

## 4. Control-plane hardening

### 4.1 Lease, process identity, and fencing protocol

Use three distinct credentials/identities:

1. **RBS authentication token:** authenticates a connection.
2. **Driver authority token:** authorizes one driver process.
3. **Mutation capability:** authorizes specific effects on a specific test game/map for a bounded interval.

They must not be interchangeable.

A proposed authority record contains:

```text
host_boot_id
driver_session_id
driver_pid + driver_creation_time
seat
authority_generation
game_pid + game_creation_time
purpose
capabilities
renewal_deadline_monotonic
```

Recommended behavior:

- Acquire under a Windows-native synchronization mechanism through the single authority process.
- Renew from driver supervision, not unrelated ledger events.
- Distinguish **driver alive**, **driver healthy**, and **operation progressing**.
- As an initial policy, renew every 10 seconds with a roughly 60-second expiry; tune after sleep and failure tests.
- Releasing authority requires the exact holder identity/token. A nonholder cannot release another holder except through explicit owner override.
- Handoff stops new work, reconciles outstanding commands, increments generation, then transfers authority.
- Owner override increments generation immediately and records reason.
- Expiry blocks new mutations and invalidates pending ones.
- An already executing synchronous engine call may be noninterruptible. Report that fact; do not claim revocation stopped it.
- Long companion operations check generation/epoch/cancellation between bounded chunks.

**A client-side gate is an interim guard.** Full enforcement requires the common RBS dispatch seam, verified against the installed version. A special companion “lease check” tool followed by an ordinary call leaves a check/use race and does not guard upstream tools.

Preserve the owner’s availability intent by making recovery explicit and fast. “Err toward allowing” can govern **taking control after verified revocation**, without permitting two active writers.

### 4.2 Version handshake and “what is actually loaded”

One provenance record must join:

| Identity | Evidence |
|---|---|
| Game process | PID, creation time, executable path, host boot |
| Runtime | RimWorld revision, Unity/Mono information available from verified sources |
| Bridge closure | RBS/SDK/Lib.GAB/Harmony hashes and loaded assembly identities |
| Companion | Build ID, dirty/input tree hash, deployed SHA-256, runtime MVID/embedded identity, selected module path |
| Content | Ordered package IDs, selected roots, content fingerprints |
| Execution | Absolute Python path/version; script, client, schema, suite hashes |
| Fixture | Save content hash, scenario/settings identity, Game epoch, map identity |
| Instrumentation | Install states, switches, patch-chain digest, observer code/configuration |
| Authority | Driver session, seat, generation, allowed effects |

**Runtime MVID is useful but is not a cryptographic replacement for the DLL hash.** File hashing plus prevention of in-process replacement joins disk identity to the loaded module more strongly. Where exact loaded bytes cannot be established, say so.

Do not include the token itself. Logs and exports should redact credentials.

Fetch live schemas at session open and bind them to the server/tool-set identity. If unavailable, required mutations refuse. Use tool-specific result adapters; a universal requirement for `payload.success is True` would incorrectly reject tools whose legitimate clean answer is `success:false, "No open window"`.

### 4.3 Make `launch_and_wait` truthful

Its contract should be:

> Launch once through Steam; identify the resulting process; wait for the requested readiness stage; return success only with a current-process readiness receipt.

Required fixes:

- Never print “log truncated” unless observed.
- Never accept an old log marker.
- Verify listener owner PID; reject unexpected hosts and duplicate processes.
- Distinguish launch rejection/dialog/update, process exit, authentication failure, dispatcher failure, invalid load, and deadline exceeded.
- A deadline exceeded result says whether the process is still alive. It does **not** imply automatic termination.
- Archive logs before kill and before launch.
- Terminate by verified process identity, wait for exit, and verify no surviving driver children.
- Preserve startup error evidence even if the game later appears healthy.
- Expose MENU_READY and TEST_READY separately.

A current-run log generation is better than “mtime newer than launch.” Timestamp resolution, clock changes, and stale drvfs reads make the latter weak.

### 4.4 Unify the cold-load budgets

Create one versioned deadline policy used by launcher, watchdog, runner, and agent briefing.

Separate:

- Launch request → process creation.
- Process creation → authenticated bridge.
- Bridge → menu/dispatcher readiness.
- Fixture request → map readiness.
- Individual tool execution.
- Whole suite.

Key cold-load history by **content/order fingerprint, runtime, instrumentation, and workload**, not mod count alone.

For the next load, lacking calibrated history:

- **25 minutes:** warning/investigation threshold.
- **45 minutes:** supervisory deadline for the cold-load attempt.
- **Neither is a kill trigger by itself.**

These are proposed conservative defaults, not measured healthy-load limits.

Progress evidence should combine milestones, main-thread progress when available, process/thread activity, and resource state. **Log growth can be an exception storm; a quiet log can be a healthy menu.**

Declare a load failed immediately on a known fatal condition. Otherwise capture diagnostics and classify suspected stall. Automated kill requires:

- Test profile.
- Correct process identity.
- Current authority.
- No unresolved save in progress.
- Sustained lack of relevant progress with supporting evidence.
- Evidence archived first.
- A bounded restart policy—never an infinite reload loop.

A hard operational deadline can end the *attempt* without declaring the *game* hung.

### 4.5 Idempotency, cancellation, and mutation receipts

Use a client-generated command ID **before transmission**. Proposed command envelope:

```text
command_id
driver_session_id
authority_generation
expected_game_epoch
expected_map_id
tool_name
normalized_arguments_hash
preconditions
execution_deadline
required_postconditions
```

Processing:

1. Validate capability and target.
2. Persist command intent before forwarding.
3. Admit once under the serialized mutation queue.
4. Return/record an acceptance receipt separately from the final result.
5. Recheck authority and target immediately before execution.
6. Execute.
7. Record effects and verified postconditions.
8. Publish a terminal receipt.

Duplicate command ID with identical arguments returns the same receipt. Same ID with different arguments is a protocol error.

Terminal statuses should distinguish:

- Rejected before execution.
- Cancelled before execution.
- Completed and verified.
- Completed with refusals/partial effects.
- Failed with known effects.
- **Indeterminate**.

A socket timeout is a **client observation event**, not a server terminal status.

For mutating batches, receipts need per-item status and actual IDs/kinds/cells. For time advancement, record requested and observed tick deltas plus interruption reason. For saves, record actual changed paths/content.

**Do not promise exactly-once execution across process crashes.** A game mutation and an external durable journal generally cannot be committed atomically. An intent with no terminal receipt after a crash remains indeterminate; never replay it into a new Game epoch automatically.

Cancellation means:

- Remove queued work if it has not begun.
- Cooperatively stop chunked work at declared boundaries.
- Report noncancellable synchronous work honestly.
- Preserve partial-effect receipts.
- Never infer cancellation from disconnect.

### 4.6 Mutation ledger

One append-oriented journal should contain:

- Intent.
- Admission/rejection.
- Execution start.
- Effect/partial-effect receipt.
- Verification result.
- Timeout/cancellation observations.
- Final reconciliation.

Every row joins run, command, process, authority generation, Game epoch, map, UTC, and process monotonic time. Use one writer, bounded payloads, rotation, and explicit write failures.

For required mutating evidence, “telemetry never raises” is insufficient. **If intent cannot be durably recorded, do not admit the mutation.** Diagnostic telemetry may degrade gracefully and report gaps.

### 4.7 Save protection

Checking afterward is necessary but too late to protect a keeper.

Before execution:

- Preserve verified recoverable keeper copies.
- Hash protected saves.
- Confine test save output to an explicitly allowed environment.
- Enforce save destination policy at the actual write/save boundary.
- Cover autosaves and mod-driven saves.
- Refuse path escapes and existing-target replacement unless specifically authorized.

After execution:

- Enumerate **all** changed files, not merely requested target existence.
- Hash protected files and verify unchanged.
- Require a nonempty, well-formed target.
- On a disposable state, reload it and verify expected map/pawn invariants.

A companion wrapper cannot fully fix an upstream save tool that may write the current slot unless bypasses are blocked or the save boundary itself is guarded.

### 4.8 Campaign safe mode: what must be stripped

The campaign build/profile must remove more than the 48 GM tools.

**Absent or denied at the common dispatch boundary:**

- Arbitrary static invocation and unrestricted reflection mutation.
- Lua/JSON scripts capable of invoking mutations.
- Debug action execution and dangerous discovery.
- Hot def reload.
- Spawn/destroy/damage/raid/incident/world/map authoring.
- Pawn edits, research completion, time/tick stepping and unpause.
- Save/load/menu transitions and automatic save commands.
- Quiet-world/blocking prefixes and hostile sweeps.
- Preference changes, focus/input automation.
- Unconfined filesystem output.
- Test hitches, hangs, and recorder fault injection.

Allowed diagnostics must be bounded and reviewed; some nominal getters invoke expensive or stateful code.

Passive instrumentation should have independent switches and measured overhead. Campaign mode must not alter speed boost, log-window behavior, storyteller state, or spawning.

**Stripping companion exports does not remove RBS built-ins or startup side effects.** If the installed RBS cannot enforce a read-only profile—including its documented speed-boost behavior—the reliable campaign option is **RBS absent**. Save-name checks cannot substitute for that boundary.

---

## 5. Observability and clean acceptance experiments

### 5.1 Instrument-to-symptom mapping

| Question | Primary evidence | Important limit |
|---|---|---|
| Did a process launch/exit? | External Windows observer, held process identity, exit status | Nonzero exit does not identify root cause; forced termination may resemble failure. |
| Where did cold loading stop? | Current-run Player.log + external milestones/process activity | Before companion startup, in-game instruments are blind. |
| Is the Unity main thread progressing? | Root heartbeat + bounded dispatcher round trips | Fresh watchdog timestamp proves only the watchdog thread is running. |
| Is an RPC queued, executing, or abandoned? | Command receipts + queue/execution timing | Client elapsed time alone cannot distinguish these. |
| Was simulation slow? | TPS ratio, ambiguity bounds, coverage, effective multiplier | Root.Update cadence is not displayed FPS; elapsed scopes are not pure CPU cost. |
| Was the host resource-starved? | Process/thread CPU, private bytes, commit headroom, competing workloads | CPU total does not identify the main thread or culprit. |
| Was a log quiet because errors stopped? | Logger/cap state plus output growth | No emitted errors under suppression means error activity unknown. |
| Did the intended defs survive? | Resolved-def census + semantic audit | Source XML presence and clean log are insufficient. |
| What arrived and under which observed chain? | Baseline census + incident/origin records + epochs | Missing row does not prove missing event; coverage may exclude overrides or pre-start activity. |
| Did a visitor affect this criterion? | Criterion-specific damage/job/need/path observations | Current detector coverage cannot establish universal nondisruption. |
| Did a save go to the right place and reload? | Save write ledger, hashes, parse/reload verification | Exists/mtime/size alone are weak. |
| What was a native hang/crash doing? | Verified dump capture, native stacks/modules, archived log | Symbols and managed heap visibility may be incomplete. |
| Is a result comparable? | Start/end manifest + fixture/settings/instrumentation identity | Commit SHA and package-ID digest alone are insufficient. |

### 5.2 Recorder interaction risks

The dangerous interactions are not limited to average overhead:

- TPS phase-stack mutation and awareness provenance-stack mutation can reenter each other.
- Error reporting from a recorder can recursively invoke logging hooks.
- Awareness rows share TPS queue/retention capacity and can displace other evidence.
- “Critical reserve” still overflows during a sustained incident storm.
- Shutdown logging, archives, heartbeat writes, health tailing, and antivirus compete for the same disk.
- Turning a metric off can leave patch dispatch overhead installed.
- Runtime enable/disable can unbalance scopes already in flight.
- Game reload can retain old references or stale context.
- Patch order can change what “original ran” means and which code is timed.
- Performance Optimizer can change the call tree without making the game incorrect.
- RealFoW can fail because the fixture recipe is destructive, independent of recorder cost.
- Census/reflection can itself expand lifetime-long metadata and GC work.

Unity documents Mono JIT behavior, Boehm GC, and persistent reflection metadata costs. Those establish credible mechanisms; the exact RimWorld build configuration and incremental-GC state still require runtime verification. [Unity .NET overview](https://docs.unity3d.com/2022.3/Documentation/Manual/overview-of-dot-net-in-unity.html)

### 5.3 De-confound C0–C5

**The six configurations are not fully defined in the inlined documents.** The TPS document still specifies three configurations. Freeze one normative matrix before testing.

A useful proposed six-cell cumulative matrix is:

| Cell | Enabled sources |
|---|---|
| C0 | RBS + companion tool host; sampler, attribution, awareness, and external collectors off |
| C1 | C0 + external health observer |
| C2 | C1 + TPS sampling/lifecycle/watchdog/writer; attribution off |
| C3 | C2 + attribution |
| C4 | C3 + awareness in-memory hooks; awareness disk rows off |
| C5 | C4 + awareness disk rows at a declared event workload |

This estimates incremental effects **conditional on the previous cell**, not all interactions.

Also specify TPS observer/archive behavior. Either hold it identically enabled throughout or include it explicitly in the matrix. “C0” cannot quietly include an undeclared scheduled collector.

Requirements:

1. **One frozen companion binary**, all mod bytes/order, fixture, client, and suite. Only declared settings differ.
2. Verify that “off” actually prevents the intended hooks/threads/work. If dispatch remains installed, label the cell accordingly.
3. Restart for every cell. Do not toggle patches during a measurement window.
4. Start from the same immutable save; discard all mutated outputs.
5. Separate startup/map-generation cost from steady-state cost.
6. Define exact tick workload, pawn counts, speed, camera/UI state, focus/background behavior, difficulty, and event policy.
7. Use fixed-tick completion time and independent wall timing as primary throughput measures.
8. Any reference frame/memory measurement must be common to every cell. If a metric cannot be measured in C0, it cannot support that comparison.
9. Counterbalance order with repeated blocks; do not run C0 once on a quiet machine and C5 once after hours of memory growth.
10. Record actual tick overshoot, missed samples, writer drops/errors, attribution-invalid rates, and observation coverage.
11. Declare acceptable overhead and uncertainty before collecting results.
12. A noisy result with an interval spanning unacceptable overhead is **UNMEASURED**, not PASS.
13. A crash, suppressed required log source, changed manifest, missing cell, or unresolved hook error prevents overall acceptance.

To separate optimizer interaction, add a **four-cell subset**:

- Recorder off/on × Performance Optimizer off/on.
- Same companion, fixture, and all other content.
- Compare the recorder effect with and without the optimizer.

Do not remove Performance Optimizer from the canonical primary experiment and still call it full-list evidence.

For RealFoW, first use a fixture recipe that avoids the known destructive second-map failure. Prove the recipe separately. If RealFoW is removed, label the result as a qualified subset.

### 5.4 Proving awareness safe enough for the 551-mod load

You cannot prove universal safety. You can obtain strong, bounded evidence for a particular content/runtime fingerprint.

Before that load:

1. **Production-hook fault injection** on the actual Mono/Harmony combination:
   - Prefix skipped.
   - Another prefix returns false.
   - Original throws.
   - Another patch throws.
   - Recursive generation/spawn/incident.
   - Worker-thread invocation.
   - Queue/context crosses a schedule.
   - Late installation.
   - Game replacement during outstanding work.
   - Rings/seen-set full.
   - Writer stopped/full/failing.
   - Metric switched off mid-scope.
2. Verify the game exception remains unchanged and the recorder exception never escapes.
3. Verify stacks/tokens clean up and old epochs cannot contaminate new ones.
4. Verify install failure removes only that feature’s own patches.
5. Verify constructors/static initializers are contained and do not synchronously perform heavy census/archive work.
6. Verify hot empty-context paths do no allocation, reflection, filesystem access, or unbounded lookup.
7. Cap context depth, text length, associations, and retained objects—not only row count.
8. Test optional-dependency absence during registration.
9. Test actual overridden incident workers and non-base execution paths.
10. Measure microbenchmarks **on Mono**, then minimal-list generation/load, then the frozen full list.

For the first full-list launch, keep **unproven generation hooks disabled**. They can be enabled for controlled map generation after menu/readiness validation if runtime installation is itself safe. That sacrifices some provenance but avoids making a 15-minute load the first safety experiment.

Important Harmony correction: published v2 documentation describes unskippable observation prefixes as `void` with **no ref/out parameters**. Your claim about `void out __state` depends on the exact installed implementation and must be tested there. Finalizers also execute in an exception path; their own bodies must be contained. [Harmony finalizer documentation](https://harmony.pardeike.net/v2/articles/patching-finalizer.html)

An external observer can capture before the companion exists. Enable it in every comparable startup-safety trial, with the same configuration. Keep standalone no-client autostart acceptance separate so a watchdog call cannot accidentally initialize the recorder.

---

## 6. Process, enforcement, and conflicting rulings

### 6.1 Where agents waste time

The supplied history points to five avoidable loops:

1. Running against the wrong list/artifact, then investigating apparent mod bugs.
2. Polling a process whose runner already finished.
3. Treating quiet logs as hangs.
4. Rebuilding or weakening a harness before proving it observes the symptom.
5. Rediscovering lessons through unrecorded ad-hoc scripts.

Make the normal client path automatically create a run, provenance record, heartbeat, call telemetry, and mutation journal. An ad-hoc script is a **real run with fewer declared checks**, not an exemption.

Use one immutable run bundle per invocation. The convenience launcher should stage and execute it automatically; agents should not manually synchronize mirrors or remember wrapper imports.

### 6.2 Enforcement points

| Rule | Enforcement point |
|---|---|
| One driver, configuration/lifecycle exclusivity | Windows authority process |
| No stale-holder mutation | Server execution fence |
| Correct interpreter and exact scripts | Run-bundle launcher |
| No retired/dangerous tools | Compiled profile plus common dispatch filter |
| No mutation with unchecked schema | Client and server binder |
| No automatic retry of uncertain mutation | Client outcome state machine |
| No wrong map/game | Server-side epoch/map preconditions |
| No unsafe save | Save boundary and protected output environment |
| No focus stealing | Remove unattended focus calls; lint imports/calls |
| No vacuous/missing acceptance | Required-check report gate |
| No drift during proof | Start/end fingerprints and drift invalidation |
| No child survives cancellation | Process-tree supervision plus server cancellation |
| No contaminated blanket GREEN | Criterion evidence/coverage/validity gate |

Agent hooks are useful reminders, but they are not system safety boundaries. Alternative clients, scheduled tasks, and owner UI do not necessarily traverse them.

### 6.3 Conflicts and required resolutions

| Conflict | Resolution |
|---|---|
| No focus stealing vs `focus_heal`/runbook “fix focus first” | Remove automatic focus healing everywhere, including FOUNDRY. Require Run in background. BENCH-only removal is insufficient. |
| One driver vs stale/read-failure fail-open lease | Preserve owner override, but revoke/fence old authority before admitting a new writer. |
| Blanket bridge authorization vs exception for owner actively playing | Campaign/owner-playing state overrides test lifecycle authority. Unknown game identity gets read-only attach. |
| Read-only observers vs main-thread watchdog probes | Coordinate all game-bound calls through the same scheduler; prefer external evidence during reserved operations. |
| GM opt-in vs build refusing safe tool removal | Make expected tool surface profile-specific. Campaign shrink is required, not accidental. |
| Hot reload retired vs exported DLL method | Remove the export/implementation path; client ban alone is incomplete. |
| FULL canonical claim vs omitted new IDs and RealFoW exclusion | Resolve an explicit canonical manifest; qualify every deviation. |
| TPS constructor startup evidence vs older lazy-init claims | Update architecture to the supplied decompiled chain; keep installed-version live acceptance. |
| Three-cell TPS acceptance vs six-cell health plan | One frozen normative experiment; archive superseded criteria. |
| Harmony safety FAIL vs pending overhead deployment | Safety hardening precedes measurement; freeze the hardened artifact afterward. |
| “Slow is not hung” vs health record never affecting verdict | TPS must not declare a hang, but lost heartbeat/writer/coverage can invalidate health evidence and suite eligibility. |
| Visitor CLEAN-with-note vs acknowledged invisible disruption | Preserve the owner’s operational rule while stating criterion coverage limits; stronger visitor-sensitive acceptance needs a policy decision. |
| DRAFT/PENDING owner review counted passing vs “unknown never clean” | Administrative status must not satisfy functional/acceptance checks. |
| Save safety net vs same-process autosave possibility | Protect actual writes, including autosaves; avoiding explicit `save_game` is insufficient. |
| Reboot whenever free/yours vs nonholder release/force | Owner override is explicit; ordinary agents cannot silently release another live driver. |
| No worldgen vs quicktest world creation | Define whether quicktest is an authorized disposable fixture exception. Do not silently infer that all world-generation tools are permitted. |

### 6.4 Small rule set to add

1. **No mutation without current process, Game epoch, target, and authority generation.**
2. **A timeout leaves outcome unknown until reconciled; unknown mutations block dependent work.**
3. **Every launch and live call runs from an immutable, automatically recorded bundle.**
4. **All lifecycle, configuration, deployment, and save operations use the same authority path.**
5. **Required UNKNOWN, missing, waived, or vacuous evidence cannot become GREEN.**
6. **Instrumentation failure must preserve gameplay and explicitly reduce coverage.**
7. **A recurring incident closes only with a regression check that fails for that defect—or an explicit explanation of why automation cannot decide it.**

Measure diagnosis time from the **earliest recorded detectable symptom**, separately from first owner report and first agent investigation. Record detection latency, diagnosis latency, recovery time, and bridge time lost. That prevents “we diagnosed it quickly once we looked” from hiding hours of missed detection.

---

## 7. Prioritized build plan

The score below is an **illustrative planning model**:

`estimated probability of recurrence × minutes avoided ÷ engineer-hours`

These are judgments, not calibrated probabilities. Costs include invalidated experiments; keeper loss is conservatively understated. Effort assumes a focused increment using existing tooling, not completion of the eventual architecture.

| Rank | Build item | P / avoided min / hours / score | Acceptance that cannot pass while defect exists |
|---:|---|---|---|
| 1 | Freeze experiment manifest and gate known recorder defects | .6 / 240 / 2 / **72** | Redeploy companion, toggle collector, change mod bytes, or leave required safety FAIL: experiment refuses and cannot mark C4 complete. |
| 2 | Protected-save admission and hash-backed recovery | .4 / 600 / 4 / **60** | Fake/save tool writes current slot or same-size keeper, writes zero bytes, or autosaves campaign: admission blocks or protected copy survives and result fails. |
| 3 | Truthful single launcher/readiness receipt | .8 / 60 / 2 / **24** | Old token/log with no process, unrelated listener, delayed truncation, failed Steam launch, zombie load: never exits success. |
| 4 | Canonical ordered mod manifest and startup/runtime comparison | .8 / 60 / 2 / **24** | Core-only reset, omitted shipping ID, same IDs reordered, duplicate roots: pre-flight refuses or invalidates run. |
| 5 | Build/deploy/run provenance closure | .8 / 60 / 3 / **16** | Dirty source, stale sibling, stale mirror, same-size texture change, wrong loaded companion: no proof/GREEN. |
| 6 | Effective-def load-killer and cost-reference lint | .5 / 90 / 3 / **15** | Raw-valid XML becomes invalid after patch/inheritance; unresolved cost material points to writer and fails before launch. |
| 7 | Remove focus/retired/discovery bypasses | .6 / 30 / 1.5 / **12** | Unattended focus call, alternate hot-reload route, banned discovery call through script/nested dispatch: rejected by applicable boundary. |
| 8 | Minimal exclusive Windows driver/lifecycle supervisor | .7 / 60 / 4 / **10.5** | Simultaneous same-seat acquisitions, unreadable lock, nonholder release, dead child: at most one admitted driver; failure is explicit. |
| 9 | Transport parser and absolute-deadline fault suite | .5 / 60 / 3 / **10** | Split every byte boundary, Unicode, partial timeout/EOF, event flood, malformed lengths: bounded failure; no false result or duplicate dispatch. |
| 10 | Unknown-mutation state machine and no-retry enforcement | .5 / 60 / 3 / **10** | Execute mutation then drop response: ledger says indeterminate; no retry/dependent mutation until reconciliation. |
| 11 | Production Harmony safety hardening | .4 / 180 / 8 / **9** | Reentrancy, skipped prefix, exception, off-thread, late install, writer fault: game result/exception preserved, coverage failure visible, stacks clean. |
| 12 | Game/map epoch guards and verified cleanup | .4 / 90 / 4 / **9** | Load equal-tick save, cull/switch map, leak quiet block, kill runner: stale targets rejected; dead-man/cleanup evidence accurate. |
| 13 | Unconditional client run/call evidence | .8 / 30 / 3 / **8** | Direct scratch client invocation still yields identity, calls, unfinished operation, result evidence; sink failure blocks required mutation evidence. |
| 14 | Spoiled-run and acceptance regression suite | .7 / 30 / 4 / **5.25** | Unknown blocking window, visitor-sensitive gap, empty rows, DRAFT status, capped list, log blindness: cannot produce blanket GREEN. |
| 15 | Full optimizer-aware overhead/utility acceptance | .6 / 240 / 30 / **4.8** | Missing cell, changed manifest, unsafe hook, invalid attribution, dropped required evidence, inadequate precision: overall acceptance remains unmet. |

Full server fencing, durable receipts, and release transactions are larger follow-ons to rows 8–12. Do not claim the narrow first increments complete those guarantees.

### DO NOW before the next full-list cold load

1. **Resolve the intended list.** Reconcile the reported 551 canonical IDs, 67 active IDs, and 14 extra IDs. Freeze order and selected roots.
2. **Choose and freeze the exact companion release.** No mid-experiment awareness redeploy. Known Harmony safety FAIL blocks the affected hooks; disable them or fix and test them first.
3. **Fingerprint the dependency closure.** Include the installed RBS 2.3.0 assemblies, SDK, Harmony, game assemblies, and hard-linked mod DLLs.
4. **Run cost/null-reference and known load-killer lint.** Include effective patch/inheritance outcomes wherever tooling supports them; explicitly list unsupported scope.
5. **Protect keepers and campaign saves with recoverable copies and hashes.** Use a disposable fixture. Do not rely on save size or requested filename.
6. **Replace or bypass the false-ready launcher.** Require current PID/token/listener ownership, dispatcher readiness, and current-run error audit.
7. **Ensure exactly one driver and no surviving old driver/operation.** A temporary supervised serial runner is acceptable; a courtesy lease alone is not.
8. **Remove automatic focus healing.** Verify Run in background without moving the owner’s foreground window.
9. **Ban dangerous discovery/hot reload and unsafe direct saves in the exact upcoming script.**
10. **Stage exact scripts/client/schema in an immutable Windows bundle.**
11. **Archive logs before launch and start the declared external observer.**
12. **Use one conservative deadline policy; no 25-minute automatic kill.**
13. **After startup, verify actual ordered mods, loaded companion, resolved critical defs, fixture, and epoch before mutations.**

If the full fencing/receipt system is not built yet, the next run must use a constrained fallback: **one supervised driver, no mutation retry, stop on uncertain outcome, no campaign access, protected saves, frozen inputs**. Document the remaining boundary weakness.

### Later

- Full common-dispatch capability enforcement.
- Per-mod companion adapters.
- Atomic multi-artifact release activation/rollback.
- Durable command receipts and cooperative cancellation.
- Criterion-specific interference coverage.
- Unified timeline and retrospective invalidation.
- Full C0–C5/optimizer experiments.
- Verified native dump pipeline.
- Resource-growth, sleep/resume, retention, and overnight soak tests.

---

## 8. Answers to the authors’ open questions

### Architecture document: 15 answers

| # | Answer |
|---:|---|
| 1 | **Pin a tested bridge closure.** Upgrade deliberately in an isolated candidate release: compile, metadata/schema compatibility, transport fixtures, minimal registration, mutation/save receipts, then full-list qualification. Automatic rebuild is a prerequisite, not approval. |
| 2 | **Installed direct-mode gating remains UNKNOWN.** Current published policy opens attention for error/fatal logs and failed/cancelled/timed-out operations, but specifically describes GABS enforcement. Capture attention and stop affected mutations; do not auto-ack unexplained failures. [RBS attention policy](https://github.com/pardeike/RimBridgeServer/blob/main/docs/attention-policy.md) |
| 3 | **Enforce at execution.** Client gating helps ergonomics; companion gating is partial; courtesy alone is insufficient. Authority-store failure denies new automated mutations but retains diagnostics and explicit owner recovery. |
| 4 | **UNKNOWN.** Run two controlled clients on disposable state and inspect exact-version dispatcher code. Until then serialize game-bound observers with driver work. |
| 5 | **Use phase/tool deadlines, not one 30-second timeout.** Distinguish admission, queue, execution, and client wait. Reconcile by client-correlated receipt; existing operation tools require verified schema/correlation. |
| 6 | **Campaign should expose bounded read-only diagnostics and proven passive sources only.** No blocking prefixes, test mutations, arbitrary execution, or unapproved startup effects. |
| 7 | **`UP` should mean verified usable dispatcher/menu readiness**, with explicit TEST_READY/MUTATION_READY for a valid fixture. Process/listener are separate observed fields. |
| 8 | **One launcher.** Steam URI versus `-applaunch` is secondary to a correct process/readiness contract. Kill by verified identity, archive first, verify exit. |
| 9 | **Progress-aware supervision plus a bounded deadline.** Neither log silence nor elapsed 25 minutes proves a hang. Kill requires test authority and supporting evidence. |
| 10 | **Split dependency-heavy adapters.** RBS partial-registration behavior is UNKNOWN for installed binaries. Minimal-list acceptance must inspect core and adapter coverage separately. |
| 11 | **Build profile plus runtime capabilities.** Build omission prevents discovery/bypass; runtime scope/expiry protects the active game. A coarse GM flag does neither adequately alone. |
| 12 | **Replace unsafe save access with guarded save orchestration.** Existing-target refusal is necessary but not sufficient; protect actual write destinations and automatic saves. |
| 13 | **Yes: one joined provenance record**, continued by command receipts and end-of-run drift checks. |
| 14 | **Identify the driver process/session.** Parent→child handoff drains/reconciles work and increments authority generation. No shared inherited writer token. |
| 15 | **Yes, for explicitly armed test sessions.** Pause on lost renewal, expire quiet controls, and record the reason. If the main thread is hung, the dead-man cannot pause immediately; its external supervisor remains necessary. Never arm it implicitly in campaign play. |

The retrieved RBS policy is on current upstream `main`; it is **not proof of equivalence to the installed 2.3.0 binaries**. Archive source/decompilation keyed to their hashes before using it to settle server internals.

### Debugging document: 14 answers

| # | Answer |
|---:|---|
| 1 | **One shared check library, multiple entry points.** Standalone launch pre-flight and existing runners call the same checks and evidence model. |
| 2 | **Yes, automated config/lifecycle actions require common authority.** Owner UI and Steam may act independently; detect them, revoke/invalidate automation, and avoid pretending they are enforceable through agent hooks. |
| 3 | **Base client records calls; run layer adds structure.** Every ad-hoc process gets a run ID. Parent correlation handles deliberate multi-process runs. |
| 4 | **CLEAN-with-note is not enough evidence for every criterion.** For need/mood/job criteria, missing relevant coverage means eligibility is unknown. Changing the owner’s redo policy needs his decision; report the limitation meanwhile. |
| 5 | **Keep Performance Optimizer in the primary canonical experiment; add the four-cell ablation.** Measure interaction rather than assume it is the cause. |
| 6 | **Always-on generation hooks require startup safety and measured cost first.** Initially disable unproven ones. Empty-context counter paths must be allocation-free and bounded. |
| 7 | **Reduce confidence in precise P/C numbers.** Raise persistence damage, uncertain mutations, process/epoch targeting, effective-def patching, and multi-file deployment. Add host presentation/power, commit exhaustion, parser faults, and evidence races. |
| 8 | **Do not classify every unknown window as blocking.** Record type and verified pause/input behavior; distinguish overlay from modal. Unknown potentially blocking windows prevent affected input-dependent checks until classified. |
| 9 | **Enable a capped, verified dump path.** WER may not catch the actual game crash path; verify it. Use an on-demand identity-bound dump for hangs, without a five-second “hung window” trigger during normal loading. Native stacks/modules still have value without complete Mono symbols. [ProcDump documentation](https://learn.microsoft.com/en-us/sysinternals/downloads/procdump) |
| 10 | **Automate interpreter, deploy, identity, list, save, banned-call, missing-check, and lease rules.** Judgement remains for fun/style, unexplained interference, and causality. |
| 11 | **Comparability is a precondition, not another ladder rung.** Also distinguish current-run correctness from regression comparison; a unique stochastic run may be valid without being deterministically comparable. |
| 12 | **Use fixed fixture state and scoped RNG control where supported.** Do not reset global RNG mid-game. Record available state; for stochastic behaviors use repeated trials and declared distributional criteria. “Spawn many” alone is not a statistical design. |
| 13 | **Measure from earliest detectable recorded evidence**, alongside owner report and agent discovery. Add separate detection/diagnosis/recovery fields. |
| 14 | **Slow is not hung.** Low TPS alone should not fail a tick-semantic check. It can invalidate wall-time/UI timing checks or budgets. Lost coverage, wrong epoch, skipped ticks, and unresolved outcomes directly affect eligibility. |

---

## 9. Four genuine owner decisions

1. **Campaign boundary:** should campaign play omit RBS entirely, or retain a strictly enforced read-only profile?  
   **Recommendation:** omit it until upstream built-ins, scripting, and startup side effects can be constrained and verified.

2. **Canonical FULL identity:** which of the 14 extra package IDs belong in the shipping list, and does RealFoW remain mandatory?  
   **Recommendation:** approve an explicit ordered shipping manifest; qualify any test subset and repair the RealFoW fixture recipe separately.

3. **Visitor-sensitive acceptance:** may need/mood/job criteria become INDETERMINATE when relevant interference was not observed well enough, even if the visitor is removed and the run continues?  
   **Recommendation:** yes; preserve operational continuation while withholding unsupported acceptance.

4. **Instrumentation value/cost:** what maximum throughput loss, tail-latency increase, and memory/I/O growth are acceptable in campaign play, and how much controlled full-list experimentation is authorized?  
   **Recommendation:** separate campaign and diagnostic budgets, with thresholds declared before C0–C5. A metric earns always-on status only through measured utility and cost.