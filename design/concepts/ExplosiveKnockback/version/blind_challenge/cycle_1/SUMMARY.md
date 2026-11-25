# ExplosiveKnockback 0.2.0 — blind challenge, cycle 1

## Start time
2026-11-25T12:54:57Z (2026-11-25 4:54 AM PST)

## Lane 1
Written blind from the bars (tree.json, sheet.md, plan.md, record.json bar rows, VERSION.json, bars.md), the shipped
settings (RM_KnockbackMod.cs, read by regex) and the patches. `lane1/BlindLane1.cs` compiles against the shipped kernel
`RM_KnockbackMath.cs`; `lane1/run_lane1.py [--kernel <file>]` also runs Python rows on the inv_proof_scenes kernels
(proof_build_gate.py by behaviour, the settings' initializer/Scribe/Reset defaults, the scene dispatch, the release DLL,
and the proof build compiled under a private WINBUILD_ROOT).

- 100 rows [measured]: 28 PASS, 0 FAIL, 1 INFO, 71 UNSETTLED. Every UNSETTLED row is one `not_kernel` row per
  game-side bar (all 71 bars other than the two offline ones prove in game); none names an offline bar.
- inv_kernel: 23 rows (fixed, random with seeds 20261125, 7, 11, 3, 5, 9, 13, 17, and sweeps through every shipped
  slider range, every kernel switch off) PASS. inv_proof_scenes: 5 rows PASS.
- Two of my own oracles were wrong on the first run and were corrected before this record (a throw backed off a
  sandbag ends `Distance` short of its cells; the all-off lane never reached its pit). No kernel change.
- Committed before anything closed to lane 1 was opened.

## Lane 2 reruns
(not started)

## Planted
(not started)

## Faults
(not started)

## Fixes
(not started)

## Steward's decisions enacted
(not started)

## Tests edited
(not started)

## Unsettled
(not started)

## Exit
offline_bars: {inv_kernel: red, inv_proof_scenes: red}
problems_open: 0
exit_met: false

## Owed
(in progress)
