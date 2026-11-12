---
state: proposed
needs: offline
---

# HOSE_OVERDRAW_FIX_PATCH_FORGOT_REPAINT

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

RM_MapComponent_Hoses.DrawOverBuildings (~line 1724) re-derives a hose's over-building draw only when mapVersion changes; since buildings/trees are patched (HoseWorldPatch) instead of bumping the version, a building placed or removed under a hose that does not reroute leaves that draw stale (pre-existing since HOSE_TICK_REBUILD_ZERO_ALLOC; the old 16k overflow bump refreshed it by accident, gone with HOSE_DIRTY_LIST_WIDEN_NO_OVERFLOW_REBUILD)

## what is left

- proposed: nothing recorded as owed beyond the title; read `rimflow show HOSE_OVERDRAW_FIX_PATCH_FORGOT_REPAINT` history before building.

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify HOSE_OVERDRAW_FIX_PATCH_FORGOT_REPAINT --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=HOSE_OVERDRAW_FIX_PATCH_FORGOT_REPAINT` first: another commit may already do it.
