**Recommendation: build a smaller option F—persistent external observation, a minimal extension to the existing recorder, and narrowly targeted diagnostic captures.** The design has the right architecture, but several proposed numbers would be confidently misleading. Its cost estimates, attribution labels, frame partition, leak detector, and profiler-overhead report need substantial revision.

I reviewed the inlined material only. Unity/Harmony/Windows documentation establishes general behavior; it does **not** establish capabilities, performance, or safety in the installed RimWorld player. The design’s reported decompilation findings remain supplied evidence, not independently verified source.

## 1. Answers to the 12 open questions

### 1.1 Release-player memory and render counters

**VERIFIED-from-knowledge:** `ProfilerRecorder` supports release players, but availability is **counter-specific**. Unity 2022.3 documents these as release-accessible:

| Counter | Documented release availability | Interpretation |
|---|---:|---|
| `Total Used Memory`, `Total Reserved Memory` | Yes | Unity-tracked memory; not a complete process-memory accounting |
| `GC Used Memory`, `GC Reserved Memory` | Yes | Managed occupied/reserved memory |
| `GC Allocated In Frame` | No | Do not promise release-player allocation rate |
| `Draw Calls Count` | Yes | Submitted draw calls |
| `Total Batches Count` | Yes | **Correct documented name**, rather than the design’s `"Batches Count"` |
| `SetPass Calls Count` | Yes | Shader-pass changes |
| Texture/mesh/material counts and associated memory counters | No | These particular profiler counters require more than ordinary release availability |

