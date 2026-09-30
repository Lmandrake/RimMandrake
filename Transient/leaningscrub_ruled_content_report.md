# LEANINGSCRUB_RULED_CONTENT_1 report

## Status
Landed (parts 1-4, 6 wiring); parts 5 and 7 are report-only by spec.

## Parts
1. Four fills (Fuzzrunner, Thornhold, Shokka, Zellik) - built in `src/RimMandrake/LeaningScrub/Defs/ThingDefs_Races/RM_LeaningScrubFauna.xml`. Zellik is a true flyer (MaxFlightTime 10, FlightCooldown 5), no frames.
2. Nine menagerie species (Fuzzviper, Surrik, Ribbonwhip, Vissler, Dustflutter, Shirrel, Crustweevil, Rollbug, Tikkit) - same file. `RM_VisslerArm` and `RM_RawVenom` in `Defs/ThingDefs_Items/RM_LeaningScrubItems.xml`. Dustflutter flies (MaxFlightTime 2).
3. Four fuzz flora (Whipfuzz, Pillowmoss, Tanglefuzz, Cruststar) - `Defs/ThingDefs_Plants/RM_LeaningScrubFuzzFlora.xml`, Flammability 0.
4. Venomvine forms (Dripping, Twitcher, Hollow, Crown) - `Defs/ThingDefs_Plants/RM_LeaningScrubVenomvineForms.xml`, reusing the existing EnvironmentalHazards comps; no C#.
5. Blurrg - NOT built (tamed-only). Owed: RSW_Blurrg port, canon_references entry, art.
6. Donor-reskin art - four RUT_ renders wired (Fuzz, Grellbush, Grellspine, WildHealroot). Thunderstep, yanker, scrap-nest bird stay queued in artpipe.
7. `VAEWaste_Hydra` dead roster row - UNRULED, reported, not struck.

Rosters in `RM_LeaningScrub_Biome.xml` wired: 13 animals, 8 plants. Donor rows kept.

## Stubs (all owed to LEANINGSCRUB_MECHANICS_BUILD_1)
Venom quill, ambush, Vissler lure, Shirrel glide, denning, Twitcher lash (map component), Crown wind-keyed mobbing, Hollow crawl job, Pillowmoss fog-condense.

## Validation
All 9 LeaningScrub XML files parse; every RM_ roster entry resolves to a def. validate_patch: UNMEASURABLE here (590 of 612 mods absent from WSL path; the files are defs, not patches). run_selftests 75/78: two failures pre-exist and are unrelated (`selftest_deployed_biome_refs.py`, `selftest_retired_mods.py` - Mo'Events FindMod blocks in Doctrine and UtinniPatches); one unmeasurable.
