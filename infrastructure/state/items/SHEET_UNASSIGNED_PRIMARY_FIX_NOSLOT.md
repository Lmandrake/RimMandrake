# SHEET_UNASSIGNED_PRIMARY_FIX_NOSLOT

Found while vetting c3a382b9e0 (ART_SHEET_HOTKEY_GUARD_VET_UNREVIEWED), FOUNDRY 2026-10-24. Pre-existing; not
introduced by c3a382b9e0.

The c3a382b9e0 guard takes the row's primary lane as `gi == 0`. On a row whose first lane is the 'unassigned' (or
'reference') lane, there is no graphic, so `g` is null. The guard then falls back to `it.letters`, which are that
lane's letters. The right-hand option buttons and number hotkeys then record `decision = L` with no `slots{}` entry.
Enact routes such a letter by graphic_of (`_byname`): it installs only on a single-graphic row and is otherwise a
conflict. So he gets a decision that silently does nothing, or a conflict line, for a click that looked accepted.

Fix sketch: when the primary lane is not a slot, either disable the letter hotkeys and option buttons for that row,
or route them to the first real graphic lane.

Failing test sketch (jsdom harness): build a row whose lanes are `[unassigned(R), adult(A,B)]`, call
`window.setDecision(id, "R")`, and assert that it was refused (DEC[id].decision is unchanged). Today R is recorded.
