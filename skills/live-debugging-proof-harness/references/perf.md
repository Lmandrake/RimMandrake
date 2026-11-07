# Perf readings

`debug_process.md` §4 puts performance outside Boolean checks: no instrument yet
gives a pass/fail it would be safe to trust. A perf row is still worth having,
because the only mod bug found in the 2026-10-11 validation was a perf bug. The rules
below are what make a perf number mean something.

## Time the production function, live

**A perf selftest that times a MODELLED cost cannot see the real one.** The hose
port's offline perf row (SelfTest `HoseNetCacheChecks`, 0.00105 ms/tick) timed a
synthetic net walk and index rebuild. It passed while:

- `RM_HoseLinks.Refresh` was O(n³ log n), and the idle debug provider walked every
  hose every tick;
- live on the full list, `RM_MapComponent_Hoses` cost **0.152 ms/tick, max 4.6 ms**,
  3x the FINAL §3.5 budget of ≤ 0.05 ms/tick for 20 reels, 4 pumps and 10 tanks.
  That was with **no pumps at all**.

**Root cause: a per-tick cache defeated by staggered per-thing checks.** Each laid
reel ran its 250-tick corridor check at `(now + thingID) % 250`. `World()` is a
whole-map 250×250 snapshot cached per tick, so it was rebuilt once per laid reel per
cycle (11 × ~3.5 ms / 250 ≈ 0.15 ms/tick, which matches). The cost grew linearly with
laid hoses. The fix was to read only the corridor cells off the map (bbox ± 2) and
build `World()` only on a real re-lay. After the fix it was 0.024 ms/tick on the same
map, and 0.032 / 0.037 on a 30-reel / 6-pump / 8-tank map (`e64a8af8a`).
- **Offline cost bounds on FlowWorks C# do not predict live cost until the gap is explained.** An offline CoreCLR harness predicted a 2.6 ms worst excavation pulse slice; live Mono measured 161 ms. The harness drove only the kernel through a fake world, so the adapter's `ComponentResolved -> SetTerrain` per look-band change (~25 us each, up to 6000 in one slice) never ran; Mono also runs the same kernel ~2x slower than CoreCLR. Count the callbacks per pulse and price each one live, and confirm every perf fix live before closing.
- **Timing `RM_LiquidNet.Components()` right after a topology bump measures only cache hits (5-7 us).** `RM_NetComponents.Build` is lazy and runs on the next query from a tick, so profile `RM_NetComponents:Build` while ticks run (the `ln2.py` pattern) or the rebuild cost is invisible.
- **`jawa/safe_advance` and `step_game_ticks` advance time with TickManager PAUSED** (DoSingleTick inside paused frames), so a `MapComponentUpdate` hook that treats Paused as 'no tick will pass, rebuild unthrottled' runs every stepped frame (RM_WallReach rebuilt ~1 labelling per tick against a throttle of 8 per 60). Judge a paused frame by whether `TicksGame` moved since the last one, never by the Paused flag alone.
- **A stall that persists while the game is PAUSED is frame work (`MapComponentUpdate`, a draw), not a tick: profile `Root_Play.Update`.** The last Player.log line before a freeze is not the cause (a freeze blamed on pond-depth pulses was `RM_MapComponent_Hoses.DrawAll` -> `EnsureLay` -> `LayFrom`, re-laying every hose in one frame after a `maxLength` settings write).

## The instrument

