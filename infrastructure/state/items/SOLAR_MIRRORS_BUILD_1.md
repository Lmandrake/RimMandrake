# SOLAR_MIRRORS_BUILD_1 — Solar Mirrors to deploy-ready: everything the design scopes that is not built

Owner, 2026-10-08: *"Fully build Solar Mirrors to full deploy ready status."* Split from
`SOLAR_MIRRORS_MOD_DESIGN_1` (design `design/RimMandrake/solar_mirrors_mod_design_2026-10-04.md`,
rulings 2026-10-04 in its §7). Mod: `src/RimMandrake/SolarMirrors/`.

## already built (measured 2026-10-08)

P0 light hook in CreatureBehaviors; P1 light layer, comps, settings, kernel with seeded fuzz and
mutation set; P2 signal/static mirror, heliostat, sun-stone, re-aim job; P3 spot and faint shaft
render, aim preview, `GroundGlowAt` postfix; E1 solar furnace (bill gate); E4 blinding (glare-blind
hediff); E13 power-loss freeze.

## spec (the remainder)

1. **§3.4 ancient mirror field (P4), the Long Shade puzzle:** `RM_MirrorFieldExtension`, a mapgen step
   gated on it and on a settings toggle, 4–6 seized ancient heliostats with 3 visible detents each,
   2–4 sun-stones, a sealed vault (loot + a repaired heliostat) that opens latched when every stone is
   lit; repair (a component + Construction) before a mirror turns; every turn is a job; mapgen solves
   the layout before placing it (≥ 1 solution, unsolved start, minimum re-aims ≥ the difficulty
   setting, chain ≤ 4, reset always possible); escalating hints. Reaches `RM_LongShade` by a patch in
   this mod.
2. **§3.2 dust:** dust/sand storms dirty mirrors and cut reflectivity until a cleaning job runs.
3. **§2.6/§3.3 concentration heat:** light above 1 adds to the vanilla felt-temperature offset, capped
   by the biome's existing `maxHeatOffsetC`; never a new hediff.
4. **E2 mirror greenhouse:** a glazed aperture that lets a beam into a roofed room; mirror light warms
   an enclosed room (`PushHeat`), and glow inside rises (the existing postfix). **E1 remainder:** the
   furnace warms its room when lit indoors.
5. **E3 heliograph:** a colonist flashes a friendly settlement in range by day from a signal mirror,
   opening the vanilla comms dialog with that faction.
6. **E4 remainder:** a dazzle accuracy penalty for hostile shooters standing in a beam.
7. **§3.5 settings:** the missing toggles and tuning (fields, difficulty, dust, heliostat power,
   concentration, greenhouse, heliograph, dazzle).
8. `RM_ShadeProbe` bridge `[Tool]` in the JawaBench companion (built, not deployed).
9. Placeholder art proven via artpipe state; owed art queued per the art ledger.
10. Walk file, validation.py, def lint, kernels with seeded fuzz and mutation sets, keyed strings,
    About.xml description.

## criteria
- [ ] A1 L0: the mod builds clean with its `.srchash`; every selftest and the SolarMirrors fuzz, lint and mutation set pass; validation.py static PASS.
- [ ] A2 L1: every SolarMirrors def loads with its comps and no error names the mod on a minimal list (CreatureBehaviors + LongShade + SolarMirrors, all five DLCs).
- [ ] A3 L2: a mirror aimed at a shaded cell lowers ShadeAt and raises ExposureAt there (read by `jawa/shade_probe`); a wall or roof on the beam takes it; a relay fires; the patch graph's version moves.
- [ ] A4 L2: a generated Long Shade map carries an ancient field whose solver report reads solvable with an unsolved start; lighting every stone opens the vault and it stays open.
- [ ] A5 L2: dust from a sandstorm lowers a mirror's delivered light; a cleaning job restores it.
- [ ] A6 L2: a beam through a glazed aperture into a roofed room warms it; the furnace lit indoors warms its room.
- [ ] A7 L2: the heliograph opens comms with a friendly faction in range by day and refuses at night.
- [ ] A8 L4: with the owner watching, the lit patch reads as light inside a rendered shadow and the herd re-routes.

## verify

Offline: `python3 src/RimMandrake/SolarMirrors/validation.py`, `python3 src/RimMandrake/Utils/selftest_solarmirrors_fuzz.py`,
`python3 src/RimMandrake/Utils/lint_solarmirrors_defs.py`. Live: `python.exe src/RimMandrake/Utils/modcheck/cli.py run SolarMirrors`.

### Exact checks 2026-10-09 (acceptance sitting)
- A2 CHECK: Existing chains in `SolarMirrors/validation.py`: `load` (`jawa/drain_log limit=400 errorsOnly=True`, filtered for the module NEEDLES) and `defs` (`jawa/get_defs defs=<ALL_DEFS> fields="defName"`, the 10 ThingDefs RM_SignalMirror RM_StaticMirror RM_Heliostat RM_SunStone RM_SolarFurnace RM_AncientHeliostat RM_MirrorDetent RM_SunVaultWall RM_SunVaultSeal RM_GlazedAperture, the 4 JobDefs RM_ReAimMirror RM_CleanMirror RM_RepairAncientMirror RM_FlashHeliograph, GenStepDef RM_GenStep_AncientMirrorField and the 3 WorkGivers). Comp resolution is implied: a ThingDef whose comp Class cannot resolve is discarded whole, so presence is the check. Companion read: `jawa/shade_probe` success=true. PASS: drain_log shows no error naming SolarMirrors; get_defs success=true with notFound empty for all ALL_DEFS; shade_probe returns present.shadeGrid/mirrorLight/mirrorField truthy and missingMembers empty. FAIL: any def in notFound (its comp or class failed), an error line naming the mod, or shade_probe success=false (companion not deployed: UNMEASURED).
