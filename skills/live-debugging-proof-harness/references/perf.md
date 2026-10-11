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

## The instrument

`jawa/map_comp_timing` (`src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchMapCompTiming.cs`)
installs a prefix+finalizer timer on every MapComponent override and waits N **real**
ticks at the speed the caller set. Unpause first, because it never changes speed. It
then unpatches and returns per-type totals with the owning mod: `sumMsPerTick`,
mean and max per type. It is a TEST-profile tool: if the JawaBench profile has lapsed
it is refused as CAMPAIGN (see `run-checklists.md`).

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
