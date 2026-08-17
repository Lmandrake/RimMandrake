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
| 7 | 0.50 | 10,797 | measured |
| **7** | **1.00** | **21,872** | ⭐ the world we shipped |

* **One subdivision step ≈ ÷3**, not ÷4 as the ×4-per-step icosphere intuition suggests.
* **Coverage scales tile count ~quadratically** (0.05→0.50 is 10× coverage and 78× tiles).

## 3. ⚠️ What planet coverage clips — partly measured now, still not modelled

A 0.05-coverage vanilla world spans only **−7.2 … +22.1 °C** and contains tundra and
alpine meadow: a narrow band, but not the equatorial slice a simple latitude-band model
predicts, and not a polar one either. **No model here survived contact with the data.**

🔴 **MEASURED 2026-08-17: coverage 0.5 amputates the NIGHT SIDE.** A tidally locked world
at coverage 0.5 bottoms out at **−38.5 °C**; the same geometry at coverage **1.0** reaches
**−105.7 °C**, the antistellar point. So half coverage silently deletes the deep dark, the
antistellar core, the chemistry lakes — everything past ~100° of arc. Two worlds were
disqualified on exactly this.
⇒ **On a tidally locked planet, coverage 1.0 is a REQUIREMENT, not a preference.** Take
tile count out of subdivisions alone. The mechanism is still unmodelled — a 0.05-coverage
vanilla world is a mid-latitude band, not the equatorial slice any simple model predicts —
but the consequence is now measured and is not a matter of taste.

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
* ~~roads and rivers — graphs~~ 🔴 **WRONG, corrected 2026-08-16: they are ARRAYS and are
  editable** — see `savegame-editing.md`. They still matter at generation because we do not
  *author* them, only prune what a repaint stranded.
* **the mod list** — biome shortHashes resolve against whatever set is loaded, so a
  changed mod list silently re-points a decoded biome rather than failing.

⭐ **Pick the seed on coastline and rivers, not on biomes.** Biomes are free to change;
the land/sea outline and the river graph are not.

## 6. 🔑 Pre-setting the whole Create World page from the Worldbuilder preset

`Page_CreateWorldParams_Reset_Patch` reads the loaded preset's `generationData` and pushes
it straight into the page — but only when `saveGenerationParameters` is **true**. So the
preset can pre-set every slider and the faction list, and the human only has to look:

```xml
<myLittlePlanetSubcount>7</myLittlePlanetSubcount>
<saveGenerationParameters>True</saveGenerationParameters>
<disableExtraBiomes>False</disableExtraBiomes>
<generationData>
  <factionCountsStrings><li>Empire</li>…</factionCountsStrings>
  <planetCoverage>1</planetCoverage>
  <rainfall>Normal</rainfall><temperature>Normal</temperature>
  <population>High</population>
  <pollution>0.05</pollution><riverDensity>1</riverDensity>
  <ancientRoadDensity>1</ancientRoadDensity><settlementRoadDensity>1</settlementRoadDensity>
  <mountainDensity>1</mountainDensity><seaLevel>1</seaLevel>
  <axialTilt>Normal</axialTilt><landmarkDensity>Normal</landmarkDensity>
</generationData>
```

🔴 **Write EVERY field the patch reads, not just the one you want.** A present-but-partial
`generationData` Scribes the missing fields to **enum 0**, which silently sets rainfall,
temperature and population to their MINIMUM while looking like you only changed coverage.
🔑 The list element is **`factionCountsStrings`**, not `factionCounts` — that is the Scribe
label, and the intuitive name does nothing.
⚠️ `OverallPopulation` is **Low / Normal / High** in 1.6, read off the game's own
`PlanetPopulation_*` translation keys. A remembered `Much` is wrong and Scribes to garbage.
⚠️ `AlienWorldsFramework.Refresh()` **deletes and rewrites the whole preset folder at every
startup**, so the setter must run AFTER the game is up — it caught us four times in one
day. `src/RimMandrake/Utils/set_planet_subcount.py` writes all of the above; poll for the
wipe and re-run rather than trusting your memory.

## 7. 🔴 The field that controls WHICH FACTIONS a world generates

**`startingCountAtWorldCreation`**, not `maxConfigurableAtWorldCreation`.

`WorldGenerationData.ResetFactionCounts()` builds the default list by walking
`FactionGenerator.ConfigurableFactions` and appending each defName
**`startingCountAtWorldCreation` times**. `maxConfigurableAtWorldCreation` is only a *cap*
on what a human may configure — patching it to 0 changes nothing about the default list,
which is why a slate built on it left every unwanted faction on the page and cost two
worlds' worth of manual clicking.

