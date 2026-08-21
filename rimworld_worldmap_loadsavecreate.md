# Making ONE world, keeping it, and shipping it

**Question asked:** we want to hand-build a single wonderful world, freeze it, reuse it,
and distribute it — ideally being able to lift it out and drop it into other savegames
if the mod list or later decisions change. What are the real mechanisms?

**Researched 2026-08-15** by CHECK, against: the live game at the world screen, a 54 MB
savegame on this disk, the RimBridgeServer source, our own companion source, the full C#
source of the Worldbuilder mod, and the web. Every claim below is marked with how it was
established. Nothing here is repeated from documentation without a check.

---

> ⛔ **SUPERSEDED IN PART, 2026-08-19 — savegame WRITING is out.** This research (2026-08-15)
> is still the best account of what a world IS, how the 18 arrays encode, and why a
> `<world>` transplant fails. But the owner has since ruled that **the map reaches the game
> over the LIVE BRIDGE**, not through any file or worldgen hook
> (`design/Jawa/worldbuilding/ASHKARR_WORLD_DEFINITION.md` §12). §6 below — the companion
> tool that writes tiles into a live world — is the route we took. **Route C in §7 is dead.**
> Nine save-writing scripts were deleted on 2026-08-19 and `worldmap.py`'s `write()` raises.
> Reading a `.rws` is untouched, as is `rimbench/savemap.py` for LOCAL map grids.

## 0. The one-paragraph answer

**A world is not a file — it is a section inside a `.rws`, and vanilla gives you no way
to export it.** One installed-but-disabled mod, **Worldbuilder**, does exactly what we
want: it writes the whole planet to a folder of XML, lets a *mod* ship that folder, and
adds a world-selection screen so a player starts in it. That is the distribution answer.
But **every route — Worldbuilder, raw savegame, or hand-editing — stores per-tile data as
2-byte def shortHashes**, so all of them are bound to the def set that produced them.
**Pinning the mod list is unavoidable on every option.** The mod list is the world.

---

## 1. What a world actually is, measured

Taken from `rimbridge_save_20260815_172812.rws`, 54,485,269 bytes, this machine.

```
savegame                                    54,485,226
  meta                            52,080     <- modIds / modSteamIds / modNames live HERE
  game                        54,433,117
    components                  24,972,102   <- BIGGER THAN THE WORLD (mod GameComponents)
    world                        9,262,532
    maps                        19,166,490
```

Inside `<world>` (9.26 MB):

| child | size | note |
|---|---|---|
| `info` | 386 B | name, `seedString`, `planetCoverage`, rainfall/temperature, `initialMapSize` |
| `grid` | 1,333,422 | **the planet itself** |
| `factionManager` | 481,745 | |
| `ideoManager` | 5,490,271 | **59% of the world block** |
| `worldPawns` | 1,656,120 | |
| `worldObjects` | 84,892 | 104 Settlements, 21 Sites, asteroids |
| `features` / `landmarks` | 84,276 / 33,232 | |
| `components` | 91,071 | 62 mod WorldComponents |

### The grid is 18 parallel byte arrays, base64 + raw DEFLATE

`world/grid/layers` holds 3 `PlanetLayer`s — one `SurfaceLayer` (subdivisions 10,
radius 100, **119,904 tiles**) and two `OrbitLayer`s (488 tiles each). Only the surface
carries real data. Decode with `zlib.decompress(b64, -15)`:

```
tileBiomeDeflate        239,808 B = 119,904 x 2   BiomeDef shortHash
tileElevationDeflate    239,808   x2 (short, metres)
tileTemperatureDeflate  239,808   x2
tileRainfallDeflate     239,808   x2
tileFeatureDeflate      239,808   x2 (0xFFFF = none)
tilePollutionDeflate    239,808   x2
tileHillinessDeflate    119,904   x1 (enum byte)
tileSwampinessDeflate   119,904   x1
tileRiverDistancesDeflate 119,904 x1
tileRoadOrigins / Adjacency / Def    9,440 / 2,360 / 4,720   (1,180 road segments)
tileRiverOrigins / Adjacency / Def  12,660 / 3,165 / 6,330
tileMutatorTilesDeflate 822,528 = 205,632 x4  ‖  tileMutatorDefsDeflate 411,264 = x2
```

