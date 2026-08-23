## spec

🔴 **26 of the 28 biomes Ash'karr is painted in no longer exist in the running game.**
That is **20,737 of 21,872 tiles — 94.8% of the planet.** Measured 2026-08-22 23:0x by
CHECK off the LIVE bridge, not off a dump or a doc.

### What is measured, and how

**Instrument:** `jawa/get_defs` against the running game, calibrated first against
known-good defs so a blanket "not found" could not pass as a finding — `ThingDef/Steel`
resolves, and `BiomeDef/Tundra` resolves, so both the tool and `BiomeDef` type
resolution work. The absences below are real.

| present in the running game | ABSENT |
|---|---|
| `Ocean` `Lake` `BorealForest` `Tundra` `TemperateForest` `TropicalRainforest` `ColdBog` `Underground` | `Desert` `ExtremeDesert` `AridShrubland` `IceSheet` `SeaIce` `Wasteland` `Volcano` `LavaField` `Scarlands` `PoisonForest` `HorrorWastes` + every `AB_*`, `ZBiome_*`, `BMT_*` the map uses |

Re-run it, read-only, no game start, no map, no writes:

```
python.exe D:\Luke\dev\Rimworld\src\RimMandrake\bridgetools\check_map_biomes_live.py
```

### 🔑 It is a REGRESSION, and the window is one day wide

Two def-dump captures, **the same 578 mods, none added and none removed**:

| capture | BiomeDefs |
|---|---|
| `2026-08-21T22-44-59Z` | **80** |
| `2026-08-23T05-05-29Z` (this load) | **54** |

**Exactly 26 lost, exactly 0 gained**, and the 26 lost are exactly the 26 the map
uses. Losses span seven different owners — `Core` (`IceSheet`, `SeaIce`), `Odyssey`
(`LavaField`, `Scarlands`), `GRiNDTerra Terrain Retexture` (`Desert`, `ExtremeDesert`,
`AridShrubland`), `Alpha Biomes` (10), `More Vanilla Biomes` (3), `Biomes! Caverns` (2),
`Advanced Biomes` (3), `Horrors` (1) — so no single mod going missing explains it.

### 🔴 The inversion, which is the part that matters

Cherry Picker's `<keys>` removal list holds **26 `BiomeDef/` entries**. They are
`BorealForest`, `Tundra`, `TemperateForest`, `TropicalRainforest`, `ColdBog`, `Savanna`,
`Wetland`, the `ZBiome_` temperate set and 18 more — **the biomes a desert world does
NOT use.** Measured against the two captures:

- of the **26 lost**, **0** are on the cut list
- of the **54 kept**, **25** are on the cut list

So the list that was *written* is the correct one — cut the wet and temperate biomes —
and **what actually happened is its exact complement**: everything the map needs was
removed and everything the cut list named survived. Two disjoint sets of exactly 26.
⚠️ **Cherry Picker's own cuts are therefore not applying at all**, which is a second
defect hiding under the first.

⛔ **Do not "fix" this by editing the Cherry Picker list.** Its contents are right. The
question is what consumed a list of 26 biomes and removed the complement, and that is
what this item is for. A hunt across the 578 mod folders and the C# was running when
this was filed; its result belongs in this file.

### Why it blocks v1

`world\ASHKARR_WORLDMAP_tiles.csv` is the frozen, hand-authored planet
(`WORLD_FROZEN_RETHINK_PLANET_1`). Stamping it through the bridge writes
`Tile.PrimaryBiome` per tile; a biome that does not resolve cannot be written and the
failure is **silent** — §12.4 of `ASHKARR_WORLD_DEFINITION.md` already requires the
importer to refuse loudly on a tile-count mismatch, but nothing checks the biome roster.
🔑 **This is also the whole of §5 F6:** `Could not resolve cross-reference` came in at
**3,037 against a baseline of 25**, almost all of it
`No RimWorld.BiomeDef named <one of these> found to give to RimWorld.AnimalBiomeRecord`,
and 99% of the 84 MB log is the candidate dump attached to those.

## verify

- `check_map_biomes_live.py` prints `every biome the map names exists in the running game`.
- A fresh def-dump capture holds **80** `BiomeDef` records, not 54.
- `Could not resolve cross-reference` returns to its baseline of **25**.
- The mechanism is named in this file — file path and operation, or C# type — not guessed.

## criteria

The planet can be stamped without a tile silently landing on a biome that does not
exist, and the cause is written down so the same inversion cannot be reintroduced.