⚠️ **Generate the target list from the ACTIVE mod set, and regenerate it after any mod-list
change.** A patch aimed at a def whose mod was dropped throws — 12 red errors per load
after Yautja was unsubscribed. Vanilla FactionDefs that must stay configurable are the
hidden/system ones (Ancients, Entities, HoraxCult, the generic hostiles, wild men, beggars,
quest crews) and every `*Player*` def.

🔴 **A faction absent at worldgen is absent forever.** Deleting one from a save does not
work (see `savegame-editing.md`) and adding one is worse. The four easiest to lose are the
vanilla vessels a Star Wars roster reskins — `Empire`, `OutlanderCivil`, `TribeCivil`,
`Pirate` — because they do not look like campaign factions in the list. `Pirate` was lost
exactly this way.

## 8. ⭐ PROVEN: the tile grid is deterministic, so a painted world is PORTABLE

Measured 2026-08-17. Two worlds, **different seeds**, same subdivisions (7) and coverage
(1.0), both 21,872 tiles. Feeding the **first** world's exported coordinates against the
**second** world's temperatures gives **correlation −0.9598**, against −0.968 for the world
the export came from.

⇒ **tile index → lat/long depends only on (subdivisions, coverage), never on the seed.**

* A coordinate export from `jawa/world_tile_export` **transfers to any world of the same
  geometry** — export once, reuse forever, no bridge needed for later worlds.
* ⭐ Therefore **regenerating is cheap**: a hand-painted planet can be reproduced on a fresh
  world by re-running the paint pipeline, so a wrong faction roster or a bad seed is no
  longer a catastrophe. Design the pipeline to be coordinate-driven, never index-driven,
  and this property is free.
* Pipeline order that works: **paint → populate → regions → factions → hydrology**.
  ⚠️ Later stages undo earlier ones if they overlap — a feature-renaming step left in the
  populate stage silently reverted 10 region names written by the regions stage.
* ⚠️ **Settlement assignment must be ORDERED BY PRIORITY**, because a world may generate
  fewer settlements than the plan wants and the last entries simply starve. Four factions
  came out with zero settlements that way, two of them story-critical.

## 9. 🔴 `Pirate` IS `PirateBandBase` — and that is why a reskinned pirate faction vanishes

Vanilla ships:

```xml
<FactionDef Name="PirateBandBase" ParentName="FactionBase">
  <defName>Pirate</defName>
  <label>pirate gang</label>
  <requiredCountAtGameStart>1</requiredCountAtGameStart>
  <permanentEnemy>true</permanentEnemy>
```

One def doing two jobs: a **concrete faction** and the **named parent template** every other
pirate faction inherits from.

⚠️ **In the faction panel it reads "pirate gang", not your campaign name** — so a human
whittling an 80-entry list down to fourteen deletes it, twice in a row, while carefully
keeping everything that looks like theirs. `requiredCountAtGameStart 1` does NOT save it: a
faction deleted at the panel stays deleted, and it is then absent from the world forever.

⇒ **Two defences, and the first is the one that works:**
1. **Patch the `label` so the panel shows the campaign name**, and confirm the patch reaches
   the panel before generating. A reskin nobody can recognise is a reskin nobody keeps.
2. Put it on a written tick-list with the other vanilla vessels — `Empire`,
   `OutlanderCivil`, `TribeCivil`, `Pirate` — flagged as *"these four wear vanilla names"*.

🔑 **And beware the inheritance:** because `Pirate` carries `Name="PirateBandBase"`, anything
patched onto it is inherited by its children — ours included (`Jawa_Junkers` has
`ParentName="PirateBandBase"`). Patch the child's own fields, never the shared parent's,
unless you intend every pirate faction in the stack to change.

## 10. The pipeline, as it finally stands

Proven on three worlds, all offline after a single coordinate export:

```
world/WORLDMAP_source.rws            pristine, never written
  -> paint_ashkarr.py                climate, biome, relief, pollution
  -> populate_ashkarr.py             settlements + sites -> our factions, named, placed
  -> name_ashkarr_regions.py         37 feature slots re-cut to our regions
  -> name_ashkarr_factions.py        every faction renamed
  -> clean_ashkarr_hydrology.py      strip roads/rivers the repaint stranded
  -> world/WORLDMAP_gen.rws          + deployed to the game's Saves folder
```

Then verify by LOADING it and reading `jawa/world_stats` — the engine's own histogram, not
the tool's success flag. Final run: 21,872 tiles, −79.4…+80.8 °C, water 6.9%, 2,550 polluted
tiles, 28 named regions, 37 settlements across 11 factions, **zero non-ours owning anything**,
zero world objects in water, zero unresolved biome hashes.

⚠️ **Re-run the world-object water mask after EVERY paint.** Landmarks sit where the source
put them, and a repaint that moves the sea drowns some — 3 the first time, 2 the second.
