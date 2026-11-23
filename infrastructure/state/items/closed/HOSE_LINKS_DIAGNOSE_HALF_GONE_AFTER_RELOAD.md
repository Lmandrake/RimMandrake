---
state: proposed
needs: offline
---

# HOSE_LINKS_DIAGNOSE_HALF_GONE_AFTER_RELOAD

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

BENCH_r17_midrain holds 100 hose rigs but RM_Levelling reads at most links=50 after a load (13-15 on the first cycle, 7 on the FlowWorks list), while the fresh scene of round5 read links=100. Cause unknown: lazy re-lay, working pumps or the mid-rain state could each explain it, and a real save/load loss of levelling links is not ruled out. Evidence D:\ClaudeWork\rimmandrake\levelling_spike\run\*_pt.txt.

## what is left

- proposed: nothing recorded as owed beyond the title; read `rimflow show HOSE_LINKS_DIAGNOSE_HALF_GONE_AFTER_RELOAD` history before building.

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify HOSE_LINKS_DIAGNOSE_HALF_GONE_AFTER_RELOAD --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=HOSE_LINKS_DIAGNOSE_HALF_GONE_AFTER_RELOAD` first: another commit may already do it.