Biome decode was **verified** against `DefDump/defs/BiomeDef.json`: 46 distinct hashes,
all resolved — Ocean 29,976 · TemperateForest 11,734 · ZBiome_CoastalDunes 9,187 ·
BorealForest 8,731 · ExtremeDesert 8,127.

`world/info` verbatim:
```xml
<name>Rastaban Suhail</name>
<planetCoverage>0.300000012</planetCoverage>
<seedString>hamlet</seedString>
<persistentRandomValue>1370544265</persistentRandomValue>
<overallRainfall>Normal</overallRainfall><overallTemperature>Normal</overallTemperature>
<initialMapSize>(250, 1, 250)</initialMapSize><factions IsNull="True" />
```

🔑 **There is no `worldGenerationSeed` and no per-world mod manifest.** Mod dependency
lives only in `savegame/meta` at the top of the file — and implicitly in every shortHash
inside the grid.

📌 **Empirically, saves already share worlds.** `racetest.rws`, `New Arrivals1.rws` and
the target save have a **byte-identical `tileBiomeDeflate`** (md5 `0168ac166dc5`) and the
same seed and `persistentRandomValue`. `ship.rws` is a different world (seed `sandal`).
So RimWorld's own "several saves, one world" behaviour is real — within one campaign.

---

## 2. 🔴 Why you cannot just transplant `<world>` into another save

**The obstacle is the ID graph, not the tiles.** Measured outbound references from
inside `<world>`: **3,968 `Faction_N`** refs (3,782 in goodwill rows), **1,659 `Thing_*`**
refs (966 `<pawn>`, 205 `loadID`, 34 faction `<leader>`), **102 `Ideo_*`**. Inbound:
every map's `<mapInfo><parent>WorldObject_156</parent>`, `game/info/startingTile`,
`startingAndOptionalPawns`, and the `uniqueIDsManager` counters.

`Faction_N` and `Thing_*` are a **shared namespace across `<world>`, `<maps>` and
`game/components`.** Swap the world and every map parent, goodwill row, pawn relation and
ID counter points at objects that no longer exist.

⚠️ Runner-up obstacle: **tile-indexed mod state lives OUTSIDE `<world>`.**
`RimworldExploration.VisibilityManager` alone held **14.2 MB** of per-tile data under
`game/components`. A transplant that changed the tile count would silently desync it.
⛔ **That mod (`TheLastBulletBender.RWExploration`) was REMOVED from the mod list
2026-08-15 by owner ruling** — its fog wrecked the world-map view, and the planet has to
read as a world seen from space. The 14.2 MB figure stays here as the measured example of
how per-tile mod state scales with world size.

⇒ **A whole-world transplant is only safe between saves that already share the same
faction/ideo/pawn roster — i.e. saves of the same campaign, where it is a no-op.**

**What IS safe offline: repainting the terrain layer.** The 18 `tile*Deflate` arrays are
pure value data — no IDs, no back-references. Rewriting biome/elevation/rainfall/hilliness
across 119,904 tiles is mechanical, and our existing `savemap.py` codec already reads
them correctly at world scale.

---

## 3. ⭐ Worldbuilder — the mod that already solves this, and it is on this disk

`ferny.Worldbuilder` · workshop **3522102833** · **1.6** · *"This mod allows to customize
worlds."* · **INSTALLED BUT NOT ACTIVE** in `ModsConfig.xml`. Ships **full C# source** at
`1.6/Source/`, which is where everything below was read from — not from the store page.

Its dependencies (`brrainz.harmony`, `OskarPotocki.VanillaFactionsExpanded.Core`) are
**both already active**, so enabling it is a one-line change.

### It writes a world to a folder of XML

`WorldPresetManager.cs:40` — `GenFilePaths.FolderUnderSaveData("Worldbuilder")`, i.e.
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Worldbuilder\`.
**That folder exists on this machine and is empty** — the mod has never been run.

```
Worldbuilder\<PresetName>\
    Preset.xml         (WorldPreset.cs:71)
    TerrainData.xml    (WorldPreset.cs:72)
    CustomImages\  CustomIdeos\  thumbnail  flavor image
