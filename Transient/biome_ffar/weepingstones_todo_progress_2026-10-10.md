# Weeping Stones — enact TODO rows (26 TODO lines, 19 rows + Huldu reference fix)

Source: `art.py enact` log `/home/mandrake/.seat-tmp/BENCH/ws_apply.log` (commit 53a55b750); decisions `Transient/biome_ffar/weepingstones_sheet_2026-10-05.decisions.json`.

| row | owner note (verbatim) | plan | status |
|---|---|---|---|
| ColossusToad (3 picks + note) | "Redo more alien, rename Colossia, regenerate description, based on the current (b) but extended." | rename + new description; queue redraw jobs referencing pick (b); install (b) as interim if slot found | DONE — new RM_Colossia (WeepingStones, Odyssey stats) replaces ColossusToad on RM_WeepingStones roster; pick B installed as interim; redraw job wsrow_colossia_v1 (b as reference); vanilla toad untouched |
| Plant_Reeds (pick + note) | "Two more variants, more realistic." | find owning/overriding mod, install pick B; queue 2 variant jobs | DONE — pick B installed in WeepingStones at Things/Plant/RM_Reeds/RM_Reeds_A (patch RM_Reeds_OwnArt.xml repoints Odyssey Plant_Reeds); 2 variant jobs |
| RM_Burrak | "Rename to Burra Burra" | rename label (and defName?) everywhere | DONE — label burra burra (ThingDef+PawnKindDef), description reworded; defName RM_Burrak kept (label-in-place rename, Wasteland thuffor precedent → no save risk) |
| RM_Dewblade | "Two more variants, more realistic." | queue 2 variant jobs | DONE — 2 variant jobs wsvar_*_{a,b}_v1 queued (pick as reference) |
| RM_Dewgourd | "Two more variants, more realistic." | queue 2 variant jobs | DONE — 2 variant jobs wsvar_*_{a,b}_v1 queued (pick as reference) |
| RM_Dewshrooms | "Improve description" | rewrite description | DONE — description rewritten (def in TheRot) |
| RM_Dripfringe | "Two more variants, more realistic." | queue 2 variant jobs | DONE — 2 variant jobs wsvar_*_{a,b}_v1 queued (pick as reference) |
| RM_Duul | "Improve description." | rewrite description | DONE — description rewritten |
| RM_Ikkal | "Improve description and call it a Softstone." | rename label to Softstone + description | DONE — label softstone (+RUT twin label), description rewritten; defName kept |
| RM_Karrek | "Rename the Iaala" | rename label | DONE — label iaala on creature, catch, meat, paste, breeding stock, recipes; defName kept |
| RM_Rockfinger | "Two more variants, more realistic. Make this 50% larger." | queue 2 variant jobs; drawSize x1.5 | DONE — visualSizeRange x1.5 + 2 variant jobs |
| RM_Salvecomb | "Two more variants, more realistic." | queue 2 variant jobs | DONE — 2 variant jobs wsvar_*_{a,b}_v1 queued (pick as reference) |
| RM_Shadefern | "Two more variants, more realistic." | queue 2 variant jobs | DONE — 2 variant jobs wsvar_*_{a,b}_v1 queued (pick as reference) |
| RM_Steamfrond | "Creates a unique Star Wars cuisine spice.  Improve the description." | description; spice product | DONE — new spice RM_Korrim (invented name, no canon hit), steamfrond harvests it, murrin broth cooks with it; description rewritten; interim texture = old seep-salt pile, art job queued |
| RM_Tirbak | "Redo the description to be more in world. Flexible wind intakes constantly drain moisture from any dampness in the breeze and make a low howling sound in a strong gust. Pack animal." | description + packAnimal | DONE — description rewritten with his intake/howl detail; packAnimal already true |
| RM_Verdimoss | "Two more variants, more realistic. Improve the description." | jobs + description | DONE — description + 2 variant jobs |
| RM_Weepmat | "Two more variants, more realistic. Improve the description" | jobs + description | DONE — description + 2 variant jobs |
| RSW_Dactillion | "Old Flyer art must be removed (remove F)" | delete old flying flip-book art F | DONE — 12 Dactillion_Flying_* frames retired via ledger (owner's words); flyingAnimation* fields removed; MaxFlightTime kept |
| RSW_Ollopom (3 picks + note) | "Nice. Give them a small beauty bonus then call them done." | install pick B; Beauty stat bonus | DONE — pick B installed at RimStarWars/SWBestiary/Ollopom/ (live texPath) via ruling 5a3ce5b0; PawnBeauty 1 added |
| RM_Huldu (reference) | "Redo based on (c) ..." | attach (c) render as reference on pending job(s) | DONE — v1 (no reference) had already fully rendered; v2 enact_huldu_from_c_v2 queued with (c) east render as canon_reference |

## Result
All 19 rows done and marked with `art.py enact --mark-done` (evidence 721d86974); enact now reports TODO 0, CONFLICTS 0.
- Renames are label-only (defName kept, so saves are safe): burra burra, iaala, softstone. ColossusToad became a new def, RM_Colossia (WeepingStones), on RM_WeepingStones only. The frozen RUT_WeepingStones twin and the vanilla toad are unchanged.
- Huldu: v1 had already finished rendering without a reference, so it shows on the sheet beside v2 (`enact_huldu_from_c_v2`, built from (c)).
- PawnBeauty on an animal (Ollopom) shows on the stat card, but RimWorld's room beauty counts only buildings, items, plants and filth. If he wants a gameplay effect, that needs a mechanism (question for him).
- Deploys refused: all three touched mods (composed Biomes, SWBestiary, UtinniPatches) would write a DLL while the game is running. Run them after the game closes. The SWBestiary deploy also removes the 12 Dactillion_Flying_* files from the game copy.
