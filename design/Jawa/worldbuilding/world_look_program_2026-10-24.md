# The world-map look program (2026-10-24)

Decided item: `WORLDMAP_FACES_DECIDE_SEPTEMBER_WAS_PRETTIER`, closed 2026-10-24 on the owner's words. Earlier study:
`world_faces_own_art_2026-10-23.md`. FOUNDRY, offline: no bridge, no deploy until a step's live look is booked.

## 1. What he said

> "Agreed, a clean background with icons drawn from the dominant land and life forms of the region. Colors drawn from
> actual biome colors. I don't mind spending some time making this look really good in-game, the players will spend a
> lot of time looking at it during the game. We will have to redo it once all the Baroque Biomes are done because we
> will know a LOT more what the biomes actually look like by then, but we should take a stab at them all now to gain
> skill in this. Especially important is to get the water right too, then the sea floors on their own layers, and to
> make mountains look BIG/mountainous rather than just little pics of mountains. Contagion-stained mountains (the only
> place we use Contagion) is particularly important, and to draw those as wet/water generators (about the only places
> that are, so important!) I wonder about making the rivers and roads more beautiful too... the whole map needs love.
> We'll eventually get to the tile contents too (mutators, etc.) but for now let's just stick with major landforms and
> such."

Read as:

- **Look C is picked.** That means a clean field in the biome's real colour, plus our own icons of the region's
  dominant land and life forms.
- **"BIG/mountainous" is Hills 2**, our own drawn mountain pass, scaled until it reads as mountains rather than as
  tokens.
- A, B and Today are not picked.

**His card answers (2026-10-24, 07:55 PDT):**

- **Contagion mountains:** "Look only: they weep." Draw stained rock, seeping streaks and spring glints. The rules get
  wired later.
- **Rivers and roads:** these join the first (water) group. The river colour vision is "start red (in the mountains)
  and then immediately turn bluish, followed by a quick fade to thick green and then death", and FlowWorks should
  allow any river colour. That colour mechanism belongs to BENCH, because BENCH owns all FlowWorks.

## 2. The principle: throwaway art, keeper infrastructure

The per-biome art will be redone once the Baroque Biomes are done. So:

- **What is kept (infrastructure):**
  - the decal submesh with its LOD fade;
  - the mountain mesh / hills pass;
  - the sea and seabed overlays;
  - the river drawing;
  - the generators, with their atlas contract written down.

  These are built properly once, behind Mod Settings toggles.
- **What is throwaway-grade (per-biome content):**
  - faces;
  - glyph atlases;
  - peak tints.

  Each one is generated from a palette row and a short glyph list taken from the biome's `the_*.md` sheet. The redo is
  "edit the row, re-run the generator, re-judge", not a rebuild. We stop polishing a biome's pixels once it reads
  right at three zooms. Effort goes to the parts that make the redo cheap and to the skill he asked us to gain.
- **Every picture still goes through the art ledger, art-eval and a prereviewed sheet.** Throwaway does not mean
  unread.
- **The planet is painted once, at the end** (`BIOME_PAINT_ONCE_AT_THE_END_1`). A biome on 0 tiles is still drawn
  and judged as art.

## 3. Sequence (tickets in order)

