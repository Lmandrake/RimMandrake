# Placeholder creatures art 2026-10-09

Follow-up to Transient/flat_square_art_check_2026-10-09.md. The sweep's "no sheet ruling" claim was wrong for 3 of 4. No jobs filed: nothing is missing art.

| def | what | sheet ruling | renders | action |
|---|---|---|---|---|
| RM_Drommath | FeverWood sap-sac animal (RM_SapSuckerGuild.xml, on RM_FeverWood roster 0.3). Only flat `FeverWood/Textures/Things/Pawn/Animal/RM_Drommath/RM_Drommath.png` (392 B), no facings installed | `redo` 2026-10-08: "can't have actual wood showing. I like the B south facing, generalize that to North and East" | _artpipe/done: feverwood_drommath_{north,east,south}, regen_fw_drommath_v2_{north,east} (v2 east/north are the redo; no v2 south, B south is the one he liked) | OWNER: review v2 east/north vs ruling, then install (not installed). No new job. |
| RM_Ollareth | FeverWood crown plant-alarm animal (RM_SapSuckerGuild.xml) | `B` 2026-10-08 | Real N/E/S already installed (46-77 KB). Only the bare `RM_Ollareth.png` (394 B) is flat: a fallback/icon file, not what the facings use | None. Optional: icon from B south. |
| RM_Sorruth | Grey Sea sessile creature (TerminalBiomes RM_GreySeaSessile.xml). Flat `RM_Sorruth.png` 912 B | `hold`, followed by note "cut don't need" (2026-10-09, greysea sheet) | greysea_sorruth_v1_{east,south} done, north failed | None. Cut; do not render. Its defs/roster rows are still in src (cut not enacted there). |
| RM_TrackPrint_Animal | NOT a creature: ground track decal texture `Things/Tracks/RM_TrackPrint_Animal` used via RM_TrackSurfaceExtension.animalTexPath (CreatureBehaviors). 624 B | none needed | artpipe done/RM_TrackPrint_Animal exists | Odd, not filed. Flat silhouette is the plausible deliberate print; owner may look at _artsrc/RM_TrackPrint_Animal if wanted. |
