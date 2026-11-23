---
state: validated
needs: bridge
---

# FLUID_PALETTE_EXHAUSTION_MEND_KEY_ZERO

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

FlowWorks P7 (GPT G3.6): an exhausted fluid palette returns key 0, so a cell's fluid identity silently changes (RM_MapComponent_Excavation.cs ~303-319) (filed from the hose port, design/RimMandrake/hose_port_to_flowworks_design_FINAL_2026-10-10.md section 5; not fixed in the port)

Built at `e393177fdb0f` (origin/main); code is in, what is owed is below.

## what is left

- A2

## latest ledger notes

- 2026-10-11: Call-site coverage added at 12c563a31: selftest_flowworks_call_sites.py asserts this fix's production call sites (scoped per method, old rule absent, caller chain, Compile list); every assertion proven red on a temp copy with the call deleted. Notes: Transient/pickAL_20261011.md.
- 2026-10-11: Correction: the call-site coverage commit on origin/main is 7e60caa7c (12c563a31 was its pre-rebase sha and is not on main).

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify FLUID_PALETTE_EXHAUSTION_MEND_KEY_ZERO --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=FLUID_PALETTE_EXHAUSTION_MEND_KEY_ZERO` first: another commit may already do it.
