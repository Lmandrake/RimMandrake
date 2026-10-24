# SHEET_HOTKEY_PROVE_VIA_KEYDOWN

Found while vetting c3a382b9e0 (ART_SHEET_HOTKEY_GUARD_VET_UNREVIEWED), FOUNDRY 2026-10-24.

The guard lives in art_sheet.py's COMMON_JS wrapper, which reassigns `window.setDecision` at DOMContentLoaded. The
template's keydown handler (review-sheets `sheet_template.html` ~L935-945) and `bulkGroup` (~L619) call the bare name
`setDecision`. The guard only works because the template is a classic script whose top-level function is a
`window` property. I proved this with a node vm experiment: a bare call resolved to the wrapper.

The selftest (hotkey tests in art_sheet's selftests) calls `window.setDecision(...)` directly. If the template ever
becomes a module or an IIFE, or captures `setDecision` in a closure, the hotkeys bypass the guard and every test stays
green.

Failing test sketch:
1. In the jsdom/node harness, dispatch `new KeyboardEvent("keydown", {key: "2"})` with focus on a row whose primary
   slot owns only A and B, where option 2 is a young-lane letter.
2. Dispatch shift+2 (bulk) the same way.
3. Assert that DEC[row] has no slot pick of that letter.

Against a template that wraps its script in an IIFE, this test must fail.
