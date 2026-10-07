# GIZKA_STOWAWAY_UNMEASURED_ROWS_1 - GizkaStowaway unmeasured rows

Filed 2026-10-07 from the GREEN-MIN / L2 sweeps (Transient/*_20261007.md).

## spec
GizkaStowaway modcheck status is RED because 10 rows read UNMEASURED (27 PASS / 0 FAIL / 10 UNMEASURED, Transient/modcheck/GizkaStowaway_20261007T191543Z.json). For each: either add the capability (bridge tool / fixture) so it measures, or reword the bar if it is unmeasurable by design, or classify it in the script as a documented gap. Parent: GIZKA_STOWAWAY_FIRST_SCRIPT_1 (owes A1/A3 GREEN-MIN).

## verify
python.exe northstar_driver run for GizkaStowaway; modcheck status.

## criteria
A1: a table of the 10 rows with cause and chosen resolution is on the item.
A2: modcheck status GizkaStowaway reads GREEN with current hash, or each remaining UNMEASURED is an explicit by-design row accepted by the status rule.

## live check
New mechanism never seen: the 10 UNMEASURED GizkaStowaway behaviours have never been observed running.

NEXT: claim this item and start with criterion A1.
