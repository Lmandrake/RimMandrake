# Our own world faces: how WME does it, what made September pretty, three looks to choose from (2026-10-23)

Item: `WORLDMAP_FACES_DECIDE_SEPTEMBER_WAS_PRETTIER`. FOUNDRY, offline (no bridge, no deploy, nothing installed).

**The owner's ruling** (question card, 2026-10-23): *"Do a background deep dive for (3) [make our own face textures]
right now ... inspire yourself by World Map Enhanced's approaches and make variations to try out, then a sheet to
select for the user. We definitely should own our own world art."* So World Map Enhanced (WME) and GRimTerra are
**not** re-added. They are studied for technique only. No donor bytes are copied, kept or read into any of our art.

- **Review sheet:** stem `world_faces_review_2026-10-23`, built by `world_face_variants.py sheet` and served by
  `serve_gated.py`. His picks land in the tracked `world_faces_review_2026-10-23.decisions.json`.
- **Generator:** `src/RimMandrake/Utils/art/world_face_variants.py` (`gen` makes faces and renders, `sheet` builds the page).
- **Pictures:** `D:\ClaudeWork\rimmandrake\scratch\worldfaces_variants\` (`<approach>\face_<Biome>.png`, `scene_mid.png`,
  `scene_far.png`, `stats.json`, `sheet\`).

## 1. How World Map Enhanced and GRimTerra make their faces

Measured from the Workshop folders under `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\`. Both were
re-listed on 2026-10-23.

- **World Map Enhanced (Continued)** (`zal.worldmapenhanced`, Workshop 3599967849) is **textures only**. The folder holds
  `About/` and `Textures/`, and nothing else: no Defs, Patches, Assemblies or shaders. It works by shipping a PNG at the
  same path as another mod's face, so the file loaded later wins.
  - 32 faces under `World/Biomes/`, 15 under `Biomes/` (Alpha Biomes and others), 7 at the root, 2 for MorrowRim.
    All are 512 px opaque RGB, except Ocean at 1024.
  - 173 hill and forest sprites under `WorldMaterials/BiomesKit/<biome>/{Hills,Forest}/`. Only the Biomes Kit / WMBP mods
    (`zal.biomeskit`, `zal.wmbp`) read that path, and **neither is installed here**. So in our game WME changed the
    faces and nothing else.
- **GRimTerra World Map** (`GRimTerra.Worldmap`, Workshop 3546956014) also ships textures, plus two patches. One is an
  unguarded `PatchOperationReplace` that repoints vanilla AridShrubland and Tundra at its own files. The other adds
  BiomesKit extensions to GRimTerra's own biomes, which are not on our list. Its faces look photographic: 4-10x the
  contrast of WME's, and blotchy at planet scale.

**WME's technique, from its pixels** (8x8 block-average std is "blockiness"; seam is compared with the mean neighbour
difference):

1. **A face is close to one flat colour.** The mean per-channel sd is 3-9 and the blockiness is 1-2, so no big blotch
   repeats.
2. **Detail lives at 4-30 px:** soft, organic mottle in 2-3 close hues of one family, small lichen or crust specks,
   and on some faces a fine crease network with a pale side and a dark side (LavaFields, IceSheet).
3. **Muted colour, value 60-160, one hue family per biome**, so neighbours blend at hex borders.
4. **Water is the one cool, dark face**, with a single direction of ripple streaks. Depth comes from the shader, not
   the texture.
5. **Every face is seamless.**
6. **Hills (Biomes Kit route only):** 256 px RGBA sprites of 2-3 low-poly wedge peaks. The lit face and the shade face
   are flat colours with a dark drop-shadow edge, and the bigger hill levels carry snow caps. Biomes Kit draws them
   **unrotated**, so the lighting holds. Vanilla rotates hill quads at random.

## 2. What actually made September pretty

The 2026-09-11 in-game shot (`D:\ClaudeWork\rimmandrake\scratch\worldlook2\CMP1_twilight_sea_before_after.png`, left)
shows three things. WME's texture grain is not one of them:

- **Light, clearly separate colours per biome:** cream desert, olive scrub, bright green forest, lilac crags, deep blue
  sea. Values sit high (150-230) and hue jumps between neighbours are large.
- **A small drawn mark on nearly every hex:** tufts, cobbles, clumps and little tree glyphs, with hard hex edges. That
  gives the "board game" charm, and it carries each biome's character far more than the face does.
- **Hills as small dark clumps**, not as blots.

Our installed faces (`0f01bd5f7`, calmed in `fce7ac7b4`; the Abyss/Rot/Rust redraw in `793dbc3df`) were built to a
"calm" spec taken from WME's statistics. In our rendering that spec lands as dim, low-contrast fields: Cauldron reads
olive-brown, Contagion a flat crimson, and Leaning Scrub an even olive. The spec copied WME's *texture* numbers, but the
September look came mostly from *colour* and *per-hex marks*.

## 3. How our faces draw (unchanged facts, for whoever installs)

- Each BiomeDef's `<texture>` is `World/Biomes/RM_<Biome>`, a 512 px PNG in that biome's mod. The RUT twins share the
  art. All four shipping biomes have one: `src/RimMandrake/{Pyrelands,LeaningScrub,Cauldron,Contagion}/Textures/World/Biomes/`.
- `Custom/WorldTerrain` projects `_MainTex` in the shader, not by mesh UVs. The global `_MacroTex` (`World/WorldMacro`)
  adds large-scale variation. **How many hexes one face spans is still UNMEASURED.** The offline renderer assumes ~3.2
  (`TEX_PER_HEX = 160`).
- `RM_WorldLook` (`src/RimMandrake/BiomesShell/Source/RM_WorldLook.cs`) already adds overlay submeshes after
  `WorldDrawLayer_Terrain.Regenerate`:
  - soft borders;
  - sea films;
  - biome-wide swirls for Abyss and Rot;
  - the soft hill atlases, which replace vanilla's four shared hill materials (`HILL_DECALS_VERIFY_NO_MORE_COOKIE_CUTTERS`).

  A per-tile decal pass is the same kind of overlay.
- The planet is painted once, at the end (`BIOME_PAINT_ONCE_AT_THE_END_1`). Faces are judged as art, never by how many
  tiles a biome has today.

## 4. The three looks (variations on the sheet)

All three are procedural, periodic (seamless at 512) and from our own palettes. The palettes come from the biome sheets:

| biome | palette source | dark · mid · light · accent |
|---|---|---|
| Pyrelands | `the_pyrelands.md` (burning savanna, ash bands, flame line) | char `#3b2f25` · straw `#a8834a` · `#d0ac6c` · ember `#c2602a` |
| Leaning Scrub | `arid_shrubland.md` (silver-green fuzz, waxy gold sunward, venomvine near-black) | `#3a3d30` · `#8a916c` · `#b6b28a` · gold `#c4a24e` |
| Cauldron | `cauldron.md` (wet black and slate, sulfur yellow, bruised blue, no warm light) | `#1f2122` · `#45494a` · `#696f6f` · sulfur `#c4ac3e`, blue `#4d5878` |
| Contagion | `the_contagion.md` (red water/fog, pink-and-blue aberrations, grey-white husks) | `#4a1d22` · `#954848` · `#c79c98` · husk `#d6cec4`, blue `#6878a6` |
| Stillsand (context) | the Dune Sea all four sit in | `#8a6c46` · `#c2a06c` · `#dcc394` |

