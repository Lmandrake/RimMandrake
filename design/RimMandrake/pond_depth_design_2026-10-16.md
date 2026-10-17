# Ponds shallow out before they turn to mud: design (2026-10-16)

Item: `POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD`. Owner ruling, by card 2026-10-16: *"Should natural water get partial depth
like dug cells? → Yes, ponds shallow out"*. DESIGN ONLY: no code, bridge or game was touched to write this. Claims about
code are **MEASURED (file:line)**, read from `/home/mandrake/rm/bench` at `b35e6fe427`, or marked **UNMEASURED**.
Vanilla facts come from RimSage (1.6 source and defs). Paths below are relative to
`D:\Luke\dev\RimMandrake\` (the mirror; the seat clones carry the same tree).

## 0. Summary

- **Today a natural pond square is either full to its bed or dry.** A pond is one stock number. Its wet squares each
  hold their whole bed. Recession dries the shallowest beds first (rim, shelves, middle last), one whole square at a
  time. So a drying pond shrinks from its edges and never gets shallower. (MEASURED, §1.)
- **The change: one flat water surface per pond, lowered by whole levels.** The pond keeps its single stock number and
  its bed record. From the stock we work out where the surface sits, *s* levels below the brim. Every square with a bed
  deeper than *s* stays wet and shows *bed − s* levels of water. Squares at or above *s* are dry. The last part-level is
  laid as one connected patch, like today's level solve does for dug cells. Nothing new is stored per square, so a
  40,000-square lake costs one histogram, not a per-square grid.
- **What the player sees, by water depth *w* in a square:** full (the square's original terrain) → still chest-deep
  (new def, vanilla art) → `WaterShallow` → *thin water* (**the only new art**) → `Mud` (just exposed, explained by the
  water beside it) → the existing cracked `RM_Lakebed_*` (dry).
- **Joining the level solve:** a pond touching a dug region joins that region's solve as **one combined node** (its
  bed histogram is its band capacity). So a pond and the canal it feeds settle to one flat level in a single pulse,
  and water moves between them by stock debit and credit. This uses paths that exist today; no new exit from the
  ledger.
- **Exempt:** limitless bodies (oceans, edge rivers: they never run down, ruling 16), all moving water, and the canyon
  flood's own cells.
- **Save migration:** none is forced. The stock is already the truth. A version marker re-lays touched ponds once on
  load. Ponds no canal has touched are never formed, so they change nothing.
- **Cost:** one histogram per limited pond, rebuilt at formation or load. Terrain writes happen only when *s* crosses a
  level, and are capped per pulse. ESTIMATED under 1 ms a pulse on the 14,400-square basin row. Its stated cost today
  is 6.2 ms a pulse against a 40 ms bar (`LevelSetChecks.cs:266-284`); the 6.2 is the caller's figure, re-measure it.

## 1. How it works today (MEASURED)

| fact | where |
|---|---|
| A natural square is a **source** only while undug: `depth == 0 && IsNaturalLiquid`; it reads as `Superdeep` through `DepthAt`. | `Source/RM_FlowKernel.cs:176-179`, `Source/RM_MapComponent_Excavation.cs:814-862` |
| "Natural liquid" = base terrain `IsWater`. Vanilla `IsWater` = has tag `Water` (`Verse/TerrainDef.cs:324`). So `WaterShallow`, `WaterDeep`, `Marsh` (via `WaterShallowBase`), the moving waters, and every terrain of ours parented to a vanilla water base are all "natural liquid". | `RM_MapComponent_Excavation.cs:814-818` |
| A body forms **lazily**, on first contact with a canal (`BodyAt` → `FormBody`, an 8-way walk of same-fluid source squares). Limitless = drain edge, or edge contact + size (ruling 16: classified once, never re-argued). | `Source/RM_LiquidStock.cs:112-248`, `Source/RM_StockMath.cs:91` |
| Bed per square: shallow water 2 levels, deep water (impassable, or path cost ≥ 40) 4 levels; a drainable lake's middle runs deeper, +1 level per 4 squares beyond 3 from shore, capped at 20, recorded once in the scribed `bedRecord`. | `Source/RM_Volume.cs:97-116`, `Source/RM_BedMath.cs:28-106`, `RM_MapComponent_Excavation.cs:124-129, 864+` |
| Capacity = Σ beds × `levelUnit`. A body is `stock`, `capacity`, `levelUnit`, `cells`, `receded` (a LIFO stack). | `Source/RM_LiquidBody.cs:26-130`, `RM_LiquidStock.cs:266-307` |
| **Recession sheds whole squares:** while the wet squares' beds (Σ) exceed the levels the stock covers, dry one more, shallowest bed first. `DryNaturalCell` writes `RM_Lakebed_{Shallow,Deep,Abyss}` (or the fluid's `recededTerrain`, `Mud`, with hollows off). Restore re-wets last-in, first-out, only when the square's **whole bed** fits. | `RM_LiquidStock.cs:669-704, 720-790`, `RM_BedMath.cs:119-140`, `RM_MapComponent_Excavation.cs:1560-1590` |
| Refill = seepage + rain × season, per pulse, for limited bodies only. A full, unreceded body is skipped. | `RM_LiquidStock.cs:509-573` |
| **No evaporation exists anywhere in FlowWorks.** `grep -i evapor` over `Source/` (selftests excluded) returns nothing. A pond loses water only to canals, pumps and drivers. | grep, 2026-10-16 |
| Dug cells show fill as **temp terrain** (`SetTempTerrain`) from `FluidDef.FillTerrainFor(FillTier(f,d), d)` (tiers at ≤⅓, ≤⅔, above). Natural squares change **base** terrain. | `RM_MapComponent_Excavation.cs:2077-2120`, `Source/RM_ExcavationDepth.cs:113-123`, `Source/FluidDef.cs:139+` |
| Level solve regions are **dug cells only**: the region walk requires `IsExcavated`. Natural sources pour in through the ordinary donor pass before the solve. | `RM_FlowKernel.cs:396-398, 653-731` (walk test at :696) |
| The solve counts at most 8 bands (`LsMaxBands`); deeper cells are clipped with `Math.Min`. | `RM_FlowKernel.cs:633, 785` |
| Edge sinks act only on **excavated** cells. A drain edge set by the map controls makes a touching body limitless. | `RM_MapComponent_Excavation.cs:1603-1617`, `RM_LiquidStock.cs:155-216` |
| The canyon flood writes base `WaterMovingShallow` on undug cells (and raises fill on dug ones through the engine). At recede it turns them to `SoilRich`, but only where its own terrain still stands. | `src/RimMandrake/FloodedCanyon/Source/RM_MapComponent_CanyonFlood.cs:28-43, 485-499, 555-576` |

Vanilla 1.6 still water has **only two depths**: `WaterShallow` (path 30) and `WaterDeep` (impassable). Chest-deep
exists only as moving water (`WaterMovingChestDeep`). Its abstract parent `WaterChestDeepBase` (path 42, texture
`Terrain/Surfaces/WaterChestDeepRamp`, walkable) is free to inherit. `Marsh` is a `WaterShallowBase` child
(`driesTo` Soil). RimSage: `Defs/Core/TerrainDefs/Terrain_Water.xml`.

## 2. How natural squares get levels

**No new per-square state.** The bed is already defined for every pond square (§1: terrain rule 2/4, or `bedRecord`
for a deep lake middle). A square's water is a function of the pond's surface:

```
V      = stock / levelUnit                       (levels the stock covers, RM_BedMath.SupportedLevels)
H[L]   = squares of the body whose bed ≥ L        (L = 1 .. maxBed; the band histogram)
s      = the smallest drawdown with Σ_{L > s} H[L] ≤ V
r      = V − Σ_{L > s} H[L]                        (whole levels left over for band s, 0 ≤ r < H[s])
w(sq)  = bed(sq) − s     if bed > s
       = 1               if bed == s and sq is in the r-patch
       = 0               otherwise
