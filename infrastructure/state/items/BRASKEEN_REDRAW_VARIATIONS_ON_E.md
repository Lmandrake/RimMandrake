# BRASKEEN_REDRAW_VARIATIONS_ON_E — variations of the asymmetric variant E

Owner, 2026-10-16, on `phase0_remaining_art_sheet_2026-10-16` (verbatim): *"Add variations based on E. The others
are too symmetric and should be removed."*

## state

- **E** (`0b0264cb3dd0…`, artpipe `b07_braskeenA`) is live and is the only PNG in
  `src/RimMandrake/Miasma/Textures/Things/Plant/RM_Braskeen/`.
- **Purged** on his words: C `b75e7088…` and D `268aace1…` (his miasma_sheet_2026-10-05 keeps, released with
  `--release-keep`); F `ce4d35a9…` (`b07_braskeenB`) was already purged by the sheet enact.
- **Graphic_Random fix:** `RM_Braskeen`'s texPath named the file (`…/RM_Braskeen/RM_Braskeen`), so Graphic_Random
  found no folder and could load no texture. It now names the folder `Things/Plant/RM_Braskeen`, where each PNG is
  one variant. Not deployed (coordinator deploys).
- **Commissioned:** artpipe jobs `braskeen_onE_v1`, `braskeen_onE_v2`, `braskeen_onE_v3`, each with
  `reference` = E (`_artpipe/_refs/RM_Braskeen_E_2026-10-16.png`) and a different asymmetric individual
  (five sprawling arms with one shut on a husk / young and crowded / old and ragged with a broken arm).

## NEXT

`BRASKEEN_REDRAW_VARIATIONS_ON_E` — jobs queued, nothing installed; NEXT: when `braskeen_onE_v1..v3` reach
`_artpipe/done/`, show them beside E on a review sheet at true scale; install only his picks with `art.py install`
as extra PNGs in `Textures/Things/Plant/RM_Braskeen/` (e.g. `RM_Braskeen_b.png`), then deploy Miasma.
If reskin-validate rejects them for drifting from E's silhouette, re-file reference-less with E described in the prompt.
