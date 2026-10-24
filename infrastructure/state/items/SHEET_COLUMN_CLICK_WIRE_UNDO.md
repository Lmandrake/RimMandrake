# SHEET_COLUMN_CLICK_WIRE_UNDO

Found while vetting c3a382b9e0 (ART_SHEET_HOTKEY_GUARD_VET_UNREVIEWED), FOUNDRY 2026-10-24.

Column clicks on an art sheet go through `artAct` → `SLX.pick`/`SLX.accept`/... (art_sheet.py ~L1621-1824,
~L2110-2140). They rewrite DEC[row] but push NO entry on the template's undo stack. The template's undo
(`applyEntries`, ~L596-618) restores a whole deep-copied record.

Sequence:
1. Press hotkey B on a row. This records undo entry U, holding the record from before B.
2. Click column C in the same row's lane. The slot pick becomes C, and no undo entry is pushed.
3. Press `u`. U restores the record from before B, so the C click is lost as well.

The loss is visible on the row, so this is moderate, not silent. Still, one undo drops two of his actions.

Fix sketch: every SLX mutation pushes `{id, before: deepcopy(DEC[id])}` the same way the template's
setDecision does.

Failing test sketch (jsdom harness): `window.setDecision(id,"B")`, then `artAct(pick C)`, then `undo()`. Assert that
DEC[id] equals the record after B. Today it equals the record from before B.