```

- **Shallow vs deep vs marsh:** set by the bed, as today. Shallow water and marsh are bed 2; deep water is bed 4; a
  lake middle is 4–20 from `bedRecord`. Marsh shallows exactly like shallow water. Its full-stage look stays
  `Marsh`.
- **The r-patch** is the band-*s* squares grown best-first as ONE connected patch. The order: nearest a draining mouth
  (when the pond is being drawn), else the deepest neighbourhood, then cell index. This is the same rule the dug solve
  uses (`RM_FlowKernel.CellKey`, `:899-912`; patch growth `:946-990`). So a pond with less than a level left is one
  puddle at the minimum depth, never a scatter.
- **Rounding:** today's `SupportedLevels` floor with its slack is kept. The fraction below one level stays in `stock`
  and shows nothing, exactly as today.
- The `receded` stack becomes **derived** (the squares with *w* = 0). It is kept in the save for one version so a
  downgrade still loads (§7).

## 3. How natural squares join the level solve

The dug-cell solve lays a region's volume over bands (`RM_FlowKernel.cs:635-652`). A pond is a band-structured
reservoir whose surface is always flat, so it fits as **one aggregate node**:

1. **Region building:** when a wet dug region (or its dry rim) touches a wet square of a LIMITED pond, the region
   records the pond's body id. It does not walk the pond's squares. Several ponds touching one region each become a
   node.
2. **Merge tree:** at band *L*, the pond node owns `H[L]` squares of capacity and joins the piece its touching dug
   cells belong to. A pond is connected at every band it holds water in. The rim-first assumption below is
   **UNMEASURED** on real map lakes: a ring-shaped pond could split at depth. A pond whose wet set splits is treated as
   one node, its surface shared, which matches today's `RM_RecessionSet` refusing to split a body (`RM_BedMath.cs:428`).
3. **Volume:** region volume + the pond's V. The solve lays it top-down as today.
4. **Write-back:** dug cells get their new fill. The pond's new V' becomes a stock change of (V' − V) × `levelUnit`,
   booked through the existing `TryDebitLevel` / `TryReturnLevels` paths (`RM_MapComponent_Excavation.cs:1461`). So the
   component ledger and the body ledger stay the only books (P-L0 conservation unchanged).
5. **Mouth rate:** today a pond gives at most `flowPerPulse` a donor per pulse. The aggregate solve moves the whole
   difference in one pulse, which a big pond and a small basin would make instant. **Keep the mouth limit:** the solve
   computes the target, then the stock moves at most `flowPerPulse × (mouth squares)` per pulse toward it. The dug side
   is re-laid with what actually moved. The level is still flat on each side, and the front still visibly advances.
6. **Head rule (RULED, a real behaviour change): water sloshes until it levels, and nothing climbs above the surface.**
   Owner's words (D2, 2026-10-16): *"It should slosh around until it levels, pond or canal or otherwise."* The rule: **one
   surface level across all connected water, whatever the body is**. A pond feeds a dug cell only while its surface is above
   that cell's water, and never once the pond has dropped below the channel's floor: water never rises into a ditch floor above
   the surface. Today a natural source is a `Superdeep` donor that supplies until its stock is empty
   (`RM_FlowKernel.cs:1050, 1153-1156`). Under this rule a one-deep ditch stops drawing once the pond has fallen two levels,
   and the player digs deeper to keep drawing. Test: after settling, every connected wet square (pond, canal, basin) sits at
   the same surface height, and no wet square has a bed floor above it holding water.
7. **Limitless bodies** join as a fixed head at the brim (s = 0, infinite H). That is today's behaviour, in solve
   form.

## 4. Visible stages

The shown terrain is a function of *w* and the square's original terrain *T0* (already recorded by
`RecordOriginalTerrain` before any write):

| *w* | shows | source | new? |
|---|---|---|---|
| *w* = bed (full) | *T0* itself (`WaterDeep`, `WaterShallow`, `Marsh`, our biome water) | the map | no |
| ≥ 4 (below full) | `WaterDeep` (or *T0* when *T0* is deep) | vanilla | no |
| 3 | **`RM_WaterChestDeepStill`**: a def on `WaterChestDeepBase`, vanilla `WaterChestDeepRamp` art, path 42, walkable, no `MovingFluid`, no `River` tag | vanilla art, new def | def only |
| 2 | `WaterShallow` (marsh: `Marsh`) | vanilla | no |
| 1 | **`RM_WaterThin`**: ankle-deep, the bed showing through. Water tag kept (fish, splashes and fire still behave as water), path 18 or so | **new art** | **yes, 1 texture** |
| 0, just exposed | `Mud` (vanilla). It is wet ground and counts as riverbank (ruling W2) | vanilla | no |
| 0, after the mud time | `RM_Lakebed_Shallow` / `_Deep` / `_Abyss` by bed (`RM_Volume.LakebedFor`, `:150-160`) | ours, exists | no |

- **Non-water fluids** (tar, slime, brine, our coloured waters) reuse their existing fill tiers.
  `FluidDef.FillTerrainFor(tier, 4)` already holds three depth looks per fluid, painted from vanilla's three ramps
  (`RM_LiquidLooks.TierTexture`, `Source/RM_LiquidLooks.cs:220-225`). A fluid with no tiers authored keeps
  full-or-empty for its ponds and logs once: a missing look is better than a wrong one. Same stance as
  `DryNaturalCell` (`RM_MapComponent_Excavation.cs:1566-1580`).
- **Mud time:** a square stays `Mud` for `pondMudDays` (Mod Setting, default 2 days), then turns to lakebed. Water
  returning in that time skips the lakebed step. The mud is always explained by the pond beside it (ruling GM1, *"Nothing
  stays wet for long without an obvious reason"*).
- **Art owed:** one terrain texture, `RM_WaterThin`, judged against vanilla `WaterShallowRamp` at true scale on a review
  sheet. RULED D4 (by card): yes, make it, judged on a true-scale sheet beside vanilla shallow water (the art round is approved). Fallback if the art is rejected, *w* = 1 shows
  `WaterShallow`. A bed-2 pond then looks unchanged for its first level, and only deep squares visibly shallow.

## 5. Evaporation, refill and growth

- **Evaporation:** none exists today (§1). This item adds none by default. Ponds on this world are seep-fed and the
  owner ruled water is *used up* by people and plants, not by the sky. RULED D3 (by card): no evaporation; only people and plants use water up. No evaporation setting is built.
- **Refill:** unchanged in source (seepage + rain × season). The surface rises, so every wet square deepens at once,
  and lakebed squares re-wet when *s* rises past their bed. **Ruling 5** (*"water waits for people and buildings; items
  wash ashore"*) still holds per square: an occupied square stays dry. Its band share goes to the next square in patch
  order. If no square can take it, the stock is not spent (the stock is the truth and the terrain is only the
  picture), so conservation is exact.
- **Explosive growth** (`design/RimMandrake/explosive_growth_rulings_2026-10-16.md`):
  - W3: *"It always counts as fresh as long as it's there. It's continuous."* Every square with *w* ≥ 1, and every
    mud square, is fresh ground for as long as it stays that way. No timer.
  - W2 (riverbank): only the water and mud squares count. A cracked lakebed square does **not**. So a drying pond's
    growth ring follows the shoreline inward, as the shore moves.
  - The handoff is `ExplosiveGrowthAPI.SoakCells` (`src/RimMandrake/ExplosiveGrowth/Source/ExplosiveGrowthAPI.cs:25`,
    used by the canyon flood at `RM_MapComponent_CanyonFlood.cs:499`). Each mud write soaks the square for the mud
    time.
  - How growth reads "a water square" today is **UNMEASURED**. `RM_SoakSources.cs:147` skips `IsWater` terrain for
    rain soak. The new `RM_WaterThin` and `RM_WaterChestDeepStill` carry the `Water` tag, so any `IsWater` test treats
    them like vanilla water.

## 6. Rivers, moving water and the canyon flood

- **Moving water is exempt** (`MovingFluid` affordance, or the `River` tag). A river that touches the map edge is
  limitless, so it never recedes (ruling 16, `RM_LiquidStock.cs:520-528`). An inland moving-water body is also skipped
  by the depth model: there is no still-water picture for a current. **UNMEASURED:** whether any inland moving-water
  body forms as LIMITED today; the selftest row S6 below pins whichever answer the code gives. Weir pools
  (`Source/Rivers/RM_Weir.cs`) keep their own model; folding them in is a later item.
- **Sources:** a pond's sources stay what they are: seepage and rain into stock. A river feeding a pond (a limitless
  body touching a limited one) is a separate body today, so it does not refill the pond. Unchanged.
- **Canyon flood:** the flood's `WaterMovingShallow` squares are `IsWater`, so a canal touching flood water could form
  a body from them. That would be a pond the flood later paints `SoilRich`. This design **excludes flood-owned squares
  from body formation** (the flood ledger already knows them). It is required because the depth model would otherwise
  rewrite those squares' terrain while the flood owns them. Whether this already happens today is **UNMEASURED**: it
  is filed as a check, not as a confirmed bug. In the Utinni campaign this is the only natural flood (ruling WP1).
- **Moisture pump** (vanilla `CompTerrainPumpDry`, which dries terrain to its `driesTo`): it rewrites base terrain under
  a pond. A pond square the pump dried leaves the footprint the way a dug bed square does
  (`RM_LiquidStock.DetachBedCell`, `:355-380`), so the stock is not shown on a square that is no longer water.
  **UNMEASURED** whether FlowWorks handles the pump today.

## 7. Save migration

- New scribed int on `RM_MapComponent_Excavation`: `RM_pondDepthModel` (missing = 0, the full-or-empty model).
- On load with the model at 0 and `pondDepthEnabled` on: for each LIMITED body that is not full, or that has any
  receded squares, build the histogram, compute *s*/*r*, and queue the stage terrain writes. Bodies that are full and
  unreceded, limitless bodies, and never-formed ponds change nothing. Then set the model to 1.
- **Conservation:** the stock is unchanged, and only its picture moves. A half-drained pond that loaded as "rim
  squares dry, middle full" re-lays as "every bed-4 square half full, rim mud". One log line per body: id, *s*, wet
  squares before and after.
- **Original terrain:** each stage write records *T0* first, as `DryNaturalCell` does
  (`RM_MapComponent_Excavation.cs:1581`). A square already receded keeps its record.
- **Turning it off** (or a downgrade): re-lay with the old shed rule from the same stock. This is the same code path
  as the migration, run the other way, and the selftest pins it (S5).

## 8. Cost

- **Histogram:** O(footprint) once per formation or load. A 40,000-square lake (`DefaultDrainableLakeCells`,
  `RM_BedMath.cs:46`) is ESTIMATED at about 0.5 ms, once.
- **Per pulse, per drawn pond:** O(maxBed) to find *s* (at most 20). The r-patch is regrown only when *r* changes, as an
  incremental add or remove on its frontier. ESTIMATED O(Δr log H[s]).
- **Terrain writes:** only when *s* crosses a level, or when a square enters or leaves the patch. One crossing on a
  40,000-square lake can restage thousands of squares, and the cost of `SetTerrain` per square (section mesh rebuild,
  path grid) is **UNMEASURED**. So writes go through a queue capped at `pondStageWritesPerPulse` (Mod Setting, default
  400). The terrain may lag the stock by a few pulses; the stock and the solve never lag.
- **Bar:** a new cost row (S7) on a 40,000-square drawn lake, plus the existing 14,400-square basin row with a pond
  attached. Bar: under 10 ms a pulse added, in the selftest harness. Today's figure for the 14,400 row is 6.2 ms a pulse
  (the caller's figure; the row lives at `LevelSetChecks.cs:266-284`; re-measure it).
- **`LsMaxBands = 8`:** a pond node can hold beds to 20. The aggregate node keeps its own histogram, so the 8-band clip
  stays on dug cells only. **UNMEASURED:** whether a dug cell deeper than 8 is reachable today. Dug depth tops out at
  `Superdeep` (4) on the normal path.

## 9. Mod Settings

All of these go under the existing ponds group, with defaults equal to the shipped behaviour:

| setting | default | when it takes effect | meaning |
|---|---|---|---|
| `pondDepthEnabled` | on | next pulse (re-lays touched ponds) | Ponds shallow all over. Off: today's full-or-empty squares. |
| `pondMudDays` | 2.0 | next pulse | How long an exposed pond square stays mud before it cracks to lakebed. |
| `pondStageWritesPerPulse` | 400 | now | Terrain restages per pulse (cost guard). |
| `pondHeadRuleEnabled` | **on** (RULED D2) | next pulse | One surface level across connected water: a ditch draws from a pond only while the pond's surface is above its floor. Off: today's draw-to-empty. |

All-off degrades to today exactly. The biome promise (owner 2026-10-15) still applies: ponds in our biomes are the
validated case.

## 10. Tests

**Offline selftests** (the C# SelfTest project plus the Python `PulseOracle` mirror, which must agree,
3000/3000 differential, as the level solve does today):

| row | scene | passes when |
|---|---|---|
| S1 shallow-out | 10×10 pond, rim bed 2, middle bed 4, drawn one level a pulse by a canal | after 1 level: no square is dry, every bed-4 square reads 3. After 2: the rim is mud and the middle reads 2. The sum of the terrain-implied levels always equals floor(V). |
| S2 min-depth patch | the same pond with V < H[s] | the wet squares at band *s* form one 4-connected patch; never 0,1,0,1 |
| S3 join | a 5-square pond plus a 100-cell dug basin, mouth one square | settles flat across both, within the mouth-limited pulses; ledger imbalance ≤ 0.001 |
| S4 head rule | a pond drawn below a depth-1 ditch's floor | the ditch stops receiving (with the rule on), or matches today's numbers (off) |
| S5 migration round trip | a model-0 save body, half drained → load → toggle off → on | the stock is identical at every step, and *s* and the wet set are identical after each re-lay |
| S6 exemptions | a limitless edge river, an inland moving-water body, a canyon flood cell next to a canal | none of them is ever restaged, and no body forms from a flood-owned square |
| S7 cost | a 40,000-square lake drawn for 100 pulses, plus the existing 14,400-square basin with a pond | added ms a pulse under the bar in §8; the queue drains |
| S8 refill with occupants | a pawn on a lakebed square as the surface rises over it | the square waits; its share goes to the next square; the stock is conserved |

**One live row** (`northstar/liquid_checks.py`, new `L8`, on the review map): a station pond is drawn by a pump for N
pulses. Read through `jawa/flowworks_body_report`: *s*, the wet count, and a terrain census over the footprint (counts
of deep, chest, shallow, thin, mud and lakebed). PASS when the wet count holds while *s* rises by one, and the census
moves deep → chest → shallow. A shrinking wet count means FAIL. Read the state with two reads a pulse apart; no
screenshots are needed.

## 11. Order of work (ESTIMATED)

1. Histogram, *s*/*r*, the derived recession set, the toggle, and S1, S2, S5. About 1 day.
2. Stage terrains: the `RM_WaterChestDeepStill` def, the write queue, mud time, the growth soak, and S6, S8. About
   1 day.
3. Joining the solve (aggregate node, mouth limit, head rule), S3, S4, S7, and the oracle mirror. About 1.5 days.
4. `RM_WaterThin` art (D4 approved), then the live row L8.

## 12. Rulings (owner, 2026-10-16)

- **D1 RULED (by card):** one flat level, flowing through the mouth at the mouth's pace (§3).
- **D2 RULED (owner's words):** *"It should slosh around until it levels, pond or canal or otherwise."* One surface level across connected water, whatever the body; nothing climbs above the surface (§3.6).
- **D3 RULED (by card):** no evaporation; only people and plants use water up (§5).
- **D4 RULED (by card):** yes, make `RM_WaterThin`, judged on a true-scale sheet beside vanilla shallow water; art round approved (§4).

## 13. Build consequences

1. Aggregate pond node joins the level solve with the mouth-rate limit (D1); the head rule is built, default on, and is the general law: any connected water (pond, canal, basin, and "otherwise") levels to one surface, not only pond-to-ditch.
2. Add selftest S4 as the leveling law (all connected water equal surface); extend S3 to assert equal surface across a pond, a canal and a third body.
3. No evaporation code and no evaporation setting.
4. Commission `RM_WaterThin` now: one texture, review sheet beside vanilla `WaterShallow` at true scale.
5. Mud-before-lakebed (`pondMudDays`) and the other stages are unchanged.
