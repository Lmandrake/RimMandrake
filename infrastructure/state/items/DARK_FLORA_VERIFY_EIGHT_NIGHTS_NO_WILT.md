# DARK_FLORA_VERIFY_EIGHT_NIGHTS_NO_WILT

Filed 2026-10-20 (FOUNDRY). Live readback for `DARK_FLORA_FIX_WILTS_WITHOUT_A_SUN`, fixed offline in commit
`48f2c1ad9d4d` and NOT yet deployed. Spec of the fix: `design/RimMandrake/glow_consumers_2026-10-20.md` §A.

What changed (repo only): sunless plants now set `growMinGlow 0` AND `growOptimalGlow 0`, so the light factor is 1
at any glow. Mods touched: TheSump, TheRot, Cauldron, Abyss, GelatinousSlime, Wasteland, TerminalBiomes. Offline
guard: `src/RimMandrake/Utils/selftest_plant_glow_halfset.py`.

## spec
- Deploy the seven mods above with the next deploy (`deploy_custom_mods.py --mod <name>`, then `--apply`).
- Read live: `growOptimalGlow` and `growMinGlow` of `RM_Brindeth` (Sump), `RM_Bryolux` (Rot, inherited from
  `RM_TheRotPortedCavePlantBase`) and `RM_Xithess` (Cauldron) all read 0.
- Watch a night-side plant survive: on a map with sky glow 0 (night-side tile under the tidal lock), spawn a
  `RM_Brindeth` or `RM_Bryolux`, advance 8 in-game days, and state-read the plant: still spawned, `Growth`
  rising, `unlitTicks` 0 (vanilla kills at 450000).

## verify
- All three defs read 0/0 live, and the plant is alive and has grown after 8 days.

NEXT: after the next deploy, read growOptimalGlow of Sump flora live and watch a night-side plant survive 8 days via a state read.
