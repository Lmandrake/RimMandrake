---
state: built
needs: bridge
---

# HOSE_SELFTESTS_FIX_MISPLACED_DOC_NAMES

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

FlowWorks SelfTest cosmetics from review 2026-10-26: HoseCarryChecks.cs ~233 Row6Legacy's <summary> now sits above CarryBranchDropsStrand (two summaries on one member, Row6Legacy undocumented); HoseReviewChecks.cs NozzleCouplerOnTop names a Rot=2 south-facing reel 'west'. No behaviour change; files marked CLEAN

Built at `e4544cc001ab` (origin/main); code is in, what is owed is below.

## what is left

- A1

## latest ledger notes

- 2026-10-26: skipped by FlowWorks C# fix batch 2: hose files (Source/Hose/*, _Shared/SlackGeometry/*) were owned by the hose-memory helper at the time; still open
- 2026-11-01: Fixed in local commit 069abc50e5 (Row6Legacy summary moved back onto it; Rot=2 reel var west->south; winbuild FlowWorks 0 errors, DLL committed). NOT published: origin/main carries 7 Utils files, lane rules forbid pulling them into the live arena tree. Owed: publish then implemented; L1: in-game FlowWorks selftest still passes the hose carry row6 and NozzleCouplerOnTop rows (comment/rename only).

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify HOSE_SELFTESTS_FIX_MISPLACED_DOC_NAMES --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=HOSE_SELFTESTS_FIX_MISPLACED_DOC_NAMES` first: another commit may already do it.
