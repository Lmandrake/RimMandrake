# RUT_PLANT_BIOMEPLANTRECORD_CROSSREF_1

## What was found (live, full 578-mod cold load, 2026-09-10)

`check_config_errors.py` against a live load surfaced 18 unresolvable
`RimWorld.BiomePlantRecord` cross-references, all in the same shape:

```
Could not resolve cross-reference: No Verse.ThingDef named RUT_Arpeau found to
give to RimWorld.BiomePlantRecord RimWorld.BiomePlantRecord
```

Full list of missing defNames: `RUT_Arpeau`, `RUT_BlastpodShroom`,
`RUT_BleedingTooth`, `RUT_Brightbell`, `RUT_CrimsonCap`, `RUT_Dewshrooms`,
`RUT_FlakespireFungus`, `RUT_FruitingBodies`, `RUT_GreyLady`,
`RUT_MortalMorelPlant`, `RUT_Nogtyl`, `RUT_Nuitae`, `RUT_Pusmelon`,
`RUT_RustPuff`, `RUT_Sagecrust`, `RUT_Shinecap`, `RUT_Skulltop`,
`RUT_VioletWimple`, `RUT_Wrinklecap` (19 names, some may repeat across
biomes — count them fresh, don't trust this list's count).

**Not this session's droid-retirement work** — verified: none of these
names relate to Asimov/DroidDepot/MSEDroidFix. Likely candidates, not yet
confirmed:
- A `wildPlants` dictionary in some `RUT_*` BiomeDef (probably a
  RotSporeKit-adjacent or fungal biome — several of these names read as
  mushroom/fungus flavor: Shroom, MortalMorel, FruitingBodies, Skulltop)
  listing these as keys, but the actual `RUT_*` ThingDefs either were never
  built, were renamed, or live in a mod not currently active/deployed.
- Given tonight's `RUT_Wasteland.xml` fix found a near-identical bug shape
  (a stray non-ThingDef element sitting in a `wildPlants` dict), check
  whether one of these is the SAME stray-element pattern rather than a
  genuinely missing ThingDef — that fix was file-specific and this may be
  a sibling file with the same defect, undiscovered until now.
- `RUT_Nuitae`/`RUT_Wrinklecap` were independently flagged tonight
  (`FUNGALFOREST_RAID_MERGE_1`'s offline follow-up) as **unreachable** —
  present in `RotSporeKit` but appearing in no `wildPlants` table anywhere
  in the repo. If a table now DOES reference them and it doesn't resolve,
  that's either a deploy-sync gap (RotSporeKit not deployed/enabled) or a
  defName mismatch between the roster and the def.

## spec

1. Find which `BiomeDef`(s) carry these 18-19 names in `wildPlants` — grep
   `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/*.xml` for each name.
2. For each: confirm whether a real ThingDef with that exact name exists
   anywhere in the active mod set (RotSporeKit, UtinniPatches, or a donor) —
   check via rimsage or a fresh def dump, not a stale one.
3. Fix per what's actually true: if the ThingDef exists under a different
   name, repoint; if it's a genuinely-missing/never-built def, either build
   it or remove the wildPlants entry; if it's a deploy-sync gap (mod built
   but not deployed/enabled), deploy/enable it.

## verify

`check_config_errors.py` on a live load shows zero of these 18-19 lines.
