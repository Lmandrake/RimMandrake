---
state: proposed
needs: offline
---

# DRAWBRIDGE_BUTTON_FIX_CLICK_SEEMS_DEAD

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

Clicking the raise/lower button appeared to do nothing for the owner in game 2026-11-03. Code reads as an order waiting for a colonist at the winch (RM_DrawbridgeMath OrderRaise/OrderLower); not yet confirmed live. At minimum the player gets no visible feedback.

## what is left

- proposed: nothing recorded as owed beyond the title; read `rimflow show DRAWBRIDGE_BUTTON_FIX_CLICK_SEEMS_DEAD` history before building.

## latest ledger notes

- 2026-11-03: TESTPILOT_SAT: 16eff7aa52 read only. VERDICT MEASURED: order was taken; working as designed with almost no feedback; the design is the defect. Leaf 5 (timber, winch 95844 at 133,62): pendingOrder Lower, progress 960, inspect 'Waiting for a colonist to lower (winch bank only) it'. Nelvaanian holds job RM_WorkDrawbridge on it from (98,90), about 50 cells away; workgiver_probe confirms canReserve and hasJobOnThing for him, and the other four probed pawns fail only on reservation. Game paused at 348

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify DRAWBRIDGE_BUTTON_FIX_CLICK_SEEMS_DEAD --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=DRAWBRIDGE_BUTTON_FIX_CLICK_SEEMS_DEAD` first: another commit may already do it.
