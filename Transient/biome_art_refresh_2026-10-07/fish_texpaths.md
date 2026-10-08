# Fish texPaths — untangled from timber (2026-10-07)

## Status
- [x] census  - [x] repoint  - [x] art / queue  - [x] validate  - [x] commit

## Census (texPath shared with RUT_Hardwood / RUT_Greenwood)
- Things/Item/Resource/RUT_Hardwood: RUT_Hardwood (timber), RUT_Tekk, RUT_Tubbik
- Things/Item/Resource/RUT_Greenwood: RUT_Greenwood (timber), RUT_Zhurr, RUT_BladderboilCatch
- Timber defs keep their paths, so phfix_RUT_Hardwood*/phfix_RUT_Greenwood* now touch timber only.
- Other fish still on non-fish vanilla/plant/meat sprites (~70 RUT_/RM_ defs on plant sprites, Meat_Small, ToxicMeat, CrystalHorn): NOT touched, out of scope; list from the texPath census (scratch) if wanted.

## Done
- RUT_Tekk -> Things/Item/Fish/RUT_Tekk (src/RimUtinni/UtinniPatches/Textures), bytes = RM_Tekk's finished art, installed with `art install` (--reason script).
- RUT_Tubbik, RUT_Zhurr, RUT_BladderboilCatch -> TEMPORARY vanilla Meat_Small (commented in XML; not a placeholder, lint 0 failures, allowlist untouched).
  Jobs phfix_RUT_{Tubbik,Zhurr,BladderboilCatch}_{a,b} queued at priority 0 (build_fish_texpath_jobs.py); target Things/Item/Fish/<def>, 128x128.
- RUT_BladderboilCatch has finished RM_ twin renders (done/scald2_bladderboilcatch_a/b/c) but RM_BladderboilCatch.png is not in the repo yet — unreviewed, not installed.
- Note: Things/Item/Fish/Dogfish (RM_CoolantEelCatch) does not resolve under any Textures root per validate_patch — not fixed here.
