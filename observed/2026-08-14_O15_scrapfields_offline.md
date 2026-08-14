# O15 — scrapfields shortfall, the OFFLINE half

_2026-08-14. Read-only investigation. Assembly `RimWorld 1.6.4871 rev591` at
`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64_Data\Managed\Assembly-CSharp.dll`,
disassembled with `D:\Luke\dev\Rimworld\src\RimMandrake\Utils\ilprobe\il.py`.
A DLL has no line numbers; every engine claim below carries type + method + IL offset._

---

## 🔴 Headline: the framing question "where did the other 64+ go?" is not answerable as asked, because the offline evidence says **they did not go anywhere — they were placed**

Three facts, each independently established below, cannot all be true at once. Two
of them are engine behaviour read out of the IL and are not negotiable. The third
is the measurement. **The measurement is the term that has to give.**

| # | fact | source |
|---|---|---|
| 1 | The hulk warned ⇒ its `finalCount >= 1` ⇒ the tile's placement factor **f >= 1** | `Player.log:6759` + IL below |
| 2 | Scrapfields **did not** warn ⇒ its placement loop never failed ⇒ it ran to completion ⇒ **>= 75 chunks were spawned** | live `Player.log`, measured zero + IL below |
| 3 | A 8,100-cell sample found **1** chunk, extrapolated to ~7 map-wide | `observed/2026-08-14_row4_live.md:99-107` |

(1) and (2) are joined by the fact that both gensteps ran **on the same map, on
the same tile, with the same `isJunk` and the same `allowInWaterBiome`**, and that
`GenStep_ScatterGroupPrefabs` overrides **neither** `CalculateFinalCount` nor
`GetPlacementFactor` — its full method list is `get_SeedPart, Generate, GetGroup,
TryFindScatterCell, CalculateScatterInformation, ScatterAt, CanScatterAt, .ctor,
.cctor` plus two local functions (`meta.py GenStep_ScatterGroupPrefabs`, typedef
row 1191). So the two steps share the count arithmetic exactly.

⇒ **The surviving explanations are only two, and "silent give-up" is not one of them:**

* **(a) the measurement is unrepresentative** — the 9 sample rects were not where
  the chunks were; or
* **(b) something removed the chunks after order 960.**

(b) is weak on the numbers — see §4 — which leaves (a) as the leading candidate.
**O15 may be a measurement defect, not a placement defect.**

---

## 1. Line of attack 1 — placement rejection · **EVIDENCE PRODUCED, and it DISPROVES the hypothesis**

The brief's hypothesis was *"a bounded retry that silently gives up would explain
11-of-75 completely."* **The bound exists; the silence does not.**

### 1a. The attempt bound is 1000

`Verse.CellFinderLoose::TryFindRandomNotEdgeCellWith`

```
IL_002d: ldloc.0
IL_002e: ldc.i4      1000      <- the bound
IL_0033: blt.s       IL_0004
IL_0035: ldarg.3
IL_0036: ldsfld      IntVec3::Invalid
IL_003b: stobj       IntVec3
IL_0040: ldc.i4.0
IL_0041: ret                    <- returns false after 1000 tries
```

Each try is `CellFinder::RandomNotEdgeCell` (IL_0007) filtered by a predicate
(IL_0020) that resolves to `CanScatterAt`. This is the path our def takes:
`GenStep_Scatterer::TryFindScatterCell` reaches it at IL_0066 only when
`nearMapCenter` is false (IL_0014) and `nearPlayerStart` is false (IL_0038) —
neither is set in our def.

### 1b. 🔴 Giving up is **LOGGED, not silent**, and `warnOnFail` defaults to TRUE

`Verse.GenStep_Scatterer::TryFindScatterCell`

```
IL_0083: ldarg.0
IL_0084: ldfld     GenStep_Scatterer::warnOnFail
IL_0089: brfalse   IL_011e                 <- only silent if warnOnFail is FALSE
...
IL_00cd: ldstr     " could not find cell to generate at, trying fallback validators."
IL_00d8: call      Log::Warning
...
IL_010e: ldstr     " could not find cell to generate at."
IL_0119: call      Log::Warning
IL_011e: ldc.i4.0
IL_011f: ret
```

