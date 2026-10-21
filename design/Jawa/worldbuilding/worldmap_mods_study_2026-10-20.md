# World-map graphics mods: what they do and how (study, 2026-10-20)

Owner, 2026-10-20, looking at the in-game map: *"Can we study the other worldmap graphics mods to see what they
do and how they do it? Maybe we just need to get some inspiration."* What he wants: real MOUNTAINS (ours read as
farm fields, soft blots barely visible), the Abyss much darker with eerie swirls, The Rot heavily textured with
swirls of wild colour, and the Rust Cathedral showing harsh rusty machinery.

This is a study of methods only. **No donor bytes are copied into the repo** (no-donor-art rule). The contact
sheets below contain donor art, so they live in agent storage and are not committed.

Method: offline only. Every mod in the Steam workshop folder (1,270 items) and the game's `Mods` folder was
scanned for PNGs under `Textures/World*` (1,785 files in 76 mods). About.xml was read for the relevant ones,
and the code that draws them was decompiled (`ilspycmd`) or read through RimSage. The raw lists are in
`D:\ClaudeWork\rimmandrake\scratch\wmstudy\` (`worldpngs.txt`, `inventory.tsv`; decompiled code under `decomp\`).

## Contact sheets (phone-reviewable, 1200 px wide)

| sheet | path |
|---|---|
| mountains and hills | `D:\ClaudeWork\rimmandrake\scratch\wmstudy\sheet_mountains.png` |
| dark and eerie biomes (Abyss) | `D:\ClaudeWork\rimmandrake\scratch\wmstudy\sheet_dark.png` |
| wild-colour toxic biomes (The Rot) | `D:\ClaudeWork\rimmandrake\scratch\wmstudy\sheet_tox.png` |
| rust and machinery (Rust Cathedral) | `D:\ClaudeWork\rimmandrake\scratch\wmstudy\sheet_rust.png` |
| survey: every Mountains atlas (77) | `D:\ClaudeWork\rimmandrake\scratch\wmstudy\survey_mountains.png` |
| survey: every biome face (114) | `D:\ClaudeWork\rimmandrake\scratch\wmstudy\survey_faces.png` |

Each sheet opens with OUR current texture as the first cell, for comparison.

## Which mods matter

Of the 76 mods, most only ship world-object icons (settlement or site markers), which are irrelevant here.
These are the ones that change how the planet itself looks:

| mod (workshop id) | replaces | technique |
|---|---|---|
| **ReGrowth 2 core** (2260097569), which carries the "World Map Beautification Project" (WMBP) layer and the BiomesKit hill code | hills and mountains per biome; a "forest" decal per biome | a new `WorldDrawLayer_Beautification`, plus a Harmony prefix that stops vanilla `WorldDrawLayer_Hills` for biomes that opt in. Textures go at `WorldMaterials/BiomesKit/<BiomeDefName>/Hills/{SmallHills,LargeHills,Mountains,Impassable}[_SemiSnowy\|_Snowy\|_VerySnowy\|_FullySnowy]` and `.../Forest/Forest[_Sparse\|_Dense\|_Snowy...]`. Opt-in is a `BiomesKit.BiomesKitControl` modExtension on the BiomeDef (`uniqueHills`, `forested`, snow and rainfall thresholds). |
| **World Map Enhanced (Continued)** (3599967849) | 32 biome faces (512 px, one 1024 px) plus WMBP hill and forest sets for vanilla and Odyssey biomes | painted, lightly photographic faces; hill sets in the WMBP layout |
| **GRimTerra World Map** (3546956014) | 24 faces for vanilla, Odyssey and More Vanilla Biomes | the most detailed faces of all: high-frequency photographic ground with clumps, cracks and streaks |
| **GRiNDTerra Biomes** (3537211820) | 15 alien biome faces plus WMBP hill and forest sets | wild-colour faces (Toxlands acid streaks, GRuby red veins, GRuquoise marbling, GRimond cell cracks) |
| **ReGrowth 2 WMB for Alpha Biomes / More Vanilla Biomes / Advanced Biomes** (3564679302, 3564679624, 3564679844) | WMBP hill and forest sets for other mods' biomes | the best examples of themed decals: RockyCrags black spires, Pyroclastic flame ridges, MechanoidIntrusion machine-hulk "forest", OcularForest eyes, Mycotic fungi, Gelatinous slime |
| **Lightless Empyrean Reborn** (3517488959) | a near-black biome face, plus hill and forest decals | the closest thing to an Abyss: a dark face, with pale rim-lit decals so it still reads |
| **Comigo's Greater Swamps**, **Gulden Biome** (3620545124, 3607066070) | WMBP sets for their biomes | the same master shapes, recoloured |
| **Odyssey (DLC) landmarks** (in the bundle cache) | 40 landmark textures, 256 px, as 2x2 atlases | `LandmarkDef.drawType = TerrainMask`: the terrain shader takes a mask texture and blends a *second* texture (the layer's background biome, usually water) into the tile face, picking a random atlas cell and rotating the tile toward or away from the coast (`coastRotateMode`) |
| **RW - Planet Atmosphere** (3272330410) | none: it adds an atmosphere, clouds, rings and a sun flare | **custom shaders shipped in an AssetBundle** (one per Windows, Linux and macOS), with the Unity project included under `src/`. Clouds are a textured sphere (`CloudDef.cloudTexturePath`). It is proof that a world-map mod can ship its own shader. |
| **New Anomaly Threats** (3274840013) | rusted mech world objects and debris | flat-shaded plate sprites for world objects, not terrain |
| **Tang's UI Retexture** (3141849282), **More Vanilla Biomes** (1931453053) | faces | flat colour fills; nothing to learn |
| Geological Landforms, Vanilla Landmarks Expanded, Worldbuilder | map generation, landmarks, editing | no planet-surface art technique of note |

**No installed mod has swirling or animated faces.** Every face is a 512 px tile of fairly even texture. The
loud ones (GRiNDTerra) get their energy from strong low-frequency streaks and high contrast, not from
large-scale motion.

## How vanilla draws hills, and why ours read as farm fields

Read through RimSage (`WorldDrawLayer_Hills.Regenerate`, `WorldMaterials`, `WorldRendererUtility`):

- There are four shared materials, `World/Hills/{SmallHills,LargeHills,Mountains,Impassable}`, on the shader
  `WorldOverlayTransparentLit` with render queue 3510. Each texture is a 128 px 2x2 atlas, so each hill is a
  64 px cell.
- Each hilly tile that has no landmark gets one quad, 0.9 to 1.1 times the tile size, lifted 0.005 off the
  surface. Its centre is jittered by up to 0.37 of a tile for small hills and up to 0.08 for mountains. It takes
  a random atlas cell and **`Rand.Range(0f, 360f)` rotation**.
- The vanilla cells are flat tan blots with a dark outline (`D:\ClaudeWork\rimmandrake\scratch\wmstudy\vanilla_hills.png`).
  There is no shading in them at all.
- Ours (`src/RimMandrake/TerminalBiomes/Textures/World/RM_Hills/*`, made by
  `src/RimMandrake/Utils/art/world_hill_decals.py`) were made rotation-invariant on purpose: only alpha
  darkens, and there is no light direction. That is exactly why they read as "soft blots". A mountain with no
  lit side and no shaded side has no silhouette and no relief, so it reads as a stain on the ground.

`WorldOverlayTransparentLit` lights the quad by the planet's surface normal (day and night) only. A flat quad
has no relief of its own, so **every bit of relief has to be painted into the sprite.**

## What WMBP does differently, and why it works

From the decompiled `ReGrowthCore.WorldDrawLayer_Beautification`:

- **No random rotation.** The per-biome hills are printed with `rotation: 0.01f`. In
  `GetTangentsToPlanet`, a rotation of about 0 aligns the quad's up axis with the world up vector projected onto
  the tangent plane, which means **planet north**. So the sprite is always upright, and the painted light can
  come from a fixed side. (Only the `Default` fallback set keeps the random rotation, and those are vanilla-style
  blots.)
- The sprites are 256 px 2x2 atlases (128 px cells), drawn at about one average tile size, with no centre
  jitter, on render queue 3600.
- **Hills are skipped on tiles that carry a road or river**, so routes stay legible.
- **There is one master drawing for every biome.** All 77 Mountains atlases in the survey are the same peak
  cluster recoloured (`survey_mountains.png`). Only a few themed sets redraw the shape: RockyCrags, Pyroclastic
  and MechanoidIntrusion.
- **Snow is tiered by tile temperature.** There are five variants per hilliness, chosen by thresholds in the
  BiomeDef extension. Snow sits on the lit faces and upper slopes.
- The "forest" decal is a separate quad per tile, chosen by rainfall (`_Sparse`, base, `_Dense`) and by
  temperature (`_Snowy`). The themed biomes put any object they like in this slot: machines, eyes, fungi, slime.

**What makes those mountains read as mountains at planet scale** (seen in `sheet_mountains.png`):

1. **Silhouette.** Peaks taper to a point, the outline has notches and spurs, and the base is wider than the
   top. A blob has none of these.
2. **A hard split between the lit side and the shaded side along one sun direction.** Each peak is two or three
   flat facets, a pale one facing the light and a dark one away from it. This split carries most of the effect,
   and it only works if the sprite is never rotated.
3. **Ridge lines.** A dark crease runs down each facet edge, plus a thin dark outline on the shaded side only.
4. **Clustering and overlap.** Each cell is three to five peaks overlapping front to back, so one tile reads as
   a range. Impassable is the same drawing, denser and bigger.
5. **Snowcaps on the lit upper facets** (the Tundra cells in the sheet). They raise contrast and imply height.
6. **Darker than the face, with the hue taken from the face** (desert peaks are brown on sand, toxic peaks green
   on green), so the range belongs to its biome and still stands out.
7. **Density.** Every mountainous tile gets one, at full tile size, and they abut. A massif reads as a
   continuous texture of peaks, not as scattered stamps.

## The rotation problem: verdict

**It can be avoided, without a custom shader or mesh.** The rotation is only a float argument to
`WorldRendererUtility.PrintQuadTangentialToPlanet`. WMBP already passes a constant and gets consistent lighting.
For Ash'karr we can do better than "north-up":

- The planet is tidally locked, with the substellar point at (lat 0, long 0) (see `ASHKARR_WORLD_DEFINITION.md`).
  Let S be the unit vector to that point and n the tile normal. The sun's direction along the ground at that
  tile is `t = normalize(S - (S·n) n)`.
- Compute the quad's north tangent the way `GetTangentsToPlanet(pos, rotation: 0)` does. The rotation to pass is
  then the signed angle from north to `t` about `n`, plus a constant for the side the art is lit from. **Every
  peak's lit face then points at the sun**, which is exactly the "One Direct Sun, a pure function of geometry"
  ruling, applied on the world map.
- The sun's elevation (`90 - arc`) can also pick the atlas row. Near the substellar point the sun is overhead,
  so use short-shadow, evenly lit cells. Toward the terminator, use long shadows cast away from the sun. On the
  night side, use unlit cells. The vanilla `Lit` shader already darkens the night side.
- Mechanism: either a Harmony prefix on `WorldDrawLayer_Hills.Regenerate` that substitutes our own iterator (this
  is ReGrowth's pattern: `Patch_WorldDrawLayer_Hills_Regenerate`, prefix returns false), or our own
  `WorldDrawLayer` subclass beside it. `RM_WorldLook` already appends to the terrain layer and swaps the hill
  textures, so this extends code we already have rather than starting a new mod.
- What a custom shader would add: sprites with a normal map, lit per pixel by the sun vector, so that any
  rotation looks right and the light could move. Planet Atmosphere shows this can ship (an AssetBundle per
  platform). On a tidally locked world the sun never moves, so the rotation approach gets the same result with
  no shader build. **Keep the shader route in reserve; it is not needed for mountains.**

## Making swirls and turbulence (for the Abyss and The Rot)

- **Domain warping, or flow-warped noise:** evaluate fBm at a point pushed around by another fBm,
  `f(p) = fbm(p + k·fbm(p + k·fbm(p)))`. This is what produces marbled, smoke-like, "eerie" swirls. Reference:
  Inigo Quilez, "Domain warping", https://iquilezles.org/articles/warp ; also *The Book of Shaders*, chapter 13
  (fBm). The technique goes back to Ken Perlin's 1984 marble texture.
- **Curl noise:** take the curl of a noise potential to get a divergence-free velocity field, then advect dye or
  colour along it, or use line-integral convolution, to get coherent swirling streamlines with no sinks or
  sources. Bridson, Hourihan and Nordenstam, "Curl-Noise for Procedural Fluid Flow", ACM TOG 26(3), 2007
  (https://www.dneg.com/wp-content/uploads/2022/11/2007.pdf). A smoother boundary variant: Ding and Batty,
  "Differentiable Curl-Noise", 2023 (https://cs.uwaterloo.ca/~c2batty/papers/Ding2023/Differentiable_Curl_Noise.pdf).
- **Library:** FastNoiseLite (MIT, C#, single file) has OpenSimplex2 domain warp and fractal warp built in
  (https://github.com/Auburn/FastNoiseLite). It drops into our offline Python or C# texture generators. Godot's
  documentation of the same class lists its parameters (`domain_warp_amplitude` and others).
- **Wild colours:** map the warped scalar through a multi-stop palette (a cosine palette, or an authored
  gradient), and colour a second warped field differently on top of it. GRiNDTerra's Toxlands and GRuquoise get
  their look from two contrasting layers: strong streaks over a dark base.
- 🔑 **Planet-scale catch:** a face is one 512 px texture repeated across the biome. A swirl large enough to see
  from orbit would visibly repeat. Two ways out:
  1. Make the face texture seamless, with mid-scale swirl detail (2 to 4 swirl cells per tile), and accept the
     repetition.
  2. **A per-tile overlay polygon with world-continuous UVs (uv = position × small k), the way
     `WorldDrawLayer_Pollution` and our `RM_WorldLook` border blend already draw.** One large swirl texture then
     spans many tiles with no visible repeat. This is the way to get "eerie swirling" across the whole Abyss.
     Animating it (a material texture offset updated each frame) is possible but is new work, and the owner
     would need to see it before it ships.
- **Abyss "far darker":** Lightless Empyrean (`sheet_dark.png`) shows the trick. Make the face near-black and
  low in saturation, then carry legibility with pale **rim-lit** decals and a faint cold swirl overlay. If the
  face is dark and there is nothing light on top of it, the biome reads as a hole in the map.

## Rust Cathedral machinery

The best example in the corpus is WMB Alpha's `AB_MechanoidIntrusion` (`sheet_rust.png`). It uses the "forest"
decal slot for machine hulks (density tiered by rainfall) and a grid-textured hill set. Odyssey's
Ruins, AncientVents and AbandonedColony masks show the vocabulary that reads as built structure at this scale:
hard rectangles, rings and arcs, with a dark outline. The plan for us: a per-biome decal layer on the
Rust Cathedral (gantries, pipe runs, cooling-tower rings, rust-orange lit faces lit by the same sun rule, black
shade), and a face with plate seams and streaks of rust bleed.

## Five techniques to adopt

1. **Never rotate hills at random. Rotate each one toward the substellar point** (the rotation float, a hills
   prefix, extending `RM_WorldLook`), and paint mountains with a hard split between the lit and shaded sides.
2. **Peak-cluster sprites** with a pointed silhouette, ridge creases, an outline on the shaded side only, three
   to five overlapping peaks per cell, and denser and larger cells for Impassable. Snowcaps go on the lit upper
   facets, chosen by temperature or sun elevation.
3. **Per-biome hill and decal sets, keyed by BiomeDef** (WMBP's layout): one master shape recoloured from the
   face's palette, plus themed redraws for the hero biomes (Rust Cathedral machinery, Rot fungal growth, Abyss
   rim-lit spires). Skip tiles that have roads or rivers.
4. **A world-continuous overlay layer** (pollution-style polygons with uv = position × k) carrying
   domain-warped or curl-noise swirl textures, so the Abyss and The Rot get swirls at continent scale with no
   visible tile repeat.
5. **Two-layer, high-contrast faces** (strong low-frequency streaks or veins over a dark base, with GRiNDTerra
   as the example), generated procedurally with FastNoiseLite domain warp and multi-stop palettes. For the
   Abyss, a near-black face made legible by light decals.

The custom-shader route (Planet Atmosphere's AssetBundle pattern) stays in reserve, for normal-mapped or
animated effects only.

## Provenance

- Engine facts: RimSage reads of `WorldDrawLayer_Hills`, `WorldDrawLayer_Terrain`, `WorldMaterials`,
  `WorldRendererUtility.PrintQuadTangentialToPlanet` and `GetTangentsToPlanet`, and `LandmarkDef.terrainParameters`.
- Donor code: decompiled `ReGrowthCore.dll` 1.6 (2260097569), `BiomesKit.dll` 1.6 (3333951497) and
  `GRimTerraBiomes.dll` (3537211820), under `D:\ClaudeWork\rimmandrake\scratch\wmstudy\decomp\`. Only the
  method was studied; nothing was copied.
- Sheet builder: `D:\ClaudeWork\rimmandrake\scratch\wmstudy\sheet.py` with its JSON specs beside it.
