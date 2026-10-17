# KERNEL_SELFTEST_WIRE_SHIPPED_TUPLE_NEVER

Found by V&V pilot 1 (`design/RimMandrake/vv_methods/pilot1_shipped_matrix_2026-10-16.md` §5). A test gap, not a mod bug.

## What

A dynamic flag lint ran the whole FlowWorks SelfTest (435 cases) and recorded the RM_FlowKernel flags at every pulse.

- 34 cases pulse a kernel. **None of them ever runs the full shipped flag combination** (all nine adapter-set flags at their
  shipped values at once).
- `creepEnabled` (thick creep, shipped ON) is ON in 1 case only (THICK_LIQUID_CREEP_1 front speed), with levelBySurface off.
- `seamRotationEnabled` (shipped ON) is ON in 2 cases, both with a cap of 50, never at the shipped 6000.
- `edgeSinksEnabled` (shipped ON) is ON in 9 cases.
- The random families (`Kernel_fuzz_ledger_bounds_nomix_settles`, `Kernel_limitless_source_fills_its_component`) run at the
  C# defaults (all off) except for the flags their scenes randomise. Their scenes never contain a pump/drill input
  (`externalInput`) or a door (`sealedCell`).

The pilot's harness `src/RimMandrake/Utils/vv_shipped_matrix.py` covers the combination today: 0 failures in 10,000 + 10,000 +
1,000 scenes at SHIPPED. But it is not part of `run_selftests.py` or the nightly sweep. The selftest itself still never runs the
combination.

## NEXT

Add a SHIPPED variant of `Kernel_fuzz_ledger_bounds_nomix_settles` (all nine flags at shipped values, read from one table)
to Program.cs, or register `vv_shipped_matrix.py` in the nightly selftest sweep. Re-run the pilot's lint to show at least one case
on the full tuple.
