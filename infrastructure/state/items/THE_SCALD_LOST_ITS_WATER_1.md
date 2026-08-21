## spec
`jawa/world_stats` reports **6.71% water** on the painted planet. The bundle says
**8.14%** — 1,780 of 21,872 tiles. The shortfall is exactly **312**, which is exactly the
Scald.

**The mechanism, read from source, not inferred:**

    RimWorld/Planet/SurfaceTile.cs:28
    public override bool WaterCovered => elevation <= 0f;

The Scald's 312 `Lake` tiles are authored at **elevation +1411 m** — it is a crater lake
inside a 2,050 m rim, by design. RimWorld defines water as *elevation at or below zero*, so
**the engine does not consider the Scald to be water at all.** `world_lint` was already
saying so: `lakesAboveSeaLevel: 312`.

⚠️ **DO NOT "FIX" THIS BY DROPPING THE ELEVATION** until the cost below is weighed. The
relief, the rain shadow, the Spine and the whole drainage story are computed from that
1411 m. Moving it re-rolls more than it repairs.

### What `WaterCovered == false` actually costs, enumerated from every call site

| call site | consequence for the Scald | material? |
|---|---|---|
| `GenStep_ElevationFertility:81` | a map generated on a Scald tile builds as **dry land, not a lake** | ⚠️ see below |
| `GenStep_RocksFromGrid:50`, `GenStep_RockChunks:21` | such a map also gets **rock**, which water tiles skip | ⚠️ same |
| `TileMutatorWorker_RiverDelta:65`, `RiverConfluence:30-33` | both pick the neighbour that is **not** water-covered. A delta emptying into the Scald does not behave as a mouth | ✅ **real** — we place `RiverDelta` on 2 tiles |
| `WorldDrawLayer_Roads:42` | roads draw only on non-water tiles, so a road across the Scald **draws** | cosmetic |
| `WorldGenStep_Rivers:67` | rivers terminate at water — only runs at worldgen, and we author links ourselves | none |
| the 14 vanilla `BiomeWorker_*` | only run at worldgen; we set the biome directly | none |

🔑 **The first two are mostly moot, and that is the finding.** `Lake` has
`canBuildBase: false`, so **a player can never land on a Scald tile** — the local-map
gensteps do not run for it in normal play. They would only fire for a quest site or a
caravan event placed there, which is rare and survivable.

⇒ **The honest cost is one broken `RiverDelta` behaviour, a road that draws where a boat
should be, and a water statistic that reads 1.4 points low.** That is a much smaller bill
than "the Scald is not water", and it is worth knowing before anyone edits 312 elevations.

### The three ways out, for DECIDE or the owner
1. **Accept it.** The design calls the Scald a *hypersaline pool*; brine over ground that
   plays as ground is arguably correct, and it costs almost nothing measurable.
2. **Drop the 312 tiles to elevation ≤ 0.** One column, same discipline as the rain clamp,
   and it makes the Scald real water — a caldera below sea level inside a 2,050 m rim is
   physically ordinary. ⚠️ But `elev_m` feeds the relief renderer and the lint's own
   `lakesAboveSeaLevel` check, so it must be looked at afterwards, not just measured.
3. **Leave the elevation and fix only the delta**, by moving the two `RiverDelta` mutators
   to mouths that empty into a real sea.

## verify
Whichever is chosen: `jawa/world_stats` water percentage, and `jawa/world_lint`'s
`lakesAboveSeaLevel` count, read back after the change. Option 2 should move water to
**8.14%** and `lakesAboveSeaLevel` to **0**.

## criteria
- the chosen option is recorded with its reason, so nobody re-opens this from the statistic
  alone
- if option 2: the owner looks at the relief around the Scald afterwards and does not name
  it as a defect
- if option 1 or 3: `lakesAboveSeaLevel: 312` is annotated in the lint as expected, so it
  stops reading as an unfixed fault

## notes
Filed for CHECK 2026-08-21. The statistic is the symptom; the mechanism is a one-line
definition in `SurfaceTile`. ⚠️ I nearly dismissed the 6.71/8.14 gap as "stats counts Ocean
only" when I first saw it — that guess was wrong in a way that would have hidden a real
mechanism, and the difference was reading the source instead of rationalising the number.
