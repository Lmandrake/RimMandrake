# SUMP_FAUNA_WIRING_BUILD_1

Spec: `design/Jawa/worldbuilding/biomes/sump_bedazzle_review_2026-10-01.md` §3 and §4 row 0b. Executes the ruled roster (`sump_fauna_roster_2026-09-24.md`).

Wire the four built, unwired animals inline in `RM_TheSump`'s `<wildAnimals>` at the roster's ruled weights: `RM_Gulveth` 0.45, `RM_Thrummel` 0.35, `RM_ThrummelWarden` 0.15, `RM_ThrummelBroodmother` 0.05. Additive: the four `AA_` donor rows stay (evictions are stopped; their replacement is a later per-biome ruling). The thrummel mound (defend-radius aggression) is follow-up work; wire the castes as plain animals first. Check their art in `infrastructure/artpipe/` before treating any as owed.

## verify
- A Sump quicktest map spawns gulveth and thrummels; the four donor rows still spawn.
