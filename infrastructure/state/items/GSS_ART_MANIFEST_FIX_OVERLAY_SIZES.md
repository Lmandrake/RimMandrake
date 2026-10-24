## spec
found-by: GPT art review, verified (BENCH, 2026-10-23/24; whole-FlowWorks+GSS art sheet at true scale, gpt_consult default model).
Report: `Transient/flowworks_takeover_20261023/GPT_ART_REVIEW.md`. Sheet: `Transient/biome_ffar/flowworks_gpt_art_review_sheet_2026-10-23.html` (untracked; snapshot in infrastructure/state/art/sheets/).
Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_art_review\raw\C.md line 7 (mast overlays); A.md 06 family (hose pieces)`. Severity: MINOR (review-tool defect). Not fixed: this item only records the defect; no art was regenerated or installed.

### defect (verified against the pictures)
gss_art_manifest.py gives the aerial mast tops and lamp-mast tops a [2,4] world size (lines 38/40) but RM_MapComponent_Aerial.cs:535 draws them width/128 x 1 cell (2x1). It gives hose Mouth and Binding 1.52 x 1.52 squares (lines 71-73) but RM_MapComponent_Hoses.cs draws Mouth edge-on as a lip (1167-1172) and Binding as len x WrapWidth (1616). Every review sheet built from the manifest shows these pieces stretched or squashed, and GPT judged them on that (two false findings this round).

### evidence
src/RimMandrake/Utils/art/gss_art_manifest.py:38,40,71-73; the code lines above.

### done when
Manifest sizes match what the code draws (or the row is marked overlay/edge-on and drawn that way); a selftest pins the four sizes.