`Verse.GenStep_Scatterer::.ctor` — the default:

```
IL_004f: ldarg.0
IL_0050: ldc.i4.1
IL_0051: stfld     GenStep_Scatterer::warnOnFail     <- default TRUE
```

`JawaScrapfields.xml` never sets `warnOnFail`. **⇒ if this genStep had given up,
the log would say so.** It does not (§3).

The warning names the def, which is what makes it usable as evidence:
`"Scatterer " + this.ToString() + " from def " + this.def.defName + " could not find cell to generate at."`
(IL_00a6 / IL_00b7 / IL_00c5 / IL_010e).

### 1c. It warns **ONCE per genStep, not per item** — the first failure aborts the whole step

`Verse.GenStep_ScatterThings::Generate` (this override is what runs, not the base):

```
IL_00a8: ldarg.0
IL_00aa: ldloca.s  3
IL_00ac: callvirt  GenStep_Scatterer::TryFindScatterCell
IL_00b1: brtrue.s  IL_00b4
IL_00b3: ret                       <- 🔴 RET, not CONTINUE. Whole step ends.
IL_00b4: ...ScatterAt...           <- success path
IL_00d4: ldloc.2
IL_00d6: get_Count
IL_00db: blt.s     IL_00a8         <- loop
```

The base `GenStep_Scatterer::Generate` behaves the same, with one extra
fallback-validator retry first (IL_0031 `brtrue.s`, IL_003b sets `useFallback`,
IL_004d / IL_004e both `ret`). Our def declares no `fallbackValidators`, so the
`HasFallbackValidators` branch at IL_0039 is false and it is the single-warning
`" could not find cell to generate at."` phrasing that would fire.

**This is corroborated in the live log**: the hulk's warning appears exactly once
(`Player.log:6759`, count 1) even though it is a whole genStep — consistent with
once-per-step, not once-per-item.

### 1d. What actually rejects a cell (for the live test to aim at)

`GenStep_Scatterer::CanScatterAt`, in order:
`layoutStructureSketches` rect contains the cell (IL_0020-002b) · `extraNoBuildEdgeDist`
(IL_004a-0066) · `minEdgeDist` (IL_0067-0080) · `minEdgeDistPct` (IL_0081-00bc) ·
**`NearUsedSpot(cell, CalculateFinalMinSpacing(map))` (IL_00bd-00ce)** ·
`minDistToPlayerStart` (IL_00d7-0104) · `minDistToPlayerStartPct` (IL_0105-014c) ·
`spotMustBeStandable` (IL_014d-015f) · `allowFoggedPositions` (IL_0160-0172) ·
`allowRoofed` (IL_0173-0185) · then `validators` / `fallbackValidators` (IL_0186-01ca+).

Then `GenStep_ScatterThings::CanScatterAt` adds, on top of the base (IL_0000-000b):
`GenSpawn::CanSpawnAt` (IL_001e-0026) · `TryGetRandomValidRotation` (IL_002c-0034) ·
`terrainValidationRadius` / `terrainValidationDisallowed` / `terrainValidationAllowed`
(IL_0035-0122).

**Of all of these, the measured scrapfields def sets exactly one:** `minSpacing 4`.
No validators, no terrain validation, no edge distance, no `spotMustBeStandable`.

⚠️ One number worth knowing: `GenStep_Scatterer::CalculateFinalMinSpacing` IL_0016-001e
is `minSpacing / GetPlacementFactor` — spacing is **divided** by the junk factor, so a
Junkyard tile (f=15) would give spacing 0.27, not 4.

---

## 2. Line of attack 2 — what our own def asks for · **EVIDENCE PRODUCED; the units-mismatch is RULED OUT**

The brief flagged this as cheap and possibly decisive. It was cheap. It is decisive
in the negative.

### 2a. The def on disk today is NOT the def that was measured

`D:\Luke\dev\Rimworld\src\Jawa\Jawa_Patches\Defs\MapGeneration\JawaScrapfields.xml`
has been rewritten twice since the measurement:

| commit | time | change |
|---|---|---|
| `73ca76c` | 08-13 16:52 | **the version that was deployed and measured** |
| `de1018b` | 08-14 02:28 | `isJunk` removed |
| `f396d45` | 08-14 02:32 | comment correction |
| `2ddd388` | 08-14 02:38 | `countPer10kCellsRange` 12~20 → **7~9**; **`clusterSize 10` added** |

The measured def (`git show 73ca76c:...`) was:

```xml
<thingDef>ChunkSlagSteel</thingDef>
<allowInWaterBiome>false</allowInWaterBiome>
<isJunk>true</isJunk>
<minSpacing>4</minSpacing>
<countPer10kCellsRange>12~20</countPer10kCellsRange>
<filthDef>Filth_MachineBits</filthDef>
<filthExpandBy>1</filthExpandBy>
<filthChance>0.35</filthChance>
```

🔴 **There was no `clusterSize` at measurement time.** `clusterSize` was added
*after*, at `2ddd388`.

### 2b. ⇒ 11 (or 1, or 7) was a count of THINGS, not of clusters

`Verse.GenStep_ScatterThings::TryFindScatterCell` takes the cluster path only when
`clusterSize > 1`:

```
IL_0014: ldfld     GenStep_ScatterThings::clusterSize
IL_001a: ldc.i4.1
IL_001b: ble       IL_00a3            <- clusterSize <= 1 -> plain base path
...
IL_00a3: ldarg.0
IL_00ab: call      GenStep_Scatterer::TryFindScatterCell
IL_00b0: ret
```

And one loop iteration places one chunk, because `ChunkSlagSteel` does not stack.
`GenStep_ScatterThings::Generate` builds the stack-size range from `stackLimit`:

```
IL_0047: ldfld    ThingDef::stackLimit
IL_0052: ldc.i4.5
IL_0053: ble.s    IL_0080            <- stackLimit <= 5 -> range (limit, limit)
IL_0080: ldloca.s 0
IL_0098: call     IntRange::.ctor    <- (stackLimit, stackLimit) = (1,1)
IL_009e: call     GenStep_ScatterThings::CountDividedIntoStacks
```

`ChunkSlagSteel` inherits `ChunkBase`:
`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data\Core\Defs\ThingDefs_Misc\Various_Stone.xml`
line 6 `<ThingDef Name="ChunkBase" Abstract="True">`, line 25 `<stackLimit>1</stackLimit>`,
line 104 `<ThingDef Name="ChunkSlagSteel" ParentName="ChunkBase">`.

`CountDividedIntoStacks` IL_0000-0024 then emits `finalCount` stacks of 1.
**⇒ finalCount items = finalCount loop iterations = finalCount chunks on the ground.**
No units mismatch. The whole discrepancy is *not* explained this way.

### 2c. Nothing else in the measured def narrows the valid cells

No `<validators>`, no `terrainValidationRadius`, no `minEdgeDist`, no
`spotMustBeStandable`, no `spacingNoiseThreshold` (that field does not exist on this
class — `meta.py GenStep_Scatterer` lists all 24 fields and it is absent).
`minSpacing 4` against 62,500 cells and ~75 placements is not a binding constraint.

### 2d. ⚠️ Forward-looking hazard, please carry this into any re-measurement

The **current** def has `clusterSize 10`, which switches on the cluster path above.
Two consequences a future counter must not trip on:

* Cells now come from `CellFinder::RandomClosewalkCellNear(clusterCenter, map, 4, …)`
  (`GenStep_ScatterThings::TryFindScatterCell` IL_0078-0092), so the spatial
  distribution is **clumped, not uniform** — and a rect-sampling instrument is
  *much* more badly behaved against a clumped field than a uniform one. A 13%
  sample of 4–6 clumps can easily contain zero.
* A failed cluster centre logs `Log::Error("Could not find cluster center to
  scatter " + thingDef)` at IL_003d-0059 and then **carries on with a stale
  `clusterCenter`** rather than returning — a different failure signature from
  the one in §1, and an *error*, not a warning.

---

## 3. Line of attack 3 — the log · **EVIDENCE PRODUCED; a measured zero, not an absent one**

Read: `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Player.log`
— mtime **2026-08-14 12:05**, 7,453 lines, session start marker `[01:04:06]` at
line 649, game version line 22 `RimWorld 1.6.4871 rev591`. It contains **exactly one**
map generation.

