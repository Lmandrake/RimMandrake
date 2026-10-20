# World Map Enhanced and GRimTerra World Map: what they are, and a spec for our own faces (2026-10-20)

Offline research, FOUNDRY subagent. Measured from the Workshop folders on `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100`
(images opened with PIL; stats and contact sheets in `D:\ClaudeWork\rimmandrake\scratch\wme\`: `stats.txt`, `wme_montage.png`,
`grt_montage.png`, `wme_hills.png`, `ocean_768.png`, `sheet_small.png`).

## 1. Answer

- **World Map Enhanced (Continued)** (`zal.worldmapenhanced`, Workshop 3599967849, author Zaljerem, v1.0.1) is **textures only**.
  The whole folder is `About/` (About.xml, Changelog, icons) and `Textures/` (229 PNGs, 31 MB). There is **no `Defs`, no `Patches`,
  no `Assemblies`, no `Languages`, no `Shaders`, no `loadFolders.xml`, no settings.** About.xml only has a `loadAfter` (Core, Royalty, Harmony).
  Everything it does, it does by shipping a PNG at the same path as another mod's texture so the later-loaded file wins.
- **GRimTerra World Map** (`GRimTerra.Worldmap`, Workshop 3546956014, author ItsMePaulieB) is **textures plus two small patch files**
  (no Assemblies, no Defs, no shaders). 1.6 only; `LoadFolders/` gates texture sets on More Vanilla Biomes, Alpha Biomes and Odyssey.
  - `1.6/Patches/GRimWMPatch1.xml`: an **unguarded** `PatchOperationReplace` that repoints the `<texture>` of vanilla `AridShrubland`
    to `World/Biomes/AridShrubland1` and `Tundra` to `World/Biomes/Tundra1`. This is a real def change, not a path override.
  - `1.6/Patches/GRimTerra Biomes.xml`: 9 `PatchOperationFindMod` ("GRimTerra Biomes") blocks adding a `BiomesKit.BiomesKitControls`
    mod extension (forested, uniqueHills, snow thresholds, hill size multipliers 1.3 to 2.0) to the GRimTerra biomes (`BiomeGRimberlands`,
    `BiomeGRimerald`, `BiomeGRimethyst`, `BiomeGRimonade`, `BiomeGRimond`, `BiomeGRimphire`, `BiomeGRimworld`, `BiomeGRuby`, `BiomeGRuquoise`).
    Irrelevant to us (those biomes are not in our list).
- Two sibling GRimTerra mods exist (`GRimTerra.Biomesmod` 3537211820 = biome defs, needs VFE Core; `GRimTerra.TerrainRetexturemod` 3543925559 =
  in-map terrain). Not inventoried; they are not world-map art.
- **Neither touches** rivers, roads, `World/Hills*`, mutator icons, feature labels, ocean shaders, WorldLayers or any C#. Verified by listing
  every folder in both mods (below). The only "layer" content is hill/forest **decal sprites** under `WorldMaterials/BiomesKit/<Biome>/`, a path
  read by the **Biomes Kit / WMBP** mods (`zal.biomeskit`, `zal.wmbp`), not by vanilla.
- **Where the depth of the old ocean came from:** not from WME. `Ocean.png` has no depth gradient at all (section 4). Vanilla `WorldOcean` shader
  shades by per-vertex elevation. In September our seas drew navy because they pointed at `World/Biomes/Ocean` and WME replaced that file; they
  never had the WorldOcean shader (the 2026-10-20 audit built that fix, deploy owed).

## 2. Inventory

### World Map Enhanced, folder by folder

| folder | PNGs | size px | note |
|---|---:|---|---|
| `Textures/World/Biomes/` | 32 | 512x512 (Ocean 1024x1024), RGB opaque | the biome faces. Vanilla names: AridShrubland, BorealForest, ColdBog, Desert, ExtremeDesert, Grasslands, IceSheet, IceSheetOcean, TemperateForest, TemperateSwamp, TropicalRainforest, TropicalSwamp, Tundra, Ocean. Odyssey: GlacialPlains, Glowforest, LavaFields, Scarlands, VolcanicIceSheet, Wasteland (note: the Odyssey names `Grasslands`/`Scarlands` are re-used by path). More Vanilla Biomes (`ZBiome_*`): AlpineMeadow, CloudForest, CoastalDunes, Grasslands, Iceberg, Marsh, Oasis, Sandbar. Others: AspenForest, HSBambooForest, MorrowRim_Grazelands, MorrowRim_VolcanicAshlands |
| `Textures/Biomes/` | 15 | 512x512, RGB (AB_MechanoidBiome RGBA) | Alpha Biomes `AB_*` (10), plus PoisonForest, Savanna, Volcano, Wasteland, Wetland (other biome mods' paths) |
| `Textures/` (root) | 7 | 512x512 | Biome_Permafrost, Permafrost, Grassland, Oasis, Savanna, Steppes, TemperateDesert |
| `Textures/MorrowRim/Biomes/` | 2 | 512x512 | MorrowRim ashlands, blightedAshlands |
| `Textures/WorldMaterials/BiomesKit/<18 biome kits>/{Hills,Forest}/` | 173 | 256x256 (a few 255/176/206 wide; RGBA) | hill/mountain/impassable/snowpile sprite sets (`SmallHills`, `LargeHills`, `Mountains`, `Impassable`, `*_SemiSnowy/_Snowy/_VerySnowy/_FullySnowy`, `SmallSnowpiles`, `LargeSnowpiles`), and `Forest`/`Forest_Dense`/`Forest_Sparse` (+Snowy) for GlacialPlain, Glowforest, Grasslands. Kits: AridShrubland, BorealForest, ColdBog, Desert, ExtremeDesert, GlacialPlain, Glowforest, Grasslands, IceSheet, LavaField, Scarlands, TemperateForest, TemperateSwamp, TropicalRainforest, TropicalSwamp, Tundra |
| About | 4 | | icon, preview |

Texture count total 229 PNGs. Several files are byte-identical copies (e.g. `Desert/Hills/Mountains.png` = `Mountains_FullySnowy.png` = ... 76183 B; Impassable x5 = 87878 B), so the snowy variants of the Desert kit are the same picture.

### GRimTerra World Map, folder by folder

| folder | PNGs | size px | note |
|---|---:|---|---|
| `1.6/Textures/World/Biomes/` | 10 | 512x512 RGBA | AridShrubland1, BorealForest, ColdBog, Desert, ExtremeDesert, TemperateForest, TemperateSwamp, TropicalRainforest, TropicalSwamp, Tundra1. 5.4 MB |
| `LoadFolders/MoreVanillaBiomes/` | 9 | 512x512 | ZBiome_AlpineMeadow, Badlands, CloudForest, CoastalDunes, GlacialShield, Grasslands, Marsh, Oasis, Sandbar |
| `LoadFolders/AlphaBiomes/Textures/Biomes/` | 12 | 512x512 | AB_* faces |
| `LoadFolders/Odyssey/` | 5 | 512x512 | GlacialPlains, Glowforest, Grasslands, LavaFields, Scarlands |
| `1.6/Patches/` | 2 XML | | described above |

### Which vanilla textures get overridden

Only **biome faces** (`World/Biomes/*`, same file names as vanilla 1.6 and Odyssey) and, in WME, Biomes Kit hill/forest sprites
(`WorldMaterials/BiomesKit/...`, not a vanilla path). **Not touched:** `World/Hills*`, `World/Rivers`/`Roads`, mutators, feature labels, world
objects, planet atmosphere. (The "honeycomb" hill blots are vanilla 1.6 hill decals; WME's decal sets would only replace them on biomes
that carry a Biomes Kit extension.)

## 3. Texture set measured (World/Biomes faces)

Columns: mean RGB; sd = mean of per-channel pixel std (0-255); blk = std of an 8x8 block-average (large-scale blotchiness); seam = mean
abs difference across the wrap edge; nbr = mean abs difference between neighbouring pixels (seam ≈ 1-2x nbr means tileable).

| file (WME) | px | mean RGB | sd | blk | seam | nbr | tileable | replaces |
|---|---|---|---:|---:|---:|---:|---|---|
| Ocean | 1024 | 52,63,85 | 3.8 | 0.6 | 3.0 | 1.4 | yes, faint seam | vanilla `World/Biomes/Ocean` |
| Desert | 512 | 141,107,68 | 3.4 | 0.8 | 2.4 | 1.5 | yes | vanilla Desert |
| ExtremeDesert | 512 | 159,128,91 | 3.0 | 0.8 | 2.2 | 1.4 | yes | vanilla ExtremeDesert |
| AridShrubland | 512 | 114,80,43 | 5.5 | 1.0 | 3.4 | 3.2 | yes | vanilla AridShrubland |
| Grasslands | 512 | 118,96,55 | 8.3 | 1.6 | 5.1 | 5.2 | yes | Odyssey/Grasslands |
| TemperateForest | 512 | 97,86,34 | 6.8 | 1.3 | 4.2 | 4.2 | yes | vanilla |
| BorealForest | 512 | 95,75,29 | 8.0 | 1.5 | 4.9 | 4.9 | yes | vanilla |
| TropicalRainforest | 512 | 78,79,27 | 6.8 | 1.6 | 4.1 | 3.4 | yes | vanilla |
| Tundra | 512 | 117,87,67 | 7.5 | 1.7 | 4.4 | 4.3 | yes | vanilla |
| ColdBog | 512 | 108,91,72 | 7.5 | 1.7 | 4.5 | 4.4 | yes | vanilla |
| IceSheet | 512 | 202,202,202 | 4.3 | 0.9 | 2.4 | 1.7 | yes | vanilla |
| IceSheetOcean | 512 | 197,198,208 | 4.5 | 1.1 | 2.6 | 1.8 | yes | vanilla (also the Tidally Locked unrendered-planet texture) |
| Glowforest | 512 | 83,74,61 | 8.4 | 1.9 | 4.7 | 4.6 | yes | Odyssey |
| LavaFields | 512 | 133,103,95 | 8.5 | 2.1 | 5.2 | 4.9 | yes | Odyssey |
| Scarlands | 512 | 95,83,94 | 9.4 | 2.1 | 5.5 | 4.7 | yes | Odyssey |
| Wasteland | 512 | 119,115,111 | 8.8 | 1.5 | 5.1 | 5.1 | yes | Odyssey |
| GlacialPlains | 512 | 137,139,145 | 4.1 | 1.0 | 2.8 | 2.4 | yes | Odyssey |
| ZBiome_Oasis / Marsh / Sandbar / ... | 512 | various | 3-7 | 1-1.4 | 2-4 | 1.3-4 | yes | More Vanilla Biomes |
| GRimTerra Tundra1 (for contrast) | 512 | 134,134,147 | 30.7 | 12.9 | 18.8 | 18.4 | yes | vanilla Tundra via patch |
| GRimTerra ColdBog (contrast) | 512 | 67,56,45 | 27.1 | 6.4 | 14.7 | 14.0 | yes | vanilla ColdBog |

Full table for all 42 faces: `D:\ClaudeWork\rimmandrake\scratch\wme\stats.txt`. Tileability is by edge statistics, not by 2x2 inspection;
the Ocean seam (3.0 vs 1.4) is the weakest and is hidden because ocean tiles blend and the texture is nearly flat.

## 4. What the images actually look like (6 WME faces, Ocean, hills; 6 GRimTerra)

- **Ocean (1024):** flat navy (52,63,85), sd 3.8. Horizontal, slightly wavy, **elongated ripple streaks** 15-40 px long in a lighter blue, all the
  same direction. **No depth gradient, no vignette, no shore light.** All depth cues came from the WorldOcean shader. Its virtue is calm,
  low contrast and an unambiguous "water" direction cue.
- **Desert:** warm sand (141,107,68), almost featureless, with faint dune-ripple striations about 6-10 px apart. sd 3.4.
- **Grasslands / Glowforest / TemperateForest:** mottled, soft-edged organic noise in 2-3 close hues of one colour family, small
  irregular "lichen/crust" speckle 4-20 px; one hue family per biome (olive-brown, grey-brown, olive-green), never saturated.
- **LavaFields:** dusty rose-brown with a **network of fine dark cracks and pale veins**, the only face with a linear motif, still sd 8.5.
- **Scarlands:** purple-grey mottling, sd 9.4. **IceSheet:** near-white with faint grey crease lines.
- **GRimTerra versions (contrast):** photographic, 4-10x higher contrast: green moss on rust rock, grey snow on rock (sd 24-31), tonal
  jumps of 100+ levels. Good close up, but **busy and blotchy at planet scale** (blk 6-13 vs 1-2) so the hex tiles would read as patches.
- **Hill decals (256 px, RGBA):** low-poly brown wedge/fan mountains with a darker drop shadow edge and optional white snow caps, 2-3
  mountain clumps per sprite on transparent; Impassable is the largest/darkest (grey in Tundra/Lava).

**Why the old look read as good (measured):** (1) every face is *close to* one flat colour (blk ≈ 1-2, so no large repeating blotch);
(2) detail lives at 4-30 px, which at planet zoom turns into fine grain rather than a pattern; (3) saturation is muted, values 60-160,
and every biome is one hue family, so neighbouring biomes blend cleanly at hex borders; (4) the water is the one **cool, dark** face
with a directional ripple, so it can never be mistaken for land; (5) all are seamless, so the repeat is invisible.

## 5. How vanilla 1.6 draws a biome face (from repo notes; gaps flagged)

- `BiomeDef.DrawMaterial` (1.6): `BiomeDefOf.Ocean`/`Lake` by identity get the **WorldOcean** shader; a biome with `!allowRoads && !allowRivers` gets
  **WorldIce**; everything else **WorldTerrain** (`src/RimMandrake/BiomesShell/Source/RM_WorldTerrainShader.cs`,
  `design/Jawa/worldbuilding/worldmap_in_game_audit_2026-10-20.md` §2). Our water biomes now get WorldOcean (built, not deployed).
- `WorldDrawLayer_Terrain` clamps any non-Ocean vertex below 0 m to 0 m (depth is thrown away for non-ocean-shader seas) (same audit).
- The face is loaded as an ordinary loose PNG through `ContentFinder<Texture2D>`; there is a 1024 face (Ocean) and 512 faces in shipping mods,
  vanilla Ocean_512 mean is also navy (59,70,91) (`Transient/worldlook_research_2026-10-20.md`).
- **UNMEASURED here:** the exact UV scale (how many hexes one 512 texture spans), whether the shader reads mipmaps/anisotropy, whether the
  terrain shader blends biome faces across tile borders. Repo notes hold none of it and no decompiled game source is on disk. Resolve with
  `mcp__rimsage__*` (`read_csharp_symbol` on `WorldDrawLayer_Terrain`, `WorldMaterials`) or the cold-load check below. Note the WME faces are
  seamless and low-contrast, which suggests the face is repeated many times across the sphere and blended.
- **Present ours:** 65 PNGs under `src/**/Textures/World/Biomes/`, 63 at 512x512 and 2 at 500x500 (non power of two). All are procedural
  placeholders from `Transient/biome_worldtex_2026-10-18/gen.py` (62 defs, 36 pictures, 2026-10-18): **bricks (Grey Sea), voronoi cells
  (Twilight Sea, Cracked Lands), isolated rings/dots/ladder lines (Warscar, Fever Wood, Miasma, Rust Cathedral), blue diamonds (Lantern Deeps)**.
  Contact sheet: `D:\ClaudeWork\rimmandrake\scratch\wme\sheet_small.png`. They break the WME rules above: high-contrast discrete motifs repeat
  as a visible stamp at planet scale and the colours are saturated (Slime 148,188,32; Abyss purple; Twilight Sea teal/violet cells).

## 6. Spec for our biome world textures

Intent sources: `design/Jawa/worldbuilding/biomes/<biome>.md` (the `the_*.md` set: blue_desert, chill (propane_lakes), contagion, cracked_lands,
fever_wood, forge, greentide, grey_deep, lantern_deeps, miasma, pyrelands, rot, rust_cathedral, scald, scarlands, slime, sump,
twilight_deep, webwork, plus `abyss.md`, `cauldron.md`, `nightside_ice.md`, `dune_sea.md`, `desert.md`, `arid_shrubland.md`, `deep_desert.md`,
`terminator_sea.md`), the palette per def in `Transient/biome_worldtex_2026-10-18/palette.json` (starting colours), and the mean-RGB census
`Transient/biome_worldtex_2026-10-18/census.md`. Generation goes through the art ledger (`art install`), review via the review-sheet
workflow, and **cosmetic changes need the owner's permission** (CLAUDE.md).

1. **Format:** 512x512, 8-bit RGB, **opaque**, power of two, **seamless on both axes** (wrap test: edge difference ≤ 2x the interior neighbour
   difference). Water/sea faces may be 1024 like WME's Ocean. One file per BiomeDef under `Textures/World/Biomes/<defName>.png`; twins share
   the same art. Hill/forest decal sets are optional, 256x256 RGBA, Biomes Kit paths, **not** needed for a first pass.
2. **Detail and contrast (the planet-scale budget):** mean per-channel sd **3-9**, large-scale blockiness (8x8 block-average std) **≤ 2.5**;
   features 4-30 px, soft edged, no motif larger than ~64 px, **no isolated discrete shapes** (no rings, dots, bricks, cells or diamonds that
   repeat as a stamp). Texture, not pattern. One 80-px "tell" per biome at most (a crack network, a ripple, a speckle).
3. **Palette:** one hue family per biome, dominant colour = the biome's colour from its `the_*.md` doc and `palette.json`, desaturated to
   roughly 30-60% HSV saturation, value 60-170 (ice and salt flats up to 200-230). Neighbouring biomes must stay distinguishable by hue
   or value at a glance; avoid pure saturated primaries (current Slime, Abyss, Contagion are the extreme cases). Keep the 70s-brown family
   for land and a **cool dark** hue for water.
4. **Water biomes (Grey Sea, Twilight Sea, Scald, Chill, mineral water):** these draw with the WorldOcean shader once the 2026-10-20 swap
   deploys, so the face carries **colour and ripple only, never depth**: a calm, nearly flat tinted field (sd 3-5), **directional wavelet
   streaks 15-40 px**, all one direction, no shore gradient, no vignette, no tile outline (depth gradient comes from the shader).
   Target means: Grey Sea steel grey-blue (~75,95,110), Twilight Sea deep teal-violet (~40,70,105), Scald teal (~55,120,130), Chill cold steel
   (~45,65,95); all darker than land, never brighter than ~140. The vanilla/WME mean (52-59,63-70,85-91) is the baseline. Seabed floor
   faces (`RM_Seabed*`, only drawn through the floor layer) are land-style rock/sediment faces and need no water ripple.
5. **Verification before accepting:** (a) the wrap/seam test and the stats above run by script (`stats.txt` recipe: PIL+numpy); (b) tile 3x3
   to look for repetition; (c) one **cold-load check** of the world view at three zooms with the Ash'karr dev world, judged by looking, including
   hex borders between each pair of neighbouring biomes; (d) log the UV-scale/mip facts (section 5 UNMEASURED) so the next generation is tuned.
   Never repoint a face at WME/GRimTerra bytes ("no donor art kept"); WME's Ocean can serve only as a reference.

## 7. Cautions for whoever acts on this

- Re-adding WME is a cosmetic mod change needing his card; it would also put donor art in the world look. Generating our own faces to the
  spec above is the owner's stated direction.
- A biome with zero tiles is not a defect; do not judge faces by today's map. Faces are painted-once art.
- The GRimTerra patch unconditionally repoints vanilla AridShrubland/Tundra textures, so it is not safe to treat that mod as a drop-in
  texture pack either.
