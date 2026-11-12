---
state: validated
needs: bridge
---

# TAR_COOLING_GLASS_MEND_ENGINE_CELLS

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

FlowWorks P6b (GPT G3.5): tar cooling writes glass onto cells the depth engine owns (Flood_FlowWorks.cs ~377-390) (filed from the hose port, design/RimMandrake/hose_port_to_flowworks_design_FINAL_2026-10-10.md section 5; not fixed in the port)

Built at `ae21b56dbb89` (origin/main); code is in, what is owed is below.

## what is left

- A2

## latest ledger notes

- 2026-10-11: Call-site coverage added at 12c563a31: selftest_flowworks_call_sites.py asserts this fix's production call sites (scoped per method, old rule absent, caller chain, Compile list); every assertion proven red on a temp copy with the call deleted. Notes: Transient/pickAL_20261011.md.
- 2026-10-11: Correction: the call-site coverage commit on origin/main is 7e60caa7c (12c563a31 was its pre-rebase sha and is not on main).

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify TAR_COOLING_GLASS_MEND_ENGINE_CELLS --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=TAR_COOLING_GLASS_MEND_ENGINE_CELLS` first: another commit may already do it.
