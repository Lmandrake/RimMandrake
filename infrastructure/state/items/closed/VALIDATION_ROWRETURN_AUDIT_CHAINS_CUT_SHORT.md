# VALIDATION_ROWRETURN_AUDIT_CHAINS_CUT_SHORT

## proof (corrected 2026-11-17, drain of the retired judge)
    python3 src/RimMandrake/Utils/modcheck/prove_required_checks_current.py

## what it reads, measured 2026-11-17 — rc=1, a REAL failure
    STALE: committed ed77a9e0e573728c, current (root-normalised) 77d5a89ffae6a899; 9 mod(s) differ

This is not an environment gap and not a parser refusal: the committed required-checks digest no longer
matches what the tree computes, for nine mods. The proof is correct as written and the thing it measures is
genuinely out of date. Evidence:
/Users/mandrake/ClaudeWork/scratch/rm-drain-logs/proofs/VALIDATION_ROWRETURN_AUDIT_CHAINS_CUT_SHORT.txt

Next worker: find out WHY the nine differ before regenerating anything. A digest that drifted is evidence
about a change somebody made to the required checks or to the mod set; re-committing the new digest to make
the proof green would erase that evidence. Identify the nine mods and the change that moved them, then either
accept the drift with a reason or repair the checks.
