# STILLSAND_SUN_LANCE_1 — the sun lance heliostat turret

From `STILLSAND_GLASS_LENS_CHAIN_1` §7 (slate IN), which that pass did not build.

## spec

A heliostat turret: an array of mirrors that focuses the fixed sun on one target. It heats and
never ignites. It is useless in the gale or in shade, and its strength scales with the sun's
elevation. Keep it distinct from the Long Shade's heliograph (that one signals, this one burns).

- It can share `RM_Verb_MirrorBeam` (`src/RimMandrake/Stillsand/Source/RM_Verb_MirrorBeam.cs`).
  That is the muurrok's beam, already gated on sun and already fire-free. Check whether the verb
  works with a turret as its caster before writing a new one.
- Sun-factor helper: `RM_SunPower` in `RM_SunPowered.cs`.
- Art: artpipe jobs `RM_SunLance_Base` and `RM_SunLance_Top` are registered.
- A Mod Settings toggle in `RM_GlassChainSettings`.

## criteria
- The sun lance damages a target and starts no fire. It does nothing in shade or in the gale.