| grep | count |
|---|---|
| `^Scatterer` | **1** |
| `could not find cell to generate at` | **1** |
| `Jawa_StampGroundHulk` | 1 — **line 6759**, fires **once**, not per item |
| `Jawa_ScatterScrapfields` | **0** |
| `Scrapfield` / `ChunkSlagSteel` / `SlagSteel` | **0** |

**This is a measured zero.** The log covers the map generation in question, and the
scrapfields step is absent from it entirely.

### Explicitly UNMEASURABLE (per the method rule — reported as absent, not as zero)

| file | why it cannot answer |
|---|---|
| `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Player-prev.log` | contains **no map generation at all** |
| `D:\Luke\dev\Rimworld\observed\2026-08-14\Player.log.prelaunch` | byte-identical to `Player-prev.log` (same md5) — same non-answer |
| `D:\Luke\dev\Rimworld\observed\2026-08-13\logs\Player.startup.585.2026-08-14.log` | byte-exact **prefix** of the live log, harvested 01:23; the mapgen was ~01:27. Not independent evidence, and blind to mapgen by construction |
| `D:\Luke\dev\Rimworld\observed\2026-08-13\logs\Player.2026-08-13_session2.log` | mtime 08-13 10:05, **predates the Jawa mapgen defs**. Its 2 scatterer warnings are vanilla (`AncientMechs` line 6747, `AncientExostriderRemains` line 6749) |

🔴 **`observed/2026-08-14_row4_live.md` reports the hulk failing on TWO maps. Only ONE
of those two maps has a surviving log.** The first quicktest session's `Player.log` has
been rotated away. So §3 speaks for one map, not two.

---

## 4. Assessing the two survivors

### (b) removal after order 960 — **weak, but not zero**

Scrapfields is order 960. The only vanilla genStep on `Base_Player` ordered after it
that could plausibly delete items is `GravshipMarker`, **order 1700**
(`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data\Odyssey\Defs\MapGeneration\BasePlayerMapGenerator.xml` lines 11-12).

Relevant because our def sets **no `avoidUsedRects` and no validators**, so scrapfields
places freely *into* the area `GenStep_ReserveGravshipArea` (order 600, same file lines
5-6) reserved — and anything there is wiped when the ship arrives.

**But the arithmetic does not reach:** a gravship footprint is order 10^3 cells against
62,500, i.e. a few percent. That removes ~2 chunks of 75, not 64. And
`observed/2026-08-14_row4_live.md:3` records that `Page_ChooseGravship` was never
touched on these quicktests.

⚠️ Not fully closed: this only enumerates **vanilla** gensteps. A mod genStep ordered
>960 on a 585-mod stack is not ruled out, and enumerating that offline needs the full
resolved `Base_Player.genSteps` with per-def orders. The dumps on disk
(`observed/2026-08-13/dumps/defnames.585.2026-08-14.json`) carry **defNames only, no
def bodies**, so ordering cannot be resolved from them — **UNMEASURABLE offline with
what is on disk.**

### (a) the measurement is unrepresentative — **leading candidate**

`observed/2026-08-14_row4_live.md:99` is the whole method statement:
*"9 rects of 30×30 = 8,100 cells, ~13% of each map."*

🔴 **Where those 9 rects were placed is recorded nowhere.** A grep for
`30x30` / `30×30` / `9 rects` / `8100` / `8,100` across `observed/`,
`src/RimMandrake/` and `infrastructure/` returns only that one sentence and
unrelated hits. **The sampling geometry is UNMEASURABLE from the repo.** "13% of the
cells" only implies "13% of the chunks" if the rects were spread; nothing on record
says they were.

Two further notes on the measurement, given honestly because they cut both ways:

* **Against (a):** the filth is internally consistent with the chunk count. The sample
  held 4 `Filth_MachineBits` to 1 `ChunkSlagSteel`; at `filthChance 0.35` over
  `filthExpandBy 1` (a 9-cell area) each chunk yields ~3 filth. 4:1 is exactly one
  chunk's worth. So the instrument was not simply blind to chunks — it saw a
  coherent local picture.
