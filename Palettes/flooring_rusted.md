# flooring_rusted — corroded metal decking

**Material × condition: metal × rusted.** Everything a thousand-year-old metal deck
can legitimately be built from in the current mod set — floors, the colours that
tint them, the materials that colour a hull without paint, and the constraints that
decide whether any of it reads on screen.

Lifted 2026-08-27 from `src/RimMandrake/Utils/gravship_floor_v2.py` and
`src/RimMandrake/Utils/apply_wall_stuff.py`, which had carried it inline. Every def
below was checked against the def dump the same day: 34 of 34 present, types and
supplying mods as recorded.

## Options versus choices

🔑 **This file is the option set, not a verdict.** `ramp` lines are the *choices* —
ordered walks through the colours for one job. The Gravship Cradle took the brown
ramps, so its hull is warm and unsaturated. That was a decision about **that ship**,
not a finding that rust is never orange. `wall_rust` — running out through HK47Rust,
Auburn and 212thOrange — is the saturated corrosion ramp, fully available, simply
not the one that ship took. Do not delete a colour because one build passed it over.

## What actually decides whether this reads

The colour grid is a **multiply**, so every tint can only darken. That single fact
generates most of the rules below, and it is why a "brighter rust" is not
expressible — you reach it by choosing a lighter *terrain*, not a lighter colour.

The value relationships matter more than the hues:

- the crossed grate renders **(35,29,22)**, the plating **(57,53,49)** — a heavy
  multiply on the plating collapses the gap and the wear pattern stops existing
- the desert reads about **(107,86,57)** at full bright, so a warm ship is only
  visible if it sits *darker* than the ground it lands on
- the hull must stay **lighter than the deck** or the two merge into one mass at
  map zoom and the ship loses its silhouette

## Holes

`GROUND` is the role for a cell eaten right through — no floor and no substructure,
the map showing underneath. It is not a terrain; it is the absence of one, which is
why its def is `-`. Blisters past `eat_min` lose their substrate as well as their
plating.

