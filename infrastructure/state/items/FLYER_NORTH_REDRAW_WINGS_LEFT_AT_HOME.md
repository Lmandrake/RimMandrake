# FLYER_NORTH_REDRAW_WINGS_LEFT_AT_HOME — flyer idle north facings that hide the wings

## spec
Owner 2026-10-15 saw the fire-hawk's idle NORTH facing as "just its wingless form, grotesquely" (folded wings invisible from above; north w/h 0.25 vs south 0.66). Fixed for RM_FireHawk the same day (art install, owner-said). Census of all 70 flyer kinds in src/ (Baroque Biomes per-biome folders, Pyrelands, SWBestiary, UtinniPatches): `Transient/flyer_orray_fix_2026-10-15/flyer_north_census.{py,csv}`, sheet `flyer_north_sheet.png` (north beside south).

Same north-idle defect, by eye on the sheet:
- RM_FleetFlier and RUT_FleetFlier: north shows a tiny bird with stub wings; south shows full spread wings (north/south area 0.40).
- RM_Murrelith: all three idle facings are a flat grey placeholder square (no art at all).

Flip-book gaps (NOT this item; FLYER_STABLE_BODY_GATE_1 owns them): 37/70 kinds set no flyingAnimationFramePathPrefix; 10 SWBestiary kinds have a 1-frame "flip-book"; 6 set a prefix whose frames are not under src/ (may be donor/vanilla, unverified). Pilot-tier kinds with no prefix: RSW_Dactillion, RSW_FacetMoth, RSW_Mynock. The fire-hawk's 5-frame book is wired but not body-locked.

## scope
Redraw the idle north facing of RM_FleetFlier/RUT_FleetFlier with folded wings that read from above, and give RM_Murrelith real art. Every new north must match its south/east as the same animal. Install via `art install` only, with the owner's permission (cosmetic).

## criteria
Each fixed kind's north beside its south on one sheet, owner-ruled keep. No flight is live-tested.

NEXT: redraw RM_FleetFlier north (editing-images, south+east as references) and show north/south side by side.
