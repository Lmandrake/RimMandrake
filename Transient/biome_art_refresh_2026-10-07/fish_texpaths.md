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

## Pass 2 — every fish catch def (fishTypes entries), 2026-10-07
- RM_CoolantEelCatch: Things/Item/Fish/Dogfish DOES resolve in game (Odyssey `resources_odyssey` AssetBundle manifest lists it; validate_patch only scans loose src Textures, so it cannot see it). Not magenta, but it was vanilla's dogfish. Now own path, finished render gapall_RM_CoolantEelCatch_v1 installed.
- Also found 9 Scald catches (RM_Bladderboil/Doss/Eesh/Ekkel/Karrash/Muddal/Saal/Shulla/Thuum) pointing at Things/Item/Resource/RM_<def> where NO file exists in any src Textures root (would render magenta); fixed by the same move.
- Census: 81 fish catch defs with a borrowed (plant/meat/pawn/vanilla) or missing texture. Left alone: RSW_Boneblade, RSW_Rocktooth (their own donor fish art), defs already on their own existing path.
- INSTALLED 66 to Things/Item/Fish/<def> from finished passing artpipe renders (catch-targeted job; RUT_ twins get their RM_ twin's art; capped at 256px; art install --reason script).
- QUEUED 10 defs, 20 jobs phfix_<def>_a/_b priority 0 (fish_catch_jobs.json, build_fish_catch_jobs.py): RM_FessuCatch, RM_KrellikCatch, RM_OdduCatch, RM_OovuCatch, RM_TarnnCatch, RSW_FaaCatch, RSW_LaaCatch, RSW_MeeCatch, RUT_Hurrok, RUT_Vhessa. Each keeps a commented vanilla Meat_Small temp sprite.
- TWIN-WAIT 5 RUT_ defs (RUT_Fessu, RUT_Krellik, RUT_Oddu, RUT_Oovu, RUT_Tarnn) sit on the temp sprite until their RM_ twin's phfix art lands; copy its bytes to Things/Item/Fish/<RUT_def>.
- Note: phfix_RUT_BladderboilCatch_a/_b (pass 1) are now redundant, the finished scald2 render was installed; harmless to let them run or withdraw.
- Allowlist: no entries matched; untouched. placeholder_lint: 0 failures.
