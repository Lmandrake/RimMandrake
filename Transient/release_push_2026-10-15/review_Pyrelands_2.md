# Pyrelands review pass 2 — BENCH, 2026-10-15

Scope frozen (owner: "We need to stop increasing scope") — bug fixes only. Offline: no deploy, no bridge.

## Tasks
| # | task | outcome | sha |
|---|---|---|---|
| 1 | FIREFOAM_DIAGNOSE_CANNOT_AIM_AT_FIRE | Verb_Shoot gets targetParams canTargetLocations + canTargetFires (vanilla incendiary/smoke launcher shape; canTargetFires confirmed a TargetingParameters field in Assembly-CSharp). Row `firefoam_can_aim_at_fire` reads the def: true/true, passes by design. Live aim check still owed (item noted). | 17e90dc6ca |
| 2 | RM_TerrainDig designator text -> Keyed | label, desc and the three refusal strings -> `RM_ShovelSand*` keys in Languages/English/Keyed/Pyrelands.xml | 17e90dc6ca |
| 3 | full-file review + mark-clean | 10 files CLEAN, 1 DIRTY (below) | 17e90dc6ca + this commit |
| 4 | CANONICAL_SAVE.md | FALSE: named CANONICAL_ASHKARR_2026-09-09.rws and its .bak chain; none of them is in the Saves folder (only CANONICAL_ASHKARR_START_2026-09-12.rws + its .bak-*). Rewritten to the start save (owner 2026-09-12 ruling, canon.yml planet.start_savegame). canon.yml line 76-78 still says the 09-09 file is "kept as the owner's keeper" — it is not in the Saves folder; left for the canon owner. | this commit |

## Full-file reviews
| file | findings | fixed | verdict |
|---|---|---|---|
| Pyrelands/validation.py (2763) | firefoam row comment said "carries no targetParams" (now false) | comment corrected | CLEAN |
| Source/SelfTest/Fuzz/PyrelandsFuzz.cs (1128) | none significant (several table checks sit inside the 1-in-20 cohort branch; still ~200 runs) | - | CLEAN |
| Source/FireEcologyHook.cs (591) | FIRE_ECOLOGY_DIAGNOSE_FOREST_FIRES_FRUIT: fire-tick hook treats vanilla Soil/Sand/Gravel/SoilRich as scorchable on ANY biome (no AppliesToBiome gate) — confirmed by reading. Open design question in the item (generic engine vs Pyrelands-only), and the live row assumes "no fruit on Soil even on the Pyrelands site"; not a scope-frozen bug fix | not fixed | **DIRTY** |
| Source/PyrelandsAshField.cs (587) | mouseover sign ", watered" / ", fresh burn +N (N days)" hard-coded English | keyed RM_AshSignWatered / RM_AshSignFreshBurn | CLEAN |
| Source/MapComponent_BurnLine.cs (434) | none | - | CLEAN |
| Source/Kernel/RM_FireEcoKernel.cs (421) | none (the predicate is right; the missing gate belongs to the hook) | - | CLEAN |
| Source/Kernel/RM_BurnKernel.cs (360) | none | - | CLEAN |
| Utils/lint_pyrelands_defs.py (382) | density-enforcer constants unparsed -> check silently skipped | blindness ERROR added | CLEAN |
| Source/RM_TerrainDig.cs (253) | hard-coded English (task 2); SAND_SHOVEL_DIAGNOSE_DIGS_UNDER_WALLS real: HasJobOnCell/JobDriver never checked an edifice | keyed; HasJobOnCell refuses + FailOn an edificed cell | CLEAN |
| Defs/ThingDefs_Sprayer/FirefoamSprayer.xml, Languages/English/Keyed/Pyrelands.xml | (edited above) | - | CLEAN |

Out of scope, noted: RM_PyrelandsMod.cs settings UI and RM_LightningBreaker.cs also hard-code English strings (project-wide, not a ship bug).

## Build / tests
- FireEcologyHook.dll rebuilt from committed source 17e90dc6ca (winbuild, stamp clean), 0 warnings.
- selftest_pyrelands_fuzz: 15602 cases OK. selftest_pyrelands_lint: 31/31. lint_pyrelands_defs: 0 ERROR, 1 WARN (intentional key). validation.py compiles; firefoam row offline read true/true; every RM_*.Translate key in Source exists in Keyed.
