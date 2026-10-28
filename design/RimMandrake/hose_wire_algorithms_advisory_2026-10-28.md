# Hose and wire algorithms: advisory report (2026-10-28)

Asked by the owner on 2026-10-28: a deep GPT web review of the core algorithms behind hoses (FlowWorks) and wires
(Gimme Some Slack power cords). He wanted published variants, standard optimizations and acceptable approximations,
plus an answer to "was this even the right question?". The goal is to stop the constant live testing and tuning.

How to read this report:
- **MEASURED** means a number from a live run record or a ledger/commit note.
- **UNMEASURED** means nobody has measured it.
- **[GPT]** marks a claim from the GPT research rounds. GPT's own effort and gain estimates are its judgement, not data.
- **[verified]** marks something I checked myself, in our code or in the cited source.

The research material is in `D:\ClaudeWork\rimmandrake\research\hose_wire_2026-10-28\`:
- `brief.md` is the brief GPT was given;
- `q1`..`q7` hold the seven rounds (prompt.md, answer.md, codex.log);
- `r1a`, `r1b` and `r2` are three over-broad first attempts that timed out without an answer;
- `spot\` holds the source pages I fetched to check citations.

## 1. Short answer

**It was only partly the right question.** We already run the standard algorithms: A* with line-of-sight smoothing
for routing, and BFS components for networks. No published variant fixes what actually hurts us. Three things do:

1. **Single pieces of main-thread work have no upper bound.** Measured examples: an 18.3 ms hose recheck, a 17.2 ms
   Signal walk, a 16k-cell overflow that forces a whole-world rebuild, and whole-map relabels.
2. **Garbage-collection pauses of 120-140 ms** land in whichever system happens to be ticking.
3. **The live measure-and-fix loop is slow and noisy.** One round takes about 94 minutes from verdict to verdict, and
   other mods' spikes pollute the maxima.

Better algorithms matter only after work is bounded and measurable offline. Specifically, a reusable-array A* and
targeted invalidation are worth doing; exotic replacements are not. GPT reached the same verdict (q7) when asked to
attack this hypothesis. Its one caveat is worth keeping: slicing work does not remove it, so a sliced queue can still
build a backlog. Throughput under bursts has to be tested too.

The five better questions (sections 4 and 6 develop them):

1. What bounded unit of work can every expensive operation yield after, and what work and allocation limit applies
   to that unit?
2. Under rain, a settings change, a cold load or repeated edits, does the deferred work keep up? What limits how old a
   queued result can get?
3. What must become true at once after an edit (a cut hose stops carrying liquid), and what may wait (geometry,
   reachability labels, which answer "unknown" until fresh)?
4. Which edits actually affect which hoses or networks? Can we touch only those instead of re-checking everything on a
   timer?
5. Can a recorded map plus a recorded event stream replay thousands of ticks offline, and gate work counts,
   allocations and conservation on every commit?

## 2. What we run today and why it hurts

The full description is in `brief.md`. Only the load-bearing numbers are repeated here.

| System | Algorithm today | Worst cost seen |
|---|---|---|
| CordPlanner (hoses and wires) | 8-connected A*, octile heuristic. Open list is a `SortedSet` of tuples. `g` and came-from are `Dictionary`s **allocated on every call** [verified `CordPlanner.cs:46-48`, `:106`]. Then string-pull, corner rounding and Catmull-Rom. Hoses add clothoid fits and stiffening against a clearance field computed per query point | Typical lay 121 ms mean / 537 ms max, off-thread (MEASURED). Before the lay queue, a settings change re-laid 150 hoses in one 90.5 s frame (MEASURED) |
| CordWorld snapshot | Plain arrays, patched from a dirty-cell list. The dirty list holds 16,384 cells; past that it overflows and rebuilds the whole world [verified `HoseWorldPatch.cs:22`] | Whole rebuild up to 188 ms (MEASURED). Rain dirtied 12,080 and 15,429 cells, and 2 overflow rebuilds hit one deluge window (MEASURED) |
| Hose tick | Per reel per tick: watch, tint, Signal provider chain. Every 250 ticks per reel: corridor hash, then `CheckReplan` (an A*) **synchronously on the tick** [verified `RM_MapComponent_Hoses.cs:1333`; the draw side has budgets, the tick recheck has none] | Map1 max: DRY 19.8-20.7 ms (recheck body 18.3), SETUP 30.1 ms (Signal 17.2), RAIN 12.4 ms. Bar < 10 ms, **not met** (MEASURED) |
| RM_HoseLinks | Polls every tick: a 64-bit signature over every reel's ends; any change rebuilds the links | Was 10-40 ms, now 0.48-2.25 ms (MEASURED). A mid-tick cut was once missed, and liquid crossed a dead link (fixed by a check before every Move) |
| RM_LiquidNet | BFS components cached by revision. **Any** topology bump rebuilds **all** components. Settle runs once per 250 ticks as integer tank-to-tank moves | Offline budget ≤ 0.05 ms mean / ≤ 1 ms worst (MEASURED offline on .NET 8 only) |
| RM_WallReach | A whole-map flood-fill labelling per climb band and per pawn class, redone on any change and rate-limited | Rain tail 23.6, then 19.9/16.4 ms (MEASURED) |
| GSS wires | Section-dirty-driven rebuild. Only changed edges are re-planned, the snapshot is patched, and the build is sliced across frames | A full build once held one frame ~1 s. After slicing, live round 9 windows ran 4.3-6.8 ms max, with 7 of 8 windows under 7.4 ms (MEASURED) |

Cross-cutting facts:

- **GC.** Full collections cost 120-140 ms on the full mod list (MEASURED).
- **Incremental GC is on.** Our own GSS probe recorded `gcIncremental=true` live in round 9 [verified ledger
  `BENCH.jsonl` line 6364, probe `GimmeSomeSlackProbe.cs:619`]. So these pauses are *fallbacks to full
  collections*, not a disabled setting. Unity documents that incremental GC falls back to a full, non-incremental
  collection when reference changes outpace it [verified in the Unity 2022.3 manual page, see section 3].
- **Ludeon adopted incremental GC in RimWorld 1.1** [GPT, verified on the devtrackers mirror of the 1.1
  announcement].
- **Offline timings do not transfer.** The offline SelfTest runs on .NET 8 CoreCLR, which has a generational,
  precise GC. The game runs Unity Mono with a Boehm GC. Offline timings and allocation behaviour therefore do not
  carry over [verified: the SelfTest project targets net8.0].
- **The live loop is slow.** Since 2026-10-01 at least 20 performance items on these systems were each found live,
  fixed, re-measured live, and usually spawned a child item. Seven excavation rounds took 8 h 05 min for five
  verdicts. A cold load on the full list costs 12-13 min (all MEASURED).

Why it hurts, in one line: the maxima come from rare bursts we cannot reproduce offline, so each fix waits about 94
minutes for a noisy verdict.

## 3. Named algorithms and techniques, and whether they fit

The table lists each technique with its source and GPT's fit judgement (my agreement noted). "Spot-checked" means I
fetched the page and found the claim in it.

| Technique (search name) | What it is | Fit for us | Source |
|---|---|---|---|
| **Array-backed binary heap / indexed priority queue** for A* | Replaces the `SortedSet` with remove+add decrease-key | **Yes.** Standard and low risk. Needs deterministic tie-breaking, because GSS must be identical on load | redblobgames.com/pathfinding/a-star/implementation.html [GPT] |
| **Flat arrays with generation stamps** (`id = y*w + x`; reset only by bumping a stamp) | Removes the per-call `Dictionary` allocation | **Yes.** One scratch set per concurrent search slot, not one per hose. The published source here is weak (GPT: UNSOURCED); it is common practice | [GPT, UNSOURCED] |
| **Bucket queue / radix heap** | Integer-key priority queues | Weak fit, because the large dive costs widen the key range | redblobgames.com/pathfinding/grids/algorithms.html [GPT] |
| **Connected-component early reject** before A* | Skip an A* whose two ends are in different components | Yes, if the labels respect bands and dive rules. A stale label must mean "unknown", never "unreachable" | redblobgames A* implementation page [GPT] |
| **Lifelong Planning A* (LPA*)**, **D* Lite** | Incremental replanning that reuses the last search after edge costs change | **Defer.** Search state for ~200 hoses over 106k-160k cells is costly, and there is no worst-case guarantee | idm-lab.org/bib/abstracts/papers/aij04.pdf (LPA*, spot-checked: the title and keywords say "Lifelong Planning A*", incremental search); idm-lab.org/.../aaai02b.pdf (D* Lite) [GPT] |
| **Jump Point Search / JPS+** | Prunes symmetric paths on uniform-cost grids | **No.** Per-cell extra costs, bands and dive costs break the symmetry it relies on, and JPS+ preprocessing must be maintained under edits | harabor.net/data/papers/harabor-grastien-icaps14.pdf [GPT] |
| **HPA\*** (hierarchical path-finding A*) | Cluster abstraction, then local refinement | **Not for routing now.** Hoses are short (maxLength 40). The idea is useful for WallReach labels (below) | Botea, Mueller, Schaeffer 2004. GPT's fetch of the paper failed, so it is UNSOURCED here |
| **Theta\* / Lazy Theta\*** (any-angle) | Line-of-sight parents during search | Optional. It may improve route topology over post-smoothing, but it must respect doors, bands and dives. Measure first | idm-lab.org/bib/abstracts/papers/aimag13.pdf [GPT] |
| **Field D\*** | Interpolated continuous headings | No: wrong fit for band and door rules | ri.cmu.edu ... ferguson_david_2005_3.pdf [GPT] |
| **Funnel algorithm** | Straightens a path through a corridor of portals | No: we have no portal corridor | digestingduck.blogspot.com/2010/03/simple-stupid-funnel-algorithm.html [GPT] |
| **Felzenszwalb-Huttenlocher distance transform** | An exact distance field computed in linear time with separable passes | **Worth a benchmark.** One clearance field shared by all queries, truncated at the useful radius and patched in dirty tiles, would replace per-point nearest-blocker searches | cs.brown.edu/people/pfelzens/papers/dt-final.pdf [GPT] |
| **Time-sliced pathfinding** (Recast/Detour `initSlicedFindPath` / `updateSlicedFindPath(maxIter)` / `finalizeSlicedFindPath`) | A search keeps its state between ticks and runs a fixed number of iterations per update | **Yes.** This is the production precedent for bounding `CheckReplan` | recastnav.com/classdtNavMeshQuery.html (spot-checked: `updateSlicedFindPath` is present) [GPT] |
| **Path corridor repair** (Detour `dtPathCorridor`: `trimInvalidPath`, `isValid`) | Repair the broken part of a path, not the whole path | Later, after slicing | recastnav.com/classdtPathCorridor.html [GPT] |
| **Dirty Flag / Observer / Update Method** (Game Programming Patterns) | Mark derived state dirty on mutation, notify subscribers, and update only active objects | **Yes**, for HoseLinks and the hose recheck. Keep notification callbacks cheap, or the spike moves into the edit | gameprogrammingpatterns.com, chapters dirty-flag, observer, update-method [GPT] |
| **Double buffering** | Build the next state while readers keep using the current one; publish atomically | Yes, for WallReach labels and snapshots | Game Programming Patterns, double-buffer chapter [GPT] |
| **Union-find (disjoint-set union)** | Incremental connectivity | Handles additions only. Deletions (cuts, demolition) cannot be undone in it | [GPT, UNSOURCED in its pass] |
| **Holm-de Lichtenberg-Thorup dynamic connectivity, Euler tour trees** | Fully dynamic connectivity with O(log² n) amortized updates | **No.** It is heavy to build and verify, its cost is amortized rather than bounded per update, and GPT found no game using it | people.csail.mit.edu/rahul/papers/dyncon-jea2001.pdf [GPT] |
| **Affected-component rebuild** | On a deletion, re-flood only the old component that held the removed edge | **Yes.** This is the practical game approach. Our RM_LiquidNet rebuilds *all* components on any bump | [GPT, UNSOURCED: an engineering proposal] |
| **Chunked (hierarchical) connected-component labelling** | Label inside 16×16 chunks, then join the chunks in a coarse graph | Yes, for WallReach (441 chunks at 325², 625 at 400²). Edits relabel only their chunks, but a split can still change global connectivity | [GPT, UNSOURCED: a proposal] |
| **Factorio Fluids 2.0 "segments"** | Pipes, underground pipes and tanks merge into one segment; fluid is available throughout it; pull rate is proportional to fill | Our settle scheduler already makes the same abstraction choice (components, not per-pipe flow). Keep it | factorio.com/blog/post/fff-416 (spot-checked: "Pipes, underground pipes, and storage tanks are merged into fluid segments"; pull rate proportional to fill). This was the 2024 proposal |
| **RimWorld TickList** | 250 buckets for TickRare and 2000 for TickLong; each Thing is bucketed by hash; one bucket ticks per tick | This is already how vanilla spreads periodic work. Our phasing by thing id matches it | github josh-m/RW-Decompile Verse/TickList.cs (spot-checked: 250/2000 and `BucketOf` by `GetHashCode`; the decompile is historical, not 1.6) |
| **Unity incremental GC** | Boehm GC with the work spread over frames; non-compacting; **falls back to a full collection** when reference changes outpace it | Explains our 120-140 ms pauses with incremental GC on. The cure is allocating less, not changing a setting | docs.unity3d.com/2022.3/Documentation/Manual/performance-incremental-garbage-collection.html (spot-checked: "falls back to doing a full, non-incremental collection") |
| **Unity allocation best practices** | Boxing, capturing lambdas, string concatenation, collection growth | We already follow this (the zero-alloc work). Audit remaining LINQ, interface `foreach`, `params` and `yield` in hot paths | docs.unity3d.com/2022.3/Documentation/Manual/performance-garbage-collection-best-practices.html [GPT] |
| **BenchmarkDotNet on Mono** (`[SimpleJob(RuntimeMoniker.Mono)]`, `MonoRuntime.Default`) plus `MemoryDiagnoser` | Benchmarks the same code under the Mono runtime and counts allocated bytes | Yes, as a lane that approximates the game. Equivalence to Unity's Mono is not proven | benchmarkdotnet.org/articles/configs/toolchains.html (spot-checked: both forms present); /diagnosers.html [GPT] |
| **`GC.GetAllocatedBytesForCurrentThread()`** | A per-thread count of bytes allocated | The right allocation counter on .NET 8. Whether it works on the game's Mono is UNMEASURED; probe it with a known allocation first | learn.microsoft.com ... system.gc.getallocatedbytesforcurrentthread [GPT] |
| **Factorio `--benchmark` / `--benchmark-verbose`**, and Factorio's determinism "heavy mode" | Loads a save headless and reports per-tick timings; save/reload each tick and compare CRCs | This is the model for our offline harness | wiki.factorio.com/Command_line_parameters; factorio.com/blog/post/fff-315 [GPT] |
| **Unity Performance Testing Extension** | Profiler-marker measurement in built players | Only for a separate Unity calibration project | docs.unity3d.com/Packages/com.unity.test-framework.performance@3.0 [GPT] |
| **SharpFuzz** | .NET fuzzing | Possible later, to mutate edit sequences towards worst-case work | github.com/Metalnem/sharpfuzz [GPT] |

Not established by the research:
- how Factorio, ONI, Satisfactory or Timberborn route slack cables;
- how ONI's conduit networks rebuild;
- how Factorio splits electric networks;
- whether Performance Fish, RocketMan or Dubs use recorded-map perf gates;
- any published per-mod millisecond budget for RimWorld.

GPT marked all of these UNSOURCED. Do not quote them as known.

## 4. Ranked recommendations

The gain and effort figures are estimates (GPT's tables, adjusted by me against the code). None is measured.

| # | Change | Expected gain | Effort | Risk |
|---|---|---|---|---|
| 1 | **Build the offline replay perf harness first** (section 5). Record one 325×325 map snapshot plus an ordered event stream. Replay thousands of ticks headless. Gate work counts, allocations, conservation and same-tick cut safety on every commit. Add a Mono timing lane | No direct speedup. Turns each ~94 min live round into a run of a few minutes, and makes every later item provable offline | 4-7 days | Low. The main risk is a recorded workload that misses an input |
| 2 | **Bound the hose recheck.** Move `CheckReplan` off the tick, either onto the existing HoseLayQueue worker or as a sliced A* with a fixed expansion quota per tick (the Detour `updateSlicedFindPath` pattern). Run rechecks under one shared per-tick work quota across maps, counted in operations, not wall time | Removes the 18.3 ms recheck body, the main reason the < 10 ms bar fails. Live GSS slicing already took windows from 15-86 ms down to 4-7 ms (MEASURED, round 9) | 2-4 days | Medium. A pending replan must not count as "no route", and must not authorize flow over a cut hose |
| 3 | **Remove the overflow cliff.** Size the dirty list to the whole map (160k ints, about 625 KiB at 400×400). Process the patches in bounded batches, so the 16,385th cell no longer triggers a synchronous whole-world rebuild | Removes the rain overflow rebuilds. The whole build cost up to 188 ms historically | 1-2 days | Low. Correctness is already checked offline as patch == rebuild |
| 4 | **Make the CordPlanner A* allocation-free.** Use reusable flat `g`/parent/stamp arrays and an indexed binary heap with a fixed tie-break order | Fewer allocations in a path every lay and recheck uses, so fewer GC fallbacks. Likely a large cut in the 121 ms mean lay time (UNMEASURED) | 2-3 days | Low-medium. A tie-break change alters routes, and GSS must stay identical on load |
| 5 | **Replace polling with event-driven dirty marking.** (a) Keep a cell-to-hose reverse index of each hose's dependency cells (crossed cells, corner-cut sides, clearance footprint), so an edit marks only the affected hoses instead of every hose hashing its corridor every 250 ticks. (b) Give HoseLinks mutation versions and a dirty queue fed by cut, retract, despawn and relay events, keeping a slow phased audit as a backstop | Removes the routine recheck and refresh work. Closes the same-tick invalidation class (the dead-link bug) by design | 3-6 days | Medium. A missed dependency or subscription leaves a stale hose; the audit and the pre-Move check remain the safety net |
| 6 | **Make the Signal lease an expiry tick.** Store "flowing until tick T" and compare it, instead of walking the provider chain or relay chain each tick | Targets the 17.2 ms Signal spike in SETUP | 1-2 days | Low-medium. Every wake condition must be covered |
| 7 | **Scope RM_LiquidNet rebuilds to the affected component.** An addition merges two components; a deletion re-floods only the old component | Avoids rebuilding unrelated networks on every bump | 2-4 days | Medium. Splits and cached routes are the hard part |
| 8 | **Slice and double-buffer WallReach**, publishing labels atomically; "unknown" means no veto. Chunked labels (16×16, plus a coarse graph) come later if the rebuild is still too big | Takes the whole-map relabel out of a single tick | 3-5 days (slicing); 6-10 more for chunks | Medium. Stale data must never produce a false NO (the W1-W4 class) |

Also worth one small item: **measure allocations on the game's Mono.** Test whether
`GC.GetAllocatedBytesForCurrentThread()` works there, calibrating it against a known allocation. Then report bytes per
tick per system, so "0 GCs attributed to hoses" stops standing in for "0 bytes allocated". GPT and the Unity docs agree
that a GC pause lands in whoever is running, not in whoever allocated.

What I would not do now:
- JPS/JPS+, because our costs break it.
- LPA*/D* Lite: memory per hose and no tail guarantee.
- HDT dynamic connectivity: heavy, and nobody in games uses it.
- Field D* and the funnel algorithm: wrong fit.
- Factorio-style pressure or flow simulation: our scheduler already makes the segment abstraction choice.

## 5. What to stop doing, and the harness that replaces live tuning

Stop:

- **Treating one live maximum as a verdict.** One stall of 125 ms passed at 15.58 ms on a rerun (MEASURED). Live maxima
  include other mods (LargePawns 63-255 ms) and GCs anyone could have caused.
- **Using the full 321-mod list as the first experiment.** It should be the final integration check, not the
  optimization loop.
- **Calling a queue budgeted when one dequeued item can exceed the budget.** "One job per tick" is no bound if the job
  is unbounded. The same goes for a fallback that rebuilds everything synchronously.
- **Reading "0 GCs in my window" as "0 allocation".**
- **Trusting .NET 8 SelfTest timings as game timings.** Use them for correctness and operation counts only.

The offline harness, based on GPT's q6 design and fitted to our core:

1. **Record at the boundary of the Verse-free core:**
   - an initial snapshot: CordWorld arrays, hose endpoints and settings, tanks, topology, phases, pending queues;
   - an ordered event stream of `(tick, phase, sequence, event)`: edits, cuts, despawns, settings flips, rain cells,
     transfer requests;
   - outside values that the core cannot derive.

   Never record our own algorithm's answers as replay inputs. Start with traces of map1 under DRY, SETUP, RAIN and a
   cold load, over at least 10,000 ticks each. Add edge cases: 16,383, 16,384 and 16,385 dirty cells; a settings change
   touching every hose; aligned 250-tick rechecks; split and rejoin edits.
2. **Measure per tick, per system:**
   - elapsed time;
   - allocated bytes;
   - GC count;
   - work counts: A* expansions, cells patched, component visits, rechecks, relay steps, snapshot bytes copied;
   - queue depth and the age of the oldest job.

   Report mean, p99, max and the count of ticks over the bar. **A p99 pass never excuses a max failure.**
3. **Gate in two layers.**
   - **Every commit, on CoreCLR:** invariants (conservation, no flow over a cut, no stale false-NO), identical results
     on replay, zero steady-state allocation in the named hot paths, operation-count ceilings, bounded queues.
   - **Controlled timing lane:** fixed machine, the Mono runtime through BenchmarkDotNet's Mono job, plus an occasional
     calibration against the game's Mono. This lane is advisory; the counters are the gate.
4. **Keep live runs for calibration**, as one confirmation run per batch of fixes. They catch Verse integration costs,
   contention with other mods and real GC behaviour, and stop being the place where tuning happens.

## 6. Open questions

- **What causes the full-GC fallbacks?** Incremental GC is on (MEASURED), yet full pauses of 120-140 ms still happen.
  The cause could be total allocation across all 321 mods, reference churn, heap size, or an explicit
  `GC.Collect`. Our share of it is UNMEASURED.
- **Does `GC.GetAllocatedBytesForCurrentThread()` return real numbers on RimWorld 1.6's Mono?** UNMEASURED. The Unity
  version of 1.6 (GPT: 2022.3.35f1) is also UNSOURCED; read `Application.unityVersion` live.
- **What per-tick budget may one mod take on a 300-mod list?** No published figure was found. GPT's arithmetic for
  ultra speed is not verified: 360 TPS would leave 2.78 ms per tick. Our bars (< 10 ms per component max, ~0.2 ms
  mean) are our own.
- **How big is the backlog under the worst rain burst once work is sliced, and how stale can a hose look?** The replay
  harness has to answer this before slicing ships.
- **Is the clearance computed per query point a real cost?** It is UNMEASURED within lay time. Profile it before
  building the distance-transform field.
- **Could GSS re-plans run through the same sliced A* as hoses?** That would give one shared budget. This is a design
  question for whoever takes recommendation 2.

## 7. Method and limits

- **Rounds.** Seven GPT rounds ran with live web search (gpt-6.1-sol, high effort, read-only). Three earlier
  broad prompts timed out at 520 s without answering. The broad questions were split into six focused ones (q1-q6)
  plus a verdict round (q7). The transcripts are in the research folder.
- **Source checks.** I fetched 7 cited sources and found the cited claim in each: Factorio FFF-416, the Unity
  incremental-GC page, Detour's sliced API, the RimWorld TickList decompile, BenchmarkDotNet toolchains, the RimWorld
  1.1 announcement mirror and the LPA* paper.
- **Code checks.** I checked the following facts about our code directly:
  - per-call allocation in A*;
  - the dirty-list capacity and overflow;
  - the synchronous `CheckReplan` on the tick;
  - `Cell` implements `IEquatable` (so the A* `Dictionary` does not box);
  - `gcIncremental=true` live.
- **Not verified by me:** GPT's effort and gain estimates, and every row marked [GPT] that is not spot-checked.
