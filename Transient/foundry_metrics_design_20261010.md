# Game-health metrics beyond TPS: design pass (FOUNDRY, 2026-10-10)

Offline design only; nothing built, nothing measured live. Engine claims tagged **VERIFIED** were read in the
decompiled 1.6 source through RimSage this session (file named). **UNVERIFIED** means reasoned, not read:
a Unity behaviour, a Windows API detail, or a cost guess. Costs in µs/ms are estimates unless stated.

## 1. Why / intent, and what TPS taught us

**Intent.** The owner wants the bridge companion to report game *health*, not just speed: memory, rendering,
load delays, error storms, stability — continuously, so "it was slow / it ate 20 GB / that load took 40 min
last night" can be answered after the fact, and so a mod we ship can be shown to cost X before he finds it.
Two jobs, different shapes: **(a) incident forensics** (what was the game doing at T) and **(b) mod
optimisation** (which mod, which code path, how much). (a) wants cheap, always-on, coarse; (b) wants
expensive, attributable, on demand.

**What TPS taught us (each lesson is a rule for every metric below):**

| TPS lesson (Opus + two GPT reviews, 35 findings) | rule for new metrics |
|---|---|
| Sampler only started on a `jawa/` call → owner's solo play unrecorded | every always-on metric rides the **bridge-registration** autostart (`JawaBenchTpsTools` ctor); anything needing earlier start (cold-load phases) cannot live in the companion at all — see §2.C |
| 60 s stalls discarded; hangs left no row | **never drop the extreme**; extreme values are the product. Record max and incident rows, not just means |
| Endpoint normalisation (multiplier read once) gave false SUSTAINED LOW | integrate per frame against the state actually in force; carry ambiguity explicitly (`expectedLo`) rather than guessing |
| Thread-pool writes out of order; non-commit-aware retry | reuse the **one ordered bounded writer** (`JawaBenchTpsWriter`), its seq numbers and critical-row reserve; never a second writer |
| State leaked across games | everything game-scoped resets at the `game` boundary; every row carries `session` + `game` |
| Profiler prefixes skippable / postfix without prefix → garbage durations | prefix + **finalizer**, `__state`, `profSkipped`, main-thread check, disable-on-exception, install rollback |
| GC watchdog limits: a managed thread cannot run during stop-the-world GC | in-process watchdog is blind during GC and full-process suspension; anything that must see those needs an **external observer** |
| Observer cost "trivial" was asserted, never measured (MUST 17 still owed) | every tier ships with a declared budget and is accepted only after an on/off A/B on the full list |
| `tickMs` (lagged EMA) was read as attribution | engine smoothed values are **context, never evidence** |
| "Why" from scope time is a lead, not a verdict | elapsed scope time includes GC, scheduler deprivation and I/O; label hypotheses as hypotheses |

## 2. Hypothesis catalogue

Columns: **Source** (E = engine field/API, U = Unity API, H = Harmony hook we add, O = OS/process, L = log
parse, X = external process). **Res** = natural resolution. **Attr** = can it name one mod? (Y / P = partial,
via type→assembly→packageId or Harmony owner / N).

### 2.A Memory

| # | metric | source & how | res | attr | helps debug |
|---|---|---|---|---|---|
| M1 | managed heap in use | E/.NET `GC.GetTotalMemory(false)` (already in `heapMB`) | per window | N | leaks, heap growth before a GC storm |
| M2 | GC collection count + delta per window | `GC.CollectionCount(0)` (already `gc`); Boehm, no generations | per window | N | GC-bound slowness; rate rising = churn |
| M3 | GC pause duration | **no managed API on Unity Mono/Boehm** (UNVERIFIED); approximations: frame gap coinciding with `gc` delta; `Unity.Profiling.ProfilerRecorder` "GC.Collect" marker if it works in a release player (UNVERIFIED) | per incident | N | "was that hitch GC" — the big open question TPS could not answer |
| M4 | managed bytes allocated (rate) | U `Profiler.GetMonoUsedSizeLong` / `GetMonoHeapSizeLong` (UNVERIFIED that values are live in a non-development player); or ProfilerRecorder "GC Allocated In Frame" (dev builds only, UNVERIFIED) | per window | N | allocation churn per scenario; regression of our mods |
| M5 | reserved vs used heap (fragmentation) | U `Profiler.GetMonoHeapSizeLong` vs `GetMonoUsedSizeLong`; Boehm never returns memory to OS (UNVERIFIED) | per minute | N | "heap is 6 GB but 2 GB used" — fragmentation after map loads |
| M6 | process working set / private bytes / commit | O `Process.WorkingSet64` (already in `context`), `PrivateMemorySize64`, `PagedMemorySize64` | per minute | N | total footprint, native leaks, page-file thrash |
| M7 | native Unity memory (total allocated/reserved) | U `Profiler.GetTotalAllocatedMemoryLong`, `GetTotalReservedMemoryLong` (UNVERIFIED in release) | per minute | N | native vs managed split: is growth textures or C# |
| M8 | texture memory / count | U `Texture.currentTextureMemory`, `Texture.totalTextureMemory`, `Resources.FindObjectsOfTypeAll<Texture2D>().Length` (the last is **expensive**, seconds on 600 mods) | on demand | P (texture name→mod folder) | VRAM pressure; a mod shipping 4K textures |
| M9 | mesh count / memory | U `FindObjectsOfTypeAll<Mesh>` (expensive); MapDrawer section meshes estimable from map size | on demand | N | MapMesh leaks across map loads |
| M10 | GraphicDatabase size | E `GraphicDatabase.allGraphics` (private static dict, VERIFIED `Verse/GraphicDatabase.cs:12`) count via reflection | per minute | P (graphic path → mod) | graphic cache growth: dynamic recolours creating unbounded graphics (a classic mod leak) |
| M11 | thing / pawn / world-pawn counts | E per map `listerThings.AllThings.Count`, `mapPawns.AllPawnsSpawnedCount`, `Find.WorldPawns.AllPawnsAliveOrDead.Count` (context row already has spawned pawns, things, world pawns) | per minute | P (by def→mod) | world-pawn bloat, filth/item explosion, spawn loops from our mods |
| M12 | thing counts by def (top N) | E walk `listerThings` by def → `def.modContentPack.PackageId` | on demand / hourly | **Y** | which mod spawns the 40,000 things |
| M13 | heap delta across map unload / game reload | M1/M6 sampled at `menu`/`game` boundaries after a forced `GC.Collect` (on demand only) | per boundary | N | leaks surviving a return-to-menu (static caches holding Map) |
| M14 | static-cache retention suspects | reflection scan of static fields of mod assemblies holding `Map`/`Pawn`/collections, sized | on demand | **Y** | the leak culprit after M13 shows one |
| M15 | Unity object count (all) | U `FindObjectsOfTypeAll<Object>` (very expensive) | on demand | N | material/texture leaks from runtime `new Material` |

### 2.B Graphics / frame

