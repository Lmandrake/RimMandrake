---
state: proposed
needs: offline
---

# DRAWBRIDGE_GATE_BUILD_SEE_THROUGH_DOOR

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

Drawbridge build spec 2026-11-04, part 3: option B gate frame (posts + lintel, all widths); interior transparent like a doorway, not black; winch and hinge on the friendly bank; near-side lines taut from leaf tip over the lintel to the winch, far side slack or disconnected, nothing crosses the gap; rewrite design R12 and the art contract (design/RimMandrake/flowworks_drawbridge_design_2026-10-20.md lines 168-197). Ref v3 notes D:\ClaudeWork\rimmandrake\conductor\session_2026-11-03\06_DRAWBRIDGE\mockups\v3\notes.md.

## what is left

- proposed: nothing recorded as owed beyond the title; read `rimflow show DRAWBRIDGE_GATE_BUILD_SEE_THROUGH_DOOR` history before building.

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify DRAWBRIDGE_GATE_BUILD_SEE_THROUGH_DOOR --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=DRAWBRIDGE_GATE_BUILD_SEE_THROUGH_DOOR` first: another commit may already do it.
