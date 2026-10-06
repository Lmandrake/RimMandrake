# LANTERNDEEPS_SHEET_ART_REDO_1 — the owner's Lantern Deeps art sheet: collect and install the repaints and variants

Source: `Transient/biome_ffar/lanterndeeps_sheet_2026-10-05.decisions.json` (ingested; notes verbatim there).
Progress record: `Transient/biome_ffar/lanterndeeps_close_progress_2026-10-05.md`. Jobs filed:
`Transient/biome_ffar/lanterndeeps_redo_jobs_2026-10-05.json` (36 artpipe jobs, owner_note verbatim on each).

## spec

Install each render once it lands and passes, through `art.py install` only:
- Eye repaints, edits of the live picture per facing (`deeps_<x>_eyes_v1_<facing>`): RM_BloodropMoth, RM_FacetMothLarvae,
  RM_Megapleura, RM_MossBeetleLarvae ("remove eyes"), RM_Gembug Blue ("pale blue gems"). Install over the same
  `RM_LanternDeeps/Fauna/BMT_Caverns/...` files. RM_Gembug also draws Green/Red/Yellow colour sets the sheet never showed;
  they still carry the old eyes. Derive them from the accepted Blue once it lands.
- RM_Blinker (`deeps_blinker_v2_*`): three arms radiating out, legless and clumsy. East is an edit of `RM_Blinker_east`;
  north and south derive from the new east.
- Plant variants (`deeps_<plant>_var{b,c}_v1`): BrellikBulb, DeepMycelium (from his E), KuvraSpout, NurrikGill,
  PrennaLace (grown), QuorrFern, TwitchingPuffer (grown), VellokReed, ZivvitTaper. Each plant is already a Graphic_Random
  folder. Add the new pictures under the next free letter and never overwrite a picture he kept.
- Run `placeholder_detect.py file` on every picture before installing it.

Already installed at the sitting: Mycelium/A.png = his E; ThrakkCap/C.png = his B (variant of A);
LanternstoneMedium/A.png = his C (variant of A). LanternstoneMedium is shared with the natural RM_LanternstoneFormations
medium crystal, so that crystal also draws the new variant.

## verify

`art.py status <texPath>` shows each new picture LIVE with a ruling or artpipe-collect reason; the eye-repaint creatures
draw without eyes (Gembug: blue gem eyes) on a quicktest spawn.
