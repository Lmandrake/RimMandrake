# GAMEENV_FIX_PROOFSITE_54339AD0_ITEMS_WAIT

## proof (corrected 2026-11-17, drain of the retired judge)
    "$RM_CV_PYTHON" src/RimMandrake/FlowWorks/northstar/proof_hose.py --offline-gate

The hose offline gate imports numpy through `validation_hose_offline.py` and `design_spec.py`, so it needs the
CV interpreter; under a bare system python3 two of its steps go red on `ModuleNotFoundError: numpy`, which is
an interpreter artifact and not a defect. Note also that `validation_hose_offline.py` lives in
`src/RimMandrake/FlowWorks/`, not `.../northstar/` — proof_hose's `MOD` is the parent directory.

## what it reads, measured 2026-11-17
Five of the six gate steps green. The sixth, `csharp_selftest`, prints its own verdict: dotnet.exe not found,
UNMEASURED, not a pass or a fail. That leg needs the Windows toolchain under C:\, so it cannot be read on a
Mac clone. Work landed at 15131f4577 (HoseSelfTest.cs re-pin, prove_terrain_overlays_cleared.py).
Evidence: /Users/mandrake/ClaudeWork/scratch/rm-drain-logs/proofs/GAMEENV_FIX_PROOFSITE_54339AD0_ITEMS_WAIT.txt

Next worker: run the line above on the Windows bench and read `csharp_selftest`; close only when all six are
green, since one UNMEASURED leg is not a pass.
