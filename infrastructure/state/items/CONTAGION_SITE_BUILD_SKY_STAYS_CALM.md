# CONTAGION_SITE_BUILD_SKY_STAYS_CALM

Packet: `design/RimMandrake/biome_sprint_kickoff_2026-10-15.md` §1.2 (row 2: "a saved Contagion site is already
Contagion") and §4 D0 (BENCH tooling slice). Sibling of the Cauldron site (e1e5a6ff3a) and
`LEANING_SCRUB_SITE_BUILD_LEANS_ONE_WAY`.

## What
A saved `RM_Contagion` test site (`RM_TestSite_contagion_v1`) for the on-Contagion chains (sky state, Bloom/Burn
tells, burn_forced/burn_natural, uv, coalescence, genome, spawner, Sunbeam, limbs). The off-Contagion arm
(`repulsor_clear.site_ready_baseline` + downstream, `site.retile_to_contagion`) stays on the calm site.

## Built (offline, 2026-10-16, BENCH helper)
- `src/RimMandrake/Contagion/site_spec.py` (data; tile 25 C / 60 mm / 1387 m / Flat -- test values, reasons inline;
  natives = the BiomeDef's 23 MayRequire-free rows) + `src/RimMandrake/Contagion/prep_site.py` (thin; recipe shared in
  `src/RimMandrake/Utils/modcheck/biome_site.py`).
- `SITES["contagion"]` in `src/RimMandrake/Utils/modcheck/test_site_saves.py` (`builder` key).
- Guard: nothing saved unless check_map is clean, >=1 native lives, and `RM_MapComponent_ContagionSky.BurnActive`
  reads False (jawa/map_comp_read); the reload re-reads all three -> registry `loadVerified`.
- `src/RimMandrake/Contagion/selftest_contagion_site.py` GREEN (fake bridge; roster drift; food cache off every pad).
- preflight O-SITE now needs `loadVerified True` to PASS.

## Live round must
1. On `biomes_sprint`, bridge held: `python.exe src/RimMandrake/Utils/modcheck/test_site_saves.py build contagion`,
   then `load contagion`. First live use: map_comp_read on ContagionSky and the shared recipe are UNPROVEN live.
2. Before the driver can run on it: split the arms. `src/RimMandrake/Contagion/northstar_site.py` preflight REFUSES an
   RM_Contagion map ("the retile has no control"); the on-Contagion arm needs its own preflight (harness work).
