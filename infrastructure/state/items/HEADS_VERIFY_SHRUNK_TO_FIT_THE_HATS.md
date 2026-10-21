# HEADS_VERIFY_SHRUNK_TO_FIT_THE_HATS

Live check of the four species heads (Lasat, Mimbanese, Nelvaanian, Ortolan) as shipped at cb6e354c2. They were refit on the SKULL MASS (owner 2026-10-20: centre on the bulk of the head, ignore ears, horns and trunks): skull crown and chin sit on the vanilla head box on every facing, and ears, horns and trunks hang free. The earlier bbox-seated fit (6d77ea123) is gone. Offline numbers and flags: design/RimStarWars/head_envelope_2026-10-20.md, "Fit applied to the shipped heads". Known exception: the Ortolan side view is drawn at 0.74x vanilla skull height (ORTOLAN_SIDE_EAR_REDRAW_OUTGROWS_ITS_CANVAS).

## verify (live, needs bridge)
Deploy src/RimStarWars/StarWarsRaces. Shoot all facings of each species beside a vanilla pawn, bare-headed and in a vanilla helmet, with shoot_lineup_facings.py. Compare against an offline `fit_head_canvas.py lineup` render. Check that the skull sits where the vanilla head does and that the helmet covers the skull. Ears and trunks may show around the helmet. Watch for the Ortolan ears and nape overlapping the body.

NEXT: deploy RimStarWars heads and shoot the four species, bare and helmeted, beside a vanilla pawn on all facings.
