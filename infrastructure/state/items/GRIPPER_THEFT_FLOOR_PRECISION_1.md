# GRIPPER_THEFT_FLOOR_PRECISION_1 — Wasteland gripper steals one unit fewer after kernel extraction

Found by the kernel extraction audit, `Transient/kernel_audit_20261008.md` (2026-10-08).

## spec
Commit `44de46280`. Old `src/RimMandrake/Wasteland/Source/RM_GripperTheft.cs:248`:
`Mathf.FloorToInt(props.maxCarryMass / unitMass)` — float division. New
`src/RimMandrake/Wasteland/Source/Kernel/RM_DoseKernel.cs:36`: `Math.Floor((double)maxCarryMass / unitMass)`.
Widening a float mass such as 0.6f to double gives 0.6000000238…, so the quotient lands just below
the whole number and floors one lower. Measured: float 3/0.6 → 5, double → 4. Shipped gripper
`maxCarryMass` 3 (`RM_Gripper.xml:88`): mass 0.6 goes 5→4, 0.3 10→9, 0.1 30→29.

The double floor was added for the builder's overflow fix (quotient > 2^31); keep that clamp but
compute the quotient in float (as before), then clamp before the int cast.

## verify
Kernel fuzz/unit case: UnitsTaken(maxCarryMass 3, unitMass 0.6f) == 5.

## criteria
Byte-for-byte equal to the pre-extraction count for all in-range inputs; overflow clamp retained.
