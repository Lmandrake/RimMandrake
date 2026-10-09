# ELDER_TREASURE_PROOF_HOOK_1

## spec

Add public static string ProofTreasures(string) to src/RimMandrake/DivingInteraction/Source/RM_ElderTradeUtility.cs returning the sorted names from RmUniqueTreasureDefNames, so ELDER_TREASURE_TAG_TABLE_1.A1 is readable through jawa/static_call. No current tool reads the private table.

Filed from the 2026-10-09 acceptance-check pass (Transient/belt_acceptance_checks_20261009.md).

## verify

A state read through `jawa/static_call` on a loaded quicktest map returns the named fields; the owning acceptance criterion records the result.
