---
state: proposed
needs: offline
---

# DRAWBRIDGE_EDGE_FIX_RAISED_READS_AS_POLE

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

A raised drawbridge leaf on an east/west span draws the Edge view (58/256 px wide art), a thin 4-cell pole at the hinge; the raised state is readable only by the missing deck. North spans show the Face and read well. Evidence D:\ClaudeWork\rimmandrake\conductor\session_2026-11-03\06_DRAWBRIDGE\2_timber_raised.png, 4_steel_raised.png vs 5_raised_northward_timber_and_steel.png

## what is left

- proposed: nothing recorded as owed beyond the title; read `rimflow show DRAWBRIDGE_EDGE_FIX_RAISED_READS_AS_POLE` history before building.

## latest ledger notes

- 2026-11-03: Owner's verdict in game 2026-11-03: not acceptable. The raised east-west bridge is so thin he could not find it on the map.

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify DRAWBRIDGE_EDGE_FIX_RAISED_READS_AS_POLE --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=DRAWBRIDGE_EDGE_FIX_RAISED_READS_AS_POLE` first: another commit may already do it.