* **For (a):** that is equally consistent with *"the rects genuinely contained one
  chunk"*, which is a statement about **where the instrument looked**, not about how
  many are on the map. The two readings are not separable without a full-map count.

⭐ **Generalises** — and it is the same family as O14 and as the `traps.md` entry *"can
the instrument see this at all"*: a **sample** whose geometry is not recorded is not a
measurement, it is an anecdote with a denominator attached. The extrapolation
`1 / 0.13 = 7` silently assumes uniform coverage that was never established.

---

## 5. Scoreboard against the brief

| line of attack | outcome |
|---|---|
| **1. placement rejection / silent give-up** | ✅ **EVIDENCE — and the hypothesis is DISPROVED.** Bound is 1000; give-up is logged; `warnOnFail` defaults true; warns once per step. A silent bounded give-up does not exist on this code path. |
| **2. what our def asks for / units mismatch** | ✅ **EVIDENCE — units mismatch RULED OUT.** No `clusterSize` at measurement time; `stackLimit 1`; one iteration = one chunk. Nothing else in the def narrows cells but `minSpacing 4`, which is not binding. |
| **3. the log** | ✅ **EVIDENCE — measured zero** scrapfields warnings in the one log that covers a mapgen. Four other logs explicitly **UNMEASURABLE**; one of the two quicktest maps has **no surviving log**. |
| genStep ordering after 960 across mods | ⛔ **UNMEASURABLE offline** — dumps hold defNames only, no def bodies. |
| sampling geometry of the 9 rects | ⛔ **UNMEASURABLE offline** — recorded nowhere in the repo. |

### Numbers, for the record

`GenStep_Scatterer::CountFromPer10kCells` IL_0011-0024 (confirmed independently here,
matching the queue's derivation): `RoundToInt(size*size / RoundToInt(10000/value))`,
where `size` defaults to **`map.Size.x`** (IL_0000-000f) and is **squared** — so a
non-square map is scored off its x dimension alone.

`GenStep_Scatterer::GetPlacementFactor` IL_0000-0046 confirmed as **exactly** the
product of `TileMutatorDef::junkDensityFactor` over `map.TileInfo.Mutators`, seeded at
1.0, with **no other term** — no difficulty scaling, no settings, no storyteller.

---

## 6. The smallest live test that settles the remainder

Everything above reduces to one unknown: **how many `ChunkSlagSteel` are actually on
the map, counted without sampling.**

> **One bridge call, on whatever map is already loaded. No new load, no def edit.**
>
> 1. **Full-map count of `ChunkSlagSteel` by def** — `map.listerThings` enumerated by
>    ThingDef, *not* a rect sample. One number.
> 2. In the same call, **read the tile's mutator list** (`map.TileInfo.Mutators`) and
>    the **map size**.

That single number discriminates the two survivors outright:

| result | reading | action |
|---|---|---|
| **>= 75** | the genStep worked; the 8,100-cell sample was unrepresentative | **close O15 as a measurement defect**, and file the sampling-geometry lesson |
| **~7-11** | genuine under-placement. Since no warning fired, the loop *completed* — so `CalculateFinalCount` really did return ~7-11, and by §1/§5 the **only** free term left is `GetPlacementFactor`. Step 2's mutator list gives it directly | multiply the `junkDensityFactor`s from step 2; if the product is not 1, the queue's `f >= 1` inference (and with it the hulk-warned proof) is what breaks |
| **0** | the step never ran on this map | check `ShouldSkipMap` (IL_0000-0016: `allowInWaterBiome false` + `TileInfo.WaterCovered`) |

🔴 **Pick the comparison band to match the def the map was BUILT with, not the def on
disk today.** A map generated before `de1018b`/`2ddd388` predicts **75–125**
(`12~20`, `isJunk`). A map generated after them predicts **44–56 in 4–6 clumps**
(`7~9`, `clusterSize 10`, no `isJunk`). Comparing a new count against the old band —
or the reverse — reproduces exactly the kind of false shortfall this file is about.

⚠️ And whichever map is counted, **record where the count came from.** A full-map
`listerThings` count needs no geometry note; anything less than full-map must record
the rects, or it is not re-usable evidence.
