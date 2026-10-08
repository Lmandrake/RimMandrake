# Acceptance map build 2026-10-07 (FOUNDRY, offline, nothing committed)

Files (all new, uncommitted):
- `/home/mandrake/rm/foundry/infrastructure/state/acceptance_map/README.md` (schema) and 8 tables: Greentide, PyrelandsMechanics, LuminousPigment, Stillsand, FloodedCanyon, FallLineArrivals, EmpirePursuit, RustCathedral (`.json`, same dir)
- `/home/mandrake/rm/foundry/src/RimMandrake/Utils/acceptance_map.py` (tool)
- `/home/mandrake/rm/foundry/src/RimMandrake/Utils/selftest_acceptance_map.py` (52 checks, GREEN; discovered by run_selftests via selftest*.py)

Rows: 24 total. Mapped: 8 (Greentide A2/A3 + MOD_OPTIONS A3, PyrelandsMechanics A2/A3, Luminous A2, Stillsand A2, FloodedCanyon A1, FallLine A2). Unmapped with reason: 16.
Reproduction (AC A2 of the item): real PyrelandsMechanics run -> A2, A3 PASS; real Greentide run -> A2 PASS, A3 UNMEASURED until a --classified file exists (judgement is human), MOD_OPTIONS A3 UNMEASURED (its component was UNMEASURED).

Refuses to record: FAIL, UNMEASURED, absent component, UNMAPPED, criterion not outstanding, level differing from ledger, unknown item/criterion, anything without --record; classified rows without a person-written classification file.
Run: `python3 src/RimMandrake/Utils/acceptance_map.py check | list | apply <result.json> --config <tier> [--classified f.json] [--record]`
Decision for the item: location = infrastructure/state/acceptance_map/<Mod>.json (README there), tool = Utils/acceptance_map.py (not a modcheck verb; no edit to modcheck core).
