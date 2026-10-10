# Weeping Stones fix progress — 2026-10-10

## Part 1 — enact.py root fixes — DONE

`src/RimMandrake/Utils/art/enact.py`, proven by `src/RimMandrake/Utils/art/selftest_enact_ws.py`
(28 checks; 20 of them FAIL on the pre-fix enact.py, every class represented; art selftests 19/19 GREEN).

1. Pick on donor art no longer counts as "already live" (old ~L582): only a pick of the **donor original** column
   itself does. A render pick goes to OUR path — a Graphic_Random folder of ours (`<base>_<letter>.png`), or
   `<category>/<row>/<row>` in the def's mod with the row's own def texPath moved there (placeholder `<color>` tint
   dropped; other defs on the same vanilla path untouched). A folder this run fills sheds unkept pictures (retired, archived).
2. Ticked variants (explicit, not `variantsDefault`) ship: folder files, or `<res>V_<L>` + `alternateGraphics` (GorgV_G convention).
3. A note asking for rename/description is NOT followed by an art job alone: TODO until `--mark-done`; also re-raised
   for notes an earlier run already moved to notes_followed; `--mark-done` records that def half.
4. Redraw reference: "based on (x)" -> column x; "drop/remove ... art", "redo completely", "total regen", or a ✕ -> none.
5. Catch rows (`RM_XCatch`) wait for `RM_X` to be settled (picked letter, or a live render of its redraw); catch jobs drawn
   earlier are withdrawn to `_withdrawn/` (active ones listed); once settled the catch is filed with RM_X's picture as reference.

code_review_status: enact.py and the new selftest are DIRTY by default (no review run) — nothing extra is required to commit.

## Part 2 — Weeping Stones rows
(pending)

## Scope invented by earlier agents (owner decides; NOT reverted)
(pending)

## Deploys
(pending)

## Re-verification
(pending)

## Commits
(pending)