| # | ticket | what | kind |
|---|---|---|---|
| 1 | `WORLD_WATER_REDRAW_SEAS_THAT_READ_DEEP` | each sea gets its own face (colour + ripple) on both twins, with film tunables taken from the pick | art, then small C# |
| 1b | `CONTAGION_PEAKS_REDRAW_AS_RAIN_MAKERS` | "they weep": dark stained rock, seeping streaks, spring glints; look only | art (+ C# overlay if needed) |
| 1c | `RIVERS_ROADS_REDESIGN_WORTH_LOOKING_AT` | river taper, soft banks, mouths and dry ends; roads worn or broken by type (look side) | C# `RM_WorldPaths` |
| 1d | `RIVER_COLORS_WIDEN_RED_BLUE_GREEN_DEATH` (BENCH) | FlowWorks: any colour per tile, plus the red → bluish → green → dies ramp | C# FlowWorks |
| 2 | `SEABED_LAYER_DESIGN_ITS_OWN_SEA_FLOOR` | the floor layer drawn in its own right: per-sea faces, depth tint, continent mask, real gizmo | art + C# |
| 3 | `MOUNTAINS_REDRAW_BIG_NOT_LITTLE_PICS` | our own hills pass: ranges, lit and shade faces, silhouette at every zoom; Contagion variant first | C# + art |
| 4a | `WORLD_DECALS_BUILD_ATLAS_PIPELINE_ONCE` | per-tile glyph submesh, one atlas per biome, altitude fade | C# |
| 4b | `WORLD_GLYPHS_SKETCH_EVERY_BIOME_FIRST_STAB` | every biome: a clean real-colour face plus a glyph atlas | art |
| 5 | `WORLD_MAP_POLISH_THE_REST_LATER` | terminator, caps, coasts, rim, labels; re-scoped after steps 1-3 | mixed |
| - | `CONTAGION_PEAKS_WIRE_WEEPING_RULES_LATER` | what a weeping peak *does*; not started until he asks | design |

Superseded:

- `WORLD_DECALS_BUILD_SEPTEMBER_CHARM_REDRAWN` is replaced by 4a and 3. Its ledger pointer names 1c by a filing slip,
  and the correction is noted on the item.
- `WORLD_FACES_INSTALL_OUR_OWN_AT_LAST` is replaced by 4b.

Why this order:

- **He named it.** Water first, then the sea floors, then the mountains.
- **Water is the cheapest win.** The faces exist and only colour and ripple are open.
- **3 and 1b share code.** The mountain pass is the bigger C# job, and the Contagion variant rides on it. 1b's art can
  be drawn first and judged on offline renders.
- **4a comes after 3** because both add draw passes between the blend (queue 3505) and the rivers (3520). The order of
  those passes is settled once.

## 4. Each ticket carries

- **Spec.**
- **Verify:**
  - an offline render review at full resolution, 1:1, at three zooms, with every image prereviewed;
  - then the art ledger, art-eval and a sheet;
  - then an owner look, planned as an owner-attended or bridge-holding session: 18 grid points at altitude 900 plus
    close-ups at 320, with soft and hard edges both.
- **Risks:**
  - The hex scale is unmeasured (about 3.2 hexes per face is assumed).
  - Landmark-icon speckle (`LANDMARK_ICONS_DECIDE_THE_REAL_SPECKLE`).
  - Hard vs soft hex edges.
  - Draw order below the hills and rivers.
- **Mod Settings toggles:** the existing `worldSeaDepth`, `worldBorderBlend`, `worldBiomeSwirls` and `worldSoftHills`,
  plus the proposed "drawn mountains", "biome decals", "sea-floor shading", "drawn rivers" and "weeping Contagion
  peaks".
- **Art or C#:** C# is built with `winbuild.py`, with its `.srchash`.

## 5. Hard questions, three options each

The GPT pass of deep-design-3x2 was **NOT RUN**: this seat runs without subagents and the brief scoped it out. So the
options below are pass 1 only. **This section is INCOMPLETE as a 3x2.**

**Water depth.** `Custom/WorldOcean` ignores UV0, so the face cannot carry depth. The options:

- (a) Keep the films and tune them per sea. This is cheap and live-tunable.
- (b) Bake a "deep" and a "shore" face per sea and choose per tile by distance to land. This needs a second material
  per sea and loses the smooth ramp.
- (c) Write our own ocean shader. This is the most control, and a new shader bundle to own.

**Pick: (a).** It is the only one that is already measured working.

**Big mountains:**

- (a) A range mesh across adjacent hilly tiles.
- (b) Oversized per-tile sprites, sorted back to front.
- (c) A relief film under smaller peaks.

(a) reads the biggest and costs the most. (b) is the fastest test of "big". **Pick: prototype (b) offline, then
decide** between (a) and (b) on renders.

**Decal LOD:**

- (a) Material alpha set per frame from altitude.
- (b) Two meshes swapped at a threshold.
- (c) No fade, with sparse decals.

**Pick: (a).** The speckle seen at far zoom rules out (c).

**Claims this rests on:**

| claim | status |
|---|---|
| Custom/WorldOcean ignores UV0 | measured (live, earlier session; RM_WorldLook comment) |
| sea films reach only the root surface | measured (source: `IsRootSurface` gate) |
| FlowWorks river colour is per tile, by biome switch | measured (source, `RM_RiverColors.cs`) |
| ~3.2 hexes per face * | **unmeasured**; changes glyph and ripple size |
| hills quads rotate at random | measured (vanilla source, 2026-10-23 study) |

## 6. River colour: what is realizable

From the FlowWorks source as read on 2026-10-24:

- **How it works today.** The river colour is chosen per **tile**, by a switch on the tile's biome: Contagion, Miasma,
  Wastes and Rust Cathedral get their own colours, and everything else gets water. Vanilla already writes per-vertex
  alpha along each path.
- **Any colour on any tile is cheap.** A per-tile override table replaces the switch.
- **The red → bluish → thick green → death ramp is realizable as per-tile steps,** counted downstream from each
  river's head. Smoothing it inside a tile needs a vertex-recolouring postfix. That is more work, but feasible.
- **"Death" can be drawn** as a fade to a dry trace. Actually ending the river is an authoring edit to its links, not
  a colour.

All of this is BENCH's ticket. FOUNDRY's river look (1c) must agree on the bank colour hand-off with it.

## 7. Open questions for him

1. **Water:** which colour and ripple option per sea? The first offline sheet answers this.
2. **Mountains:** may a big mountain spill visibly over its neighbouring hexes (oversized), or must it stay inside its
   own tile?
3. **Edges:** for the next live look, should the default be hard hex edges (September) or soft?