```palette
# --------------------------------------------------------------- the floors
role  CONNECT  AG_RustedTile                              @mod=Alpha Genes | rusted biotech lab tile
role  PLATE    guy762_FloorTiles_DoomgiverFoorMetal_dark  @mod=Star Wars KotOR Resources and Materials | metal plating (iron)
role  GRATE_I  guy762_FloorTiles_XGrate_iron              @mod=Star Wars KotOR Resources and Materials | crossed grate (iron) - means the plating is GONE, not trim
role  DIVOT    guy762_FloorTiles_DivotedTile_rust         @mod=Star Wars KotOR Resources and Materials | divoted tile (rust)
role  SCAFF    UCScaffoldTile                             @mod=Utility Columns | scaffold tile
role  HULL     VQE_AncientHullTile                        @mod=Vanilla Quests Expanded - Cryptoforge | ancient hull tile
role  GROUND   -                                                       | eaten through: no floor, no substructure, the map below

# ------------------------------------------------------- colours, and the RGB
# the game MULTIPLIES by. Nothing here can lighten anything.
color Structure_BrownFaded    86,76,57      @mod=Core
color Structure_BrownSubtle   101,88,67     @mod=Core
color Structure_BrownDark     90,69,38      @mod=Core
color Structure_BrownDirt     119,91,50     @mod=Core
color Structure_UmberBurnt    90,58,32      @mod=Core
color Structure_BrownWood     108,78,55     @mod=Core
color Structure_BrownLight    131,110,78    @mod=Core
color ReddishBrown            132,83,47     @mod=Core
color Structure_RedSubtle     132,84,72     @mod=Core
color Structure_Auburn        138,51,36     @mod=Core
color Structure_Burgundy      91,41,45      @mod=Core
color Structure_Sandstone     126,104,94    @mod=Core
color Structure_Granite       105,95,97     @mod=Core
color Structure_GreyDark      81,81,81      @mod=Core
color Structure_Slate         70,70,70      @mod=Core
color Structure_Marble        132,135,132   @mod=Core
color Structure_GrayLight     166,166,166   @mod=Core
color Structure_Limestone     158,153,135   @mod=Core
color Structure_Cream         195,192,176   @mod=Core
color Structure_White         184,184,184   @mod=Core
color Structure_Mustard       163,131,49    @mod=Core
color Structure_Orange        167,96,39     @mod=Core
color guy762_StructureColor_212thOrange   170,70,0     @mod=Star Wars KotOR Resources and Materials
color guy762_StructureColor_BespinBeige   175,150,120  @mod=Star Wars KotOR Resources and Materials
color guy762_StructureColor_ImpArmySlate  110,120,115  @mod=Star Wars KotOR Resources and Materials
color guy762_StructureColor_HK47Rust      200,100,50   @mod=Star Wars KotOR Resources and Materials
color guy762_StructureColor_CinnagarIron  90,70,50     @mod=Star Wars KotOR Resources and Materials

# ------------------------------------------------------------------- ramps
# Ordered pale -> deep. `-` is no colour at all, i.e. the terrain's own art.
ramp floor_light  - > Structure_Cream > Structure_White > guy762_StructureColor_BespinBeige > Structure_GrayLight > Structure_Limestone > Structure_Mustard > guy762_StructureColor_HK47Rust > Structure_Orange | floors that keep their value up; hue does the work
ramp floor_brown  Structure_Sandstone > Structure_BrownSubtle > Structure_BrownWood > guy762_StructureColor_CinnagarIron > Structure_BrownDark > Structure_UmberBurnt > ReddishBrown | warm deck, 90-130 band, darker than desert ground
ramp wall_brown_hot   Structure_BrownSubtle > Structure_BrownWood > Structure_BrownDirt > Structure_BrownDark > Structure_UmberBurnt > ReddishBrown | hull near the wounds
ramp wall_brown_cold  guy762_StructureColor_BespinBeige > Structure_Limestone > Structure_Sandstone > guy762_StructureColor_CinnagarIron > Structure_BrownFaded | hull where the plating is sound
ramp wall_rust    Structure_BrownSubtle > Structure_BrownWood > guy762_StructureColor_CinnagarIron > Structure_BrownDark > ReddishBrown > Structure_UmberBurnt > guy762_StructureColor_HK47Rust > Structure_Auburn > guy762_StructureColor_212thOrange | SATURATED corrosion, runs out to true orange
ramp wall_cold    Structure_GrayLight > Structure_Marble > guy762_StructureColor_ImpArmySlate > Structure_Granite > Structure_GreyDark > Structure_Slate | unweathered steel, no warmth at all

# --------------------------------------------------- colour without painting
stuff HULL  warm=DinoChitin  @mod=Jurassic Rimworld - Dinosaurs Only (Continued) | rich warm brown, permanent, survives a reload
stuff HULL  cold=MA_MegaBone @mod=Mythic Ages: Megafauna Bestiary | warm grey; reads LIGHT without going back to cold steel

# ------------------------------------------------------- the Cradle's numbers
param blister_cover   0.17   | fraction of deck taken by corrosion blisters
param blister_eat_min 26     | past this a blister loses its substrate too - a hole
param noise_seed      20260827 | seeded value noise, so the wear is reproducible

# ------------------------------------------------------------------- rules
rule Colour MULTIPLIES. A tint can only darken; reach a lighter result by choosing a lighter TERRAIN.
rule Floor tints stay at or above ~155. Below that the plating (57,53,49) crushes to mud and the grate (35,29,22) stops reading against it.
rule A warm ship must be DARKER than the desert (~107,86,57) or it washes out into the ground. Keep the deck ramp in the 90-130 band.
rule The hull must stay LIGHTER than the deck, or hull and deck merge into one mass at map zoom and the silhouette is lost.
rule Do not paint a hull. The dev Set Color tool has a per-GAME-SESSION budget of roughly 380 and then silently misses while still reporting success. Use stuff.
rule Rebuilding a wall cell WIPES what shares it. Re-place conduits from the layout afterwards; the layout is the authority for where they were.
rule Only the DEEPEST two of a hot ramp should become the dark stuff. Taking all six put dark plating on 60% of the hull and swamped the halo.

# -------------------------------------------------------------------- used
used Gravship Cradle, 2026-08-27: floor_brown for the deck, wall_brown_hot/cold for the hull. wall_rust and wall_cold were available and not taken.
```

## Where it is consumed

`src/RimMandrake/Utils/gravship_floor_v2.py` imports these tables rather than
declaring them. Check the palette against the live def set with:

```
python3 src/RimMandrake/Utils/palette.py flooring_rusted --check
```
