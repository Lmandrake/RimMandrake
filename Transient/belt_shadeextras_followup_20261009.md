# Shade extras follow-up 2026-10-09

## task1 live-check items
(pending)

## task2 art
(pending)

## task3 cleanup
(pending)

### task1 done
Filed 5 bridge items (items/*.md written): LONGSHADE_SCENE_LIVECHECK_1 (tollok+lure awning+harrok), LONGSHADE_PATCH_LIVECHECK_1, LONGSHADE_STAMPEDE_LIVECHECK_1, LONGSHADE_JAWATOW_LIVECHECK_1, GELATINOUSSLIME_JOININGWATER_LIVECHECK_1. Mirror field superseded (SOLAR_MIRRORS_BUILD_1), no check.
Findings: empty-patch item asked to add tollok to lairRaces, but RM_Tollok is a hediff not a race; lairRaces still Mirrak/Gulloth, so its static verify could not hold. No tool exists to read hediff lists / inspect strings / RM_MapComponent_CrawlerHull; items say UNMEASURED in those cases.

### task2 done
artpipe_state find: 0 hits for harrok, RM_Harrok, RM_LureAwning, RM_SlimeHandRing, hand ring, joining water (awning/lure hits were unrelated substring noise in Gloomcast/ShadeTent/Ulgga jobs). Queued 5 jobs from Transient/belt_shadeextras_art_20261009.json: RM_LureAwning_v1, RM_SlimeHandRing_v1, RM_Harrok_v1_{east,north,south} (harrok invented, no canon). No install_to set; current placeholders (ShadeTent, ChunkSlag, Mirrak) stay until the art ledger installs. Nothing replaced.

### task3 done
Origin now carries only 2 live copies next to closed/ (LONGSHADE_HARROK_STILT_1, LONGSHADE_JAWA_RETURN_1); the other four (EMPTY_PATCH_WARNING, LURE_AWNING, STAMPEDE_ROOF, TOLLOK_TICKS) are already gone from origin/main and local. closed/ copies byte-identical to origin's live copies' counterparts; rimflow show: HARROK_STILT done, JAWA_RETURN done. Deleted the two live copies on origin by plumbing commit (local clone is 25 ahead/28 behind).