- **A. Painted (WME's technique, our colours).** Domain-warped mottle in three close hues, soft crust patches, a faint
  crease net with a pale and a dark side, and grain blurred to σ ≥ 1.3 px (no sub-3-px sparkle). One tell per biome:
  - Pyrelands: diagonal ash smears with ember edges;
  - Leaning Scrub: gold patches, wind streaks all one way, venomvine islands;
  - Cauldron: sulfur seams, bruised-blue patches, wet-black pools;
  - Contagion: dark-red veins, pale husk crusts, blue flecks.

  Textures only: install and deploy, no code.
- **B. Relief (shaded landform).** A heightfield per biome, lit from the upper left, coloured by height:
  - Pyrelands: rolling grass with burn scars and an ember rim;
  - Leaning Scrub: wind-combed ridges;
  - Cauldron: pocked crust with sulfur rims;
  - Contagion: swollen growths with veins in the valleys.

  Textures only. It is the busiest look at far zoom, and its repeat shows there.
- **C. Clean field + our own decals (the September route).** A light, nearly flat face in the biome's colour, plus 2-3
  small drawn glyphs per flat tile:
  - Pyrelands: straw tufts and ember-lit burn lines;
  - Leaning Scrub: leaning shrubs, one dark venomvine clump;
  - Cauldron: dark vent mounds with sulfur caps and grey steam;
  - Contagion: pustule clusters, some blue.

  The glyphs are lit from the upper left, have a soft shadow, are never white, and are drawn **unrotated**. **They fade out
  past mid zoom**, because at far zoom any decal becomes speckle (seen in the first render). Cost: a new per-tile decal
  submesh in `RM_WorldLook`, built like the soft-border overlay. It needs a Mod Settings toggle ("Planet: biome
  decals"), one glyph atlas per biome, and an altitude fade.
- **Hills (independent of the look).**
  - **1. Soft relief:** the installed `RM_Hills`.
  - **2. Our own drawn mountain clumps:** low-poly 2-4 peaks with a lit face and a shade face, tinted by the biome,
    unrotated, and soft relief past mid zoom. This needs our own hill pass, because vanilla's quads rotate at random and
    would spin the lighting.

**Statistics** (`stats.json`). Every new face is seamless: its seam is within 1.1x its neighbour difference. Each look
breaks the old calm bounds (sd 3-9, blockiness ≤ 2.5) on purpose. Pyrelands, for example, runs sd 15.2 and blockiness
7.7 in A, 26.8 and 12.7 in B, and 8.4 and 4.5 in C. `biome_worldfaces.py check` would refuse them, so whichever look is
picked needs its own bounds written into that checker at install (the follow-up item says so).

**Pre-review.** The seat and a naive judge (`gpt_consult.py`, gpt-6.1-sol) looked at every picture.

| what the judge saw | what changed | state |
|---|---|---|
| Painted Pyrelands smears repeated like stamps; Cauldron was noisy | both quieted | fixed |
| Relief looked embossed and crunchy, Contagion "like minced meat" | shading cut by about 45% | still flagged busy; prefilled No |
| C's mountains read as "game pieces", brown on Cauldron | flattened, tinted per biome, lighter shadows | fixed |

The judge preferred A for textures alone. The seat's lean is C, because the September shot's charm is per-hex marks plus
clear colour. The sheet prefills C = Pick, A = Maybe, B and Today = No, Hills 1 = Pick, Hills 2 = Maybe.

## 5. The rest of the roster

The chosen look then extends to every biome in `biome_worldfaces.py`'s table. That covers the land and seabed faces;
water keeps colour and ripple only, because depth is the ocean shader's job. The palette for each biome comes from its
`the_*.md` sheet. The owner-overridden three keep their overrides: Abyss near-black with swirls, Rot with wild-colour
swirls, Rust Cathedral as harsh machinery. If C is picked, each biome also needs one glyph set, and the doc sheets
already name each biome's signature life and landforms.

## 6. What is still unmeasured

- The real face scale (hexes per face) and how the repeat looks live. Look at the first install at three zooms, then
  set `TEX_PER_HEX` from it.
- Whether the decal fade altitude matches the zoom at which the white-speckle complaint arose. The speckle on Rust
  Cathedral is Odyssey landmark icons (`LANDMARK_ICONS_DECIDE_THE_REAL_SPECKLE`), not faces.
- Hard hex edges against our soft borders. September had hard edges. The soft-border toggle exists ("Planet: soft
  borders between biomes"), so trying both is a settings flip at the live look.