```

`WorldPreset` stores: `saveFactions`, `saveIdeologies`, `saveTerrain`, `saveBases`,
`saveMapMarkers`, `saveWorldFeatures`, `saveStorykeeperEntries`, `saveWorldTechLevel`,
`saveGenerationParameters`, `disableExtraBiomes`, `saveFactionCustomizations`,
`List<ScenPart> scenParts`, `worldTechLevel`, faction name/description/icon/colour/
**population** overrides, `savedIdeoFactionMapping`, `worldInfo`, `generationData`.

`WorldPresetTerrainData` stores the planet as **the same byte arrays the savegame uses** —
`tileBiome`, `tileElevation`, `tileHilliness`, `tileTemperature`, `tileRainfall`,
`tileSwampiness`, `tilePollution`, `tileFeature`, roads, rivers, `tileMutatorTiles`,
`tileMutatorDefs` — plus `Dictionary<PlanetTile, Landmark> landmarks`,
`List<WorldFeature> features`, `rockTypeOverrides`.

`WorldbuilderMod.cs:360-369` copies them **straight off the live surface layer**:
```csharp
presetToSaveTo.TerrainData.tileBiome       = surface.tileBiome;
presetToSaveTo.TerrainData.tileElevation   = surface.tileElevation;
...
```

### 🔑 A MOD can ship a world

`WorldPresetManager.cs:145-158`:
```csharp
foreach (var mod in LoadedModManager.RunningMods)
  foreach (var folder in mod.foldersToLoadDescendingOrder)
    string modPresetBaseDir = Path.Combine(folder, "Worldbuilder");
    if (Directory.Exists(modPresetBaseDir))
        allPresetDirs.AddRange(Directory.GetDirectories(modPresetBaseDir));
