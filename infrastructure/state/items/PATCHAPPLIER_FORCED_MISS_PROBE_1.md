# PATCHAPPLIER_FORCED_MISS_PROBE_1

## spec

A throwaway [HarmonyPatch] class with a deliberately missing target, in the JawaBench companion, so HARMONY_PATCH_RESILIENCE_1.A2 can be proven live: Player.log must show exactly that feature switched off, census missing 1, every other mod census missing 0. Read the state with jawa/static_call type=RimMandrake.Shared.PatchApplier method=IsBroken args=<field>. Without it A2 stays UNMEASURED. Source: src/RimMandrake/_Shared/HarmonyResilience/PatchApplier.cs.

Filed from the 2026-10-09 acceptance-check pass (Transient/belt_acceptance_checks_20261009.md).

## verify

A state read through `jawa/static_call` on a loaded quicktest map returns the named fields; the owning acceptance criterion records the result.
