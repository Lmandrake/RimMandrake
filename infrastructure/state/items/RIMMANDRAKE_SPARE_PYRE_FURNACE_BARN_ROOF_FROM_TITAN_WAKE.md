## spec
Pyrelands 0.1.0, in-game visit 7, class MOD (the steward read it and agrees). The furnace-beast unroofs the barn it heats:
Huge Things rates it tier T2 (body size 9, threshold 8) and a T2 wake holes each thin roof cell the body enters. Measured
both ways (`visit_7/rows.jsonl`, `visit_7/evidence/script_roof_probe.log`): wake roof holing off PASS (+24.8 C, 0 open roof
cells), on FAIL twice (+0.3 C, 25 of 25 open), no beast: roofs stay. The bar `furnacebeast_warms` says a closed room that
holds a furnace-beast grows clearly hotter; its description promises that it heats a barn for weeks.

Lowest stage that shows the fault: offline (the cause is measured and is in the defs and one Huge Things call), so needs is
`offline`; the live read is Stage 6's.

Route (delegated call under Evidence-for-Ask, the steward's; take another only with evidence): a per-def roof exemption
(`sparesRoofs` on `RM_TitanicExtension`, read where the wake holes roofs; true on RM_FurnaceBeast). Why not the whole opt-out
(`forceEnabled` false): it takes the beast out of the titan pool, and RIMMANDRAKE_READ_PYRE_LONG_RUN_FOUR_OWED_ZHAKKA_FIRST
part 3 (owner, 2026-10-21: "Every biome should have something like this.") counts this beast as the Pyrelands' T2 giant.
Every other titan keeps his card #1 (thin roofs are destroyed as a titan passes). The default of the new field is false, so
no other race changes.

## verify
Offline: the acceptance command below; Huge Things' own selftest (`Source/SelfTest`, TitanicFuzz `HolesRoof`) gains the
exempt case, red on the parent. Build the Huge Things DLL with its `.srchash`.
Stage 6, record UNRUN with `maturation.py unrun` at the close: test table id `P_furnace_room`, command
`python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod Pyrelands --plan src/RimMandrake/Pyrelands/northstar_plan.py --no-record --chains furnace_room`
on the pyrelands tier with Huge Things at its defaults.

## criteria
- `accept_furnace_beast_spares_roof.py` exits 0 (FAIL on the base; the steward saw it FAIL on 4 planted states, PASS on a
  built exemption and on an opt-out, UNMEASURED on a missing file).
- P_furnace_room reads PASS live with Huge Things at its defaults.

## launch-checks
must-fail: python3 design/concepts/Pyrelands/version/evidence/accept_furnace_beast_spares_roof.py

## refs
file: src/RimMandrake/Pyrelands/Defs/ThingDefs_Races/RM_PyrelandsFauna.xml
file: src/RimMandrake/HugeThings/Source/Titanic/Tiering/RM_TitanicExtension.cs
file: src/RimMandrake/HugeThings/Source/Titanic/Wake/TitanicWakeProcessor.cs
file: src/RimMandrake/HugeThings/Source/Kernel/RM_TitanicKernel.cs
