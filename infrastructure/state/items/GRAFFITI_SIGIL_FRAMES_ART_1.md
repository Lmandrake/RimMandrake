# GRAFFITI_SIGIL_FRAMES_ART_1

Caused by `GRAFFITI_PUNK_IDEOLIGION_SCOPE_1` (forks ruled by question card 2026-10-09; rulings in that item and `design/RM_GRAFFITI_SCOPE_WIDENING.md` §7). Code: `src/RimMandrake/Graffiti/`.

## spec
Design §1.3-A names three tier-A frames (halo, stencil-box, drip-frame). Only `RM_Graffiti_SigilFrame_Halo` exists on disk; a render named `graffiti_sigilframe_stencilbox` exists in the artpipe state but is unbound. Search the artpipe state first (`artpipe_state.py find`), install what exists through the art ledger, generate only what is missing, then add one `RM_Graffiti_IdeoSigil_*` variant def per frame (pool-weighted beside the halo). Art register: NYC wildstyle + UK stencil (ruled); asemic only (F5).

## criteria
- O1 L0: both frame texPaths resolve on disk; validate_patch clean on the new defs
- H1 L4: the owner sees the three frames in game (folds into GRAFFITI_PUNK_ART_REVIEW_1)