```
⇒ **Drop `Worldbuilder\OurWorld\` inside our own mod folder and it is offered to every
player.** This is how the published "[Worldbuilder] The Earth" and "Worlds for
Worldbuilder" mods work.

### And a scenario can force it

`UI/ScenPart_StartInWorld.cs` — a `ScenPart` with a `worldPresetName` field, picked from
a float menu of all presets. ⇒ **our scenario can start the player in our world with no
choice to make.**

### The UI it adds (from `1.6/Source/UI/`)

`Page_SelectWorld` (world-selection screen at new game) · `Window_CreateOrEditWorld` ·
`Window_MapEditor` (+ `.RockTypes`, `.Pollution`, `.DefPickers`) · `Window_ManageFactions`
· `Window_AddFaction` · `Window_FactionCustomization` · `Window_PopulationEditor` ·
`Window_SettlementCustomization` · `Window_MapMarkerCustomization` · `Window_MapTextEditor`
· `Window_PawnCustomization`.

🔴 **`Window_ManageFactions` / `Window_AddFaction` matter to us directly:** they add and
remove factions *after* generation. That is the problem C17 exists for — currently a
one-shot tick pass on the Configure Factions page with no second chance.

⚠️ **`TileBrush/` is a MAP brush, not a planet brush.** Its `Apply(...)` signature takes
`Map map, IntVec3 cell` (`TileBrushModel.cs:303`) — mountains, ores, local terrain. Do
not plan planet-scale work around it.

⚠️ Author's own warning, repeated on the Workshop page: **do not add Worldbuilder
mid-game.** Once used, its `WorldComponent`s, markers and customization data make it a
hard dependency of the save.

---

## 3b. ⭐⭐ WorldEdit 2.0 — a full planet editor, and it is ALREADY ACTIVE

`FunkyShit.Mods.WorldEdit.alpha` · workshop **3590928058** ·
`...\steamapps\workshop\content\294100\3590928058` · **ACTIVE in `ModsConfig.xml` right now.**

🔴 **This corrects an earlier conclusion in this document.** The web search found the OLD
WorldEdit (1750390635), which is genuinely abandoned for 1.6 and redirects users
elsewhere. **That is not what is installed.** WorldEdit **2.0** is a separate, current
mod, it is already enabled, and it is the most capable world editor on this machine.

Turned on by an **"Enable editor"** checkbox on the world-creation page, after which it
runs **live on the world screen**; each editor is an `ImmediateWindow` on its own
rebindable hotkey. Seven editors, read from its `Languages\English\Keyed` strings:

| editor | what it changes |
|---|---|
| **Tiles** | per-tile **biome, hilliness, temperature, elevation, rainfall, swampiness**, caves on/off, natural rock types — with a **RADIUS BRUSH** and mass ops **`SetToAllMap`** / **`SetToAllBiome`**. Layer-refresh buttons bake the change into the render. |
| **Rivers** | place river sources from ocean/lake tiles, choose type, delete-mode, wipe all |
| **Roads** | paint road types, delete-mode, wipe all |
| **Factions** | create/delete factions, pick FactionDef, name, leader, defeated flag, **assign an Ideology**, edit relations — applied immediately |
| **Settlements** | add / drag-to-move / delete, choose faction and SettlementDef |
| **World objects** | sites with site parts and comps (timeout, item stash, defeat-all-enemies reward), abandoned settlements, escape ships, peace talks |
| **World features** | create/name/rotate/resize the "Great Desert"-style map labels |
| **Templates** | save the finished planet as a **`WorldTemplateDef`** with forced storyteller, scenario and pre-made starting pawns — loadable from "Load Game" |

⭐ **The radius brush and `SetToAllBiome` are precisely the "don't click one tile at a
time" capability that was asked for**, and they need no new code from us.

⭐ **`WorldTemplateDef` is a second, independent world-distribution format** — a Def,
therefore ordinary mod content, therefore shippable inside our mod exactly like a
Worldbuilder preset.

⚠️ Untested by us: whether templates survive a def-set change (same shortHash question as
§5), and how it interacts with Worldbuilder if both are enabled. **Do not enable both and
edit the same world until that is tested.**

### Also installed and relevant

- **`Hali.ModifyLandingTile`** — Modify Tiles at Game Start, **ACTIVE**. This is the mod
  supplying the `Set biome (mod)...` / `Set landmark (mod)...` / `Clear Landmark (mod)`
  entries we found in the live debug menu. Single-tile, mouse-targeted.
- **`Oblitus.MyLittlePlanet`** — ✅ **ACTIVE** (corrected 2026-08-21 by CHECK: index 194 of the live 578; it was read as inactive while the 13-mod minimal list was installed). The only way to change world size / tile count.
  Note `WorldPreset` carries a `myLittlePlanetSubcount` field, so Worldbuilder expects it.
- ⚠️ **`7f.alienworlds` (Alien Worlds Framework) is ACTIVE and states it is "fully
  integrated with Worldbuilder"** — which is inactive. The active planet-type framework is
  running without its intended companion. That is also what created the empty
  `Worldbuilder\` folder we found.
- **Prepare Landing (Continued)**, **Map Preview**, **Map Mode Framework**,
  **Choose Biome Commonality**, **Faction Control**, **Map Designer**,
  **Geological Landforms** — all ACTIVE, none of them planet editors: they filter,
  preview, overlay, or tune generation parameters.

---

## 4. What else is out there (web research, sourced)

| thing | what it really does | verdict |
|---|---|---|
| **Vanilla** | no world-only file; `<world>` lives in the `.rws`. Multi-colony (up to 5) is *within one save*. [wiki](https://rimworldwiki.com/wiki/Save_file) | no export |
| **Worldbuilder** 3522102833 | as §3. Repo pushed 2026-08-11, actively maintained. [repo](https://github.com/fernyrepos/Worldbuilder) | ⭐ best |
| **World Presets** 3336572355 | saves a *startup* world (factions, settlements, ideologies) to `WorldPresets\`. **Cannot save mid-game**; DLC mismatch hangs. | fallback |
| **WorldEdit 2.0** `FunkyShit.Mods.WorldEdit.alpha` | ⭐ **ACTIVE ON THIS MACHINE** — see §3b. The *old* WorldEdit (1750390635) is the outdated one; 2.0 (3590928058) is a different, current mod. | ⭐ already ours |
| **Map Designer** `zylle.mapdesigner` | **local colony map only** — not world tiles. | not relevant |
| **Prepare Landing** | read-only tile filter/highlight. Changes nothing. | not an editor |
| **Geological Landforms** | local map-gen driven by world-tile properties; ~14 of 43 landforms auto-disable under Odyssey. | not an editor |
| **Map Preview / Map Mode Framework** | preview and overlays. | not editors |
| **Faction Control** | faction count/density/clustering at generation. | pre-gen only |
| **Realistic Planets** | original discontinued for 1.6; RP2 (3776715150) is the live successor. Pre-generation. | pre-gen only |
| **Persistent RimWorlds** | start a new colony on a world from a previous save. 1.6 support **UNCONFIRMED**. | watch |
| **Modify Tiles at Game Start** 3667490447 | dev-mode Set Biome / Set Landmark at game start. | matches what we saw live |

**External `.rws` tooling: essentially none.** EnzoMartin's save editor is archived
(2026-07-01). Python parsers cover pawns, mod lists and history — **none touch the world
grid**. RimSort/RimPy read only `<modIds>` metadata. No tool transplants a world. The only
documented transplant is *hand-copying tags* (a community 1.5→1.6 guide moves
`tileMutatorDefsDeflate`, `tileMutatorTilesDeflate` and `landmarks` by hand).

**Odyssey/1.6 changed the world model** (Ludeon's own modder primer): the surface is one
`PlanetLayer` among several; tile ids became a layer-scoped `PlanetTile` struct instead of
a bare `int`; the world pathfinder moved into the layer; rivers/caves/coasts became
`TileMutatorDef` workers; Landmarks bundle mutators + icon + naming. That churn is what
killed WorldEdit and Realistic Planets and forced the Prepare Landing fork.

---

## 5. 🔴 The portability ceiling — same problem on every route

Per-tile data is **2-byte def shortHashes** in every representation: the savegame's
`tile*Deflate`, and Worldbuilder's `TerrainData.xml` (`WorldPresetTerrainData.ExposeData`
is a bare `DataExposeUtility.LookByteArray` per array — **no defName table, no remapping
layer**).

Consequences, stated honestly:

- **A seed is not portable.** Same seed + different mod list = different planet, because
  any mod touching worldgen changes the arithmetic. Do not treat the seed as the artifact.
- **Additive mod changes are usually survivable; subtractive ones are not.** Removing a
  biome/faction/world-object mod leaves dangling references. That is exactly what
  "Mid-saver Saver" exists to prune.
- **Decode drift is silent.** A grid decoded under a different def set can be *wrong*
  rather than erroring — the byte still resolves, just to a different biome.
- Error grammar tells you which side you are on: `Could not resolve cross-reference` =
  def loader, fixable by restoring the mod. `Could not load reference to` = Scribe, the
  saved file holds a dead name and **no mod change fixes it**.
- Our own def dump exposes `shortHash` per def (`BiomeDef.json` has a `shortHash` field on
  all 65 biomes), so we can build the mapping table ourselves and **detect** drift even if
  we cannot prevent it.

⇒ **Whatever we ship, we ship the mod list with it, pinned.** That is not a limitation of
the chosen route; it is a property of RimWorld's world storage.

---

## 6. Editing the world from the bridge — what we can and cannot do today

Measured live at `Page_SelectStartingSite` (see `skills/rimworld-world-editing`):

- ✅ read the planet: `jawa/world_stats` (per-biome tile histogram), `jawa/list_factions`,
  `Outputs\All Factions`, `Outputs\World Gen Steps`.
- ✅ resolve and execute debug paths under `Actions\` — even though listing the `Actions`
  **root NREs**, its children resolve. `Set biome (mod)...` has **54** biomes,
  `Set landmark (mod)...` has **113** landmarks.
- 🔴 **but nothing can target a world tile.** `execute_debug_action` accepts only
  `pawnId`/`x`/`z`/`thingId`, all map-scoped; the vanilla `SetBiome` closure reads
  `GenWorld.MouseTile(false)`. Proven no-op: `Set biome -> ice sheet` returned
  `success: true` and the IceSheet tile count stayed at **6070**.

### Writing a companion tool IS feasible — verdict from the source audit

- `Tile.set_PrimaryBiome` is a public one-line `stfld Tile::biome`; only 6 methods touch
  the field, none of them a cache.
- `World.landmarks` (`WorldLandmarks`) exposes public **`AddLandmark(LandmarkDef,
  PlanetTile, string, PlanetLayer)`** and **`RemoveLandmark(PlanetTile)`**.
- Vanilla's own recipe, decompiled from `LudeonTK.DebugToolsMisc.SetBiome`:
  ```
  tile.Tile.PrimaryBiome = biome;
  Find.World.renderer.GetLayer<WorldDrawLayer_Terrain>(PlanetLayer.Selected).RegenerateNow();
  ```
  Non-generic equivalents exist and dodge the generic-argument problem:
  **`SetAllLayersDirty()`**, **`RegenerateAllLayersNow()`**, `SetDirty(PlanetLayer)`.
- Also recalc world pathing after a biome write:
  `Find.World.pathGrid.RecalculateAllLayersPathCosts()` — movement difficulty is
  biome-derived and cached.
- Guards: wrap in `ctx.MainThread.InvokeAsync`; `ModsConfig.OdysseyActive` before any
  landmark call; `LandmarkDef.IsValidTile` first; `RemoveLandmark` before `AddLandmark`
  on an occupied tile.
- **Proof the no-map case works:** our own `jawa/world_stats` already falls back to
  `Find.World ?? Current.CreatingWorld` and runs at the world screen.

⚠️ **One real caveat:** flipping a biome edits ONE field. It does **not** re-run the
tile's mutators or worldgen steps — a desert tile turned tropical keeps its
desert-derived rivers, hilliness and ore. To be consistent you must also set
`temperature`, `rainfall` and `swampiness`.

---

## 7. The three routes, and what each costs

**A0. Use WorldEdit 2.0 to AUTHOR — it is already active and needs nothing.**
Radius brush, `SetToAllBiome`, rivers, roads, factions, settlements. This is the editing
tool; the question of which *format* we ship in is separate and answered by A or B.

**A. Worldbuilder preset shipped inside our own mod — recommended for DISTRIBUTION.**
Author the world by hand once, save it as a preset, drop the folder into our mod, and
optionally force it with `ScenPart_StartInWorld`. Players get it on a world-select screen.
*Cost:* Worldbuilder becomes a permanent hard dependency; presets are shortHash-bound so
the mod list must be pinned; do not add it mid-game.

**B. Ship the `.rws` itself.** Zero new dependencies and maximum fidelity — it is
literally the world we played. *Cost:* players must reproduce the exact mod set, and any
removal risks dangling world references. This is the current plan and it still works.

~~**C. Offline terrain repaint (ours to build).** The 18 tile arrays are pure value data
and safely rewritable with `savemap.py`'s existing codec.~~
⛔ DELETED 2026-08-19 — savegame writing is out; the map reaches the game over the live
bridge (`design/Jawa/worldbuilding/ASHKARR_WORLD_DEFINITION.md` §12). It was built, it was
tried twice, and it produced a dead load both times (owner, 2026-08-18); the scripts are
gone. 🔑 **The premise that failed:** "pure value data, safely rewritable" was true of the
BYTES and false of the SAVE — a `.rws` is a reference graph, and a repaint that is
byte-correct still loads dead. ⚠️ `savemap.py` is unaffected and stays: it does LOCAL map
grids, not the planet, refuses to overwrite its source, and passes `fogGrid` through
untouched.

**Not viable:** lifting `<world>` from one save into another (§2), and treating the seed
as the artifact (§5).

---

## 8. What is unresolved

- Whether Worldbuilder's preset **apply** path rebuilds a world cleanly under a *changed*
  def set, or silently mis-decodes. The code shows no remapping layer — **assume it does
  not remap** until tested.
- Whether `Persistent RimWorlds` works on 1.6. Unconfirmed.
- **Whether WorldEdit 2.0's `WorldTemplateDef` or Worldbuilder's preset is the better
  shipping format.** Both are mod content; neither has been round-tripped here. Test both
  before committing.
- **Whether WorldEdit 2.0 and Worldbuilder conflict.** Both hook world creation and both
  claim to persist world state. Untested.
- Whether a preset round-trips our 575-mod stack at all. Untested — nobody has run
  Worldbuilder on this machine; its data folder is still empty.
