# PYRELANDS_NORTHSTAR_WIRING_1 — wire every Pyrelands bar to a test (`shows=`)

**For:** FOUNDRY. **Parent:** PYRELANDS_NORTHSTAR_TRIAL_1. **Plan:** `design/RimMandrake/northstar_trials/Pyrelands_trial_plan.md` §2, §2.3, §2.3a.
**Depends on:** PYRELANDS_NORTHSTAR_VALIDATE_1 (bar ids are final) and BIOME_MOD_UNIFICATION_1
(the composed packaging).

## acceptance

- [ ] `src/RimMandrake/Pyrelands/validation.py` has exactly one component per validated bar, each
      with `shows=[<bar id>]`. `floor.uncovered_shows` and `floor.orphan_shows` both return [].
- [ ] Suite bugs fixed (plan §2.3):
      - `biome_def_wiring` targets `RM_Pyrelands`;
      - `fulgurite_armed_only` matches `fulgurite-spawn`, not the dead `StarWars.FireEcology` prefix;
      - the ash ladder burns grass on ground, as a fixed cell cohort;
      - ashfall is counted over the whole map from zero.
- [ ] Predicates use immutable manifests (plan §1.3: 3 plants, 15 kinds) and cell-for-cell
      coverage. Per plan §2.3a, ⚖ thresholds are reported, not gated, until ruled.
- [ ] OFF-arms of the floor use `jawa/mod_settings_field` (static fields), restored in a `finally`.
- [ ] Walk header `subject:`/`list:` and the `validation.py` docstring are corrected to the
      composed packaging. This is **outside** the hashed section, and the hash must still match
      afterwards.
- [ ] `WildAnimals_Pyrelands.xml` header comment corrected: the herd is `RSW_*`, not bare names.
      Its two top-level `<Operation MayRequire>` guards are noted on `PATCH_MAYREQUIRE_GUARD_INERT_1`.
- [ ] `python3 src/RimMandrake/Utils/run_selftests.py` passes, and an offline modcheck lint is clean.
