## spec
Pyrelands 0.1.0, MOD fault from in-game visit 3 (game b, 2026-11-21). Bar `flamefang_bite_carries_venom`: venom
smoulders worse over the hours "until treated or thrown off". Measured: one untended bite read `RM_FlamefangVenom`
0.434, then 0.784 a day later, and the colonist died by day 2, before immunity completes (def: `severityPerDayNotImmune`
+0.35, `immunityPerDaySick` 0.5, `lethalSeverity` 1). So a healthy colonist cannot throw off one bite: the bar fails.
The offline model (`selftest_pyrelands_venom_staging.py`) assumes a flat 0.2 a bite and never sees it; why the live
dose is ~0.43 (bite damage x `severityPerDamageDealt` 0.02) is part of the fix.
Which number moves (the dose a bite, the rise, or the immunity rate) is the Designer's tuning call; see the open
Designer question `RIMMANDRAKE_WEIGH_PYRE_TWO_FLAMEFANG_BITES_KILL_UNTENDED`. The card for him after his walk
(`RIMMANDRAKE_CARD_FLAMEFANG_ONE_BITE_KILLS_UNTENDED_HIS_DANGER_CALL`) does not hold this fix: the bar's own words
decide it (steward, delegated: evidence-for-ask, 2026-11-21).
Evidence: `design/concepts/Pyrelands/version/in_game/visit_3/SUMMARY.md`, `design/concepts/Pyrelands/version/in_game/visit_3/evidence/run_flamefang_venom_repaired4.log`.

## verify
Offline first (the fault is a pure function of the def numbers and the bite's dose). Then the in-game check
`sc_flamefang_venom`: `python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod Pyrelands --plan src/RimMandrake/Pyrelands/northstar_plan.py --no-record --chains flamefang_venom` (venom_wait_out). Close on the offline test and record the in-game
check UNRUN for Stage 6 with `maturation.py unrun`.

## criteria
- The venom staging model takes its dose from the defs (`severityPerDamageDealt` x the bite's damage), not a flat 0.2.
- With that dose, one untended bite on a healthy colonist peaks below `lethalSeverity` before immunity completes.
- The venom still rises hourly when untended (the bar's "smouldering worse").

## Acceptance test
Offline: `python3 src/RimMandrake/Pyrelands/selftest_pyrelands_venom_staging.py` with the def-derived dose: red on
the current defs (0.434 + 0.35 x 2 = 1.13 > 1), green on the fix. Write that assertion first and see it red.
Live: `python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod Pyrelands --plan src/RimMandrake/Pyrelands/northstar_plan.py --no-record --chains flamefang_venom`: venom_wait_out PASS (the subject lives and the hediff goes); red now (died day 2).
