# DUNES_TINT_GATE_PROOF_1

## spec

Add RM_DunesProof.ProofTint(string) in src/RimMandrake/MovingDunes/Source returning shader=<name> hasColorProp=<B> usesVertexColor=<B> for the live dune material, so MOVING_DUNES_BUILD_1.A3 (MaterialColor vs VertexColor gate) is resolved by a state read, not a screenshot.

Filed from the 2026-10-09 acceptance-check pass (Transient/belt_acceptance_checks_20261009.md).

## verify

A state read through `jawa/static_call` on a loaded quicktest map returns the named fields; the owning acceptance criterion records the result.
