---
state: proposed
needs: harvest
---

# DRAWBRIDGE_PROOF_DIAGNOSE_RESULT_WANDERS_OFF

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

drawbridge_proof ran in testq J20261027T083004Z-554c07 and J20261101T083223Z-8cf7fd (after the CPU18 mask) but its 14 driver rows read UNMEASURED 'no drawbridge_proof.py result at the current mod hash'; no stranded marker, sheet written. Either the driver died without a result or stamped another mod hash. Read both jobs' modcheck.log driver tail on SteveDesktop (/mnt/d/RimTest/testq/attempts/<job>.a1/modcheck.log) when ssh is back

## what is left

- proposed: nothing recorded as owed beyond the title; read `rimflow show DRAWBRIDGE_PROOF_DIAGNOSE_RESULT_WANDERS_OFF` history before building.

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify DRAWBRIDGE_PROOF_DIAGNOSE_RESULT_WANDERS_OFF --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=DRAWBRIDGE_PROOF_DIAGNOSE_RESULT_WANDERS_OFF` first: another commit may already do it.
