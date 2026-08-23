## spec

🔴 **Cherry Picker is NOT why 26 biomes read missing, and the live reading is INVERTED.**
Measured offline 2026-08-23 against the **live** config
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\Mod_3521312241_Mod_CherryPicker.xml`.

`MAP_BIOMES_REMOVED_LIVE_1` names Cherry Picker as the leading suspect — its own header says
*"Cherry Picker removes defs late… the DefDump is a PRE-REMOVAL reading."* Reasonable, and
measurably wrong.

**Cherry Picker cuts 26 `BiomeDef`s. ZERO of them are painted on Ash'karr.**

```
AB_IdyllicMeadows · AG_NereidPocketPlane · AG_PocketPlane · BorealForest
COMIGO_GreaterSwamp_Cold · COMIGO_GreaterSwamp_Temperate · ColdBog · GlacialPlain
Grasslands · Labyrinth · MetalHell · RG_BoilingForest · Savanna · TemperateForest
TemperateSwamp · TropicalRainforest · TropicalSwamp · Tundra · Wetland
ZBiome_AlpineMeadow · ZBiome_CloudForest · ZBiome_CoastalDunes · ZBiome_GlacialShield
ZBiome_Iceberg_NoBeach · ZBiome_Marsh · ZBiome_Sandbar_NoBeach
```

⇒ That list is exactly the **wrong-for-this-world vanilla set** — forests, tundra, swamps,
glaciers, meadows. **All 28 biomes the tiles CSV uses survive it**, HorrorWastes included.
The coincidence of 26 and 26 is a coincidence; the sets do not intersect at all.

## 🔑 The tell: the reading is inverted

| the live check said | Cherry Picker's own list says |
|---|---|
| PRESENT: `BorealForest` `Tundra` `TemperateForest` `TropicalRainforest` `ColdBog` | 🔴 **all five are CUT** |
| ABSENT: `Desert` `ExtremeDesert` `AridShrubland` `IceSheet` `SeaIce` | ✅ all five are **Core and NOT cut** |

**A game that had really applied this cut list would report the exact opposite.** Five of the
eight biomes reported present are the five the config removes, and the Core biomes we keep read
absent. Whatever the reading describes, it is not "Cherry Picker ran".

## what to check, in this order

1. ⭐ **Suspect the reading before the mod list.** Re-run
   `src/RimMandrake/bridgetools/check_map_biomes_live.py` at a settled main menu and see
   whether it reproduces. If `jawa/get_defs` was called mid-load, or answered from a partial
   database, the whole finding evaporates.
2. **Calibrate on a biome that must be absent.** The check calibrates on defs that must be
   PRESENT (`ThingDef/Steel`, `BiomeDef/Tundra`). Add the mirror: ask for a `BiomeDef` that
   certainly does not exist. If that returns *present*, the tool's absence signal is the bug.
   ⚠️ `BiomeDef/Tundra` is a **poor** calibrator precisely because Cherry Picker cuts it.
3. Only then look at `ModsConfig.xml` and the load order.

## verify

    python3 src/RimMandrake/bridgetools/check_map_biomes_live.py

**PASS =** all 28 biomes in `world/ASHKARR_WORLDMAP_tiles.csv` resolve. ⛔ A repeat of the
inverted pattern is NOT a pass and NOT a confirmation — it is evidence the instrument is
wrong, and it must be calibrated per step 2 before anyone acts on it.

## criteria

- [ ] The live check re-run at a settled menu, with an absence calibrator added.
- [ ] Either all 28 resolve, or the instrument is shown sound and the cause named.
- [ ] ⛔ Nobody changes the mod list or the cut list on the strength of the original reading.

## watch out

- 🔴 **This gates the world paint.** `WORLD_PORT_SURVIVES_BRIDGE_1` cannot mean anything while
  it is unclear whether the game can resolve the biomes the map names.
- ⚠️ **The def dump cannot settle it either**, and for the reason the original item gives:
  a dump is a snapshot taken before late removals. The live bridge is the only instrument,
  which is exactly why it has to be calibrated in both directions.
