# SHADE_GEAR_FAMILY_1 — carried and pitched shade, cross-biome

Ruled 2026-09-29 at the Long Shade bedazzle sitting (volley turn 4). The owner typed:

> "Actual shadow-casting gear doubles down on the idea of heat building up. I like it.
> Parisols, shade tents, simple shields you can stand behind. But again, this MUST be applied
> on other biomes where heat is extreme too... and there shade won't help you (in steam) or
> sideways shade (deep desert)."

Depends on `SOLAR_HEAT_EXPOSURE_1`, whose per-biome heat kinds set how well each piece works.
Tier: RimMandrake. **Model: sonnet**, since the defs and a comp are well defined and the
heat selftests check them. Escalate to opus if the shade-casting comp needs grid changes beyond
reading a caster.

## spec

- **Parasol**: an apparel/utility item that shades its wearer and, weakly, one adjacent cell.
  Works under `overhead` sun, is weak under `lowSun`, and does nothing under `ambient` heat.
- **Shade tent**: a cheap portable building that shades a small footprint. It is the tool for
  the Long Carry (going out into the sun for graves and salvage). It follows the same heat-kind
  rules as the parasol.
- **Sun shield**: a standing panel you stand behind. It casts a vertical shade on its lee side and
  is the one piece that works under `lowSun`. Under `overhead` it is modest.
- Every piece is useless under `ambient` heat, where the answer is insulation or leaving.
- Stuffable where it makes sense. Mirrak hide (`LONGSHADE_BEDAZZLE_MECHANICS_1`) is the best shade
  cloth: stuff made from it casts deeper shade.
- Art is commissioned by the sitting's movement 4.

## criteria

- Each piece measurably reduces sun heat on the right heat kind and does nothing on the wrong
  kind (selftest or quicktest).
- It ships with Mod Settings.
