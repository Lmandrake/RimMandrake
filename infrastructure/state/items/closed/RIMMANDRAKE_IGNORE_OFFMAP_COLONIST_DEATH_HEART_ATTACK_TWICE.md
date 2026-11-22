# RIMMANDRAKE_IGNORE_OFFMAP_COLONIST_DEATH_HEART_ATTACK_TWICE

## spec

Class HARNESS (the vitals latch's criterion, not the mod). In Pyrelands in-game visit 3 (game b, site
`NS_Pyrelands_site_1_417df172fdb5_visit3`), `jawa/safe_advance` stopped `fresh_burn_bonus` (`sc_burn_compounds`) and
`scorchfruit_spoils` (`P_scorchfruit_spoils`) on a `death` trigger: Randall (id 760, map -1), a player-faction colonist
off every map, died of a heart attack. He was a world pawn of the quicktest colony that `retire_offsite_colonies`
abandons. `JawaBenchVitalsCore.Matters` counted any colonist wherever it was, so the death read `damage` and stopped
the advance. Both rows were rerun and passed, so no bar went undecided; the fix is owed because the fault voided two
runs and reaches every site test on a world with an abandoned colony.

Fix: a Kill prefix (`KillPrefix`, `JawaBenchSituationalTools.cs`) records whether the pawn was off every map as Kill
began (not spawned or held on a map, in no caravan, transporter or other world object). Kill clears the caravan
before the postfix, so the postfix cannot read it. `PawnObs.OffMap` carries it; `Matters` excludes an off-map colonist
unless it is a declared actor; `DeathSeverity` reads `info` for it, so it stops no advance. A caravan colonist's death
still reads `damage` (conservative: a journey from the test colony still counts).

## verify

Offline: `python3 src/RimMandrake/Utils/selftest_map_awareness_core.py` (cases `vitals_offmap_*`,
`vitals_spawned_colonist_death_is_damage`, `vitals_caravan_colonist_death_is_damage`,
`vitals_site_colonist_death_still_stops`, `vitals_noncolonist_death_is_info`). Red on the parent's rule planted
(188/193, five FAIL, the off-map death reads `damage`); green on the fix (193/193). Hook audit:
`python3 src/RimMandrake/bridgetools/selftest_bridge_hooks.py` PASS, 13/13 mutants.

Live (Stage 6, UNRUN): deploy the companion with `python3 src/RimMandrake/bridgetools/build.py --apply` while the
game is down, then rerun the two rows; no stop on a world pawn.

## criteria

An off-map world-pawn colonist's death latches `info` and stops no governed advance; a spawned colonist's death still
latches `damage` and still stops it.

## refs

file: src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchVitalsCore.cs
file: src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchVitals.cs
file: src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchSituationalTools.cs
file: src/RimMandrake/bridgetools/AwarenessSelfTest/UnitsVitals.cs
tier: pyrelands
