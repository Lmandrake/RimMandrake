# SHIELD_MODS_LEVERAGE_1 — survey done, scoping (BENCH, 2026-09-02)

Survey: research/Jawa/shield_mods_survey_2026-09-02.md. Recommended shape:
- **Foundation: VEF's shield engine** (`CompShieldField`, MIT, already in our
  stack) — energy-drain-to-EMP-explosion is exactly the ruled
  overheat/collapse behavior, XML-tunable.
- **Extend Odyssey's NATIVE gravship shield slot** rather than duplicating a
  parallel system — two workshop mods already prove that hook works.
- **Module architecture from ED-Shields** (jaxxa, MIT): projector/converter
  modules match the ruling "same shields, install modules to increase
  switching capacity/configuration".
- ⚠️ Verify before building: VFE-Security 1.6 vs native gravship shield
  compat, and VEF point-defense's "slow projectiles intercepted MORE easily"
  reading — that is BACKWARDS from our pass-through canon
  (shd:shield-collapse-evacuate) and must be checked against source.
