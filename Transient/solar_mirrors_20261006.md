# SOLAR_MIRRORS_MOD_DESIGN_1 build — 2026-10-06 (FOUNDRY, offline)

## Status
Built and checked offline 2026-10-06; NOT committed (brief forbade git). Nothing live-tested.

## Sweep (reuse)
- `RM_MapComponent_ShadeGrid` (CreatureBehaviors): ShadeAt/ExposureAt/RoofShadeAt/CastShadeAt/Recompute/SunShadowDirection/SunElevationDegrees are public; `exposure[]`, `pathCustomizer`, `RebuildHeatLayers` are private.
- Design P0 hook DONE (follow-up pass, below): light reaches the shade grid through CreatureBehaviors' public `IRM_LightLayer` / `RegisterLightSource`; no patch touches the grid's internals.
- Stillsand `RM_SunLance` / `RM_Verb_MirrorBeam`: a sun-powered TURRET (burns a target). Not a light layer; nothing to share beyond its art (`RM_SunLance_Base`, used as a placeholder).
- `RM_GlareBlind` (hediff + `EyesProtected`) reused for the blinding defence.
- Packaging: non-biome mods stay standalone (spec §1 OUT, ruling 4). Like ShipVermin, depends on `mandrake.rm.biomes` (CreatureBehaviors is folded into it). No Biomes.compose.json entry.

## Shipped
All under `src/RimMandrake/SolarMirrors/` (packageId `mandrake.rm.solarmirrors`, namespace `RimMandrake.SolarMirrors`):
- Light layer `RM_MapComponent_MirrorLight`: collectors read mirror-free sun (roof + cast shade only), 3D cosine law, relays (acyclic, depth <= maxChain, consume energy), blocker rule per §2.2 (roof on path or target, closed door, wall/rock), quantised change hash, one throttled shade-grid Recompute per change, glow dirtying, central spot + beam render (fog-masked), blinding tick.
- Sun: pinned sun (Long Shade) > shade grid's fixed sun > a simple moving sun (PROVISIONAL model) for static-mirror sweep.
- `RM_CompMirror`: saved normal + target + pending, aim gizmo with live preview (line, spot edges, efficiency/blocker label), clear-aim, inspect string, heliostat tracks while powered and freezes unpowered (E13 for free).
- Re-aim WorkGiver (Construction) + JobDriver.
- Patches (vanilla only): `GlowGrid.GroundGlowAt` postfix, `Building_WorkTable.UsableForBillsAfterFueling` postfix (furnace). Shade/exposure/path cost go through the P0 hook.
- Defs: RM_SignalMirror, RM_StaticMirror (stuff reflectivity), RM_Heliostat (150 W), RM_SunStone (receiver, hysteresis), RM_SolarFurnace (E1, smelter recipes, needs >= 2 mirrors), JobDef + WorkGiverDef RM_ReAimMirror.
- E4 blinding defence (hostile humanlikes, RM_GlareBlind, EyesProtected honoured).
- Settings: 11 Scribed fields, scroll view + maxOneColumn, reset button.

## Deferred
- P4 Long Shade ancient mirror field (detents, solver, sun-stone vault, latch) — large; needs the biome to carry `RM_MirrorFieldExtension` (can be done by a patch inside this mod).
- E3 heliograph signals (world comms), E2 mirror greenhouse (needs a glazed roof/aperture def), E15 sun-stone switches driving doors.
- Dust on mirrors + cleaning job; concentration > 1 into heat; furnace indoor PushHeat; SectionLayer spot render (spots are per-cell quads now).
- Walk file `design/validation_walks/RimMandrake/SolarMirrors.md` (outside the mod, read-only in this brief).

## Checks
- winbuild.py SolarMirrors: 0 warnings, 0 errors (DLL + .srchash).
- validate_patch.py Defs --defs Data: 0 errors, 5 warnings (vanilla texPaths live in bundles; class refs are our own).
- validation.py static: PASS (0 findings); failure path sanity-probed.