Sources: [Unity memory-counter availability](https://docs.unity3d.com/2022.3/Documentation/Manual/ProfilerMemory.html), [render-counter availability](https://docs.unity3d.com/2022.3/Documentation/Manual/ProfilerRendering.html).

`Profiler.GetTotalAllocatedMemoryLong()` exists, and its documentation explicitly permits a zero result when the profiler is unavailable. `GetMonoUsedSizeLong()` measures live **and not-yet-collected** managed objects; it is not allocated bytes per second. [Allocated memory API](https://docs.unity3d.com/2022.3/Documentation/ScriptReference/Profiling.Profiler.GetTotalAllocatedMemoryLong.html), [managed used-memory API](https://docs.unity3d.com/2022.3/Documentation/ScriptReference/Profiling.Profiler.GetMonoUsedSizeLong.html).

**UNKNOWN:** which sources actually work in RimWorld’s precise Unity patch version and build configuration.

**Implementation:** enumerate available recorder handles once, record names/categories/units, check validity and sample count, and exercise each selected source. `Valid` or a zero value alone does not prove useful collection. Record unavailable or unvalidated sources as unavailable, rather than healthy zeroes. Dispose recorders explicitly; they own unmanaged resources. [ProfilerRecorder documentation](https://docs.unity3d.com/2022.3/Documentation/ScriptReference/Unity.Profiling.ProfilerRecorder.html).

### 1.2 Boehm GC pause duration

**VERIFIED-from-knowledge:** Unity uses a noncompacting Boehm collector and supports incremental collection. Boehm does **not** imply every collection is one long stop-the-world pause. Record the installed mode; Unity 2022.3 documents `UnityEngine.Scripting.GarbageCollector.isIncremental`. [Collector behavior](https://docs.unity3d.com/2022.3/Documentation/Manual/performance-incremental-garbage-collection.html), [incremental-mode query](https://docs.unity3d.com/2022.3/Documentation/ScriptReference/Scripting.GarbageCollector-isIncremental.html).

**UNKNOWN:** whether this player exposes a usable native profiler callback or GC timing marker. General Mono profiler facilities exist, but their existence does not establish availability in Unity’s embedded Mono fork. Do not ship speculative `mono_gc_*` imports or assume desktop .NET GC notifications apply. [Mono profiler documentation](https://www.mono-project.com/docs/debug%2Bprofile/profile/).

**PLAUSIBLE:** a frame gap accompanied by a collection-count increase is useful **coincidence evidence**. Call it `gcCountChangedDuringGap`, not `gcPauseMs`.

It cannot establish:

- that GC caused the gap;
- how much of the gap was GC;
- whether one collection or several incremental slices occurred;
- which mod allocated the garbage.

A collection can occur inside an already expensive tick, after a log storm, or while another source causes most of the delay. External CPU data narrows possibilities but cannot identify GC uniquely.

### 1.3 Logging after the cap

**VERIFIED-from-knowledge:** ordinary `Debug.unityLogger` calls stop forwarding messages when `logEnabled` is false. The Unity reference source gates logging before calling the handler. Consequently, the threaded event cannot count those suppressed messages. Other native/custom logging paths may still emit. [Unity 2022.3 logger source](https://github.com/Unity-Technologies/UnityCsReference/blob/2022.3/Runtime/Export/Logging/Logger.cs).

The event is explicitly concurrent and can execute on different threads. [Threaded logging event](https://docs.unity3d.com/2022.3/Documentation/ScriptReference/Application-logMessageReceivedThreaded.html).

**PLAUSIBLE:** reading the private cap flag covers the **known Verse-cap condition**.

**UNKNOWN:** the exact installed cap, reset behavior, suppression patches, and whether all relevant errors traverse that logger.

The private flag is insufficient by itself. Record separately:

- Verse cap state;
- logger enabled state and filter;
- emitted Unity-message counts;
- optional Verse logging-attempt counts;
- counter resets and log-coverage transitions.

After suppression, emitted-message counts can legitimately be zero while attempted errors continue. The reader must display **“emission suppressed; error activity unknown.”**

There is an immediate evidence conflict: the design says **10,000**, while `belt_watchdog.py` says **1,000** in both its comment and displayed diagnosis. Resolve against the installed `Verse.Log` implementation; do not encode either constant into health logic prematurely.

### 1.4 T0’s `<10 µs/frame` estimate

**PLAUSIBLE:** that order of magnitude might hold for a histogram plus a handful of simple timer invocations.

**UNKNOWN:** the actual cost with Harmony 2.4.2, finalizers, phase publication, Mono, multiple maps, GUI callbacks, and the full patch chains.

The arithmetic in the estimate is wrong: five timer pairs require at least ten timestamp reads, before heartbeat and phase-stack work. “Five stage timers” also does not mean five invocations per frame.

Fix the contracts and prototype now, but **gate always-on activation on measurements**. The existing recorder’s MUST 17 remains a prerequisite for accepting additional in-process cost.

### 1.5 Runtime Harmony installation and removal

**VERIFIED-from-knowledge:** Harmony supports dynamic patching, but has runtime edge cases, including inlining that can make patches ineffective. [Harmony 2 runtime limitations](https://harmony.pardeike.net/v2/articles/patching-edgecases.html).

**UNKNOWN:** reliable repatching of an executing hot method, callback wrapping, and repeated arm/disarm cycles in this exact Unity/Mono/Harmony combination.

**PLAUSIBLE:** installation on the main thread at a known quiescent boundary reduces risk.

**Paused is insufficient.** Rendering, GUI, map updates, bridge work, long events, and workers can continue. The menu is also not universally quiescent.

Prefer, in order:

1. Direct optional instrumentation in **our own code**.
2. A small, fixed set of startup-installed diagnostic hooks with a cheap inactive branch.
3. Runtime installation for a specifically validated target family.
4. Arbitrary wrapping of other mods’ patch methods only as an experimental capability.

Patching a patch method does not establish that every generated caller routes through the new instrumentation. Transpilers are especially different: their execution usually measures **patch construction**, while their inserted instructions execute inside the target and cannot be generically charged back to the transpiler owner.

### 1.6 Native main-thread CPU time

**VERIFIED-from-knowledge:** Windows exposes cumulative user/kernel CPU time through `GetThreadTimes`. The kernel can answer while the target thread is suspended; the target need not cooperate. [GetThreadTimes](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-getthreadtimes).

**PLAUSIBLE:** capture `GetCurrentThreadId` inside a verified main-thread callback, publish it, and observe that thread externally.

Use a persistent thread handle, or verify thread identity/creation time when reopening it. Managed thread ID is not native thread ID. Dispose handles, detect exit, and invalidate baselines after failed reads.

`ProcessThread.TotalProcessorTime` may provide a convenient wrapper, but its Mono implementation and enumeration cost remain **UNKNOWN** here.

During stop-the-world GC:

- an **external observer** can still query CPU time;
- the managed watchdog may be suspended and cannot perform its query;
- CPU time identifies execution, not whether that execution was simulation, GC, spinning, or native work.

### 1.7 Fairness of a verbose load

**VERIFIED-from-knowledge:** enabling instrumentation/logging changes the workload.

**UNKNOWN:** whether the distortion is 1%, 20%, or substantially worse on this list. A logging-heavy mod or slow log destination can dominate.

Treat a verbose launch as a **diagnostic load**, not the canonical startup benchmark. Compare:

- ordinary launches with ordinary launches;
- verbose launches with equivalent verbose launches.

Use the verbose tree to select investigations. Validate proposed optimizations with ordinary launches afterward. Record log bytes, messages, cache state, and whether the load completed; a crash may prevent the profiler tree from being printed.

### 1.8 WSL observation cost and file interference

**PLAUSIBLE:** a persistent Windows collector sampling a few counters every five seconds can have low overhead.

**UNKNOWN:** the proposed WSL/PowerShell implementation’s overhead and sharing behavior.

“External” means no injected game code; it does **not** mean no observer effect. PowerShell startup, WMI enumeration, hashing large logs, antivirus activity, and drvfs traffic share CPU, RAM, and storage with the game.

Prefer a persistent Windows-side collector, with WSL consuming its output. Tail incrementally with suitable sharing permissions, detect replacement/truncation, and reopen after rotation. Test both directions: Unity rotating while the observer reads, and the observer reopening while Unity writes.

Do not repeatedly reread or hash the entire active log.

### 1.9 Minidump usefulness

**VERIFIED-from-knowledge:** small dumps can preserve native stacks, thread context, and module information. Full dumps include process memory. ProcDump supports clone-based collection to reduce target disruption, but cloning still has resource cost. [ProcDump dump types and clone mode](https://learn.microsoft.com/en-us/sysinternals/downloads/procdump).

**UNKNOWN:** useful managed stack reconstruction from a Windows dump of this Unity Mono build using the available tools. CoreCLR/SOS assumptions do not transfer automatically.

**PLAUSIBLE:** even without managed names, a small dump can distinguish native waits, Unity/driver activity, and some synchronization failures.

Before automatic collection, prove:

- a dump identifies a deliberately blocked main thread;
- useful stacks survive analysis offline;
- collection duration and size are acceptable;
- the dumper cannot strand the process suspended;
- failures and partial dumps are reported.

Do not promise “10–200 MB” or a short suspension without measurements. Keep full dumps manual. Automatic small dumps should be disabled until the utility spike passes.

### 1.10 Validity of the frame partition

**VERIFIED-from-knowledge:** the proposed scopes are not a guaranteed partition.

They can nest, execute multiple times, omit work, and include waits for workers. Drawing submission is not GPU execution. GUI can execute for different event types. Unity work outside these methods remains unmeasured.

**PLAUSIBLE:** they are useful named **main-thread elapsed scopes**, provided their overlap is handled.

Use:

- inclusive duration per scope;
- exclusive duration only for a validated nesting tree;
- invocation count;
- original-skipped/exception/incomplete coverage;
- separately measured frame interval;
- unaccounted elapsed time, without calling it rendering cost.

CPU and GPU intervals can overlap across frames. Do not sum their durations into a frame partition. FrameTimingManager itself has prerequisites, measurement overhead, and delayed results—Unity documents a four-frame delay. [FrameTimingManager](https://docs.unity3d.com/2022.3/Documentation/Manual/frame-timing-manager.html).

### 1.11 Thresholds

**UNKNOWN:** the proposed performance/leak thresholds are grounded in this workload.

Run performance thresholds in report-only mode initially, stratified by speed, focus, camera, map, workload, loading state, and instrumentation mode.

Do **not** postpone correctness alerts for a month. Immediately report:

- failed capture;
- stale coverage;
- dropped critical evidence;
- logger suppression;
- unavailable counters;
- low disk space;
- observer failure.

“Third reload +10%” is neither a leak definition nor a suitable generic warning. Use matched reload cycles, post-warm-up trends, absolute growth, natural-GC observations, and specific retained-object evidence.

### 1.12 Retention capacity

**VERIFIED-from-knowledge:** at five-second cadence there are **17,280 samples/day**.

| Sample size | Samples alone per continuous day |
|---|---:|
| 1 KiB | 16.9 MiB |
| 2 KiB | 33.8 MiB |
| Additional 200 bytes | +3.3 MiB |

A 2 KiB minute context adds another 2.8 MiB/day. Seven days of 2 KiB samples plus the proposed additions and context already exceed 256 MiB, before manifests and incidents.

Thus seven days is conditional, as the shipped document correctly acknowledges. Multiple active processes and large artifacts complicate the bound further.

Measure actual serialized bytes and report **oldest retained coverage**, bytes/day, and estimated retention horizon. Separate **bulk profile artifacts, traces, and dumps** into independently capped families. Keep compact health observations in the ordered stream; splitting every band into separate segments would create unnecessary joining and continuity problems.

## 2. Attack on the design

### 2.1 Metrics that produce wrong interpretations

| Metrics | Trap | Required correction |
|---|---|---|
| **M1, M4** | Heap occupancy is treated as live memory or allocation rate. Net growth hides allocations reclaimed during the interval. | Label occupied managed bytes. Obtain allocation rate only from a validated allocation counter. |
| **M2, M3** | A collection-count increase is interpreted as GC-bound behavior or pause duration. | Record coincidence and collector mode; timing needs a separate source. |
| **M5** | Reserved-minus-used is called fragmentation. | Call it unused reserved capacity. Fragmentation concerns free-block layout and allocation suitability, not just the difference. |
| **M5** | “Boehm never returns memory” is categorical. | Remove the universal claim. Exact heap-release behavior depends on implementation; Unity’s documentation even discusses heap-size decreases. |
| **M6, M7** | Managed/native/process values are treated as disjoint accounting categories. | Document each source’s accounting domain. They can overlap and omit memory; subtraction does not automatically identify native leaks. |
| **M8** | `totalTextureMemory` becomes “VRAM used.” | It is theoretical full-mipmap texture demand with exclusions. `currentTextureMemory` is also not complete GPU residency. [Texture semantics](https://docs.unity3d.com/2022.3/Documentation/ScriptReference/Texture-totalTextureMemory.html). |
| **M9** | Map dimensions imply mesh memory. | Geometry density, layers, capacity, and retained buffers vary. Dimensions are workload context, not measured mesh bytes. |
| **M11, M12** | Spawned-map Things describe all retained game objects. | Held Things, inventories, corpses, world objects, and despawned objects need separate investigation. |
| **M12** | Def owner identifies who spawned excessive Things. | It identifies content provenance. Another mod can spawn, duplicate, retain, or retick that Def. |
| **M13** | Heap after return-to-menu proves a leak. | Cache warming, pending collection, finalization, allocator retention, and changed workload can all explain growth. |
| **M14** | A static reference identifies a guilty mod. | A root is evidence of retention, not proof that retention is erroneous. Broad reflection can initialize types and create its own retention. |
| **G1, G2** | `Root.Update` cadence is rendered/displayed FPS. | Name it update cadence/frame interval. Validate against presentation data before calling it displayed FPS. |
| **G2** | Eight coarse buckets produce exact p50/p95/p99 values such as `16.2`. | Report a bucket range or explicitly approximate quantile. Use finer fixed buckets if precision matters. |
| **G2** | p99 captures the worst user experience. | A single 20-second stall among hundreds of frames can fall above p99. Preserve maxima, long-gap events, and total time in slow intervals. |
| **G3** | Inclusive scopes are summed and subtracted from frame duration. | Validate nesting and interval ownership. Never clamp away a negative residual. |
| **G7, G11** | Submitted things/draw calls imply visible things or GPU expense. | Distinguish candidates, submitted work, and visible/displayed output. Counts are workload indicators. |
| **G8** | A method’s declaring type identifies its caller. | It does not. Caller attribution requires additional evidence or direct instrumentation. |
| **L1, L16** | Bridge-ready/menu heartbeat equals first interactive frame. | Define separate process-start, companion-ready, menu-observed, playable-map, and interaction milestones. |
| **L3, L9** | Mod constructor time equals Harmony installation cost. | Constructor scopes include other work and may omit patching done elsewhere. Keep these separate. |
| **L5, L6** | `PatchOperation.Apply == false` means dead or incorrect XML patch. | Interpret per operation kind and nesting. Optional/conditional operations have different semantics; nested timings double-count. |
| **L8** | Patch count, owner ID, or hot-target density proves cost. | It establishes topology and candidates. Transpilers can speed code up; unpatched implementations can dominate. |
| **L12** | Patching `GenStep.Generate` captures concrete generation. | Resolve actual dispatched implementations. A base/abstract method hook is not a coverage guarantee. |
| **L15** | Save sections yield exact per-mod save bytes. | Serialization provenance is mixed; shared structures and compression defeat simple attribution. Report content/type association and physical file size separately. |
| **S3–S5** | Def/component/type timings are additive mod costs. | Shared implementations, inheritance, base calls, nesting, patch chains, and different populations matter. |
| **S6** | Patch-method time provides the complete cost of a Harmony owner. | It omits transpiler-generated execution, changed work elsewhere, skipped originals, and interactions. |
| **S7, S16** | Pathfinder scope time equals worker computation; worker CPU equals AI CPU. | Scope time can be scheduling or waiting. Shared Unity workers execute several systems. |
| **I1, I3, I4** | Emitted errors equal attempted errors; message hash equals source mod. | Record suppression and sampling. Hash identity and stack association provide leads, not causal ownership. |
| **X2** | Missing shutdown completion means crash. | It means unclean/unknown exit: kill, OS shutdown, failed recorder, or crash. Add independent crash evidence. |
| **X3, X4** | Unity exception logs equal thrown/unhandled exception counts. | Many exceptions are caught or unlogged; logged exception text can be repeated without a new throw. |
| **P1** | Process at one core proves the main thread is spinning. | A worker can consume that core. Use actual main-thread CPU and qualify conclusions. |
| **P5** | `PageFaultCount` is hard faults or pagefile thrashing. | It includes faults that need no disk read. Rename it total faults; hard-fault attribution needs another source. [Windows fault-counter semantics](https://learn.microsoft.com/en-us/previous-versions/aa394323%28v%3Dvs.85%29). |
| **P6** | GPU utilization proves GPU-bound rendering. | Other applications, copy engines, vsync, and sampling granularity matter. Use process/presentation context and controlled workload changes. |

### 2.2 Schema and analysis defects

**The bands need their own measurement contracts.** TPS windows close at `TickManagerUpdate` prefixes; proposed frame intervals begin at `Root.Update` prefixes. Attaching both to one sample does not automatically align them. Preserve each band’s interval, or deliberately synchronize collection at a shared boundary.

Every source needs:

- scope: process, game, map, profile run;
- unit and counter semantics;
- start/end or snapshot time;
- source availability and installation status;
- sample count and coverage;
- cached-data age;
- reset/wrap/discontinuity status;
- instrumentation mode.

Specific corrections:

1. **Do not reset every cumulative metric at game change.** Process CPU, logging suppression, assembly count, static caches, and process memory are process-scoped. Resetting them would erase precisely the reload accumulation being investigated.
2. **Do not average window p99s.** Merge compatible histograms and recompute quantiles. Preserve bucket definitions/version.
3. **Five-second p99s have weak tail resolution.** At 60 updates/s, p99 describes only a few observations. Show `n` and longer-range distributions.
4. **Replace “measured overhead = during / preceding minute.”** Colony activity, camera, GC, speed, and incidents can change. This ratio is a before/after observation, not observer overhead.
5. **Bulk artifacts must not be single giant JSONL rows.** Persist a bounded artifact separately and enqueue its ID, digest, coverage, and status.
6. **A line-count queue bound is insufficient for enlarged rows.** Add byte bounds, maximum row size, artifact size limits, and oldest-outstanding age.
7. **Offline log attribution requires surviving evidence.** A hash without archived text/stack association becomes unresolvable after cap, rotation, truncation, or archive failure.
8. **Leak slopes need lifecycle segmentation.** Loading a new map is a step change, not an hourly leak rate.
9. **No “85% of RAM” diagnosis from process working set alone.** System available memory, commit headroom, and actual paging evidence matter.
10. **Load-order digest is inadequate build identity.** Same IDs/versions can contain changed DLLs, XML, textures, or settings. Hash relevant content outside the measured hot path.

### 2.3 Remaining hazards visible in the supplied code

These are relevant blockers for expansion, despite the reported completion of the earlier fixes:

| Location | Visible issue | Implication |
|---|---|---|
| `TmuPrefix/TmuPostfix` | Uses global invocation state and ordinary postfix cleanup. | Reentrancy/concurrent invocation remains unsupported; an original exception can bypass timing/phase cleanup. |
| `LePrefix/LeFinalizer` | `_leOpen` is global. | Nested invocations can overwrite the outer scope’s state. |
| `TickPre` | Calls `Stages.TickBegin()` and writes `_tickId` **before** `Begin()` rejects a foreign thread. | Main-thread rejection is too late to guard the whole prefix. |
| `TickPre/TickFin` | `_tickId` is global. | Nested ticks can change the identity associated with an outer measurement. |
| `RootPrefix` | `WD.Beat()` sits outside its exception boundary. | The stated containment boundary depends on an unseen method’s nonthrowing implementation. |
| `Context` | `AllPawnsAlive` still copies living world pawns, as the comment acknowledges. | “Cheap counts only” is still a population-dependent allocation/cost claim. |
| `WriteSessionStart` | Already enumerates **all patched methods** for owner counts. | L8 partly exists; extending it is not starting from zero runtime cost. |
| Patch-chain serialization | Sorts by priority/index without preserving before/after constraints. | This is not proof of actual execution order. |
| `PreviousSession` | Uses absolute heartbeat/log-mtime distance. | Archive-session association is heuristic and can select an inappropriate overlapping session. |
| Profiler header | Still calls calibration a **LOWER bound**. | Contradicts the corrected documentation; remove it. |
| `belt_watchdog.py::cpu_rate` | Uses PID-only identity and wall-clock deltas. | Its CPU trend can cross PID reuse or clock adjustment. |
| `belt_watchdog.py::gather` | Process CPU above 0.7 cores is described as a main-thread tight loop. | Unsupported attribution already reaches owner-facing output. |
| Belt log diagnosis | Tail repetition can yield `WEDGED`; quiet logs can yield `STALLED`. | Observations can overstate game failure. Health collection should preserve evidence without inheriting these causal conclusions. |

The writer, watchdog, stage accumulator, and reader implementations are not supplied here, so their current behavior cannot be re-audited from this material.

## 3. Expansion: missing metrics

All proposed costs below are planning estimates. **E** = external sampling; **C** = cheap cached/main-thread counts; **D** = bounded diagnostic capture; **O** = offline analysis. Exact engine fields or hooks not present in the attachments must be resolved against installed source before implementation.

### 3.1 CPU, contention, workers, and bridge activity

| Missing metric | Capture method | Cost/cadence | Attributability and usefulness |
|---|---|---|---|
| **Main-thread CPU/wall ratio** | External thread CPU delta over the same recorded interval | E, 1–5 s | Separates substantial execution from substantial nonexecution; does not itself identify waiting versus descheduling |
| **CPU of other game threads** | Per-thread CPU deltas; periodically retain top threads | E, 5 s, measured enumeration cost | Locates worker-heavy sessions; names/start addresses are clues, not subsystem attribution |
| **Thread ready time versus wait time** | Bounded Windows scheduler trace | D, explicit duration | Distinguishes CPU deprivation from blocking; far stronger than low CPU alone |
| **Context switches and wakeup dependency** | Same trace; inspect main thread and readying threads | D | Helps locate worker completion, locks, and excessive wakeups |
| **Wait-chain evidence** | Windows Wait Chain Traversal at prolonged silence | E/D, one bounded attempt | Can expose supported synchronization chains; unsupported primitives and incomplete access remain unknown |
| **Worker schedule-to-complete latency** | Instrument a verified schedule/complete boundary for a selected subsystem | D; own code first | Measures latency and main-thread waiting, not worker CPU unless separately instrumented |
| **Own background queues** | Queue length, oldest work age, completion/error counts in our mods | C, snapshot every window | Strong attribution to our subsystem; explains backlogs that thread CPU cannot |
| **Bridge queue latency** | Timestamp request received, queued, execution start/end, response completion | C, aggregate per tool/category | Distinguishes bridge starvation, expensive tools, and transport delay |
| **Bridge main-thread occupancy** | Interval union of bridge execution scopes | C | A call count alone misses one expensive call |
| **Outstanding/cancelled bridge work** | Pending count, oldest age, timeout/cancellation, work completed after caller timeout | C | Identifies hidden observer load and abandoned work |
| **Per-thread CPU distribution change** | Compare stable thread identities across healthy/slow intervals | E | Detects a new busy background mod thread or worker behavior change |

Windows WPR/WPA explicitly supports CPU and wait analysis. Managed JIT symbolization is a separate limitation, not a reason to discard scheduler evidence. [WPR/WPA analysis](https://learn.microsoft.com/en-us/troubleshoot/windows-server/support-tools/support-tools-xperf-wpa-wpr).

Wait Chain Traversal cannot prove the absence of deadlock when a synchronization element is unsupported. [Wait-chain limitations](https://learn.microsoft.com/en-us/windows/win32/api/wct/nf-wct-getthreadwaitchain).

### 3.2 Simulation workload and pathological churn

| Missing metric | Capture method | Cost/cadence | Attributability and usefulness |
|---|---|---|---|
| **Tick-duration distribution** | Add a fixed histogram to existing whole-tick timing | C; reuse timestamps | Finds broad slow ticks versus rare pathological ticks |
| **Actual cap/budget exit reason** | Inspect installed tick-loop branches; diagnostic branch instrumentation if necessary | D unless an existing field exists | Establishes which limiter actually stopped ticking; requires a validated hook/transpiler |
| **Tick-list growth and registration churn** | Population snapshots plus registration/removal deltas where safe | C counts; D hooks | Finds duplicate registration and spawn/despawn storms |
| **Rare/Long bucket imbalance** | Occupancy distribution across their scheduling buckets | C, bounded minute census | Equal total population can produce different spike patterns |
| **Things actually dispatched** | Count dispatches by category; detailed Def/type counts only during capture | D or existing coarse scope augmentation | Distinguishes list population from executed workload |
| **Per-map simulation cost** | Key existing map-stage timings by bounded map slots | C if measured affordable | Explains a hidden second map consuming TPS; no mod blame |
| **Pawn workload composition** | Bounded census: spawned/world, humanlike/animal/mech, active/downed, selected job classes | C/D, minute or requested | Raw pawn count is a weak normalizer |
| **Repeated job failure/churn** | Bounded top offenders by pawn/job signature; count failure reasons | D, or low-cost counters after validation | Strong lead for instantaneous job loops; originating mod still needs trace evidence |
| **Path request complexity** | Requests, retries, failures, path length/node work if verified accessible | D | Request count alone misses expensive searches |
| **Passability/region invalidation pressure** | Dirty-work population, rebuild frequency, pending-work age where accessible | C snapshots/D hooks | Connects terrain-changing mods to repeated recomputation |
| **World workload growth** | World component, caravan, quest, faction, and relevant retained-pawn counts | C/D after getter audit | Explains slow sessions with ordinary current-map counts |
| **Own algorithm work units** | Cells scanned, candidates examined, cache hit/miss, retries, queue age in our code | C | Often more actionable than generic method timing; directly attributable |

There may be **no distinct “AI worker thread.”** Do not invent that model. Some AI work may remain on the main thread while Unity workers service pathfinding, glow, drawing, or unrelated jobs.

### 3.3 Reload accumulation, memory, and rendering

| Missing metric | Capture method | Cost/cadence | Attributability and usefulness |
|---|---|---|---|
| **Harmony topology changes** | Baseline plus delayed/bounded census after selected lifecycle boundaries | D, menu/maintenance | Finds patch accumulation that a once-per-session census misses |
| **Duplicate patch registrations** | Compare target + kind + owner + patch method + ordering metadata | D/O | Names registration evidence; duplicates are not automatically erroneous |
| **Loaded assembly growth** | Snapshot assemblies and stable identity metadata | D, boundaries | Detects dynamically loaded assemblies across reloads; not equivalent to leaked managed objects |
| **Def-count changes by database/type** | Startup baseline and controlled boundary snapshots | C/D | Detects unexpected runtime Def accumulation; persistent startup Defs are normal |
| **Graphic/material variant growth** | Cache counts plus bounded key/type summaries | C count/D details | Distinguishes expected first-use warming from repeated unique recolor/material creation |
| **Native material/render-target growth** | Validated counters if available; explicit requested Unity-object census otherwise | D | Mesh/texture-only tracking misses other native graphics resources |
| **Known cache sizes in our mods** | Count, capacity, hits/misses, evictions, entries associated with retired maps | C | Strong attribution without general heap introspection |
| **Retired-map survival** | Carefully managed weak-reference probes for known maps, checked after later natural collections | C/D | Evidence of survival, not proof of a leak or retaining root |
| **Recorder-retained references** | Audit/report queues, profile keys, closures, and bounded object references | C/O | Ensures telemetry does not manufacture the suspected leak |
| **Post-natural-GC occupancy** | Associate occupancy samples with collection-count changes | C | Better trend baseline than arbitrary pre-GC snapshots; collector semantics remain qualified |
| **Displayed frame pacing** | External presentation capture such as PresentMon | D initially; possibly E after validation | Separates update cadence from displayed frames, dropped presentation, and display latency |
| **Render workload context** | Current map, zoom, visible area, overlays, weather/effects, selected UI panels | C, change/window | Provides matched rendering comparisons |
| **Resolution/camera sensitivity** | Controlled paused/unpaused comparisons at two resolutions and zoom levels | D experiment | Helps test GPU/rendering hypotheses; sensitivity alone is not definitive proof |

PresentMon provides external CPU/GPU/display timing through Windows graphics-event analysis; validate available fields and overhead on this hardware/API. [PresentMon project](https://github.com/GameTechDev/PresentMon).

### 3.4 OS, I/O, startup, stability, and reproduction

| Missing metric | Capture method | Cost/cadence | Attributability and usefulness |
|---|---|---|---|
| **System commit headroom** | Committed bytes and commit limit | E, 5–30 s | More useful for allocation-failure risk than process working set alone |
| **Available physical memory** | OS counter | E, 5–30 s | Detects system pressure despite a stable game heap |
| **Process memory peaks** | Peak private/working-set values where source supports them | E | Preserves transient pressure missed by coarse current-value sampling |
| **Hard-fault timing and backing file** | Bounded memory/I/O trace | D | Distinguishes disk-backed faults from soft faults and pagefile versus mapped-content reads |
| **Storage latency and file attribution** | OS disk/File I/O trace around a reproducible event | D | Distinguishes save, log, mod content, recorder, and unrelated storage activity |
| **Log bytes per tick and per second** | Incremental external tail plus tick intervals | E/O | Quantifies spam exposure; byte rate still does not measure its CPU cost |
| **Logging elapsed time** | Selected logging-scope diagnostic timer, guarded against recursion | D | Measures elapsed logging residence; caller message construction outside the scope remains excluded |
| **Logger/cap/reset epochs** | Main-thread state snapshot and observed state changes | C | Prevents zero log emission from being interpreted as no errors |
| **Startup progress versus bridge readiness** | External process identity plus independent landmarks | E | Reports “loading; companion absent” rather than missing game-health coverage |
| **Cold-load CPU/I/O/memory trajectory** | External time series from process start | E | Can locate CPU-heavy versus I/O-heavy silent stretches without verbose logging |
| **Cache state of benchmark launch** | Record launch order, machine state, previous launch, cache treatment | O metadata | Prevents warm-cache improvements from being credited to a mod change |
| **Reproduction identity** | Save hash, seed/generator identity, mod content/settings hashes, machine/build identity | O + cheap references | Makes a vanished slow session reproducible |
| **Save physical growth versus content growth** | File size plus streaming offline section/type census | E/O | Separates more serialized objects from encoding/compression effects |
| **Exit code and crash evidence** | Observer holds process handle; capture exit and associated WER/crash artifacts | E | Distinguishes observed exit from inferred crash |
| **Observer health** | Collector heartbeat, sample duration, failed probes, missed deadlines, trace loss, disk usage | E | Required before trusting external gaps |
| **Power/thermal/CPU-frequency context** | Validated OS/vendor sources, capability-gated | E/D | Detects throttling or power-plan changes; reported frequency is not necessarily effective throughput |
| **Antivirus/indexer/storage competition** | Process/I/O evidence during bounded capture | E/D | Explains external competition without falsely blaming a game scope |

For reproduction snapshots, do not automatically force a save during a stall. It changes workload, can take a long time, and may overwrite useful state. Record the last existing save identity first.

## 4. Re-ranking and cost-budget discipline

### 4.1 Ranking all 100 candidates

**MUST** means necessary for trustworthy forensic coverage. It does not mean every source runs every frame. **SHOULD** includes valuable bounded diagnostics. **COULD** means capability- or question-dependent. **SKIP** means the proposed implementation or inference should not ship.

The corrections in section 2 apply throughout this table.

| Family | MUST | SHOULD | COULD | SKIP |
|---|---|---|---|---|
| Memory | **M1, M2, M6, M11** | **M5, M7, M10, M12, M13** | **M3, M4, M8, M9, M14, M15** | Heap-delta allocation/blame; reserved-minus-used fragmentation |
| Graphics | **G1, G2, G13, G14, G15** | **G3, G4, G6, G11** | **G5, G7, G8, G9, G10, G12, G16, G17** | Additive invalid frame partition; unavailable GPU values presented as zero |
| Load | **L1, L14** | **L2, L3, L7, L8, L11, L12, L13, L15, L16** | **L4, L5, L6, L9, L10** | Constructor time presented as Harmony time; Boolean no-match verdict |
| Simulation | **S1, S2, S18** | **S4, S5, S7, S8, S10, S12, S16, S17** | **S3, S6, S9, S11, S13, S14, S15** | Generic automatic mod blame |
| I/O/log | **I1, I2, I4, I5, I8** | **I3, I6, I7** | **I9** | Unlimited per-message hashing/rows/stack capture |
| Stability | **X1, X2, X7** | **X3, X5, X6, X8** | **X4, X9** | **X10** via thread suspension/in-process foreign-thread stack extraction |
| Process/OS | **P1, P2, P4, P7** | **P3, P5** | **P6** | Total faults called hard faults; process CPU called main-thread CPU |
| Environment | **V1, V2, V3, V4, V5, V6, V7** | **V8** | — | Unqualified verdicts from focus/log silence alone |

Clarifications:

- **M3:** retain GC coincidence now; exact pause duration remains experimental.
- **M4:** the proposed heap APIs do not implement it. Only a validated allocation source qualifies.
- **M13:** retain boundary observations; forced collection belongs only in an explicitly isolated diagnostic experiment.
- **M14:** a targeted audit of known cache fields is reasonable. A general recursive static-heap scanner is not a weekend feature.
- **S6:** tightly scoped callback timing may be useful; a general “per-Harmony-owner cost” report is misleading.
- **X9:** requires demonstrated diagnostic value before automation.
- **P5:** ordinary total-fault counts are useful context after renaming; actual hard faults need a different source.

### 4.2 Revised always-on tiers

| Tier | Default content | Budget principle |
|---|---|---|
| **Frame hot path** | Existing heartbeat; update-interval histogram; numeric state; reuse existing tick timestamps | No per-frame formatting, reflection, collection enumeration, locks shared with I/O, or steady-state allocation |
| **Five-second band** | Histograms, cached context, log counters, capability/coverage, bridge occupancy | Bounded snapshots; serialization budget measured separately |
| **Minute/boundary context** | Audited constant-time counts; bounded map slots; cache/ticker populations; context changes | Incremental work with per-frame deadlines; expensive getters excluded |
| **External baseline** | Process/main-thread CPU, process/system memory, I/O context, log growth, observer health | Persistent collector; independently measured observer cost |
| **Diagnostic capture** | Selected component, path, graphics, scheduler, memory investigations | Explicit target count, duration, byte budget, coverage and overhead status |
| **Offline** | Load tree, save census, attribution joins, content hashes | Avoid competing with active play unless requested or scheduled safely |

A minute budget of “2 ms once a minute” is an amortized budget, not a hitch limit. Likewise, “50 ms at an incident” can materially worsen the event. Enqueue minimal evidence first, then defer heavy work; mark it as **post-incident capture**.

### 4.3 Realistic cost estimates

These are deliberately broad **PLAUSIBLE planning ranges**, not measured limits.

| Operation | Planning estimate |
|---|---:|
| Add one histogram observation using an existing timestamp | Sub-microsecond to a few µs |
| One contained Harmony timer pair with modest accounting | Roughly 0.5–5 µs; potentially worse with phase publication or runtime effects |
| Five such invocations per frame | Roughly 3–30 µs, before other collection/emission work |
| Twenty such invocations per frame | Roughly 10–100 µs |
| Bounded five-second snapshot/serialization | Roughly 0.1–2 ms; allocation and lock behavior can dominate |
| Constant-time minute counters | Potentially tens/hundreds of µs |
| Copying/enumerating population-dependent collections | No defensible fixed bound without population measurements |

The existing profiler’s cost scales with **ticks × maps × stage invocations**, not simply frames. At high TPS it can dominate the incremental graphics instrumentation.

Keep the proposed **0.1 ms average main-thread/frame** as a provisional total budget, but add:

- p99 collection/emission latency;
- maximum introduced hitch;
- total recorder CPU across threads;
- allocation rate across all recorder threads;
- GC changes;
- I/O and queue-age limits.

Do not claim that 0.1 ms is a fixed percentage of the tick budget. Frame rate, tick rate, and tick batching change the denominator.

### 4.4 Measuring observer overhead on 600 mods

Use independently measured endpoints; recorder-off cannot provide its own performance baseline.

**Configurations:**

| Configuration | Purpose |
|---|---|
| C0: recorder and external collector off | Reference |
| C1: external collector only | External observer effect |
| C2: existing sampler without attribution + collector | Sampler/writer/watchdog cost |
| C3: existing full recorder + collector | Existing coarse profiler increment |
| C4: C3 + minimal health bands | Proposed low-cost extension |
| C5: C4 + optional frame-stage hooks | Frame instrumentation increment |
| Separate named diagnostic runs | Cost and usefulness of each deep-capture family |

Keep the baseline measurement harness identical across configurations. A stopped timer body with hooks still installed measures only part of the cost; it is not an unpatched baseline.

**Workloads:**

- demanding colony at high speed, where throughput is uncapped;
- normal-speed play;
- paused rendering at matched zoom;
- multiple maps;
- selected path/rebuild-heavy scenario;
- controlled logging storm in disposable state;
- save/load and repeated map/game transitions.

**Protocol:**

1. Freeze mod content/settings, save, camera, focus, frame cap, speed, and bridge workload.
2. Declare warm-up and measurement endpoints in advance.
3. Reload the same initial save per run; record remaining nondeterminism.
4. Counterbalance configuration order across independently restarted sessions.
5. Use repeated runs—initially at least four per important comparison—and increase repetitions if uncertainty remains too large.
6. Measure fixed-tick completion time, update/presentation distribution, CPU, memory/GC, recorder allocations where measurable, bytes written, and queue latency.
7. Report uncertainty and paired differences; retain outliers with explanations.
8. Repeat external tracing consistently if it supplies an endpoint.

With 15-minute cold loads, this is a **multi-day experiment**, not a one-hour acceptance check.

A reasonable **proposed** acceptance target for the minimal extension is an upper confidence bound below 1% throughput regression, average added main-thread work below 0.1 ms/frame, and no reproducible telemetry-created hitch above the declared deadline. If measurement uncertainty exceeds the budget, the result is **inconclusive**, not PASS.

## 5. Capture failure modes and stability

| Failure mode | Required containment |
|---|---|
| **Telemetry throws inside ticks** | Guard the entire hook, including thread checks and cleanup. Preserve original exceptions. Disable that band and emit one bounded error through the recorder—not recursive game logging. |
| **Original/another patch throws** | Per-invocation state plus finalizer cleanup. Record incomplete scope coverage; do not leave phases or timers open. |
| **Prefix skipped/original skipped** | Explicit started state and execution semantics. Do not present wrapper elapsed time as original-method execution. |
| **Reentrant invocation** | Per-invocation state and supported nesting. Reject unsupported nesting rather than overwrite global start/tick IDs. |
| **Worker-thread invocation** | Reject before touching stage/game state. Thread-safe counters must have a separately documented collection path. |
| **Runtime patch rebuild** | Exact target allowlist; no blanket `PatchAll`; install transaction/status; measured arm/disarm latency; compatibility test with actual patch chains. |
| **Timeout while main thread hangs** | A watchdog can set an atomic inactive flag; physical unpatching waits for a safe main-thread boundary. State that dispatch remains installed until then. |
| **Log-event concurrency** | Atomic counters and bounded aggregation. No game API, mutable game collection, stack extraction, string normalization, or unbounded dictionary in the callback. |
| **Long/unique error messages** | Hash/sample only within a declared character and rate budget; report truncation, sampling, collisions/overflow, and unclassified counts. |
| **Unity API from watchdog** | Use a cached immutable/versioned snapshot. Do not assume every Unity API has the same thread rules; restrict background use to specifically documented-safe sources. |
| **Managed watchdog blocked by GC** | External coverage remains independent; missing managed heartbeat is not a GC diagnosis. |
| **Collection changes during sliced census** | Record collection generation/coverage or label the result approximate. Spreading a walk over frames does not create an atomic snapshot. |
| **Recorder creates a leak** | Avoid retaining Things/maps/pawns in long-lived keys, queues, or closures. Store stable identifiers and bounded primitive snapshots. |
| **Disk stalls/full volume** | Main thread only submits bounded work. Bound outstanding bytes and age; stop bulk capture first; retain critical reserve and report loss. |
| **Critical storm exhausts reserve** | Open/close critical events; intermediate updates are coalescible bulk. A reserve is finite, not a durability guarantee. |
| **Profiles/dumps evict TPS history** | Independent artifact caps and retention; compact references in the main stream. |
| **Observer fails or sleeps** | Observer heartbeat and explicit coverage holes. No game-exit claim after a failed process probe. |
| **Dump worsens memory pressure** | Free-space/headroom checks, one capture per incident, timeout, measured clone behavior, partial-artifact status. |
| **Shutdown races producers** | Stop/seal collection, snapshot status, drain with monotonic deadline, and record completion truthfully. |
| **Capture interferes with saves** | Observe verified completion; perform `FileInfo`/hashing off-main. Tie size to the actual completed save artifact, not merely a reusable filename. |

Interaction with TPS needs particular care:

- A health-band failure should not disable otherwise sound TPS sampling.
- New bulk rows must not break existing continuity logic accidentally.
- Actual missing samples or writer loss must still break continuity.
- Process-scoped counters must survive game boundaries; game/map counters must not.
- Historical queries must distinguish cached state at the incident from state collected after recovery.
- Profile arming, configuration changes, and observer operations need explicit events, so comparison windows are identifiable.

“One writer” remains correct for ordered in-process evidence. The external observer should keep its independently ordered stream, with its own sequence, collector identity, process identity, and correlation anchors.

## 6. Options critique, sequencing, and acceptance

### 6.1 Options A–D, plus E

| Option | Assessment |
|---|---|
| **A: health line** | Best in-process direction, but scope is too broad for “low risk.” Includes unvalidated memory sources, private getters, concurrent logging, stage timing, and main-thread CPU integration. Split minimal bands from optional stage hooks. |
| **B: tiered recorder** | Useful destination, poor initial commitment. Generic Harmony attribution, leak scanning, and automatic dumps each need separate feasibility/safety work. Its “nearly everything answered” claim overstates causal attribution. |
| **C: load/profile only** | Good for named optimization questions; does not address unobserved solo-play incidents. Its generic profiler risk is understated. |
| **D: external only** | Best first forensic improvement. Replace repeated PowerShell/WMI launches with persistent collection. Add observer coverage and process identity. External collection still requires overhead acceptance. |
| **E: early load probe** | Justifiable only after ordinary/verbose/external evidence identifies the missing phase. “Top of load order” does not guarantee capture of phases already executed before its constructor. Validate reachability before writing hooks. |

E also contradicts the “one writer” principle by proposing direct load JSON output. It needs an explicit handoff/protocol and bounded load-safe writer, rather than ad hoc append behavior.

### 6.2 Better option F

**F: evidence-first health recording**

1. Persistent Windows observer with independent lifecycle and coverage.
2. Minimal TPS extension reusing existing timestamps and snapshots.
3. Capability-gated release-player counters.
4. Offline load/save analysis.
5. Direct optional instrumentation in our mods.
6. Validated named diagnostic captures for unresolved questions.
7. Early load instrumentation or dump automation only when a feasibility experiment demonstrates value.

This preserves useful standing evidence while keeping uncertain runtime capabilities outside the default path.

### 6.3 Phased plan

| Phase | Deliverable | Acceptance gate |
|---|---|---|
| **0. Establish contracts and baseline** | Source registry, scope/unit definitions, exact installed Unity/Mono/Harmony identity, current TPS runtime acceptance | Existing correctness tests and full-load MUST 17 pass; visible hazards in section 2.3 are resolved or explicitly excluded by enforced guards |
| **1. External standing evidence** | Persistent process/thread/system collector; incremental log observation; startup milestones; observer heartbeat | Survives login/relaunch; records hangs and exits without bridge calls; handles probe failure, two processes, PID reuse, sleep, rotation, and disk failure; measured observer overhead |
| **2. Minimal health extension** | Update histogram, log coverage/counts, bridge occupancy, audited population/context snapshots | Correct intervals and lifecycle; bounded allocations/bytes; reader handles unavailable sources; full-load incremental overhead passes |
| **3. Offline forensics** | Load-tree parser, save census, content identity, historical correlation | Parses actual archived outputs; distinguishes truncated/incomplete trees; preserves thread/tree identity and does not double-count nested phases |
| **4. Named optimization tools** | Own-code counters; selected component/graphics/path/scheduler captures | Target coverage demonstrated; overhead separately measured; exceptions and skips handled; expiration/disarm tested |
| **5. Conditional capabilities** | GC timing spike, early load probe, small-dump automation | Each demonstrates useful evidence on a known case before becoming available by default |

### 6.4 Acceptance criteria that cannot pass while defects exist

Acceptance should be a conjunction of explicit gates, not “the health report looked plausible.”

| Gate | Required evidence | Automatic failure |
|---|---|---|
| **Source truth** | Exact source, units, availability, and capability record | Unsupported/unvalidated value reported as a valid zero |
| **Serialization** | Production envelope composition, strict parse, versioned validation | Duplicate keys, nonfinite values, giant unbounded rows, ambiguous discriminator |
| **Interval correctness** | Long current invocation, boundary-crossing scope, clock changes, async work | Misplaced measurement, double-credit, fabricated residual |
| **Histogram correctness** | Known traces, bucket-edge cases, long stalls, merged windows | Precise quantile unsupported by bucket resolution; averaged p99s |
| **Logging correctness** | Concurrent storm, cap, logger-disabled, resets, long/unique messages | Suppressed emission displayed as no error activity; unbounded callback work |
| **Harmony safety** | Skip, original exception, postfix exception, recursion, worker call, missing target, failed installation | Telemetry changes original exception behavior or claims unsupported coverage |
| **Lifecycle** | Menu, failed load, second game, map removal, active capture during transition | Cross-game timing/key carryover or erased process accumulation |
| **Writer isolation** | Bulk flood, blocked disk, oversized artifact, kill during append | Queue byte bound exceeded, critical loss hidden, profile output evicts required evidence |
| **Observer truth** | Multiple processes, PID/TID reuse, failed probes, sleep/resume, collector restart | Failed observation interpreted as exit, deadlock, GC, or mod fault |
| **Retention** | Measured bytes/day, overlapping active sessions, artifacts, cap pressure | Claimed horizon exceeds actual retained coverage; metadata silently orphaned |
| **Cost** | Counterbalanced full-load configurations and declared limits | Budget exceeded, uncertainty too large, or only timer-body toggle tested |
| **Overnight utility** | Documented induced slowdown, exit/relaunch, next-day historical reconstruction | Wrong process/game/time, omitted incident, absent linked evidence, or unsupported cause |
| **Optional capture utility** | Known diagnostic case produces actionable evidence | Dump/profile merely creates a large artifact without identifying the known condition |

Also require explicit **PASS / FAIL / UNMEASURED / UNSUPPORTED** status per capability. Partial installation cannot become a global “health capture complete.”

Do not accept semantic correctness through C#/Python parity alone. Both can agree on the same wrong measurement model.

## 7. What I would build first in one weekend

1. **A persistent Windows observer:** process identity, process/main-thread CPU where available, working set/private memory, system memory/commit headroom, log growth, and its own coverage heartbeat.
2. **A histogram using existing frame timestamps:** count, total duration, maximum, threshold counts, and approximate quantile ranges. No new stage hooks initially.
3. **Log counts plus suppression state:** emitted error/warning/message totals, cap/logger coverage, bounded storm open/close events.
4. **Bridge occupancy and queue-delay markers:** distinguish agent-induced load from owner-only play.
5. **A read-only capability inventory:** exact engine version, collector mode, validated recorder counters, unavailable-source reasons.
6. **A compact offline health timeline:** join these observations to existing TPS incidents; print evidence and uncertainty without automatic mod blame.

I would defer generic per-Harmony profiling, forced-GC leak tests, broad object/static scans, automatic dumps, and the early load mod. The weekend deliverable should remain experimental until the existing recorder and incremental full-list overhead gates pass.