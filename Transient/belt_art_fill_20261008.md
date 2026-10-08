# Belt art fill 2026-10-08

pending/ was empty (0 jobs). Census: every Things/ texPath on an RM_/RUT_/RSW_ def checked against src Textures (folder and `_a` forms) and then against the artpipe state dir by subject.

## Queued (12 jobs, 4 subjects x east/south/north, item SHIPVERMIN_FREE_TIER_BEASTS_1)
RM_Skivvik, RM_Rattagh, RM_Gorrud, RM_Fethrik - invented franchise-free ShipVermin cast, currently vanilla placeholder textures (def header: real art owed per species). No hits in artpipe state (find) before filing. Rows: `Transient/belt_art_fill_20261008_rows.json`. Install target ShipVermin/Textures/Things/Pawn/Animal/<def>/<def>_{facing}.png.
Daemon pickup confirmed: Fethrik/Gorrud/Rattagh east went active within seconds; RM_Fethrik_east PASS at 120 s. RM_Skivvik_east hit the codex worker_error flake; requeued with requeue_flakes.py.

## Skipped (art already exists; need wiring, not generation)
Braskeen, Ismerrow (done/miasma_*), YearningFruitHarvested, SweetlineToken, RUT_Fuzz (done gapall/item jobs), all Scald catch items and Chimeglobe/Glassfern/Palefloss (PNGs in src). Alt-pose/variant paths (GreatDevourer/Groundrunner extras, Dewfall dew overlays, Drazzik_Swimming, Dakkra_rest) left alone: variants, not owed subjects.
Not queued: wreck, graffiti glyph and other zero-hit paths were not individually proven owed or approved.
