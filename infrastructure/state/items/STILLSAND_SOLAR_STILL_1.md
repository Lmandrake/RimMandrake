# STILLSAND_SOLAR_STILL_1 — the solar still and the wringing still

From `STILLSAND_GLASS_LENS_CHAIN_1` §5, which that pass did not build. Read the parent's §5 for
the full ruling.

## spec

A glazed, black-bottomed lens condenser. It distils water from brine (cave seeps) and from wet
organics (fresh kills, eggs, duumma sacs). As the **wringing still** (lore IN) it also distils
**the dead**: a corpse gives water, outsiders take a mood penalty, and Sun-Debt believers call it
*drawing* (Utinni thoughts, RUT tier).

- Output goes into FlowWorks' water liquid or DBH water, whichever is live. Check which before
  building.
- The rate scales with sun elevation. A pearl lens (`RM_PearlLens`, already built) doubles it.
- Every litre counts on the Debt (`STILLSAND_RETURN_RITUAL_1`).
- It is distinct from the moisture vaporator.

Reuse: `RM_CompProperties_SunPowered` and `RM_SunPower.FactorAt` in
`src/RimMandrake/Stillsand/Source/RM_SunPowered.cs` already provide the sun gate: roof, shade
grid, pinned-sun elevation, and the gale matched by name. Glazing is `RM_SunGlass`; the
condensers are `RM_PrecisionLens`. Art: artpipe job `RM_SolarStill` is registered. Settings: a
toggle and a still-rate slider in `RM_GlassChainSettings` (parent §12).

## criteria
- A still completes one cycle in full sun and stops in the gale. A pearl lens doubles its rate.
