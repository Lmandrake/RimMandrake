# Warscar sheet close — progress 2026-10-05
Owner typed "Done with Warscar". Sheet `warscar_sheet_2026-10-05.decisions.json`.
## Ingest — DONE
- Stamped ruled; art.py ingest --redo-jobs warscar_jobs_2026-10-05.json: 10 rulings, 11 purges, 0 refused. Holds (cuts) are not art rulings.
## Installs — DONE (all A picks already live; placeholder_detect: all `real`)
- RM_Chatrak A, RM_Tetchik A, RSW_FoundryBeetle A: live, nothing to copy. RG_Rimclaw A (picked the in-game RimclawArtOverride picture): live.
- SW_Electricgryllotalpa B, SW_Electrictick B, AA_Helixien B, SW_Juggernautbeetles B: donor defs, no owned texPath, not installed; recorded on WARSCAR_SHEET_DONOR_PORT_1 (Abyss precedent).
## Cuts — DONE
- AA_SpinedGow removed from RM_Warscar and RUT_Scarlands (twin); RSW_CrystalFairyMole removed from RUT_Scarlands and the WildAnimals_Warscar.xml patch (RM_Warscar gets it only via that patch). Header comments corrected. Defs left in place.
## Descriptions — DONE (`src/RimUtinni/UtinniPatches/Patches/Warscar_Rename.xml`, validate_patch 0 errors)
- AA_Helixien -> bileworm (label + description from the picked render). Conflict: Contagion_Rename.xml still says vulloth for the same def; the new file sorts after it so bileworm wins; the Contagion owner should drop the old block.
- RG_Rimclaw, SW_Juggernautbeetles: new descriptions written from the images.
## Jobs — DONE (5 artpipe jobs, `warscar_jobs_2026-10-05.json`, owner_note verbatim)
- warscar_MegaphoridLarva_v2 east/south/north, owner_note "redo (no note)".
- warscar_Mynock_v2 east/north (north derives from east): the liked picture is column A, the in-game single image (column B, his purge, was the render set). No finished job holds it, so it is attached via canon_reference with the prompt saying it is the accepted individual; canon: mynock. South stays that picture.
- Filed MYNOCK_FLIPBOOK_FRAMES_1 (no flip-book item existed) and WARSCAR_SHEET_DONOR_PORT_1.
