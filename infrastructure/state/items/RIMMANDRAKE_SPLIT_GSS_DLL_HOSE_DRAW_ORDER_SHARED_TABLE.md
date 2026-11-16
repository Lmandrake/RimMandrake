# RIMMANDRAKE_SPLIT_GSS_DLL_HOSE_DRAW_ORDER_SHARED_TABLE

## spec

Polish, found by the GimmeSomeSlack blind cycle 5 judge (lane-1 row NH_SHIPPED_DLL_NO_HOSE_SYMBOL, 2026-11-16): the shipped
`src/RimMandrake/GimmeSomeSlack/Assemblies/RimMandrakeGimmeSomeSlack.dll` holds `HoseBaseLift`, `HoseFittingLift`,
`HoseQueue`, `HoseTopAltitude` and `LayerHose`, compiled in from `src/RimMandrake/_Shared/SlackGeometry/DrawOrder.cs` (the
hose's altitude band; no GSS code calls them, by grep). A reader of the shipped DLL finds hose names in a mod that "draws
power cords only". Not a Problem: they are altitudes, not things, and T_NO_HOSE allows exactly these names. Smallest fix:
move the hose members of DrawOrder into a hose-only shared file FlowWorks compiles and GSS does not (FlowWorks reads
`DrawOrder.LayerHose`, `HoseQueue`, `HoseTopAltitude`), then drop them from T_NO_HOSE's ALLOWED_NAMES.

## verify

Acceptance test: after the move, remove the five names from `ALLOWED_NAMES` in
`src/RimMandrake/GimmeSomeSlack/northstar/selftest_gss_no_hose.py`, rebuild GSS (`python3 src/RimMandrake/Utils/winbuild.py
GimmeSomeSlack`) and FlowWorks: the no-hose test exits 0 (today, with the names removed, T1 reads red on the 5 assembly
names: watched in blind cycle 5's lane-1 row), and FlowWorks' C# suite stays green.
