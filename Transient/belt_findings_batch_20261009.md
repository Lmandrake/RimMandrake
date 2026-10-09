# belt findings batch 2026-10-09

(per item: ID, verdict, fix, sha)
- SKETTO_FLIGHT_DRAWSIZE_FIX_1: REAL (RSW_Sketto.xml:183 IsMultiplier false, size 1.0 vs grounded 1.25); set true.
- GOD_DELTA_DIMINISH_CLAMP_1: REAL; clamp+fuzz updated, fuzz 9501 OK, a138f069b
- SKETTO sha 14187a2ad
- FEVERWOOD_UNDECLARED_DEPS_1: FALSE (engine kits are composed members; union_about drops member ids) -> dropped
- AEROSOL_SCREEN_STATICCTOR_WARN_1: already fixed 220d7a754 (DomeMaterial nested [StaticConstructorOnStartup]); implemented
- DEEPFIRE_FAMILY_SETTINGS_KEYED_1: REAL; keyed disabled list + legacy migration; builds, fuzz+lint OK; 65798d581 (Scribe round-trip not unit tested)
- GLOW_TANK_SEED_CULTURE_1: REAL (ConsumeFuel only on blackout); established flag; build OK; 57536f0db (live sow check owed)
- WRECKAGE_SCALD_FIELD_MISCLASSIFIED_1: REAL (suite.__exit__ made every ExpectationFailed FAIL); harness fix + selftest 22/22; fddc64719
- CLUSTER_LIGHT_MEMBER_COVERAGE_1: REAL (fuzz failed 5 cases without fix); radius>=farthest+0.5; 60f715a85
Skipped (design-sensitive/owner): GARDEN_ESCALATION_PROGRESS_FIX_1, GREY_LAMP_ANSWER_RETRY_1, THORNBUG_FEAR_SCOPE_1, PRESS_GATE_BUILDABLE_RESEARCH_1
