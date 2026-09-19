# TWINKLE_FLORA_SPIKE_1 — feasibility report

Owner ruling (`flora_commission_template.md` §8.2): "TIMEBOXED SPIKE: prove
a slow glow-pulse on ONE plant, measure the per-plant tick cost, report back
before any wider use." This is that report.

## Verdict: feasible, with one load-bearing design choice

A per-plant glow-pulse is cheap **if and only if** it is built the way the
prototype here is built — quantized color steps and a rare-tick cadence.
Built the naive way (continuous color, every-tick), it has a real, ongoing
cost that would matter at scale. The difference between those two isn't
tuning; it's the whole feasibility answer.

## The mechanism (verified against Source before writing any code)

Plants are **baked into a per-cell map-mesh section** and only re-rendered
when something calls `map.mapDrawer.MapMeshDirty(pos, MapMeshFlagDefOf.Things)`
— confirmed by reading `Verse/Thing.cs`, `RimWorld/Plant.cs` and
`Verse/CompGlower.cs`, all of which call exactly this for the same reason
(their appearance changed and the baked mesh needs a redraw). A comp that
just mutates a stored color every tick does **nothing visible** without this
call — the real cost to measure was never "a tick," it's "a mesh-section
regeneration," and that's an operation with a real, nonzero cost per call
(it rebuilds the render mesh for everything sharing that map section, not
just the one plant).

The second finding matters as much as the first: `Graphic_Single.GetColoredVersion`
(the standard way to get a differently-tinted version of a plant's sprite)
routes every distinct color through `GraphicDatabase.Get<Graphic_Single>(path,
shader, drawSize, color, colorTwo, data)` — a cache keyed on the exact color
value. A continuously-varying pulse color (e.g. `Mathf.Sin` sampled fresh
every tick) would mint a **new cached Graphic and Material forever**, one
per distinct float value, and never reuse one. That's an unbounded resource
leak, not a "slightly wasteful" pattern — and it's invisible in a short test
because the growth is slow, exactly the shape of bug that looks fine in a
five-minute check and bad after a week of play.

## The prototype

`src/RimUtinni/UtinniPatches/Source/TwinkleFloraSpike.cs` (compiles clean,
0 warnings — built and verified via `dotnet build`, not just read):

- `CompGlowPulse : ThingComp`, ticking on `CompTickRare()` (every 250 ticks,
  not every tick — a 250x reduction before any other optimization).
- The pulse is **quantized to `pulseSteps` (12) discrete color values** on a
  slow sine cycle (`cyclePeriodTicks`, default 15000 ≈ 4.2 in-game hours for
  a full low→high→low cycle — "slow" as the sheet asked). This bounds the
  `GraphicDatabase` cache to exactly `pulseSteps` entries per plant instance,
  forever, instead of growing without limit.
- The comp only calls `MapMeshDirty` when the quantized step actually
  changes — most `CompTickRare()` calls (11 of 12 phase positions, most of
  the time) land on the same step as last time and skip the dirty call
  entirely. So the real trigger rate is well under "every 250 ticks," closer
  to "every 250 ticks × (1 / pulseSteps) on average," i.e. roughly once
  every ~50000 ticks (~14 in-game minutes) per plant at these settings.
- `RUT_PlantTwinkle : Plant` — a thin subclass overriding `Graphic` (a comp
  cannot override its parent Thing's virtual members, so a subclass is
  required, not a style choice). Wraps whatever the base graphic would have
  been in the comp's current quantized color via `GetColoredVersion`.
- `RUT_TwinkleSpikeTestPlant` (`Defs/ThingDefs_Plants/`) — the one test
  plant this spike was scoped to. Reuses vanilla `Things/Plant/Bush` art (no
  new art commissioned for a mechanism spike). `tickerType` set explicitly
  to `Rare`, not inherited from a donor parent — a Thing's comps tick on the
  **same channel as the Thing's own `tickerType`**, so a `Long` or `Normal`
  plant would silently never fire `CompTickRare` at all. Not wired into any
  wildPlants list, biome, or commission — spawn it by hand to observe it.

## What was NOT measured, and why

The game was running throughout this spike (`RimWorldWin64.exe` live,
bridge free but the process up — a companion DLL cannot be deployed to the
live `Mods/` copy while the game runs). So the deliverable here is the
**built, compiling prototype plus the mechanism analysis**, not a live
benchmark number. Per this project's own rule, a live check is owed to a
mechanism never once observed running, not manufactured on demand by
forcing an extra load cycle for one spike.

**The measurement protocol for whoever next has the game down/up window:**

1. Deploy this mod build (`RimMandrake.Utinni.UtinniPatches.dll` already
   rebuilt in the repo's `Assemblies/`, includes both `GeothermalDensityField`
   and this spike's classes — same assembly, two unrelated features).
2. On a quicktest map (or the minimal-list dev colony), spawn N=200 and
   N=1000 of `RUT_TwinkleSpikeTestPlant` (bridge `jawa/spawn_thing` or the
   dev spawner) clustered in one map section, to stress the worst case
   (many plants sharing a section, all capable of dirtying it).
3. Compare `TicksPerRealtimeSecond` (or simulation-speed-at-3x) against the
   same N of plain `Plant_Bush` as a baseline, over several full pulse
   cycles (`cyclePeriodTicks` × a few, ~15-45 in-game hours simulated).
4. **EXPECT**: negligible difference from baseline at these settings — the
   dirty-call rate (~once per plant per ~14 real-minutes-of-ticks) is far
   below anything RimWorld's own vanilla glowers/growth-stage-change
   traffic already produces routinely. **LIES**: a difference would show up
   only under an unrealistically large single-section cluster; test at a
   density denser than any real wildPlants placement would ever produce, to
   find the actual ceiling rather than confirm the easy case.

## Recommendation

Feasible for wider use **as built here** — rare-tick, quantized-step,
dirty-only-on-change. Do not implement it any other way (continuous color,
every-tick, or an unquantized cache) without re-deriving why those are
unbounded costs, not just slower ones. The live numeric confirmation is a
five-minute check on the next game-up window, not a blocker to ruling on
the approach.
