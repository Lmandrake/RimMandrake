# Generating the world — the settings that cannot be repainted afterwards

Measured 2026-08-16 across four generated worlds. The deliverable is one hand-made
planet shipped as a frozen savegame, so the question at the Create World page is never
"is this pretty" — it is **"can we fix this offline?"** Almost everything can. What
follows is what cannot.

## 1. 🔴 Worldbuilder overwrites My Little Planet's Scale slider — twice

**The slider cannot win, in any click order, whenever an Alien Worlds preset is loaded.**
Two writers in `ferny.Worldbuilder`:

* `Page_CreateWorldParams_Reset_Patch.Postfix` — `Surface.settings.subdivisions = 10`
  and `TrySetMLPSubcount(10)`, **hardcoded, unconditional**, on every Reset (page open,
  randomize).
* `WorldGenerator_GenerateWorld_Patch.Prefix` — at the instant you press Generate, calls
  `TrySetMLPSubcount(preset.myLittlePlanetSubcount)`, which writes MLP's field **and**
  `Surface.settings.subdivisions`.

The Alien Worlds preset is machine-generated without that element, so `WorldPreset.cs`
Scribes it to its `defaultValue: 10`. The Generate prefix is the last writer before the
grid is built, so 10 always wins.

⇒ **Fix: put the value in the preset the prefix re-applies.**

```
python3 src/RimMandrake/Utils/set_planet_subcount.py 8
```

writes `<myLittlePlanetSubcount>` into
`…\294100\3626210061\Worldbuilder\TidallyLocked\Preset.xml`. Then **re-load the preset
in game** — Worldbuilder caches the parsed object, so the file edit is not seen until it
re-reads. Verified end to end: subdivisions 10 → **8**, 295,732 tiles → **32,968**.

⚠️ **It dies at every launch.** `AlienWorldsFramework.Refresh()` deletes and rewrites
that whole folder at startup. Re-run the script before generating, after any restart.

⚠️ `TrySetMLPSubcount` **refuses outside 6..10 and returns false silently**, so
Worldbuilder's own 5..11 slider has two dead ends.

📌 The other route is switching `ferny.Worldbuilder` off for the generation run: Alien
Worlds falls back to its mod-settings radio and MLP's slider draws on the vanilla page
with nothing to stomp it. Costs a restart and the planet editor.

## 2. Tile count — the measured anchors

**Read the count off the save; do not compute it.** Two rules of thumb, both derived
from these four worlds and both weaker than a measurement:

| subdivisions | coverage | tiles | |
|---|---|---|---|
| 10 | 0.05 | 3,787 | the old throwaway |
| 10 | 0.50 | 295,732 | unauthorable by hand |
| **8** | 0.50 | **32,968** | |
| 7 | 0.50 | ~11,000 | extrapolated |

* **One subdivision step ≈ ÷3**, not ÷4 as the ×4-per-step icosphere intuition suggests.
* **Coverage scales tile count ~quadratically** (0.05→0.50 is 10× coverage and 78× tiles).

## 3. ⚠️ What planet coverage clips is NOT understood — do not reason from latitude

A 0.05-coverage vanilla world spans only **−7.2 … +22.1 °C** and contains tundra and
alpine meadow: a narrow band, but not the equatorial slice a simple latitude-band model
predicts, and not a polar one either. **No model here survived contact with the data.**

⇒ On a tidally locked planet the substellar point is at (lon 0, lat 0), so a coverage
cut could remove the hot core and the liveable ring with it. That is almost certainly
what the mod author's *"generate at least 50% of the planet is recommended"* is
protecting. **Keep coverage ≥0.5 and take tile count out of subdivisions instead.**

## 4. Verifying a generated world — entirely offline, no bridge, no load

Everything below is read straight out of the `.rws`, in seconds.

```
<world>
  <alienWorldsFrameworkPlanetType>   TidallyLocked      🔴 `Default` = vanilla planet
  <info><name> <planetCoverage> <seedString> <overallRainfall> <overallTemperature>
       <initialMapSize>                                 baked on the world, used by every map
  <grid><layers><li Class="SurfaceLayer"><subdivisions> the real tile density
```

**Three independent tidal-lock signatures**, so a wrong one is caught:

1. `alienWorldsFrameworkPlanetType` reads `TidallyLocked`.
2. Temperature spans far wider than vanilla — measured **−43 … +65.6 °C** at
   `overallTemperature: Normal`, where vanilla tops out near +40.
3. **No ice sheet, no tundra, no boreal forest.** Polar biomes are a latitude artifact;
   their absence at 50% coverage is the longitude split showing.

🔑 **`worldmap.py`'s `get()` already returns physical units.** Applying the documented
`(raw-3000)/10` on top of it produces −304 °C and reads as a broken decode. The raw
encodings belong in `savegame-editing.md`; the API hands you °C, mm and metres.

## 5. What is worth getting right at generation, and what is not

**Not worth a reroll — all per-tile arrays with proven encodings, repaint them offline:**
biome, temperature, rainfall, elevation, hilliness, swampiness, feature. A wet desert
(median 952 mm) and ~6% Alpha Biomes exotica are cosmetic at this stage.

**Worth getting right, because no tool of ours can fix it:**

* **subdivisions and coverage** — the grid itself. We edit arrays; we cannot add tiles.
* **the faction roster** — `WORLDGEN_FACTION_CHECKLIST.md`. With Worldbuilder active this
  is the planet editor's right-hand panel, with per-faction delete icons and an Add
  button, re-editable until Generate — a real improvement on vanilla's one-shot page.
* **pollution** — `tilePollution`'s encoding is a hypothesis and `worldmap.py` refuses to
  write arrays nobody has proven.
* **roads and rivers** — graphs, not arrays, deliberately untouched by our tooling.
* **the mod list** — biome shortHashes resolve against whatever set is loaded, so a
  changed mod list silently re-points a decoded biome rather than failing.

⭐ **Pick the seed on coastline and rivers, not on biomes.** Biomes are free to change;
the land/sea outline and the river graph are not.
