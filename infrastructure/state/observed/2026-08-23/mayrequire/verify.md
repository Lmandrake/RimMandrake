# MAYREQUIRE_NAMES_THE_PATCHER_1 — verify, BUILD, 2026-08-23

## the defect, confirmed against an INDEPENDENT source
  The dump's packageId credits whoever PATCHED a def last, not who DEFINED it.
  Desert, ExtremeDesert and AridShrubland are Core biomes; GRiNDTerra Terrain
  Retexture patched them, so the capture attributes all three to
  grimterra.terrainretexturemod, and the generator emitted that as MayRequire.
  => three VANILLA biomes gated on a retexture mod. Remove that mod and the
     cast silently stops applying to biomes that are still present.

## ⚠️ the first check I ran was CIRCULAR and returned a confident 0
  It compared the capture's modName against a list of Core/DLC names — but the
  capture is the very thing that mis-attributes them, so Desert read as
  'GRiNDTerra Terrain Retexture' and matched nothing. A dump cannot audit its
  own attribution. The independent source is the GAME'S OWN Data tree:
  Core/DLC DEFINE 25 BiomeDefs there, and 3 of them were gated.

## after the fix
   Desert           (none — Core/DLC defines it)
   ExtremeDesert    (none — Core/DLC defines it)
   AridShrubland    (none — Core/DLC defines it)
   Wasteland        MayRequire="mlie.advancedbiomes"
   AB_RockyCrags    MayRequire="sarg.alphabiomes"

   MayRequire attributes: 19  (was 22; the 19 mod-defined biomes keep theirs)

## unchanged otherwise — the fix is surgical
  744 records and 52 operations before and after; the ONLY diff is 3 attributes.
  validate_patch.py: OK - 0 errors, 0 warnings
  deploy: VERIFIED in sync, game copy byte-identical

## ⚠️ the fix failed silently on its first cut, and the guard is now in the code
  _vanilla_biomes() imported game_paths (not importable from that dir) then fell
  back to a WINDOWS path that does not exist under WSL, returned an empty set,
  and the caller read that as 'nothing is vanilla' — re-emitting all 22. It now
  tries the repo resolver, then both path spellings, and PRINTS A WARNING rather
  than returning an empty set silently.
