## spec
Pyrelands 0.1.0, class SITE, unrepaired in in-game visit 4 (game a, 2026-11-22). Check `sc_flamefang_venom` (bar
`flamefang_bite_carries_venom`). The repaired run (a0e6da8ce3: the hourly tended-vs-untended series starts once the
doctor's TendPatient job has ended; the plain-bite control is healed and undrafted; the chain's earlier fixtures are not
the wait-out's subjects) read venom_tended_vs_untended PASS, but venom_wait_out was stopped by the advance monitor
("starving: food category Starving") 420 ticks into a day: a colonist of the chain's earlier rows, drafted by
_bite_until and left so, starved [guess ~70%: the fixtures' daily top-up may skip pawns read as not subjects]. The
planted run (PYRE_PLANT_VENOM_TEND_WRONG_PATIENT=1) was voided by a blood-loss death before its comparison, so the
tend-start repair is not yet shown both ways. The subject's own course in the earlier rerun: severity 0.228, 0.577,
0.213, gone by day 3, no death (the dose fix of 11fca75b4b holds). Evidence: design/concepts/Pyrelands/version/in_game/visit_4/evidence/run_flamefang_venom_repaired.log,
design/concepts/Pyrelands/version/in_game/visit_4/evidence/run_flamefang_venom_planted_wrong_tend.log, design/concepts/Pyrelands/version/in_game/visit_4/evidence/run_flamefang_venom_healed.log.

## verify
Stage 6 (game-up). Undraft every fixture after its row (or feed the not-subject pawns at each day's top-up), then
`python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod Pyrelands --plan src/RimMandrake/Pyrelands/northstar_plan.py --no-record --chains flamefang_venom` real, and with PYRE_PLANT_VENOM_TEND_WRONG_PATIENT=1 (through WSLENV).

## criteria
- Real run: all five venom rows PASS (no starving or death stop of a bystander).
- Planted run: venom_tended_vs_untended FAIL.

## Acceptance test
`python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod Pyrelands --plan src/RimMandrake/Pyrelands/northstar_plan.py --no-record --chains flamefang_venom`: venom_wait_out PASS (red now: UNMEASURED, a starving stop); with
PYRE_PLANT_VENOM_TEND_WRONG_PATIENT=1, venom_tended_vs_untended FAIL (now UNMEASURED: a death voided it).

## refs
file: src/RimMandrake/Pyrelands/validation.py