`jawa/map_comp_timing` (`src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchMapCompTiming.cs`)
installs a prefix+finalizer timer on every MapComponent override and waits N **real**
ticks at the speed the caller set. Unpause first, because it never changes speed. It
then unpatches and returns per-type totals with the owning mod: `sumMsPerTick`,
mean and max per type. It is a TEST-profile tool: if the JawaBench profile has lapsed
it is refused as CAMPAIGN (see `run-checklists.md`).
- **`jawa/map_comp_timing` times only `MapComponentTick` overrides** (`JawaBenchMapCompTiming.cs`). AtmosphericBase's compositor runs in `MapComponentUpdate` (per frame, real time, also while paused) and its map component has no Tick override, so the tool reads it as absent/0 ms and a perf PASS from it is blind. Take a per-frame mod's cost from the mod's own Stopwatch around Evaluate plus its work counters, or from an Update-timing variant. Sanity probe: the component must appear in the tool's `components[]` with `calls>0` before any 0 ms reading counts.
- **`jawa/health_profile` refuses an allowlist over 32 entries and refuses overloaded methods as 'ambiguous (2 overloads)'** (`RM_MapComponent_Hoses:EnsureLay`, `HoseMath:Layer`), but the window's `map_comp_timing` still runs, so a profiled window silently yields timing with no profile, and a driver that ignores the refusal reads the PREVIOUS window's profile as the new one. Count entries before arming (MINBASE + EXTRA must be <= 32; the exprof arm with 37 entries profiled nothing), give overloads a signature or leave them out, require the arm output to match `^START True (None|\[\])`, mark the window PROFILER ARM INVALID otherwise, print the raw refusal and exit non-zero (`tprof.py` exits 3).
- **Count GC live with a row sampler, never around `jawa/map_comp_timing` windows.** `GC.CollectionCount` read around plain Superfast running (get_game_info + GC reads) gave 6.26 and 11.47 full GCs/10k ticks; 20x500-tick `map_comp_timing` windows in the same game read 22.8 and 46 because the tool's own patching and allocation inflates the count ~4x, and with a gen2 in 95-100% of windows the windows cannot pair slow ticks with GCs. A main-thread `GC.GetTotalMemory(false)` delta around a call is not that call's allocation either (other threads allocate in between; Levelling calls that allocate nothing read up to 13 MB): diff `GC.CollectionCount(0)` to ask whether a collection landed inside a call (Mono Boehm makes gc0=gc1=gc2), and measure allocation offline in the SelfTest's allocation-free cases.
- **`GC.GetAllocatedBytesForCurrentThread` is BLIND in RimWorld's Mono (1.6, Boehm):** it binds by reflection but reads 0 B across a fresh 1 MB `byte[]`, so any per-thread alloc number from it in game is a zero from a blind instrument. Prove zero-alloc offline on CoreCLR (exact there) and in game count GC collections landing inside the code's ticks.
- **On Mono a burst of allocation can stall a tick 10+ ms with `GC.CollectionCount(0)` unchanged.** `HoseRelayIndex`'s ctor (~82 KB, ~1600 small Lists plus a growing Dictionary) took 13.4 ms on a 'no-GC' tick, typically 0.8 ms. A tick splitter that files only CollectionCount-bumped ticks as GC will blame the code; time the allocating block separately and make the hot rebuild allocation-free (measure with `GC.GetAllocatedBytesForCurrentThread` in the net8 SelfTest).
- **A zero-allocation claim backed by source pins covers only the pinned bodies, not their callees.** `HOSE_TICK_REBUILD_ZERO_ALLOC` pinned `HosePorts.RawFind/RawFindAt` clean while their callee `HosePortRule.Pick` still built an EdgeCells list per side per candidate (704 B a call). Back the claim with a measured `GetAllocatedBytesForCurrentThread` delta over the whole Verse-free call, with a probe showing the counter registers an allocation.
- **RM_WallReach `TimingLine` `maxSliceMs`/`maxTickMs` are per-map session maxima that `ProofReachReset` does not clear,** so every window's ProofReach line repeats the first window's max (a 3.227 set in SETUP showed in every later window). Read per-window slice cost from the profiler (arm tprof with `RM_WallReach:Tick` and the slice parts) or add a reset before judging a slice bar. Stopwatch maxima 50-400x the mean on trivially cheap calls (BeginJob max 1.1 ms, mean 2.5 us) mean a <=1.2 ms max bar measures main-thread stalls, not the code: use a percentile.

## What a perf row owes

1. **A map at least as big as the budget's scenario.** Name the census: reels, laid,
   pumps, tanks, pipes. Name the ticks sampled (≥ 1,200).
2. **The same scenario before and after**, when the row exists to judge a fix. A
   pre-port fixture save is ideal for this.
3. **A work counter on the real inner call.** For example `HoseRelay.IntakeCellCalls == n`,
   or the census fields `worldBuilds` / `liveCorridorChecks`. Stepping 750 ticks paused
   must give `worldBuilds +0`. A time alone does not say why it is fast.
4. **A can-fail.** Run the old per-query shape through the same counter and see it
   go red.
5. **An equivalence probe** when an optimisation replaces a computation. The `corridor`
   probe compared the live hash with the snapshot hash for every laid reel (11/11,
   19/19). A mismatch would have forced a re-lay every cycle.
6. **What it does NOT cover**, said once. For example: the pumps' own ThingTick is not
   timed by a MapComponent instrument.

