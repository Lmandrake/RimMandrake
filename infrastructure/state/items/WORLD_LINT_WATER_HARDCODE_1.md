## the defect — PROVEN, read from our own source

`src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchWorldTools.cs:2850`

```csharp
bool biomeIsWater = b.defName == "Ocean" || b.defName == "SeaIce";
...
if (!biomeIsWater && b.defName != "Lake" && t.elevation <= 0f)   // -> landBiomeSubmerged
```

**Hard-coded defNames.** `RUT_TheScald`, `RUT_GreySea` and `RUT_TwilightSea` are
none of Ocean/SeaIce/Lake and all sit at **elevation −350**, so every one of
their tiles trips the check.

**MEASURED 2026-09-07:** `world_lint` reported **1245** findings, of which
**1135 = landBiomeSubmerged**, and 1135 is exactly the three seas' tile count
(312 + 381 + 442). **The map is correct; the instrument is wrong.**

Before the seas existed this check read 0, so it has never been exercised against
a modded water biome.

## the fix

The submerged test should exempt **any** water biome, which the engine already
answers: `BiomeDef.isWaterBiome`. All four of our seas set it true, and so do
vanilla Ocean, Lake and SeaIce.

```csharp
if (!b.isWaterBiome && t.elevation <= 0f)   // landBiomeSubmerged
```

⚠️ **Do NOT touch `waterBiomeOnRaisedLand` while doing this.** Its narrower
`Ocean || SeaIce` definition is deliberate and is guarded by two dated comments
(2026-08-20 `LINT_EXCLUDE_LAKE_SUBMERGED_1`, 2026-08-21): widening it re-breaks
every ordinary high-altitude lake. **Only the submerged test changes.**
✅ Note the `b.defName != "Lake"` clause becomes redundant under the fix —
`isWaterBiome` is true for Lake — so it can go, but removing it is optional.

## verification
Re-run `jawa/world_lint`: `landBiomeSubmerged` must fall from **1135 to 0** while
`waterBiomeOnRaisedLand` and `lakesAboveSeaLevel` stay where they are.

## gates
C# in the companion DLL ⇒ build + deploy in a game-DOWN window, then a restart.
`rimbridge-companion` skill.

---

## ⚠️ SECOND FINDING, NOT PROVEN — `staleMarineMutators` 99

Same lint run: `staleMarineMutators` went **0 → 99**. Examples are LAND tiles
carrying `Coast` with no water adjacency (tile 36 Wasteland elev 1.0, tile 171
AB_MiasmicMangrove elev 1.0, tile 269 ZBiome_Badlands elev 26, tile 758
AridShrubland elev 31).

**Sequence observed:** stage 3 removed stale `Coast` from 134 tiles and reported
`offenders now 0`; stage 4b then made 10084 mutator placements; the closing lint
found 99. ⇒ **stage 4b appears to re-add `Coast` to non-coastal tiles after
stage 3 has cleaned them.**

⛔ **A theory was tested and FAILED — do not repeat it.** I supposed the custom
seas had broken coastal adjacency. They have not: `SurfaceTile.WaterCovered` is
`elevation <= 0f` (RimWorld source) — pure elevation, no biome — and the seas sit
at −350, so they are water-covered and their neighbours are still coastal.

**Measure before theorising again:** whether the authored mutator CSV
(`ashkarr_populate.py` output) itself places `Coast` on those 99 tiles, and
whether stage 3 / stage 4b ordering is the cause. Do not file a root cause
without it.