## Art owed
artpipe_state.py find mirror/heliostat/sunstone/heliograph/'solar mirror'/'signal mirror': no job for any subject ("mirror" hits are other subjects' prose). Placeholders now. Jobs owed: RM_SignalMirror (1x1), RM_StaticMirror (2x2, stuff-tinted), RM_Heliostat (3x3), RM_SunStone (1x1 lit/unlit pair), RM_SolarFurnace (3x1 Graphic_Multi), beam/spot glow texture.

## Open questions
- Design §2.2 says a roof ON THE PATH blocks; §6.2 line 4 says it does not. Built per §2.2 (the later revision).
- No bridge probe reads ShadeAt/LightAt at a cell (RM_ShadeProbe owed) so every live line is UNMEASURED. Not added to the SolarMirrors DLL: the rimbridge-companion pattern puts `[Tool]`s in the JawaBench companion (RimBridge SDK reference, main-thread InvokeAsync), which a shipping mod must not depend on. Owed there: `jawa/shade_probe` reading `RM_MapComponent_ShadeGrid.ShadeAt/ExposureAt/LightAt/GridVersion` and `RM_MapComponent_MirrorLight.LightAt` at a cell.
- Legibility of the lit patch inside a vanilla shadow needs the owner watching.

## Follow-up 2026-10-06: P0 hook + review (FOUNDRY, offline, NOT committed)
- **CreatureBehaviors hook** (`RM_MapComponent_ShadeGrid.cs`): `public interface IRM_LightLayer { bool AddLight(float[] into); }`, `RegisterLightSource` / `UnregisterLightSource`, `LightAt(cell)`. Recompute order: ... moving shade → `BuildLightLayer()` → `RebuildHeatLayers()` (exposure = `WithLight(ex, light)` after the glare floor, skipped under ambient heat, so path cost and the patch graph see it) → `gridVersion++`. `ShadeAt` = `ShadeWithLight(max(roof,cast), light)` then gear/parasol/moving cover (algebraically identical to the old postfix). No source registered: `anyLight` false, nothing reads the buffer — zero behaviour change. `RM_SunHeatMath.WithLight` / `ShadeWithLight` (pure) + selftest case "light hook" PASS (31/39 overall in the staged run; the 8 FAILs are the staging dir lacking the repo tree, `src/RimMandrake not found above`, not this change).
- **SolarMirrors**: `RM_MapComponent_MirrorLight` implements `IRM_LightLayer` (registers in FinalizeInit + lazily on tick, unregisters in MapRemoved). The `RebuildHeatLayers` / `ShadeAt` postfixes and their FieldRef reflection are deleted; validation.py's name-pinning check replaced by `_hook_checks` (source regexes for every hook piece + the built CB DLL's metadata names with a sanity probe + "no Harmony patch on the shade grid"); failure path proven. NEEDLES now include `IRM_LightLayer`/`RegisterLightSource` (a stale Biomes DLL would TypeLoad). New LIVE_OWED line `hook.registered`.
- Behaviour note: shade/exposure now update when the grid recomputes (mirror change → throttled ≤60-tick rebuild, PROVISIONAL), not live per ShadeAt call — one GridVersion for all consumers, as the design wants.
- **Review fixes**: (1) spots/beams were drawn while the world view was open (`Map.MapUpdate` calls `MapComponentUpdate` regardless) — gated on `WorldRendererUtility.DrawingMap`. (2) The beam walk allocated a closure + delegate per spot cell per pass and per frame in the aim preview — `LineClear` is now a generic struct visitor (`IRM_LineVisitor`), zero allocation. (3) Blocker strings were re-Translated every pass — cached. (4) Toggling `shadeEffect` did nothing until the next 2000-tick grid rebuild (hash unchanged) — `WriteSettings` now forces a grid rebuild. (5) the static `For()` cache held a removed map — cleared in MapRemoved.
- Checked, no bug: save/load (normal/target/pending Scribed; layer rebuilt from zero; lastInDir intentionally unsaved), null maps on despawn/signals (`For(null)` safe), job driver null target (TryGetComp null-safe), blinding pawn list copied before iterating, `GlowGrid.map` field name verified (RimSage), all Unity calls on the main thread.
- Builds: `winbuild.py CreatureBehaviors` 0W/0E; `winbuild.py SolarMirrors` 0W/0E; `validation.py` static PASS.