Whole-map context helps a reader judge a number: on that map the sum over 236 patched
components was 0.64 ms/tick, and HugeThings' `MapComponent_HugeFootprints` (0.308) was
the top cost.
- **A live GC storm can be predicted offline.** Unity's Boehm GC collects about once per heap/3 bytes allocated, so GC count ~= bytes allocated / (heap/3): 200 lays x 340 MB on a 3.45 GB heap ~= 60 GCs, which is what live showed. Measure per-op garbage in the net8 SelfTest with `GC.GetAllocatedBytesForCurrentThread` around the op and split it with temporary byte-clock laps; set the bound from the target GC count (6 MB gave ~1 GC per wave; 64 KB was unreachable), not a round number. Before landing an allocation refactor, prove it behaviour-preserving by hashing every lay's points before and after (504 lays, bit-identical).
- **A per-frame timer must cover the method's publish tail.** GSS `Rebuild` timed snapshot+Build (2-5 ms) while an untimed tail (string union-find and section signatures over every piece) ran O(map cords) and made ~3.7 MB garbage per frame, feeding the stop-the-world GC (a lone 140 ms slice). Time the WHOLE method, tag frames in which `GC.CollectionCount(0)` changed, and keep a resettable window max beside any lifetime max. A wall-clock bound in a GSS selftest (`SliceGateChecks` 'planned build E=248 ... bound 20 ms' read 25.9 ms once) flakes under a parallel harness load.
- **A cross-run fingerprint (e.g. hashing hose lays to prove a refactor byte-identical) must not use `string.GetHashCode`.** The FlowWorks selftest runs on net8.0 where string hashes are randomized per process; hash the chars yourself. A 256-lay fingerprint on the 325 basin map exceeds the 540 s tool budget; 64 lays fit.
- **A windowed max reported beside a 'last' phase split cannot be attributed.** `winMaxSliceMs` of 86 ms came back with a 6-9 ms `rebuildPhasesMs` from a later rebuild: record the WHOLE record of the max sample (phases + unattributed gap) at the moment it becomes the max (GSS `SliceWindow`). RimWorld's Unity runs incremental GC (boot.config `gc-max-time-slice=3`), so an unchanged `GC.CollectionCount(0)` across a slice does not prove no collector pause landed in it; if another thread (the lay worker) stalls for the same ~90 ms, it is a process-wide pause.
- **A TPS reading is only comparable to another taken on the same save and map set.** The JawaBench sampler session records no scene key, so one map 250 (calm save) vs two maps including a mid-session 325x325 PerfSite looked like a 3x mod-list regression that a like-for-like reload disproved (355 vs 354 TPS). Loading a save made on another mod list can also raise many forcePause VEF `Dialog_NewFactionSpawning` modals that hold ticks at 0 while the bridge reports Playing: close them all before measuring (`tps_bisect/scripts/closefs.py`).
- **Measure a pulsed MapComponent over several full pulse periods (>=4000 ticks), not ~900.** Excavation read 0.62 ms/tick, max 29 ms over 982 ticks but 1.05-1.18 ms/tick, max 129-308 ms over 4000 ticks on the same scene minutes later.
- **Before optimising a per-tick phase, read its counter split.** WallReach.Tick's cost outside Build was the STAMP phase (`StampOf -> SwimVersion -> RM_SwimPathing.VersionOf -> For`, which rescans all 105k cells to rebuild the swim block grid whenever the swim version moved), not `FlushDeltas`: 4499 ticks with 30 swim bumps spent flush 4.0 ms vs stamp 544 ms (30 bumps -> 544 ms, 23 -> 62, 1 -> 38, 0 -> 9). The offline suspect was wrong. A per-tick shared refresh (e.g. `RM_HoseLinks.For`, the hose signature over every reel) is also paid by whichever system asks first in the tick, so a per-system profiler charges it to that system (Levelling's 40 ms max was 40.1 ms of HoseLinks with zero levelling work): split shared-refresh time out of every per-system timing.
- **A per-method MAX in `jawa/health_profile` can be a GC pause or setup, not the method's work.** `DrainTerrainWrites` showed max 70.8 and 137.5 ms in pocket-rain windows (budget 200 writes/tick; other windows 2-5 ms) because a gen0 collection (3.8 GB heap) landed inside the write (the slowest-write record carried gc0=1); a pocket-deluge '134 ms gc0' was the session's absolute max taken during setup, and the 137.5 ms drain was a stall outside SetTerrain. Before blaming a method for a lone spike, check whether a GC counter moved in that tick, split the max by phase (setup vs steady) and by sub-call, and attribute only a spike that repeats across windows with no GC.
