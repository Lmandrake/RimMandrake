# Leaning Scrub — bedazzle review (movements 1–2), 2026-09-29

Program row 7 of `BAROQUE_BEDAZZLE_PROGRAM_1`. Biome lives under TWO names: ruled name
**Leaning Scrub** (`src/RimMandrake/LeaningScrub/`, BiomeDef `RM_LeaningScrub`) and legacy
campaign label **"desert"** (roster `rosters/desert.json`, frozen sheet `desert.md`).
`arid_shrubland` is a different biome and is not covered here.

## Name mapping confirmation — 🔴 the brief's mapping was WRONG; corrected from the files' own headers

**Leaning Scrub's legacy campaign label is `arid_shrubland`, NOT "desert".** Confirmed from
the files themselves, three independent ways:

1. `src/RimMandrake/LeaningScrub/About/About.xml` (its own description): *"It generalizes
   the biome sketched for a frozen campaign world's own arid shrubland
   (design/Jawa/worldbuilding/biomes/arid_shrubland.md)"*.
2. `RM_LeaningScrub_Biome.xml` header: *"the RimMandrake-tier twin of the frozen
   src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_AridShrubland.xml"*. The Utinni patch
   `WildAnimals_LeaningScrub.xml` copies its 40 rows *"verbatim from the LIVE
   RUT_AridShrubland.xml wildAnimals block"*.
3. The other direction: `desert.md`'s own thematic handle is **"the long shade"**, and
   `long_shade_bedazzle_2026-09-27.md` names its subject `RUT_Desert` → `RM_LongShade`
   against `rosters/desert.json`. Desert = **Long Shade** (program row 8, sitting held
   2026-09-27) — not this biome.

So this review reads: frozen sheet **`arid_shrubland.md`** (🧊 FROZEN
`BIOME_FREEZE_FABLE_REVIEW_1` 2026-09-07, +2026-09-21 knee-height amendment), roster
**`rosters/arid_shrubland.json`** (authored 2026-09-09; `"sheet": "arid_shrubland"`,
`"defNames": ["RUT_AridShrubland"]`), twins `RM_LeaningScrub`/`RUT_AridShrubland`.
`desert.md`/`desert.json` appear below only where they carry this biome's material — the
Blurrg reservation does route here (Long Shade Q8: *"Blurrg OUT (keeps a home for the
Leaning Scrub sitting)"*), so the brief's Blurrg pointer was right even though its name
mapping was backwards. No pre-rename residue: mod folder, packageId
(`mandrake.rm.leaningscrub`), BiomeDef and all owned defs already carry the
LeaningScrub/RM_ spelling, so no Rename census section is owed.

## What's there

Sources read this pass: all of `src/RimMandrake/LeaningScrub/`, the frozen twin
`RUT_AridShrubland.xml`, `UtinniPatches/Patches/WildAnimals_LeaningScrub.xml`,
`rosters/arid_shrubland.json`, frozen `arid_shrubland.md`,
`long_shade_bedazzle_2026-09-27.md` (Blurrg ruling), the desert accent batch,
`LEANINGSCRUB_RM_MOD_BUILD_1` (closed), artpipe registry/done/_artsrc, and the design
record for the shrubland kit pieces (`SHRUBLAND_GIANT_ENRAGE_1`,
`sweetline_guardian_spec.md`, `TREE_GRAPHICS_OWNERSHIP_1`).

### BiomeDef(s)

Twin architecture, both live:

- **`RM_LeaningScrub`** — `src/RimMandrake/LeaningScrub/Defs/BiomeDefs/RM_LeaningScrub_Biome.xml`,
  ships in `mandrake.rm.leaningscrub` ("RimMandrake: Leaning Scrub"), built 2026-09-25
  (`LEANINGSCRUB_RM_MOD_BUILD_1`, Phase A row 9). animalDensity 1.8, plantDensity 0.35,
  forageability 0.5, workerClass vanilla-Core `BiomeWorker_AridShrubland` (deliberate — no
  RM worker owed), vanilla `World/Biomes/AridShrubland` worldmap texture. Weather is
  stock defs re-weighted: Clear 30 / **Fog 45** / DryThunderstorm 1 / rain+snow all 0 /
  GrayPall 1 / Overcast 5. All values byte-copied from the frozen twin (its header,
  MEASURED 2026-09-25). Hard modDependency: `mandrake.rm.environmentalhazards`.
