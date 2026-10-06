# The Sump sheet close — progress 2026-10-05
Owner typed "Sump done". Sheet `thesump_sheet_2026-10-05.decisions.json` (writeCount 38, 21 decided rows; Gulveth/Skarrid/Skellarn untouched prefill, not rulings).
## Ingest — DONE
- Stamped ruled; `art.py ingest --redo-jobs thesump_jobs_2026-10-05.json`: 22 rulings, 2 purges (Dredgel B east/north), 1 refused (2ca18c6e: live as Dredgel east, A; waits for a replacement).
## Installs — DONE (all already live; A is what the game shows)
- A kept: Brindeth, Dorvel, Korveth, Mirrelin, Pallick, Skelver, Tolleth, Velloch (plants, `_a.png`), Kethrel A (Stage0 east/north/south). placeholder_detect: all `real`.
- Nothing to copy. Graphic_Random wiring + install of variants is OWED when the var renders land and he picks them (same as Kethevar/Lisqueth).
## Cuts — DONE
- RM_Brommet and RUT_Plant_Wick removed from RM_TheSump wildAnimals / wildPlants (`RM_TheSump_Biome.xml`). RUT_Sump (the RUT_ twin) never listed either; `WildAnimals_Sump.xml` patch neither.
- Wick: no patch or recipe references it (no seepwax/bitumen patch touches it). Defs RUT_Plant_Wick / RUT_WickStem / RM_Brommet / RM_BrommetWool left in place as unspawned content; `RUT_ExplosiveGrowthRoster.xml` still lists the Wick plant (resolves, harmless). validate_patch: 0 errors.
## Jobs — DONE (45 artpipe jobs, `thesump_jobs_2026-10-05.json`, owner_note verbatim)
- Dredgel: north/south derive_from RM_Dredgel_south (the done job whose render is the live picture).
- SumpMouse: east derives from RM_SumpMouse_east; north/south derive from thesump_SumpMouse_v2_east.
- Thrummel chain: thesump_Thrummel_v2_east (fresh) -> thesump_ThrummelBroodmother_v2_east and thesump_ThrummelWarden_v2_east both derive_from it (daemon holds a derive job until its master is done); each one's north/south derive from its own east.
- Soffeth: fresh realistic thesump_Soffeth_v2, var1-3 derive from it. Plant variants: thesump_<X>_var1-3 for the 8 plants, derive_from the live RM_<X>_a job.
- Hssiss: thesump_Hssiss_v2 east/south/north, `canon: hssiss`; entry already existed at design/RimStarWars/canon_references/hssiss (4 images, brief, must-show), none created.
