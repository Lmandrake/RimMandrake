# sandscoured — what the desert does to everything left outside

**Condition palette, material-agnostic.** Wind-driven sand strips paint, softens
edges and drifts against anything that stands still. On this planet it is the
default state of every outdoor surface, which is why this palette composes with the
others rather than competing: a thing can be rusted *and* scoured, and usually is.

## The one thing that makes this palette different

🔴 **You cannot bleach with colour.** The per-cell colour grid is a **multiply**, so
every tint darkens — a "sun-bleached" ColorDef does not exist and cannot be made.
Pale is reached by choosing a pale **terrain** and a pale **stuff**, never by
choosing a pale colour.

This is the exact inverse of how `flooring_rusted` spends its colour budget, and it
is why the two palettes cannot share ramps.

The contrast rule inverts with it. The desert reads about **(107,86,57)** at full
bright. A warm brown structure has to sit *darker* than that to be visible — which
is what constrained the Gravship Cradle. A scoured structure goes the other way and
is legible **lighter** than the ground. Sandscoured is the palette that is allowed
to go pale, and it is the only one.

## Principles, not yet measured

The rules in the block below are measured. These four are design judgement and
should be treated as provisional until something is built and looked at:

- **Scour is directional.** The windward face is stripped to bare material; the lee
  face keeps its colour and collects the drift. A uniformly pale object reads as
  *faded*, which is a different and much duller thing.
- **One wind per site.** If drift piles on the east of one building and the west of
  the next, the scene reads as noise rather than weather.
- **Drift is a wedge, not a ring.** Sand banks against an obstruction on one side and
  tapers away; a symmetrical skirt looks like a decoration.
- **Salt is not sand.** `VEE_Salt` and `Jawa_SaltCrust` read as a dried *water* story
  — a lake bed, a seep — and mixing them into ordinary dune ground says something
  about the site's history that may not be true.

```palette
# --------------------------------------------------------------- loose ground
role  SAND           Sand                @mod=Core | the default
role  SAND_SOFT      SoftSand            @mod=Core | deep, slows movement
role  SAND_FINE      AB_FineSand         @mod=Alpha Biomes | finer grain, reads smoother at zoom
role  SAND_COMPACT   AB_CompactedSand    @mod=Alpha Biomes | wind-packed; the surface a path wears to
role  SAND_RED       VEE_RedSand         @mod=Vanilla Landmarks Expanded | iron-red dune sand
role  SAND_RED_SOFT  VEE_RedSoftSand     @mod=Vanilla Landmarks Expanded | the deep version
role  DUNE           VEE_LittoralDuneSand @mod=Vanilla Landmarks Expanded | dune face
role  PEBBLES        VEE_PebbleDunes     @mod=Vanilla Landmarks Expanded | loose pebbles, deflation lag
role  GRAVEL         Gravel              @mod=Core | stony soil where the fines have blown out

# ------------------------------------------------------- dried, not just dry
# These say WATER WAS HERE. Use deliberately; see the principles above.
role  PARCHED        AB_ParchedEarth     @mod=Alpha Biomes | cracked mud
role  LAKEBED        DryLakeBed          @mod=Odyssey | dry lake bed
role  SALT           VEE_Salt            @mod=Vanilla Landmarks Expanded | salt pan
role  SALT_SAND      VEE_SaltySand       @mod=Vanilla Landmarks Expanded | salt working into sand
role  SALT_CRUST     Jawa_SaltCrust      @mod=Jawa Patches (local) | ours - the crust this project authored

# ---------------------------------------- colours, RGB read from the mod XML
# ⚠️ The def dump carries 181 ColorDefs and the colour field of NONE of them, so
# these were parsed from Core/Odyssey/workshop XML and calibrated against six
# values already in flooring_rusted: 6 of 6 matched.
color Structure_Cream        195,192,176  @mod=Core
color Structure_White        184,184,184  @mod=Core
color Structure_GrayLight    166,166,166  @mod=Core
color Structure_Limestone    158,153,135  @mod=Core
color Structure_Sandstone    126,104,94   @mod=Core
color Structure_BrownLight   131,110,78   @mod=Core
color Structure_BrownFaded   86,76,57     @mod=Core
color guy762_StructureColor_CzerkaYellow    220,170,95   @mod=Star Wars KotOR Resources and Materials
color guy762_StructureColor_EchaniGold      190,170,100  @mod=Star Wars KotOR Resources and Materials
color guy762_StructureColor_BespinBeige     175,150,120  @mod=Star Wars KotOR Resources and Materials
color guy762_StructureColor_ImpOfficerOlive 125,125,110  @mod=Star Wars KotOR Resources and Materials

# ------------------------------------------------------------------- ramps
# Every one of these DARKENS toward its far end, because that is the only
# direction a multiply can travel. Read them as "clean -> caked", never as
# "dirty -> bleached".
ramp scour_neutral  - > Structure_Cream > Structure_White > Structure_GrayLight > Structure_Limestone | grey dust, no hue commitment
ramp scour_warm     - > Structure_Cream > guy762_StructureColor_BespinBeige > Structure_Limestone > Structure_BrownLight > Structure_Sandstone > Structure_BrownFaded | tan dust working into the surface
ramp scour_gold     - > guy762_StructureColor_CzerkaYellow > guy762_StructureColor_EchaniGold > guy762_StructureColor_BespinBeige > Structure_BrownLight | sunlit, for a surface that should stay warm at distance
ramp scour_drab     - > Structure_Limestone > guy762_StructureColor_ImpOfficerOlive > Structure_BrownFaded | dust that has gone grey-green; reads older and dirtier

# --------------------------------------- pale material, permanent, unrationed
stuff PALE  sandstone=BlocksSandstone @mod=Core | warm pale stone
stuff PALE  limestone=BlocksLimestone @mod=Core | cooler, lighter than sandstone
stuff PALE  marble=BlocksMarble       @mod=Core | the lightest option; use sparingly, it reads as built rather than weathered

# -------------------------------------------------------------------- rules
rule Colour MULTIPLIES. You CANNOT bleach with a tint - every ramp here darkens. Reach pale by choosing pale TERRAIN and pale STUFF.
rule The desert reads about (107,86,57) at full bright. A scoured structure is legible LIGHTER than the ground; a warm brown one must be darker. This palette is the light option, and the only one.
rule Do not paint. The dev Set Color tool has a per-GAME-SESSION budget of roughly 380 and then silently misses while reporting success. Stuff carries colour permanently and survives a reload.
rule The def dump has no colour values. RGB here came from mod XML, calibrated 6 of 6 against values sourced another way. Do not add a colour whose RGB you have not read from XML or off the screen.

# -------------------------------------------------------------------- used
used Nothing yet.
```

## Owed

Ratios and a drift model. Both palettes so far have avoided inventing proportions,
and scour probably wants a *direction plus a falloff* rather than percentages —
closer to how the Cradle's corrosion was driven off a noise field than to a
tile-frequency table.
