# RIMMANDRAKE_SHARPEN_FLOWWORKS_VOLUME_LAW_ONE_DECILITRE_SLIPS_BY

## spec
Found proving `RIMMANDRAKE_REVIVE_SHIPPED_FUZZ_WITH_LAWS` (2026-11-18). FlowWorks keeps water in decilitres ("the one water number", RM_FlowKernel.water), but
the fuzz's volume law (`volume_in_equals_out_plus_stored`, FlowKernelFuzz.cs "total volume") did not see one decilitre
appearing from nowhere: the probe planted it 1,156 times over 300 scenes and kernel_fuzz stayed green, 0/300; a whole
level (U decilitres) went red, 141/300 [measured: `D:\ClaudeWork\rimmandrake\evidence\vv_laws_first_slice\prove_conservation.json` and the two runs in its log].
So a sub-level leak would pass the law. Likely cause [guess ~70%]: `ArrayWorld.Totals()` sums `WaterLevels(i)`
(levels), not decilitres, and the 1e-3 tolerance is in levels; or the kernel re-rounds a cell to whole levels each pulse
(then nothing is lost and the law is right). Measure which first.

## criteria
- Acceptance test: with ShippedMatrixProbe's volume plant at ONE decilitre (`k.water[i] += 1`), `vv_laws.py prove
  FlowWorks --family conservation` is PROVEN; NOT_PROVEN on the base (watched 2026-11-18). If the kernel provably rounds
  the decilitre away, say so in the law's sentence instead and close with that evidence.

## verify
- The prove run above, its baseline green.

## refs
file: src/RimMandrake/FlowWorks/Source/SelfTest/FlowKernelFuzz.cs
file: src/RimMandrake/FlowWorks/Source/SelfTest/VV/ShippedMatrixProbe.cs
