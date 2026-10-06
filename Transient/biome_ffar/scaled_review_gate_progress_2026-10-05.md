# Scaled review gate - progress 2026-10-05
Gate: `src/RimMandrake/Utils/art/scaled_review_gate.py` (+ `gate_browser.py`, `serve_gated.py`); hook `.claude/hooks/block_hand_edited_sheet.py`; ingest `--redo-jobs`.
First measurement (before any fix): 0/27 pass. Req 5 (row without canon does not say so) failed on every sheet = a tool defect, fixed in art_sheet (canonTag fallback), not by weakening.
Genuine remaining failures (tool kept the last good sheet): req 3 donor-only rows with no pending/active job (desert, floodedcanyon, leaningscrub, miasma, theforge, therot); req 4 donor column missing (cauldron, desert, leaningscrub, therot, wasteland); req 2 leaningscrub RM_VenomvineThicket (picked set purged).
Blank-sheet incident: rows with no drawSize (FALLBACK size: Long Shade RM_Chorn, RM_Dunejelly, RM_Oreclaw, RM_Skiralim; Stillsand RM_LikkaLikka, RM_UltrissPad - no ThingDef in the live dump) threw in scaleBlock and blanked the page. Fixed in the template; req 13 (real browser) added.
Latest `all` run: 19/27 pass (desert's req 13 was an Edge timeout flake; it renders 834 imgs).
