# MAP_BIOMES_REMOVED_LIVE_1 — offline verify, BUILD, 2026-08-22

The fix itself landed at 0efc38ba (another seat). This is the verification
nobody had run, plus the guard that stops a third occurrence.

## the regenerated patch is correct
  0 <li> elements remain in BiomeCast_Ashkarr.xml
  repo == deployed Steam copy (diff -q, IDENTICAL)
  26 BiomeDefs targeted; all 26 xpaths MATCH on disk (1 match each,
     PatchOperationConditional + PatchOperationReplace)

## every creature name resolves as a PawnKindDef — this was never checked
live set: 1737 PawnKindDef, 24904 ThingDef, 54 BiomeDef (capture 2026-08-23T05-05-29Z)

patch replaces wildAnimals on 26 BiomeDefs

total records: 744, distinct creature names: 619

== names that are NOT a PawnKindDef in the live set: 0 ==
   NONE — all resolve as PawnKindDef

== the 26 target biomes: present in THIS capture? (expected NO — they are the destroyed ones) ==
   0 of 26 present now; 26 absent (the regression this patch caused)

## the 36 validate errors are the POISONED CAPTURE, not a defect
  18 of the 26 target biomes are absent from capture 2026-08-23T05-05-29Z
  BECAUSE THE OLD PATCH DESTROYED THEM. 18 biomes x 2 operations = 36.
  ⚠️ Do not read those as the new patch being broken. The xpaths match on
  disk, which is the test that decides whether the patch applies. The
  def-dump check is self-poisoned until a reload produces a clean capture.

## the guard, so this cannot be reintroduced a third time
  validate_patch.py now refuses an <li> inside a dictionary-keyed field.
  Field list MEASURED, not remembered: for every field in the 1,558 vanilla
  def files, the fraction of distinct child tag names that are defNames in
  the 578-mod capture. >=80% and vanilla never uses <li> => dictionary-keyed.
  45 fields, including all three that have bitten us: wildAnimals,
  skillGains, xenotypeChances. Full derivation: custom_loader_fields.txt

  Regression-tested against a known answer before being trusted:
    known-bad  <wildAnimals><li><animal>..  -> FAIL, 1 error   ✅ caught
    known-good <wildAnimals><AA_Skyeel>1.0  -> OK, 0 errors    ✅ passed
    real regenerated patch                  -> OK, 0 errors    ✅ no regression

  Repo sweep:     129 XML files under src/**/Defs|Patches  -> 0 hits
  Deployed sweep: 127 XML files under the Steam Mods copy  -> 0 hits

## NOT proven offline — needs a reload, and it is CHECK's
  A fresh capture holding 80 BiomeDef records, not 54.
  'Could not resolve cross-reference' back to its baseline of 25, from 3,037.
  check_map_biomes_live.py printing that every biome the map names exists.
