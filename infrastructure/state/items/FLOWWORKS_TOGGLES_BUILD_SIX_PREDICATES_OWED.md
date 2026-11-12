---
state: proposed
needs: offline
---

# FLOWWORKS_TOGGLES_BUILD_SIX_PREDICATES_OWED

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

FlowWorks: six toggle chains have never measured a row since they were written: fall_damage, liquid_corrosion, liquid_drilling, liquid_ignition, superdeep_shooting, typed_shores read 'owed, no predicate yet' (extensions.py _owed; validation.py EXTENSION_TOGGLES_OWED). Write each predicate (stage + read) or retire the chain with its switch named in TOGGLES_NOT_ON_FLOOR

## what is left

- proposed: nothing recorded as owed beyond the title; read `rimflow show FLOWWORKS_TOGGLES_BUILD_SIX_PREDICATES_OWED` history before building.

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify FLOWWORKS_TOGGLES_BUILD_SIX_PREDICATES_OWED --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=FLOWWORKS_TOGGLES_BUILD_SIX_PREDICATES_OWED` first: another commit may already do it.