| # | metric | source & how | res | attr | helps debug |
|---|---|---|---|---|---|
| G1 | FPS | frames per window (already `fps`) | window | N | frame-bound slowness |
| G2 | frame-time p50/p95/p99/max | Stopwatch between `Root.Update` prefixes, bucketed into a fixed log-histogram (no per-frame allocation) | window | N | stutter that a mean hides; p99 is what the owner *feels* |
| G3 | frame split: tick vs map-update vs draw vs GUI | H timers on `Game.UpdatePlay`'s children: `TickManagerUpdate` (have), `Map.MapUpdate`, `MapDrawer.MapMeshDrawerUpdate_First`, `DynamicDrawManager.DrawDynamicThings`, `UIRoot_Play.UIRootOnGUI` | window | N (P via MapComponentUpdate) | "frame-bound" hypothesis made concrete: which half of the frame |
| G4 | section regeneration count + time | H on `Section.RegenerateDirtyLayers` (private, VERIFIED `Verse/Section.cs:149`) / `SectionLayer.Regenerate` per layer type | window | P (layer type → assembly) | MapMesh churn: a building toggling graphics every tick re-dirties its section each frame |
| G5 | dirty-mark rate by flag | H prefix on `MapDrawer.MapMeshDirty` (UNVERIFIED signature) counting `MapMeshFlagDef` | window | P (caller unknown without stack) | which change type drives regen (Things vs Terrain vs Snow vs our liquids/FlowWorks overlays) |
| G6 | "AlwaysRedrawShadows" whole-map invalidation | E `Map.AlwaysRedrawShadows` → `WholeMapChanged(Things)` every update (VERIFIED `Verse/Map.cs` MapUpdate) | flag per window | N | a pathological setting that regenerates every Things layer every frame |
| G7 | dynamic things drawn | E `DynamicDrawManager` (uses Unity Jobs, VERIFIED `Verse/DynamicDrawManager.cs:7`) count of drawn things | window | P | pawn/animal crowd render cost |
| G8 | pawn graphics invalidations | H count on `PawnRenderer.SetAllGraphicsDirty` (VERIFIED `Verse/PawnRenderer.cs:671`; ~40 call sites) | window | P (declaring type of a Harmony-patched caller, else N) | apparel/gene/hediff mods re-resolving pawn graphics constantly |
| G9 | glow grid recompute | H on `GlowGrid.GlowGridUpdate_First` (VERIFIED called in MapUpdate; jobified `ComputeGlowGridsJob`) | window | N | light-source spam (our fire biomes, Pyrelands) |
| G10 | fleck/mote count | E `map.flecks` systems' active counts; mote Things in M11 | minute | P | particle storms (fire, weather) |
| G11 | draw calls / batches / SetPass | U `ProfilerRecorder` "Draw Calls Count", "Batches Count", "SetPass Calls Count" — documented as **available in release players for some render counters** (UNVERIFIED for RimWorld's 2022.3 build/renderer) | frame→window | N | GPU-side regression from shaders, unbatched materials |
| G12 | GPU frame time | U `FrameTimingManager` (needs player setting "Frame Timing Stats"; UNVERIFIED enabled) | window | N | GPU-bound vs CPU-bound |
| G13 | camera context: zoom, view rect size, current map, world view | E `Find.CameraDriver.RootSize` / `CurrentViewRect`, `WorldRendererUtility.WorldRendered` | window | N | normaliser: frame cost at max zoom-out ≠ zoomed in; essential to compare windows |
| G14 | overlays on (beauty, fertility, roofs, temperature…) | E `Find.PlaySettings` flags | window | N | overlay grids are expensive; explains outliers |
| G15 | resolution, fullscreen, vsync, target frame rate | U `Screen.width/height`, `QualitySettings.vSyncCount`, `Application.targetFrameRate`; RimWorld `Prefs` | session | N | FPS ceiling vs real bottleneck |
| G16 | world-map render & regen | H on `WorldRenderer` layer regeneration (`RegenerateDirtyLayersNow_Async`, long event, VERIFIED `WorldRenderer.cs:158`) | incident | N | world-view hitches; our planet layers (seabed) |
| G17 | texture atlas bake time | E `GlobalTextureAtlasManager.BakeStaticAtlases` (VERIFIED in PlayDataLoader), dynamic atlas rebuilds | incident | N | load time + pawn-atlas rebakes in play |

### 2.C Load / startup

⚠️ **Hard constraint (VERIFIED in `tps_record.md` §"What starts it"):** the companion is constructed by
RimBridgeServer *after play data loads*. So **nothing in the companion can time the cold load from inside**.
Load phases need one of: the engine's own `DeepProfiler`, a real early-loaded mod, or an outside observer.

**Engine fact, VERIFIED (`Verse/DeepProfiler.cs`, `ThreadLocalDeepProfiler.cs`, `LoadedModManager.cs`,
`PlayDataLoader.cs`, `MapGenerator.cs`, `SavedGameLoaderNow.cs`, `Map.cs`, `Game.cs`):** RimWorld already
wraps every load phase in `DeepProfiler.Start/End`, active **only when `Prefs.LogVerbose`**, and prints the
whole nested tree with self-times and a hotspot analysis to the log at the end of each top-level scope. It
covers: `LoadModContent`, `CreateModClasses` **per mod class** ("Loading <type> mod class" — where most
mods call `Harmony.PatchAll`), `LoadModXML`, `CombineIntoUnifiedXML`, `ErrorCheckPatches`, `ApplyPatches`,
`ParseAndProcessXML`, def copy, cross-ref resolution, implied defs, `StaticConstructorOnStartupUtility.CallAll`
(as **one** scope — no per-type split), atlas bake; save load (read file, load compressed things, spawn,
finalize geometry, `PostMapInit`, wealth recount); map generation **per GenStep**. ⇒ **the single cheapest,
highest-value load metric is "turn on LogVerbose for one load and parse the tree".** Cost: LogVerbose also
turns on other verbose logging (UNVERIFIED how much) and every `Log.Message` captures a stack trace.

| # | metric | source & how | res | attr | helps debug |
|---|---|---|---|---|---|
| L1 | cold load total wall time | X: process start time → first `Bridge token:` / first companion `session` row (both exist) | per load | N | the 15-min load trend over mod-list changes |
| L2 | cold load per-phase timeline | L: DeepProfiler tree with `LogVerbose` on; or X: tail `Player.log` from WSL stamping arrival time of known phase lines (Player.log lines carry **no timestamps**) | per load | P | which phase grew (XML patching vs defs vs textures) |
| L3 | per-mod `Mod` class ctor time | L: DeepProfiler "Loading <type> mod class" scopes (VERIFIED) | per load | **Y** | mods with heavy `PatchAll` / settings load |
| L4 | per-mod StaticConstructorOnStartup time | needs a transpiler on `CallAll` or an early mod; DeepProfiler gives only the total (VERIFIED) | per load | Y if built | the long silent stretch after "Initializing…" |
| L5 | per-mod XML patch time + op count | H on `PatchOperation.Apply` keyed by `sourceFile`/mod — **only from an early-loaded mod**; companion too late | per load | **Y** | our xpath-heavy patches (`//` xpaths cost seconds on 600 mods) |
| L6 | patches that matched nothing | same hook: `PatchOperation` result false; Conditional/FindMod return true on no-match (CLAUDE.md fact) | per load | **Y** | silent dead patches — a correctness metric that falls out of the timing hook |
| L7 | ConfigErrors / XML errors per mod | L: parse Player.log errors at load, map to packageId by def name / file path | per load | P–Y | load-time defect census per mod list |
| L8 | Harmony patch count & owners | E `Harmony.GetAllPatchedMethods()` + `GetPatchInfo` (session manifest already writes owners for measured targets) — extend to **all** methods once at registration | per session | **Y** | "mod X patches 400 methods incl. 30 hot ones"; hot-path patch density |
| L9 | Harmony patch install cost | early mod only (time `PatchAll` per owner) or L3 as proxy | per load | Y | load time owed to patching |
| L10 | texture/content load time per mod | DeepProfiler `LoadModContent` (per mod? UNVERIFIED granularity) | per load | P | 4K-texture mods |
| L11 | save load phases | L/DeepProfiler (`SavedGameLoaderNow`, VERIFIED) or H on `GameDataSaveLoader.LoadGame` + `Game.FinalizeInit` (companion is alive for in-session loads) | per load | P | "loading the canonical save takes 4 min" — which part |
| L12 | map generation per GenStep | DeepProfiler "GenStep - <def>" (VERIFIED `MapGenerator.cs:319`) or H on `GenStep.Generate` (companion OK) | per map | **Y** (GenStepDef→mod) | our biome gensteps, quicktest's 90 s |
| L13 | quicktest map wall time | X/bridge: tool call → `game` row | per test | N | the 90 s budget regression |
| L14 | save (autosave) duration + file size | `save` rows exist (seconds); add size from `FileInfo` after write | per save | N | save bloat from our Scribed comps (M11 growth) |
| L15 | save size by section | offline: parse `.rws` (existing `savemap.py`) — element counts per `Class`/def | per save | **Y** | which mod's ExposeData grows the save |
| L16 | time-to-first-interactive frame | menu `Root.Update` heartbeat already exists → first `menu` row | per load | N | Unity-side startup |

### 2.D Simulation

| # | metric | source & how | res | attr | helps debug |
|---|---|---|---|---|---|
| S1 | tick stages (have) | `attr` in TPS record | window | N | baseline |
| S2 | tick-list sizes by type | E `TickList.thingLists` buckets (private, VERIFIED `Verse/TickList.cs:10`) count per Normal/Rare/Long | minute | P (def→mod) | ticker explosions; things set to Normal that should be Rare |
| S3 | per-def tick cost | H on `Thing.Tick`/`DoTick` dispatch (1.6 name UNVERIFIED) keyed by def | **on demand only** | **Y** | the one def eating the Normal list |
| S4 | per-ThingComp-type tick cost | H on each overridden `CompTick`/`CompTickRare`/`CompTickLong` (enumerate concrete overrides by reflection; note Plant only gets `TickLong`, CLAUDE.md fact) | on demand | **Y** | our comps (`RM_CompVerminBreeder`, predation comps) |
| S5 | per-MapComponent / GameComponent / WorldComponent type cost | H on each overriding type's `MapComponentTick`/`MapComponentUpdate`/`GameComponentTick` (~hundreds of types on 600 mods) | on demand; the aggregate is S1 | **Y** | our MapComponents (`RM_MapComponent_*`) |
| S6 | per-Harmony-patch cost on hot methods | wrap patch methods themselves (time each prefix/postfix by owner) | on demand | **Y** (owner id) | the direct "which mod's patch costs X" answer — the mod-optimisation holy grail, and the riskiest hook |
| S7 | pathfinding: requests, ms, failures | H on `PathFinder.FindPath*` (1.6 PathFinder uses **Unity Jobs**, VERIFIED `Verse/PathFinder.cs`, `PathFinderJob.cs`): main-thread time is only schedule+complete; worker time invisible to main-thread timers | window | P (requesting job def) | path storms (blocked colony, our liquids changing passability) |
| S8 | region/room rebuild | H on `RegionAndRoomUpdater.TryRebuildDirtyRegionsAndRooms` (VERIFIED in MapUpdate) | window | N | terrain-edit churn (FlowWorks canals, pits) |
| S9 | ThinkTree / JobGiver cost | H on `Pawn_JobTracker.DetermineNextJob` / `ThinkNode_Priority.TryIssueJobPackage` (UNVERIFIED names) | on demand | P (JobGiver type→mod) | pawns re-thinking every tick; job-start-fail loops |
| S10 | job churn: jobs started/ended per pawn | H on `Pawn_JobTracker.StartJob`/`EndCurrentJob` counting; flag pawns > N jobs/s | window | P | the "job spam" signature (a JobDriver failing instantly) |
| S11 | WorkGiver scan cost | H on `JobGiver_Work.TryIssueJobPackage` per WorkGiverDef | on demand | **Y** | slow `PotentialWorkThingsGlobal` in our WorkGivers |
| S12 | alerts update cost | H on `AlertsReadout.AlertsReadoutUpdate` + per-`Alert` type (our `RM_` vermin alert) | on demand | **Y** | alerts are a known perf sink (run on UI, every N frames) |
| S13 | letters / messages rate | E `Find.LetterStack.LettersListForReading.Count`, `Messages` live count; H count on `Messages.Message` | window | P | message spam; often co-occurs with an error loop |
| S14 | lords / LordToil count | E `map.lordManager.lords.Count` | minute | P | stuck raids/lords never ending |
| S15 | storyteller / incident firing | H on `IncidentWorker.TryExecute` by def | event | **Y** | incident spam |
| S16 | worker-thread / job-system load | U job system has no public queue-depth API (UNVERIFIED); OS thread CPU (P4) is the proxy | minute | N | jobs (glow, path, draw) saturating cores |
| S17 | temperature / room / power net recalcs | H on `PowerNetManager.UpdatePowerNetsAndConnections_First` (VERIFIED in MapUpdate) | window | N | power net rebuild storms |
| S18 | game-speed context | multiplier, forced-normal, `NothingHappeningInGame` (have) | window | N | normaliser |

### 2.E I/O and log

| # | metric | source & how | res | attr | helps debug |
|---|---|---|---|---|---|
| I1 | errors / warnings / messages per window | H postfix on `Log.Error/Warning/Message` (or `Application.logMessageReceivedThreaded`) counting only | window | N | error storms; a stall that is really log spam |
| I2 | **log-cap reached** | E `Log.reachedMaxMessagesLimit` (private) — at **10,000** messages the engine sets `Debug.unityLogger.logEnabled = false` and the Player.log goes silent (VERIFIED `Verse/Log.cs:209-213`) | flag | N | **a session past the cap has a blind Player.log; every later log-based diagnosis is void** — must be a recorded fact |
| I3 | error rate by source mod | at error time, cheap: hash the message text, count per hash; resolve hash→mod offline from archived log (stack trace already in the log) | window + offline | **Y** offline | which mod is spamming; repeated-error dedup (`repeatsCapped`) |
| I4 | exception storm detector | I1 rate > threshold for N windows → incident row with top 3 message hashes | incident | P | "TPS halved because one NRE fires per tick" — every `Log.Error` costs `StackTraceUtility.ExtractStackTrace()` (VERIFIED `Log.cs`), so an error per tick **is** a TPS cost |
| I5 | Player.log size & growth rate | X: file size polled from WSL | minute | N | spam detection with the game hung; disk fill |
| I6 | first exception after load | L: already a rule in CLAUDE.md (read FIRST exception) — automate: archived log → first error + its mod | per load | P | load-failure triage |
| I7 | disk write bytes (process) | O `GetProcessIoCounters` (P/Invoke, Windows) or X `Get-Process`/WMI | minute | N | autosave/log I/O stalls |
| I8 | our recorder's own I/O | writer counters (have `wq`, `wdrop`…) + bytes written | window | n/a | observer cost |
| I9 | mod settings / config writes | H on `Mod.WriteSettings`, `Prefs.Save` | event | Y | settings thrash |

### 2.F Stability

| # | metric | source & how | res | attr | helps debug |
|---|---|---|---|---|---|
| X1 | stall / silence / hang (have) | TPS incidents, watchdog, observer | event | N | baseline |
| X2 | crash marker | X: process gone without `shutdown-complete` (have, `exited-without-shutdown`) + Windows Error Reporting / `crash_*` folder / `Player.log` tail scan for "Crash!!!" (UNVERIFIED marker text) | event | N | crash forensics |
| X3 | unhandled-exception count | `AppDomain.UnhandledException`, Unity `logMessageReceivedThreaded` type `Exception` | event | P | background-thread crashes |
| X4 | NRE count specifically | I3 filtered on `NullReferenceException` | window | P | regressions from our def changes |
| X5 | save size growth per in-game day | L14 against ticks | per save | N | save bloat trend |
| X6 | autosave duration trend | `save` rows | per save | N | autosave hitch getting worse with colony age |
| X7 | heap-at-incident | have (`heapMB`) | incident | N | memory pressure at hang time |
| X8 | ModsConfig reset detected | X: `ModsConfig.xml` active count drops to Core-only (the corrupted-mods recovery, CLAUDE.md incident 2026-09-27) | per launch | N | silent mod-list wipe |
| X9 | mini-dump on long silence | X: `procdump`/`MiniDumpWriteDump` from the external observer, rate-limited (GPT SHOULD 9) | incident | P (Mono stacks hard to read, UNVERIFIED tooling) | a real stack for a permanent hang |
| X10 | Mono thread stacks at silence | in-process impossible while main is blocked except via `Thread.Suspend`/`StackTrace(thread)` (obsolete/unsafe on Mono, UNVERIFIED) | incident | Y if it works | "blocked in" upgraded from phase to method |

### 2.G Process / OS

| # | metric | source & how | res | attr | helps debug |
|---|---|---|---|---|---|
| P1 | process CPU % (total, user, kernel) | O `Process.TotalProcessorTime` delta / wall (cheap, safe from watchdog thread) | 5 s | N | CPU-starved vs idle-blocked stall: **main-thread silent + CPU 0 % = waiting (I/O, lock); CPU 100 % one core = busy loop** — the cheapest upgrade to "silence" |
| P2 | main-thread CPU time | O `ProcessThread.TotalProcessorTime` for the main thread's OS id (needs native thread id captured at start, `GetCurrentThreadId` P/Invoke) | 5 s | N | same, more exact; distinguishes GC (all threads) from main-thread spin |
| P3 | thread count, handle count | O `Process.Threads.Count`, `HandleCount` | minute | N | thread/handle leaks (mods spawning threads, file handles) |
| P4 | system CPU / memory pressure | X: `typeperf`/WMI from WSL-side observer; available physical memory, commit charge | minute | N | "it was slow because something else ran" — environment discrimination (C4 item 3) |
| P5 | page faults / hard faults | O `GetProcessMemoryInfo` PageFaultCount (P/Invoke) | minute | N | paging = the real cause of 30 s stalls on a 20 GB process |
| P6 | GPU memory / utilisation | X: `nvidia-smi` (if NVIDIA, UNVERIFIED hardware) | minute | N | VRAM exhaustion → texture thrash |
| P7 | disk queue / free space | X | minute | N | save stalls; LocalLow filling |

### 2.H Environment

| # | metric | source & how | res | attr | helps debug |
|---|---|---|---|---|---|
| V1 | focus / RunInBackground (have `focused`) | E `Prefs.RunInBackground`, `Application.isFocused` | window | N | alt-tab artefacts |
| V2 | game speed, pause (have) | | window | N | |
| V3 | dev mode, god mode, LogVerbose | E `Prefs.DevMode`, `DebugSettings.godMode`, `Prefs.LogVerbose` | session/change | N | LogVerbose itself slows play (DeepProfiler + stack traces); god mode changes AI |
| V4 | mod list digest (have in manifest) | | session | Y | join every metric to a mod set |
| V5 | companion / build versions (have) | | session | n/a | |
| V6 | bridge activity | count of bridge tool calls in the window (RimBridgeServer side, or JawaBench tools only) | window | n/a | **observer effect: an agent driving the bridge is itself load** — mark windows where a bridge call ran |
| V7 | machine sleep / resume | X: Windows event log (Kernel-Power) by the observer | event | N | false stalls (C4 item 3) |
| V8 | other heavy processes | X: top-N CPU processes at incident (artpipe, builds, codex.exe) | incident | N | environmental slowness; the artpipe daemon and winbuild run on the same machine |

Count: 15 + 17 + 16 + 18 + 9 + 10 + 7 + 8 = **100 candidates**.

## 3. Usefulness assessment

Scale: **Debug** / **Opt** = value for incident debugging / mod optimisation, 0–3. **Attr** = attribution
quality (N none, P partial — leads only, Y names a mod/type). **Conf** = whether the source exists as
described (V verified in decompiled 1.6 this session or already shipped in the TPS record; U unverified).
**Cost** = implementation S (< ½ day) / M (1–2 days) / L (> 2 days or needs an early-loaded mod).
Rows grouped; candidates not listed scored ≤ 1/1 or are pure context (normalisers G13–G15, S18, V1–V5:
cheap, low value alone, mandatory alongside anything comparing windows).

| metric | Debug | Opt | Attr | Conf | Cost | note |
|---|---|---|---|---|---|---|
| **L2/L3 DeepProfiler load tree (LogVerbose one load)** | 3 | 3 | Y (mod class) | V | S | already in the engine; only parse + switch |
| **G2 frame-time percentiles** | 3 | 2 | N | V (Stopwatch exists) | S | p99 is the felt stutter; no allocation if histogrammed |
| **I1/I2/I4 log rate + cap flag + storm incident** | 3 | 2 | P | V | S | cap = blind log; error-per-tick is a real TPS cost |
| **P1/P2 process + main-thread CPU at silence/incident** | 3 | 1 | N | V(.NET) / U(native tid) | S–M | turns "silent" into busy-vs-waiting |
| **S6 per-Harmony-patch cost on hot methods (on demand)** | 2 | 3 | Y | U | L | the direct "which mod" answer; riskiest hook |
| **S4/S5 per-comp / per-component type tick cost (on demand)** | 2 | 3 | Y | V (types exist) | M | splits our `RM_` comps from the 600-mod field |
| **M12 thing counts by def→mod** | 2 | 3 | Y | V | S | spawn-loop and bloat finder; hourly cheap enough |
| **M13 heap across menu/reload** | 3 | 2 | N | V | S | the leak detector; M14 then names the field |
| **G3 frame split (tick / MapUpdate / draw / GUI)** | 3 | 2 | N | V (methods exist) | M | makes "frame-bound" a measurement |
| **G4 section regen count/time by layer type** | 2 | 3 | P | V | M | MapMesh churn is a classic mod regression; our liquids/terrain mods are prime suspects |
| **L8 full Harmony patch census** | 2 | 3 | Y | V (Harmony API) | S | once per session; static, no runtime cost |
| **L12 per-GenStep map-gen time** | 2 | 3 | Y | V | S | our biome gensteps; quicktest 90 s |
| **L11 save-load phase timing** | 2 | 2 | P | V | S | the canonical save load |
| **L14/X5 save size + duration trend** | 2 | 2 | N | V (`save` rows) | S | bloat trend; L15 offline names the mod |
| **M6/M7 working set vs native vs managed** | 2 | 2 | N | V/.NET, U/Unity | S | split growth into C# vs native |
| **S2 tick-list sizes** | 2 | 2 | P | V (private field) | S | ticker explosions |
| **S10 job churn** | 2 | 2 | P | U (names) | M | job-spam signature |
| **S7 pathfinding requests/time** | 2 | 2 | P | V (jobified) | M | worker time invisible to main-thread timers |
| **I3 error rate by message hash → mod** | 2 | 2 | Y offline | V | M | |
| **M3 GC pause duration** | 3 | 1 | N | U (no Boehm API) | M | high value, probably not directly measurable |
| **M4 allocation rate** | 2 | 3 | N | U (release-player counters) | S if API works | for opt only with per-scope alloc, which Mono lacks |
| **M8 texture memory** | 1 | 2 | P | U | S (cheap globals) / L (FindObjectsOfTypeAll) | |
| **M10 GraphicDatabase size** | 2 | 2 | P | V | S | leak signature for recolouring mods |
| **G8 SetAllGraphicsDirty rate** | 1 | 2 | P | V | S | |
| **G11/G12 draw calls, GPU time** | 1 | 2 | N | U | S if available | probably dev-build-only |
| **S9/S11/S12 think / workgiver / alert cost** | 1 | 3 | Y | U | M | on-demand profiler targets |
| **L5/L6 per-mod XML patch time + dead patches** | 1 | 3 | Y | V (engine) / needs early mod | L | the only metric needing a new always-loaded mod |
| **L4 per-type static-ctor time** | 1 | 2 | Y | V (one scope) | L | transpiler on `CallAll` |
| **X9 minidump at long silence** | 3 | 0 | P | U | M | external, rate-limited; Mono symbolisation unproven |
| **X10 in-process stack of blocked main thread** | 3 | 1 | Y | U (likely unsafe) | L | do not build without a spike |
| **P4/V7/V8 environment (system CPU, sleep, other procs)** | 3 | 0 | n/a | V (OS) | S (external) | needed to stop false "mod stall" verdicts |
| **V6 bridge-activity marker** | 2 | 1 | n/a | V | S | separates our observer effect from the game |
| **P5 hard page faults** | 2 | 0 | N | U (P/Invoke) | S | paging stalls |
| **X8 ModsConfig reset detect** | 2 | 0 | N | V | S | external, cheap, already-burnt-us class |

**Top five, by value × cheapness × confidence:**
1. **Load timeline from the engine's own DeepProfiler** (L2/L3/L11/L12) — free instrumentation already in
   1.6, per-mod-class attributable, answers the 15-minute-load question; cost is one verbose launch.
2. **Frame-time percentiles + frame split** (G2/G3) — the owner feels p99, not mean TPS; turns
   "frame-bound" from a hypothesis into a number.
3. **Log rate, storm incidents and the 10,000-message cap flag** (I1/I2/I4) — cheap, catches the
   error-per-tick slowdown, and flags when Player.log has gone blind.
4. **Process/main-thread CPU at silence and incidents** (P1/P2) — the cheapest way to tell a busy hang from
   a wait/IO/GC stall; fixes the biggest ambiguity left in the TPS incident rows.
5. **Leak and bloat probes: heap across reloads + thing counts by def→mod + tick-list sizes**
   (M13/M12/S2) — the long-session degradation that a speed metric only reports as "slower".

Honourable mention for optimisation work specifically: **on-demand per-type / per-Harmony-patch tick cost**
(S4/S5/S6) — highest attribution value, but on-demand only (§4).

## 4. Cost and risk of capture

### 4.1 Cost budget principle

- **Always-on tier: ≤ 0.1 ms main-thread per frame on average and zero steady-state allocation**
  (≈ 0.6 % of a 16.7 ms frame; ≤ 0.2 % of a tick budget at speed 3). Anything per-frame is fixed-size
  arithmetic on preallocated arrays; formatting and JSON happen once per window (5 s) and are the only
  allocations. Per-call Harmony hooks are allowed always-on **only on methods called ≤ a few hundred
  times per frame** (stage-level, as TPS attribution already is) — never per Thing, per pawn, per comp.
- **Minute tier: ≤ 2 ms once a minute** (context rows: counts, process stats).
- **Triggered tier:** may spend ≤ 50 ms once per incident, rate-limited (≤ 1 per 5 min), and only *after*
  the incident's critical row is enqueued, so the capture cannot delay the evidence.
- **On-demand tier:** bounded by an explicit duration (default 60 s), declared overhead printed in the
  report, auto-uninstall on timeout, exception, or game change. Its numbers are **relative** (the
  observer effect is large) and must say so.
- **Acceptance of any tier = an on/off A/B on the full ~600-mod list** (the TPS MUST 17 method: separately
  restarted configs, same save, counterbalanced). Nothing ships always-on on an estimate. `profEstMs`
  taught us an estimator is not a bound.

### 4.2 Per-tier costs and risks

| tier | members | main-thread cost (est.) | alloc / GC | stability risk | disk |
|---|---|---|---|---|---|
| T0 always-on per frame | G2 histogram, G3 4–5 stage timers, I1 counters (log hook), V6 flag | ~5 Stopwatch reads + ~10 int adds per frame: < 10 µs (UNVERIFIED; existing TPS hooks are the comparable) | none if preallocated | Harmony on `Log.Error/Warning/Message`: called from **any thread** — counters must be `Interlocked`; never format or allocate in the hook; a throw inside the hook would recurse into `Log.Error` → guard re-entry (the engine itself has `currentlyLoggingError`) | +~200 B/window |
| T0' always-on per window | percentiles, log totals, heap, gc, CPU from watchdog thread | ~50 µs per 5 s | one string per window (exists) | none new | as above |
| T1 minute context | M6/M7, M10, M11, S2, S13, S14, P3, P5, G13–G15 | counts walk lists: `listerThings` per def is O(defs); S2 reads 3 bucket lists — ≤ 1–2 ms on a big colony (UNVERIFIED) | ~1–3 KB per row | reflection on private fields (`TickList.thingLists`, `GraphicDatabase.allGraphics`, `Log.reachedMaxMessagesLimit`): cache `FieldInfo` at install, fail closed (field absent ⇒ metric `null` + `error` row, never throw) | ~2 KB/min ≈ 3 MB/day |
| T1' session/boundary | L8 Harmony census, M13 heap at menu (no forced GC), save size | Harmony census: `GetAllPatchedMethods` over ~10⁴ patched methods: **~100 ms–2 s once** (UNVERIFIED) → do it on the writer thread? **No — Harmony state is not thread-safe**; run once on main at registration, or split across frames | census JSON 0.5–2 MB in the manifest | one-off hitch at menu: acceptable, recorded as `explained` | once/session |
| T2 triggered | P1/P2 snapshot at incident (watchdog thread, safe), top message hashes, M12 thing-by-def at a sustained-low streak, external dump at silence > 120 s | CPU snapshot off-main: ~0; M12 on main: 5–50 ms on a big colony | M12 allocates a dictionary per capture | M12 at the moment the game is already slow makes it slower — rate-limit; dump: suspends the process for seconds (minidump of a 10–20 GB process can take **minutes** and GBs — use a small `MiniDumpNormal` with thread stacks only) | dump: 10–200 MB, cap + retention |
| T3 on-demand deep profile | S3–S6, S9–S12, G4/G5/G8 per type, M14, M8 heavy, M15 | **5–50 %** slowdown while armed (per-call timers on methods called 10⁴–10⁶ times/s) | must use preallocated per-key slots (dictionary keyed by `MethodBase`/`Type` prebuilt at arm time) | the dangerous tier: (1) **patching hot paths while the game runs** — Harmony re-JITs the method and every patch on it; mid-game install/uninstall races a method the main thread is executing? Harmony replaces the method pointer, the running frame finishes on old code (UNVERIFIED for Mono); (2) **skip-safety**: another mod's bool prefix returning false skips the original — our timing postfix still runs; use prefix+finalizer with `__state`, as TPS does; (3) wrapping *other mods' patch methods* (S6) means patching Harmony-generated replacement methods → must patch the patch method itself, not the target; (4) `FindObjectsOfTypeAll` (M8/M15) is **main-thread-only and seconds long** on 600 mods; (5) recursion (`ThingComp` calling base) → inclusive/exclusive invalid, carry `attrValid` | report file per run |
| T4 external | L1/L2 log tailing, I5, P4–P7, V7/V8, X2, X8, X9, ModsConfig, crash folders | **zero in-process** (reads files the game writes) | — | reading Player.log through drvfs while the game appends: share-mode issues seen on rotation (Opus #11); tail by size, never lock; the observer must never write in the game's folders except its own `tps\` | small |

### 4.3 Specific hazards

- **Unity API is main-thread-only.** `Profiler.*`, `Texture.*memory`, `Screen`, `QualitySettings`,
  `FindObjectsOfTypeAll`, `Application.isFocused` must be read in the main-thread window close, never from
  the watchdog thread. .NET `Process`/`GC` reads are thread-safe and belong on the watchdog thread.
- **The watchdog thread is blind during stop-the-world GC and whole-process suspension** (GPT review): any
  "GC pause" measurement from inside is an inference from frame gaps + `gc` deltas. Only an external
  sampler (P1 from outside: CPU of the process during a silence) can see GC as "CPU busy, all threads".
- **Observer effect of the bridge.** A `jawa/` tool call runs on the main thread; an agent polling
  `tps_report` every second is itself frame time. Mark windows with bridge calls (V6) and never compute a
  verdict from windows the agent was driving without saying so.
- **Log hooks change log behaviour.** Patching `Log.Error` touches the most-called failure path in the game;
  if our hook throws, the engine logs that error → infinite recursion. Prefer
  `Application.logMessageReceivedThreaded` (a Unity event subscription, no patch; fires for every Unity log
  line including ones that bypass `Verse.Log`) and count only. UNVERIFIED: whether it still fires after the
  10,000 cap sets `logEnabled = false` (probably not — so the cap flag must come from the private field).
- **LogVerbose is not free.** It turns on DeepProfiler (fine at load) but also verbose messages, each
  capturing a stack trace (VERIFIED `Log.Message` calls `StackTraceUtility.ExtractStackTrace()`). Use it for a
  measured load, then switch it off before play; never leave it on during a TPS comparison.
- **Writer saturation.** All new rows go through the one ordered writer. Bulk bands (context, histograms) must
  stay inside the existing 3,584-line bulk allowance; incident/critical rows keep the reserve. A storm metric
  (I4) must emit **one** incident per storm, not one row per error.
- **Game-scoped state.** Every cumulative counter resets at the `game` boundary; leak metrics (M13) are the
  one deliberate exception and are written as their own `boundary` row, carrying both games' ids.
- **Retention.** Dumps and per-run deep-profile reports go under `JawaBench\tps\` subfolders with their own caps;
  never the repo.

### 4.4 What NOT to capture always-on

Per-Thing, per-pawn, per-comp or per-def tick timing (S3–S5); per-Harmony-patch timing (S6); think-tree,
workgiver, alert, pathfinder per-call timing (S7, S9, S11, S12) beyond a count; `FindObjectsOfTypeAll`
anything; full Harmony census more than once per session; stack traces of anything; forced `GC.Collect`
(it *creates* the stall it measures); memory dumps except at a long silence. Also: no per-frame JSON, no
per-error rows, and no LogVerbose during play.

## 5. Architecture

Four tiers, one record. Everything in-process extends the TPS sampler rather than standing beside it: one
autostart (bridge-registration ctor), one ordered bounded writer with seq numbers and a critical reserve, one
heartbeat/watchdog, one session/game lifecycle, one settings file, one reader. New code is additional
**bands** on existing rows plus a few new row kinds.

```
            in-process (JawaBench companion, starts at bridge registration)
 main thread ──► T0 frame band (histogram, stage timers, counters) ─┐
             ──► T1 minute band (counts, Unity memory, reflection)  ├─► JawaBenchTpsWriter (ordered, bounded,
             ──► T3 on-demand profiler (armed by jawa/health_profile)│   seq, critical reserve, segments)
 watchdog thr ─► heartbeat + P1/P2 CPU + T2 incident snapshots ─────┘        │
                                                                              ▼
                                         JawaBench\tps\*.jsonl  (outside git, 7 d / 256 MB)
                                                                              ▲
            out-of-process (WSL, systemd timer or belt pass)                  │
 belt_watchdog / health_observer.py ── Player.log tail, ModsConfig, OS stats, dumps ──► observer.jsonl
 load_timeline.py ── DeepProfiler tree from archived Player.log (LogVerbose load) ──► load_<session>.json
 tps_record.py (reader) ── --at / --since / --health / --load / --profile <run>
```

### 5.1 Record schema sketch (additions to `v: 2` rows → `v: 3`)

`sample` row gains a **frame band** and a **log band** (all scalars, ~200 B):

```json
{"kind":"sample", "...existing...":0,
 "ft":{"p50":16.2,"p95":24.9,"p99":61.0,"max":212.4,"n":298,"hist":[0,4,180,90,18,4,1,1]},
 "fs":{"tick":[ms,max],"mapUpd":[ms,max],"meshUpd":[ms,max],"dyn":[ms,max],"gui":[ms,max],"rest":ms},
 "log":{"err":3,"warn":11,"msg":40,"capped":false,"topErr":["9f2c1a","03bb7e"]},
 "cpu":{"proc":38.5,"main":21.0},
 "bridge":{"calls":2,"ms":14.0}}
```

`hist` = fixed log-scale buckets (≤ 8 ms, 16, 33, 50, 100, 250, 1000, > 1000) — percentiles are derived from
the histogram so the main thread never sorts.

`context` row (every 60 s) gains a **memory band** and **load band**:

```json
{"kind":"context", "...existing...":0,
 "mem":{"heapMB":2810,"heapResMB":3900,"monoUsedMB":null,"nativeAllocMB":5200,"nativeResMB":6100,
        "texMB":1450,"wsMB":11200,"privMB":12900,"pageFaultsHard":12,"graphics":18234},
 "load":{"tickLists":[4211,9870,22013],"lords":7,"letters":12,"messages":3,"worldPawns":1830,
         "flecks":410,"threads":61,"handles":2940},
 "view":{"zoom":38.0,"world":false,"overlays":["beauty"],"res":"2560x1440","vsync":1,"fpsCap":0}}
```

New row kinds:

| kind | when | fields |
|---|---|---|
| `storm` | log rate > threshold for ≥ 3 windows; one row per storm (open/update/ended) | `rate`, `topErr[{hash,count,firstText(120 chars)}]`, `capped` |
| `boundary` | at each `menu`/`game` transition | heap/native/ws before & after, thing counts, `graphics`, for leak deltas (M13) |
| `census` | once per session after registration (and on demand) | Harmony patch census per owner: methods patched, prefix/postfix/transpiler/finalizer counts, **hot-path flags** (owners patching `Thing.Tick`, `Pawn.Tick`, `DoSingleTick` subtree, `MapUpdate` subtree, `Log.*`) — goes in `session_<id>.json`, the row carries a digest |
| `bloat` | hourly + at sustained-low trigger | top 20 defs by count with `packageId`, top 10 tick-list defs |
| `profile` | end of an on-demand run | run id, duration, armed targets, per-key `[calls, totalMs, maxMs, alloc?]`, `attrValid`, measured overhead (ratio during vs the 60 s before) |
| `loadtl` | written by the reader/observer, not the game | parsed DeepProfiler tree: phase, ms, self ms, per-mod-class ms |

### 5.2 Reader and watchdog summaries

- `tps_record.py --health [--at T]`: one block per window range — TPS ratio (existing), **p99 frame**,
  frame split share, log rate, heap / native / working-set trend with slope per hour, open storms, CPU at
  incidents. Each line carries a coverage state; `null` metrics print `n/a (source unavailable)`, never 0.
- `tps_record.py --leaks`: `boundary` rows across games in a session → heap / native / graphics retained per
  reload; WARN when the third reload is > 10 % above the first.
- `tps_record.py --load [session]`: the parsed load timeline, phase deltas against the previous load of the
  same `modOrderDigest` (so a mod-list change is compared fairly), top 15 mod classes by ctor time.
- `tps_record.py --profile <run>`: per-type/per-owner table, sorted by total ms, with the run's measured
  overhead and the warning that numbers are relative.
- `belt_watchdog.py`: two new lines — `health` (WARN on: p99 frame > 100 ms sustained, storm open, log
  cap reached, working set > 85 % of physical RAM, heap growth > N MB/h over ≥ 2 h) and `health-observer`
  (external: ModsConfig reset, crash folder new, Player.log growth > 50 MB/h). Like `tps`, **they never
  change the overall verdict**. A **standing timer** (systemd, WSL keepalive already exists) runs the
  observer pass every 5 min regardless of agent activity — this also discharges the TPS item's owed
  periodic observer.

### 5.3 The cold-load gap

No in-process component exists before bridge registration. Three routes, cheapest first:
1. **LogVerbose load** (engine DeepProfiler): set `Prefs.LogVerbose` in `Prefs.xml` before a launch the
   owner already wanted, parse the archived Player.log after; flip back before play. Zero code in-game.
   Caveat: changes the load it measures (verbose messages); compare verbose loads only to verbose loads.
2. **External tail with arrival timestamps** (no LogVerbose): the WSL observer polls Player.log size every
   1 s during a load and stamps known landmark lines ("Initializing…", mod class lines, `Bridge token:`).
   Coarse (Unity buffers log writes, UNVERIFIED flush cadence) but always available.
3. **Early-loaded instrumentation mod** (`mandrake.rm.loadprobe`, top of load order, `Mod` ctor installs
   Harmony timers on `PatchOperation.Apply`, `CreateModClasses` loop body, `CallAll`, def loading): the only
   way to get L4–L6 per mod. Costs a real mod in the list (Mod Settings rule applies), and it is a **load-time
   Harmony patch of the patch engine**: highest risk of anything here.

## 6. Implementation options

Prerequisite for every option: the TPS record's owed MUST 17 (full-list overhead A/B, autostart, overnight
reconstruction) passes first. Building on an unmeasured base doubles the unknown overhead.

### A. Health line — extend the TPS rows only (T0 + T1, no new hooks beyond 4 stage timers)

- **Scope:** frame-time histogram + percentiles (G2), frame split timers on `MapUpdate` / `MapMeshDrawerUpdate_First`
  / `DrawDynamicThings` / UI root (G3), log counters via `Application.logMessageReceivedThreaded` + cap flag via
  reflection (I1/I2), watchdog-thread CPU (P1, P2 if native tid works), minute memory band (M1/M5–M7, M10,
  M11, S2), view/env context (G13–G15, V3, V6). Reader `--health`; belt `health` line.
- **Cost:** ~3–4 days incl. selftests (trace replays for the histogram; fault-injection for the log hook).
- **Risk:** low. Four more stage hooks of the kind already shipped; one event subscription; reflection reads
  that fail closed.
- **Answers:** "was it stutter or slow ticks", "was it an error storm", "was the process busy or waiting",
  "is memory climbing", "was the agent driving the bridge".
- **Blind:** load time, which mod, GC pause length, GPU.

### B. Tiered recorder — A + triggered incidents + on-demand profiler + external observer

- **Scope:** A, plus T2 (CPU/hash snapshot at incidents, `storm` rows, `bloat` hourly and on sustained low,
  `boundary` leak rows, session Harmony census), T3 `jawa/health_profile {targets, seconds}` (per comp type,
  per Map/GameComponent type, per Harmony patch owner on a named hot method, section-layer regen by type),
  T4 standing observer timer (OS stats, ModsConfig reset, crash folder, Player.log growth, rate-limited
  small minidump at silence > 120 s).
- **Cost:** ~2–3 weeks; T3 alone ~1 week with its safety (arm/disarm, timeout, game-change disarm, rollback,
  overhead self-report).
- **Risk:** medium-high in T3 (runtime patching of hot paths, other mods' patch methods); medium for dumps
  (multi-GB process suspend). Every hazard in §4.2 applies.
- **Answers:** nearly everything in §3, including "which mod" for tick cost and bloat.
- **Blind:** cold-load phases (unless D's LogVerbose route is added), GPU internals.

### C. Load timeline + on-demand profiler only (no always-on growth)

- **Scope:** `load_timeline.py` (parse DeepProfiler trees from archived logs of LogVerbose loads, diff
  against the last load with the same mod order), map-gen per GenStep + save-load phases via companion hooks
  on `GenStep.Generate` / `GameDataSaveLoader.LoadGame` (they fire inside a running session), and T3
  on-demand profiler. Always-on record unchanged.
- **Cost:** ~1–1.5 weeks.
- **Risk:** low for load parsing (offline); T3 as in B.
- **Answers:** mod optimisation (load and tick) on request; "why is loading 15 min".
- **Blind:** incident forensics — nothing new about the slowdowns he sees in solo play.

### D. External-only observer (zero in-game change)

- **Scope:** WSL-side `health_observer.py` on the existing systemd timer: process CPU / working set / private
  bytes / handles / threads / hard faults via `powershell.exe Get-Process`/`typeperf` (or `python.exe` +
  `psutil` if installed, UNVERIFIED), Player.log size + error-line rate + cap message ("Reached max messages
  limit"), first exception per load, ModsConfig active count, crash folder, system memory/CPU, top other
  processes, sleep events, LogVerbose-load parsing.
- **Cost:** ~3–4 days.
- **Risk:** ~none to the game; cross-OS polling cost on the machine (powershell.exe startup ~0.5–1 s every
  poll — use one long-lived `typeperf` stream instead).
- **Answers:** environment and stability, memory footprint trend, log storms (coarsely), load timeline.
- **Blind:** frame times, attribution of anything in-game, GC vs work, which map/zoom.

### E. Early-loaded load-probe mod (`mandrake.rm.loadprobe`)

- **Scope:** a real mod at the top of the load order timing per-mod `PatchOperation.Apply` (and counting
  no-match), per-type static ctors (transpiler on `CallAll`'s loop), per-mod-class ctor + Harmony patch time,
  def database phases, texture load per mod. Writes `load_<session>.json` straight to `JawaBench\tps\`.
- **Cost:** ~1 week + Mod Settings + its own script (debug-process rule).
- **Risk:** medium: Harmony patches applied *during* mod loading to the patch engine itself; a bug here
  breaks every load (and a load-time NRE triggers the corrupted-mods ModsConfig reset — CLAUDE.md, 2026-09-27).
- **Answers:** the only full per-mod load attribution, plus dead-patch detection (a correctness win).
- **Blind:** everything after load.

### Recommendation

**A + D now, C's LogVerbose load parser alongside (it is offline and nearly free), B's T3 profiler later and
only for a named optimisation question; E only if the load timeline shows XML patching or static ctors
dominate.** Why: A and D close the forensic gaps the owner actually hits (stutter, storms, busy-vs-waiting,
memory creep, environment) at near-zero in-game risk and give MUST 17's A/B a wider set of numbers for free,
while the risky per-mod instrumentation stays switched off until a concrete question pays for its overhead.

## 7. Open questions for an adversarial reviewer

1. Do Unity 2022.3's `Profiler.GetTotalAllocatedMemoryLong` / `GetMonoUsedSizeLong` and `ProfilerRecorder`
   render counters ("Draw Calls Count", "GC Allocated In Frame") return live values in RimWorld's **release
   player**, or zeros? Which ones need a development build? (Decides M4/M7/G11.)
2. Is there *any* way to measure Boehm GC pause duration in RimWorld's Mono without a dev build (GC
   notifications, `mono_gc_*` exports via P/Invoke, a Unity marker)? If not, is "frame gap overlapping a `gc`
   delta" a defensible proxy or a coincidence detector?
3. Does `Application.logMessageReceivedThreaded` keep firing after `Verse.Log` sets
   `Debug.unityLogger.logEnabled = false` at 10,000 messages? If it stops, the log-rate metric silently reads
   zero exactly during the worst storm — is reading the private `reachedMaxMessagesLimit` sufficient cover?
4. Is the T0 cost estimate (< 10 µs/frame for 5 stage timers + histogram) credible on Mono with Harmony 2.4.2
   dispatch, or is per-hook overhead closer to the TPS `profEstMs` order? Should T0 be gated on MUST 17's
   numbers before any design is fixed?
5. Is runtime Harmony install/uninstall of timers on hot methods (T3) safe mid-game on Mono — specifically
   when the method being re-patched is on the current call stack, and when wrapping other mods' patch
   methods (S6)? Is arming only at the main menu or while paused a sufficient mitigation?
6. Main-thread OS CPU (P2) needs the native thread id captured on the main thread (`GetCurrentThreadId`
   P/Invoke) and `ProcessThread` lookup from the watchdog thread — is that reliable under Mono/Unity, and is
   per-thread CPU readable while the process is in a stop-the-world GC?
7. Is LogVerbose-on-for-one-load a fair load measurement given it also enables verbose messages with stack
   traces? How large is that distortion on 600 mods — 1 %, or 20 %?
8. Is a WSL-side observer polling Windows process stats every 5 s (powershell / typeperf / python.exe) cheap
   enough not to perturb the game, and does drvfs tailing of Player.log interfere with Unity's writes or
   rotation (`Player-prev.log`)?
9. Is a minidump of a 10–20 GB RimWorld process at a long silence useful at all — can Mono managed stacks be
   recovered from a Windows minidump with available tooling — or is it just a multi-GB suspend that makes the
   hang worse?
10. Are the frame-split targets (`Map.MapUpdate`, `MapDrawer.MapMeshDrawerUpdate_First`,
    `DynamicDrawManager.DrawDynamicThings`, the UI root) a valid partition of frame time, or do jobified draw
    (`DynamicDrawManager` uses Unity Jobs) and Unity's own render thread move most cost outside any main-thread
    scope, making "draw = small" a false conclusion?
11. Are the thresholds (p99 > 100 ms sustained, heap growth > N MB/h, 3rd reload +10 %) grounded in anything,
    or should the first month run report-only with thresholds fitted to the record?
12. Does extending row size (frame band + log band + memory band) push a continuous-play day past the 256 MB
    retention cap so that the 7-day guarantee silently becomes ~3 days? Should bands be split into their own
    segment family?
