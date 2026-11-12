---
state: proposed
needs: bridge
---

# HOSE_REROUTE_FIX_WALL_IGNORED_ENTIRELY

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

FlowWorks hose M2: walling the maze gap leaves the laid hose through the wall (pathLen 11.54 unchanged, 4 unwalkable points, 0 relays)

## what is left

- proposed: nothing recorded as owed beyond the title; read `rimflow show HOSE_REROUTE_FIX_WALL_IGNORED_ENTIRELY` history before building.

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify HOSE_REROUTE_FIX_WALL_IGNORED_ENTIRELY --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=HOSE_REROUTE_FIX_WALL_IGNORED_ENTIRELY` first: another commit may already do it.
