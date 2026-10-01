# PYRELANDS_GREEN_MINIMAL_1 — Pyrelands north star GREEN on the minimal tier

**For:** FOUNDRY (needs the bridge). **Parent:** PYRELANDS_NORTHSTAR_TRIAL_1. **Plan:** `design/RimMandrake/northstar_trials/Pyrelands_trial_plan.md` §3, §4.
**Depends on:**
- PYRELANDS_NORTHSTAR_WIRING_1;
- MODCHECK_COMPOSED_BIOMES_LIST_1 (or the trial's own tier, which avoids it);
- the shared `northstar_driver` (plan §7);
- BIOME_MOD_UNIFICATION_1 (the run tests the composed `mandrake.rm.biomes`).

## acceptance

- [ ] A `pyrelands` tier in `modset_builder.py` (plan §3.1): `mandrake.rm.biomes`, `rut.patches`,
      `rsw.swbestiary`, `rut.pyrelandsmechanics`, all five DLCs. It excludes biometransitions,
      Map Designer and flora injectors.
- [ ] Gates A, B and C (plan §3.8) are implemented. They report all failures at once, refuse on an
      unexpected dialog, and restore settings byte-exact.
- [ ] Sites are built per plan §3.4: a fresh quicktest world per site; a 2-ring re-tile at 50 °C,
      |lat| ≤ 25°, mutators stripped; census at tick 0; save; reload; [V] captured on the reload.
      Plus one 30 °C control site.
- [ ] Every bar passes its plan §2.2/§2.3a predicate. Animals are pooled to ≥ 150. Evidence goes to
      `Transient/modcheck/Pyrelands_<ts>.html` + summary JSON with the def fingerprint and tier
      manifest.
- [ ] `rimflow verify PYRELANDS_GREEN_MINIMAL_1 --result pass --config pyrelands-tier` with the
      evidence path. A real mod defect found by a bar is filed as its own item, never tuned around
      (for example, grass not regrowing at 50 °C is a finding about the shipped world).
- [ ] Never `modcheck run` (it rewrites ModsConfig). The bridge is released when done.
