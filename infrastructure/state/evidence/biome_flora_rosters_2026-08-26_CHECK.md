# BIOME_FLORA_LOOKS_RIGHT_1 — the rosters are right; the LOOK is not yet taken

2026-08-26, seat CHECK.

## ⚠️ First, a false zero I nearly reported

Reading `BiomeDef` straight off the dump returned `wildPlants: 0` and `plantDensity: None` for all
three biomes. **That was my query being wrong, not the data being absent** — every BiomeDef field
lives under a `fields` object, and the top level carries only
`defName defType defTypeFull fields label modName packageId shortHash`. A "0" from the wrong path
is indistinguishable from a real zero, which is the whole reason this project measures instead of
greps. Corrected reading below.

Instrument: `defs.sqlite`, `MEASURED 80 BiomeDef via dumpdb.count`,
`mods=581/d7b4f552aca233de captured=2026-08-23T22:49:51Z`.
⚠️ **The live game is running 582 mods** — a one-mod delta against this capture. Named, not hidden.

## Criterion 2 — `HorrorWastes` shows `HorrorWeb` and no `Plant_Agave`: **PASS**

```
HorrorWastes   wildPlants 8   plantDensity 0.50
  HorrorWeb · Grimtacle · AB_BloodBouquet · AB_GlobularPlant · AB_TentacularPlant
  AA_RottingMound · AB_GlobularPlant_Polluted · AB_FleshTree
  Plant_Agave: ABSENT      HorrorWeb: PRESENT
```

Exactly the rewrite the item describes: the desert succulent is gone from ground at −49 °C and the
mod's own `HorrorWeb` is in.

## Criterion 1, at the ROSTER level — **PASS**; no cross-contamination between the three

```
Desert            wildPlants 30   plantDensity 0.45
   AB_HardyGrass · Plant_PincushionCactus · Plant_Agave · GRimYellowGrass
   Plant_DesertDandelion · Plant_PebbleCactus · GRimPincushionCactus · AreebianCactus
   GRim1PincushionCactus · GRimAgave · Plant_Chakroot_Wild · VCE_Plant_JadePlant
   VCE_Plant_AloeVera · AB_BrownBarrelCactus  (+16)

AB_MycoticJungle  wildPlants 35   plantDensity 0.20
   AB_Agarilux · AB_GlowingAgarilux · AB_AgaricusDomeCap · AB_GlowingGrass
   AB_RecurvedStropharia · AB_SlimyPholiota · AB_Glowstool · AB_Bryolux
   AB_WitchesOyster · AB_TinkleGrass · AB_GiantAgarilux · AB_AgariluxPrime
   AB_Flowers · AB_LandCoral  (+21)
```

Each roster is internally coherent and drawn from its own family: Desert is cacti, succulents and
arid grasses; MycoticJungle is **entirely `AB_*` mycoid**, the family furthest from anything vanilla
ships; HorrorWastes is flesh-and-web. No plant appears in two of the three.

⚠️ **This is the roster, not the map.** Criterion 1 as written asks what a generated map actually
grows, and a roster cannot answer that — only that nothing wrong is *available* to grow.

## Criteria 1 (live) and 3 (magenta) — **UNMEASURED**

Both need a map in each biome, and there is no route to one:

* **Nothing on the bridge puts a map on a chosen world tile.** `rimworld/start_debug_game` is
  quicktest-only with **no parameters at all** (`{"properties": {}}`), so the biome is whatever it
  rolls.
* 🔴 **The debug-action route cost the bridge.** `rimworld/search_debug_actions {"query":"generate
  map","limit":10}` on this 582-mod list timed out at 30 s and left the bridge unresponsive for
  minutes — a result `limit` does not limit the WORK. Filed as
  `DEBUG_ACTION_SEARCH_WEDGES_BRIDGE_1` and written into `rimbridge/references/traps.md`.

⇒ These two criteria need either the owner settling three tiles, or the 13-mod minimal list where
the debug-action surface is affordable. ⛔ Not passed, not failed — not taken.

🔑 And the item's own warning still governs whatever is taken later: **642 of 669 plants stop at
`minGrowthTemperature 0.0 °C` and half this planet is below that, so a correct roster can still read
as bare ground. Bare is not a failure of this patch.**
