# SOLAR_MIRRORS_MOD_DESIGN_1 build — 2026-10-06 (FOUNDRY, offline)

## Status
Built and checked offline 2026-10-06; NOT committed (brief forbade git). Nothing live-tested.

## Sweep (reuse)
- `RM_MapComponent_ShadeGrid` (CreatureBehaviors): ShadeAt/ExposureAt/RoofShadeAt/CastShadeAt/Recompute/SunShadowDirection/SunElevationDegrees are public; `exposure[]`, `pathCustomizer`, `RebuildHeatLayers` are private.
- Design P0 (a public `RegisterLightSource` hook inside CreatureBehaviors) is OUT of this brief's scope (everything outside the new mod is read-only). Substitute: Harmony postfixes from SolarMirrors on `RebuildHeatLayers` (writes light into the cached exposure array + the fresh path-cost grid, so pathing and the patch graph see it), `ShadeAt` and vanilla `GlowGrid.GroundGlowAt`. Same effect as P0; P0 stays the cleaner long-term shape.
- Stillsand `RM_SunLance` / `RM_Verb_MirrorBeam`: a sun-powered TURRET (burns a target). Not a light layer; nothing to share beyond its art (`RM_SunLance_Base`, used as a placeholder).
- `RM_GlareBlind` (hediff + `EyesProtected`) reused for the blinding defence.
- Packaging: non-biome mods stay standalone (spec §1 OUT, ruling 4). Like ShipVermin, depends on `mandrake.rm.biomes` (CreatureBehaviors is folded into it). No Biomes.compose.json entry.

## Shipped
All under `src/RimMandrake/SolarMirrors/` (packageId `mandrake.rm.solarmirrors`, namespace `RimMandrake.SolarMirrors`):
- Light layer `RM_MapComponent_MirrorLight`: collectors read mirror-free sun (roof + cast shade only), 3D cosine law, relays (acyclic, depth <= maxChain, consume energy), blocker rule per §2.2 (roof on path or target, closed door, wall/rock), quantised change hash, one throttled shade-grid Recompute per change, glow dirtying, central spot + beam render (fog-masked), blinding tick.
- Sun: pinned sun (Long Shade) > shade grid's fixed sun > a simple moving sun (PROVISIONAL model) for static-mirror sweep.
- `RM_CompMirror`: saved normal + target + pending, aim gizmo with live preview (line, spot edges, efficiency/blocker label), clear-aim, inspect string, heliostat tracks while powered and freezes unpowered (E13 for free).
- Re-aim WorkGiver (Construction) + JobDriver.
- Patches: `RebuildHeatLayers` postfix (lit exposure into the cached array + fresh path-cost grid), `ShadeAt` postfix, `GlowGrid.GroundGlowAt` postfix, `Building_WorkTable.UsableForBillsAfterFueling` postfix (furnace).
- Defs: RM_SignalMirror, RM_StaticMirror (stuff reflectivity), RM_Heliostat (150 W), RM_SunStone (receiver, hysteresis), RM_SolarFurnace (E1, smelter recipes, needs >= 2 mirrors), JobDef + WorkGiverDef RM_ReAimMirror.
- E4 blinding defence (hostile humanlikes, RM_GlareBlind, EyesProtected honoured).
- Settings: 11 Scribed fields, scroll view + maxOneColumn, reset button.

## Deferred
- P4 Long Shade ancient mirror field (detents, solver, sun-stone vault, latch) — large; needs the biome to carry `RM_MirrorFieldExtension` (can be done by a patch inside this mod).
- E3 heliograph signals (world comms), E2 mirror greenhouse (needs a glazed roof/aperture def), E15 sun-stone switches driving doors.
- Dust on mirrors + cleaning job; concentration > 1 into heat; furnace indoor PushHeat; SectionLayer spot render (spots are per-cell quads now).
- P0 hook in CreatureBehaviors (out of brief scope; the postfixes stand in).
- Walk file `design/validation_walks/RimMandrake/SolarMirrors.md` (outside the mod, read-only in this brief).

## Checks
- winbuild.py SolarMirrors: 0 warnings, 0 errors (DLL + .srchash).
- validate_patch.py Defs --defs Data: 0 errors, 5 warnings (vanilla texPaths live in bundles; class refs are our own).
- validation.py static: PASS (0 findings); failure path sanity-probed.

## Art owed
artpipe_state.py find mirror/heliostat/sunstone/heliograph/'solar mirror'/'signal mirror': no job for any subject ("mirror" hits are other subjects' prose). Placeholders now. Jobs owed: RM_SignalMirror (1x1), RM_StaticMirror (2x2, stuff-tinted), RM_Heliostat (3x3), RM_SunStone (1x1 lit/unlit pair), RM_SolarFurnace (3x1 Graphic_Multi), beam/spot glow texture.

## Open questions
- Design §2.2 says a roof ON THE PATH blocks; §6.2 line 4 says it does not. Built per §2.2 (the later revision).
- No bridge probe reads ShadeAt/LightAt at a cell (RM_ShadeProbe owed) so every live line is UNMEASURED.
- Legibility of the lit patch inside a vanilla shadow needs the owner watching.
