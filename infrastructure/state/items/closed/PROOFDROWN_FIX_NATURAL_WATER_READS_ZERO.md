# PROOFDROWN_FIX_NATURAL_WATER_READS_ZERO

## proof (corrected 2026-11-17, drain of the retired judge)
The offline half:

    python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/Utils/selftest_proofdrown_natural_reader.py

Measured 2026-11-17: rc=0, RESULT: GREEN.
Evidence: /Users/mandrake/ClaudeWork/scratch/rm-drain-logs/proofs/PROOFDROWN_FIX_NATURAL_WATER_READS_ZERO.txt

## why this is ready, not done — the item's own acceptance is live
`infrastructure/state/live_proofs/PROOFDROWN_FIX_NATURAL_WATER_READS_ZERO.criteria` is a single L2 clause:
  A1 L2 — on a quicktest map, RM_PitFillEffects.ProofDrown on a standing Jawa mid-pool in natural
          RM_WaterBrineShallow at 120,120 reads water > 0.45 m (the same water RM_Swim.ProofSwim reads, not
          0.00) with under=True (jawa_shallows_proof JS3), and JS1-JS4 all PASS
The green reader selftest proves the reader's arithmetic on synthetic input. The defect this item names is
that the reader returns 0.00 against the game's NATURAL water, which only a loaded map can produce.

Next worker: run jawa_shallows_proof JS1-JS4 on a quicktest map with the game up.
