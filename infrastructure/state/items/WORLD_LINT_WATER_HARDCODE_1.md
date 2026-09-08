## 🔴 live-verified 2026-09-08 (FOUNDRY) — fix CONFIRMED, but the target was wrong: 1135 → 181, not → 0

Deployed (`build.py --apply --gm`, then `deploy_custom_mods.py` was NOT needed for
this one — it's the companion DLL, not a mod) and restarted on the owner's full
600-mod list, loaded `WORLDMAP_V23_dense_biomes_2026-09-08.rws`, ran
`jawa/world_lint` fresh.

**`landBiomeSubmerged`: 1135 → 181.** The fix works exactly as designed — checked
the full example list, `RUT_TheScald`/`RUT_GreySea`/`RUT_TwilightSea` (the three
seas) are **completely absent** from the 181 remaining findings, confirming
`isWaterBiome` now correctly exempts them. **But 181 ≠ 0**, and this item's own
"1135 is exactly the three seas' tile count (312+381+442)" claim was wrong — that
arithmetic coincidence hid the fact that some tiles at the SAME elevation (−350)
as the seas were never the seas at all. The 181 remaining findings are genuine
LAND biomes (`AridShrubland`, `Desert`, `Wasteland`, `AB_RockyCrags`,
`AB_MycoticJungle`, `ZBiome_Badlands`, sampled) sitting at elevation −350 or
similar sub-zero values — a real, separate defect (land tiles carrying the seas'
own elevation, presumably from a boundary/authoring collision during whichever
pass placed the three seas), previously **masked**, not caused, by this hardcode
bug: the old broken check flagged water-biome-at-−350 and land-biome-at-−350
identically as one undifferentiated 1135, so nobody could see the land subset
underneath until the water false-positives were correctly excluded.

**This item is closed on its own terms** (the hardcode is fixed, verified against
the real frozen world, not just a quicktest). **The 181 land-at-sea-elevation
tiles are a NEW, separate, real finding** — filed as
`WORLD_BOUNDARY_LAND_AT_SEA_ELEVATION_1` for whoever picks it up; not
investigated further here (out of this item's scope, and this session's budget).

## status 2026-09-08 — fixed, build pending deploy+restart to verify live

`landBiomeSubmerged` now reads `if (!b.isWaterBiome && t.elevation <= 0f)`. Compiles
clean (`dotnet build`, 0 errors, plan-only — no deploy, no restart). `waterBiomeOnRaisedLand`
is untouched. Owed: a game-down window to `build.py --apply` + restart, then re-run
`jawa/world_lint` and confirm `landBiomeSubmerged` 1135 → 0 with `waterBiomeOnRaisedLand`
and `lakesAboveSeaLevel` unchanged.

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
