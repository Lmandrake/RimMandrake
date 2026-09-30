# SOLAR_HEAT_EXPOSURE_1 — sun heat, planet-wide, on the game's own heat

Ruled 2026-09-29 at the Long Shade bedazzle sitting (`LONGSHADE_BEDAZZLE_SITTING_1`, volley turn 4).
The owner typed:

> "If we implement the heat load, then places like the Deep Desert and volcanic biomes should
> absolutely roast you similarly. It can't be a new "kind" of heat."

**Model: opus** (Agent_Policy: complex code generation, a new cross-cutting system with no
test that catches a wrong design). Tier: RimMandrake (`mandrake.rm.*`). The owner still has to
judge the tuning by watching it in game.

Design source: `design/Jawa/worldbuilding/biomes/longshade_shade_ideation_2026-09-29.md` §1
(feasibility, MEASURED from CreatureBehaviors source and RimSage), §3.1 (the sun angle), §6.1
(the player's experience), and the "Rulings — volley turn 4" section. Where the doc says to reuse the
shade-driven hediff comp as the heat load, the ruling above overrides it.

## spec

1. **Sun exposure feeds vanilla heat.** A pawn standing in unshaded sun on a sun-heat map takes
   a heat increment into the game's existing temperature → Heatstroke path. Do not add a new
   heat hediff. Apparel insulation, comfort range and heatstroke keep their vanilla meaning.
   Body size sets how long a pawn can stay in the open, and this is what makes dash range a
   function of size (§1.2).
2. **Heat kinds, per biome**, as a def-side extension on the BiomeDef:
   - `overhead`: the Long Shade. Roofs and overhead shade protect.
   - `lowSun`: the Deep Desert. Only a vertical shadow on the lee side protects.
   - `ambient`: steam and volcanic biomes. Shade does nothing; only insulation or leaving helps.

   Identify each extreme-heat biome by reading its BiomeDef and sheet, and list them in the
   close note. Do not guess from names.
3. **Directional shade grid** (§1.3). `RM_MapComponent_ShadeGrid` casts along the map's pinned sun
   vector, not in a radius-2 ring, so the shade the player sees and the shade animals use are
   the same cells.
4. **Sun-cost pathing** (§1.2): a per-cell sun cost fed to path requests through one Harmony
   patch, so ordinary jobs route shade-to-shade.
5. **Rest-dash-rest for animals** (§1.2): a shade-patch graph, and job givers for resting in
   shade, pausing at the rim, then sprinting to a patch within dash range. The owner's
   condition: *"a tad boring unless we get really strict about the dashing animal behavior."*
6. **Legibility**: a sun-load bar in the inspect pane, and a ring on the ground around a drafted
   pawn marking how far it can go and still get back to shade (§6.1).
7. **Mod Settings**: a master toggle, strength tuning, and per-feature toggles, per the
   every-mod-ships-settings rule.

## criteria

- The selftests cover the heat increment (sun vs shade vs roofed) and the path cost.
- Quicktest on a Long Shade map: animals visibly rest, pause at the rim and dash, and a
  colonist in the open heats up through vanilla heatstroke.
- On a steam/volcanic map, shade gives no relief. On a low-sun map, overhead shade gives none.
- An owner-watched live sitting rules on the strictness tuning.
