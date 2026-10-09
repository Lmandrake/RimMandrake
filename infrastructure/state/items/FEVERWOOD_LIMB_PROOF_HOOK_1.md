# FEVERWOOD_LIMB_PROOF_HOOK_1

## spec

Add a static RM_FeverWoodProof.ProofLimbs(string) in src/RimMandrake/FeverWood/Source returning limbs=<N> cap=<N> pressure=<N> chorusSilenced=<B> from RM_MapComponent_TentacleWatch (encounterPressure, CountLimbs, ChorusSilenced are private or unreachable; jawa/comp_read reads ThingComps only). Unblocks FEVERWOOD_LIMB_LINGER_CAP_1.A1 (pool cooldown), A2 and A3.

Filed from the 2026-10-09 acceptance-check pass (Transient/belt_acceptance_checks_20261009.md).

## verify

A state read through `jawa/static_call` on a loaded quicktest map returns the named fields; the owning acceptance criterion records the result.
