<!-- excerpt of design/RimMandrake/flowworks_pipes_across_pits_design_2026-10-20.md, section ### Levelling feasibility, as of 2026-11-12 02:44 -0800 -->
### Levelling feasibility

Item `PIPE_LEVELLING_BUILD_WATER_FINDS_ITS_LEVEL`, 2026-10-20 (owner: *"Let's see if we can do this"*). **Verdict:
feasible, and built behind a Mod Setting. The offline selftests pass, and so did the live runs (2026-11-12, below).**

- **What already existed (MEASURED).** Every body already stores exact decilitres, and all bodies share one surface
  convention (dL per square, 0 = brim, negative below ground). A dug square is `WaterDl − depth·U`. A pond is
  `RM_LevelSolve.PondSurfaceHeight(hist, stockDl)`, cached per pulse in `RM_LiquidStock.SurfaceHeightOf`. A limitless body
  stands at 0. The pump's world-to-world move already has reversible legs for both kinds of end
  (`Building_LiquidPump.cs` ~l.324: `TryTakeDl`/`TryPourDl` for a dug square, `Stock.TryDebitDl`/`CreditDl` for a pond).
  Tanks drain by gravity in `RM_LiquidNet.SettleTick`, every 250 ticks (`RM_PumpMath.CycleTicks`), from
  `RM_MapComponent_Excavation.MapComponentTick`. Levelling hooks into that same tick, just before the settle.
- **Solver shape.** The kernel is `Source/RM_LevellingMath.cs`, which is Verse-free. Each body is a floor histogram plus
  its dL, a liquid, a key, and a limitless flag. Each link records the floor under each end, what each end can give, and
  what each end can take. Links are visited in a fixed order, Gauss-Seidel style: each link plans against the volumes
  that earlier links in the same cycle left behind. That makes parallel links add up, and a body on many links is never
  overdrawn.
  - A link moves water from the higher surface to the lower one. The amount is the smaller of two limits: the rate
    (`levellingLitresPerCycle`, 1,000 L per link per cycle), and half of what would bring the two bodies level. The
    level point is found by bisection on the exact surfaces.
  - Because a move never goes past half-way, it can never reverse a gap. Heights therefore converge monotonically and
    cannot oscillate. The halving also absorbs model error, for example a run that counts too much area at a sill.
  - Same key: nothing moves. Different liquids: nothing moves. A dry receiver takes the source's liquid. A source stops
    when its surface reaches the floor under its end (exposed intake). There is no crest test, so a siphon always works.
- **Game adapter.** `Machinery/RM_Levelling.cs`. A link is two open hose ends (Intake or Outflow) on one network
  component. Each end is resolved the way a pump finds its source: the end square, then its 8 neighbours. Rigid pipe
  reaches a body only through such ends.
  - A dug end's body is the 4-way run of wet squares of its liquid, walked from that end. A natural end's body is its
    pond.
  - Skipped: a component with a working pump, and exact-level water switched off.
  - The mover is `RM_LiquidTransfer.Move` with the pump's own legs, and it credits the hose's flow art.
  - The hose's inspect line shows the link state: flowing, level, same water, different liquids, intake out of the
    water, or no room.
  - Settings: `gravityLevellingEnabled` (on) and `levellingLitresPerCycle`, in the Flexible hoses section.
- **Cost per tick (offline, MEASURED by the selftest).** The kernel plans a hard budget of 64 links per cycle; the rest
  rotate in later and catch up by up to 8 cycles' worth. The test scene had 200 bodies, 40 of them 40,000-square basins,
  and 400 links. Planning took **89 µs per cycle, about 0.36 µs per tick**.
  - The adapter's walk of dug runs is capped at 20,000 squares per run and 60,000 squares per cycle. MEASURED live
    2026-11-12 (SteveDesktop, FlowWorks tier, 325×325 map, two 38,125-square basins, 200 links, 20 timed cycles): the whole
    `RM_Levelling.Tick` averaged **14.0 ms per cycle (0.056 ms per tick)**, worst 53.8 ms in the one cycle that held a GC,
    and grew the managed heap ~460 KB per cycle (`pipe_levelling_perf_proof.py`; evidence in
    `whittle/pipe_levelling_build_water_finds_its_level/evidence/A3_perf_timed_200_links.json`).
- **Selftests** (`Source/SelfTest/LevellingChecks.cs`, all green). The four gates were checked every cycle:
  - volume exact, counting what limitless bodies gave or took;
  - energy never rising, and in two-body scenes the gap never growing;
  - no link reversing and no gap changing sign;
  - no exchange between liquids.
  The fuzz covered 300 scenes, all of which reached a fixed point. The item's L1 cases also pass: a 1-square pit
  against a 100-square basin, ten parallel links, a same-body loop, a siphon, an exposed intake, water against oil, a
  dry receiver, and the sea filling a pit to the brim.
- **Risks.**
  1. The adapter treats a dug run and a pond joined below the surface as two bodies. Their surfaces already match, so it
     moves nothing, but the readout says "level" rather than "same water".
  2. A run bigger than the walk cap is under-counted. That only slows levelling; it never overshoots.
  3. The pour lands near the receiving end and the pulse spreads it. Between pulses, that end reads high, which errs
     toward moving less.
  4. A hose's held contents do not fill from a passive move.
  5. Levelling stops whenever a working pump is on the network, and resumes when it stops: the owner kept that by card
     (2026-10-21, "With pump → Off while pumping").
- **Live (2026-11-12).** Two 3×3 pits of unequal height joined by two reels on one pipe run level out: the reel reads
  "Levelling: flowing" from the first cycle and "Levelling: level." once the surfaces are within 1 cm, total conserved;
  a water pit and a chemfuel pit joined the same way exchange nothing and both reels read "different liquids never mix".
  Save/reload mid-flow replays exactly. Evidence: `whittle/pipe_levelling_build_water_finds_its_level/evidence/`.

