# SHEET_FROZEN_WRAPPER_SILENCE_STAMP

Found while vetting c3a382b9e0 (ART_SHEET_HOTKEY_GUARD_VET_UNREVIEWED), FOUNDRY 2026-10-24. Low impact.

art_sheet.py's `window.setDecision` wrapper (~L677-703) calls the template's original, then unconditionally:
- stamps `decidedAt`,
- rewrites `slots{}`,
- calls `queue(id)`.

It does this even when the original returned early without changing anything, as on a frozen sheet (the template
refuses edits when `FROZEN`). The sidecar refuses frozen writes with 423, so nothing reaches disk. But the in-page
DEC record is mutated, and the page shows a pick that was never accepted until reload.

Fix sketch: compare DEC[id] before and after `orig(...)`, and do the post-work only if the template changed it.

Failing test sketch (jsdom harness): set `FROZEN = true`, call `window.setDecision(id, "B")`, and assert that
`DEC[id]` deep-equals its prior value. Today slots/decidedAt change.