- **`RUT_AridShrubland`** — the frozen campaign twin, still serving the live world; its
  own `wildPlants` still names the old RUT_ flora under
  `MayRequire="mandrake.rut.ashkarrflora"` (that mod is deliberately NOT dissolved yet —
  Phase B step 4 deletes both together, per the RM def's own header).

### Flora (def-inline; no Utinni flora patch for this biome)

11 rows on `RM_LeaningScrub` (shorthand `<DefName>commonality</DefName>` form, parsed as
such): **`RM_Fuzz` 0.9** (THE signature canopy plant, renamed from RUT_ per Q8),
`RG_Plant_AridGrass` 0.5, `Plant_Brambles` 0.3, **`RM_Grellbush`/`RM_Grellspine`** 0.3
each, **`RM_WildHealroot`** 0.25, `Plant_Nysyllin_Wild` 0.22 (not IP per Q11a),
`RG_Plant_CreepStern`/`RG_Plant_CrimsonCushion`/`RG_Plant_Dervish` 0.2 each,
**`RM_VenomvineThicket` 0.15** (fortress flora, shipped by the EnvironmentalHazards kit).
**`RM_SweetlineTree`** ships as a def in this mod but is deliberately NOT in wildPlants —
the frozen twin never wired it either, and `TREE_GRAPHICS_OWNERSHIP_1` owns how the
landmark tree places (hand-placed surveyor's mark, not scatter). `RM_SweetlineWool`
("giant-wool") ships as the tree's harvest item.

⚠️ Roster's own ban-9 finding stands unfixed: 10 of 11 landed flora rows measure
Flammability 0.6–1.3 against the sheet's hard ban 9 (*"no flammable living flora"*) —
every note reads "KEPT, not re-picked — no Flammability-0 donor exists that fits". Only
`RM_VenomvineThicket` (0.1) satisfies it as authored. The permanent fix is OUR flora
replacing donors, which is exactly what a bedazzle fill can do.

### Fauna (def + patch-added, merged)

- **RM def inline, 5 non-SW donor rows (Q9):** `Terrorworm` 0.7 (mlie.horrors),
  `AA_Cactipine` 0.25, `AA_Needlepost` 0.1, `AA_Wildpawn` 0.1, `AA_Wildpod` 0.025.
- **Patch-added (`WildAnimals_LeaningScrub.xml`, one PatchOperationConditional +
  PatchOperationAdd onto `RM_LeaningScrub/wildAnimals`, all
  `MayRequire="mandrake.rsw.swbestiary"` — no donor-mod gate remains):** 39 RSW_ rows,
  read from the op's own value: FrilledGorg/Gorg/Iriaz/LongtailGorg 1.0 ·
  Eopie/Lothcat/Mudhorn/Ronto/Scurrier/Sketto/Kreetle 0.8 · Igitz/Urusai/ImperialToad 0.7 ·
  Kybuck/Massiff 0.6 · Bantha/Pufferpig/TunnelSnake 0.5 · ScrapNestBird 0.45 ·
  Anooba/Corinathoth/Gizka/Nuna/Worrt 0.4 · **ShrublandGiant 0.35** · MossBeetle 0.3 ·
  Grank/Qormot/Strill 0.2 · Cannok 0.16 · Whisperbird 0.15 · Pikobis 0.1 ·
  Convor/Skalder/Vulptex 0.08 · FeralNerf/Porg 0.04 · Voorpak 0.02 ·
  KowakianMonkeyLizard 0.01.
- **Campaign cast: 44 wired species.** RM-standalone cast with no donors installed:
  **0 creatures** — every inline row is MayRequire-gated donor fauna. See Q11a gap below.

The roster's invented signature pieces are BUILT and named (`ARIDSHRUBLAND_SHIPPING_NAMES_1`,
4 of 5 ruled 2026-09-21): **thunderstep** (`RSW_ShrublandGiant`, bs 6.0, the huge grazer;
parental enrage shipped 2026-09-20 as `RM_ParentalEnrageExtension`/`RM_CompParentalEnrage`/
`RM_MentalState_ParentalEnrage` in `mandrake.rm.creaturebehaviors` — no Harmony needed),
**yanker** (`RSW_TunnelSnake`, the corridor predator), `RSW_ScrapNestBird` (treasure-nest
bird), plus `RSW_ImperialToad`. Still owed from that card: the player-facing name of **the
fuzz** (BENCH item, do not pick ahead of it) and the bird-analog/sweetline-tree names.

### Terrain / weather / mechanics / C#

- Terrain: stock Sand/Soil/SoilRich by fertility (copied from the twin). ⚠️ The sheet's
  ban 7 says **no open sand terrain** on core shrubland ("root-bound crust") — the def
  still opens with `Sand` below fertility 0.45. Latent sheet-vs-def contradiction, held
  since the frozen twin; a candidate for an owned crust terrain at this sitting.
- Weather: no biome-owned WeatherDefs. **The Stall and the Gale are RULED player-facing
  names (2026-09-21, locked "ahead of their WeatherDefs being built") and remain
  UNBUILT.** The sheet's ban 5 (every ordinary weather carries wind; calm only as the
  Stall event) is unenforced by stock defs.
- C#: `RM_LeaningScrubMod.cs` is settings-only (master toggle + venomvine passability
  gate via the shared `RM_MechanicGates` registry). The two live mechanics are library
  pieces wired by def reference: **venomvine body-size barrier**
  (`RM_MapComponent_BodySizeBarrier`, EnvironmentalHazards) and **parental enrage**
  (creaturebehaviors, on the thunderstep). Nothing else: no Stall/Gale, no canopy
  concealment, no vaporator desertification, no nest-theft, no fire-stamping — all named
  in the About.xml's own "NOT in this mod" list as unbuilt.
- `Patches/BetterTrees_SweetlineTree_Immunity.xml` — defensive tree-mod immunity for
  `RM_SweetlineTree` (matches nothing today, by design).

### Art status per cast member

- **Has art:** `RM_SweetlineTree` (14 variants A–N shipped in this mod's Textures).
  RSW_ bestiary cast rides `mandrake.rsw.swbestiary`'s own textures (ports).
- **Zero PNGs anywhere (each def's own header, MEASURED 2026-09-25):** `RM_Fuzz` — the
  signature plant of the whole biome — plus `RM_Grellbush`, `RM_Grellspine`,
  `RM_WildHealroot`, and `RM_SweetlineWool`. The def headers note existing artpipe jobs
  target the OLD RUT_ texPaths in mandrake.rut.ashkarrflora and do not benefit the RM_
  defs. Artpipe census this pass (registry.jsonl + done/ + _artsrc/, searched by both
  RUT_ and RM_ spellings): see the art table below.

## Nine-mark scorecard

PENDING

## The Blurrg sitting row

PENDING

## Roster gaps + Proposed fills

PENDING

## Candidate mechanics slate

PENDING
