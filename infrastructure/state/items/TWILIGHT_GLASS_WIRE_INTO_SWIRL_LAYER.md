# TWILIGHT_GLASS_WIRE_INTO_SWIRL_LAYER

Parent: WORLD_WATER_REDRAW_SEAS_THAT_READ_DEEP. Owner, 2026-10-24: the Twilight Sea has "a stained glass window-like
layer of life growing just below it's surface everywhere ... subtle large patches of beautiful primary colors in
organic shapes". Options on `Transient/world_water_review_r2_2026-10-24.html` rows TwilightSea_glass_{bloom,panes,jewel};
textures `*_glass.png` (512 RGBA, one repeat = 40 tiles) in `D:\ClaudeWork\rimmandrake\scratch\worldwater_variants_r2\sheet`.

## spec
Mechanism found:
- The swirl layer (`BuildSwirls`, RM_WorldLook.cs line 446) already draws a per-biome RGBA texture
  `World/RM_Swirls/<name>` at queue 3506, over the sea films and under hills/rivers, world-planar UVs. Its biome list is
  the static `swirlBiomes` (line 61). There is no water exclusion, so a sea biome can carry one.
- DATA: the png `Textures/World/RM_Swirls/TwilightGlass.png` (his picked variant) + the list entry
  `RM_TwilightSea=TwilightGlass,RUT_TwilightSea=TwilightGlass` (a live Set, or a one-line default change).
- C#: `swirlUvScale` (line 63) is global, ~25 units per repeat; the glass needs ~40 tiles per repeat, so a per-biome
  scale (`name@scale` in the list) is C#. Mod Settings: "Planet: Twilight Sea glass" (its own toggle, not
  `worldBiomeSwirls`).
- Honest limit: the glass sits ABOVE the face ripple at low alpha; the ripple shows through it, but it is not truly under
  the water. The tried in-face route (glass painted into the face) was dropped: a face spans ~3 tiles, so it speckled at
  far zoom.

## verify
Needs The owner's pick on the r2 sheet; then texture install + C# per-biome scale + toggle, winbuild + .srchash, deploy.
Then the owner-attended world look (18 grid points at 900 + close-ups at 320): no speckle at far zoom, ripple visible through it.
