# Miasma (+ Feverwood) names/tiers/roster pass — 2026-10-07 (BENCH helper)

Source: Transient/biome_ffar/miasma_sheet_2026-10-05.decisions.json (44 owner rows, last at 2026-10-08T04:02:23Z).
Other sheets scanned for 2026-10-08 rows: none besides Miasma (Feverwood added later — see below).

## Miasma renames (label + fresh description)
- AA_DecayDrake: mubbaro -> fermatalis (Slime_Rename.xml, in place; mechanic kept)
- AA_Lockjaw: lockjaw -> siezer (Miasma_Rename.xml)
- AA_Mantrap: mantrap -> lastvine (Miasma_Rename.xml)
- AA_RaptorShrimp: raptor shrimp -> sharpshrimp (+ meatLabel sharpshrimp flesh)
- AA_Thermadon: thermadon -> duskfire
- VFEI2_BlackSwarmling: black swarmlings -> ondrukka (name invented; checker pass, stem sweep clean)
- RM_SiltLampreyJuv: young silt lamprey -> gillclamper (in place)
- RSW_PodWorm: pod worm -> hell's lantern (in place; bite -> ToxicBite, MoveSpeed 2 -> 1.5 for "venomous and slow")
- RSW_AaroxisDendoria -> RM_Liliana "liliana" (tier move, below)

## Tier moves
- RSW_AaroxisDendoria -> RM_Liliana (+ RM_LilianaSilk, RM_EggLilianaFertilized/Unfertilized) in mandrake.rm.miasma;
  art copied byte-for-byte to Miasma/Textures/Things/{Pawn/Animal/RM_Liliana, Item/Resource/RM_LilianaSilk, Item/RM_LilianaEgg}.
  Cast inline in RM_Miasma.xml at 0.3; removed from WildAnimals_Miasma.xml. RSW_ defs kept: frozen RUT_Miasma twin still names them.
- RSW_RustNipperJuv: RM_RustNipperJuv already existed and was already cast in RM_Miasma (SEA_BEASTS_TIER_RULING_1);
  roster json row repointed to RM_RustNipperJuv. RSW_ def kept for frozen RUT_Miasma.

## Cut
- AA_Slurrypede removed from RM_Miasma.xml wildAnimals only; roster json -> evictions (cut). Untouched elsewhere.

## Validation
- validate_patch: Miasma_Rename/Slime_Rename/WildAnimals_Miasma 0 errors; every op matches exactly 1 def.
- selftests 332/333; only failure bridgetools/selftest_tool_metadata.py (stale bridge DLL, unrelated).

## Commits
- af2b54fe2 Miasma pass (pushed)

## Feverwood (Transient/biome_ffar/feverwood_sheet_2026-10-05.decisions.json, 38 owner rows)
- VFEI2_Megathrips: megathrips -> kasselith (invented; FeverWood_Rename.xml, validate 0 errors, 1 match each)
- Descriptions rewritten: RM_Brathek (rasping larva, gripper pegs, no drill head), RM_Silloch (regenerated),
  RM_Grolth (from its in-game art), RM_Skellick (a thief), RM_Chellow (beakless whistling skin-flap mouth)
- Cut from RM_FeverWood only: RM_Thavrik, RM_Lommerel, RM_Nemmel, RM_Gorrameth (wildAnimals), RM_Skethral (wildPlants)
- Design: fever_wood_fauna_roster_2026-09-23.md, fever_wood_rm_cast_proposal_2026-09-24.md, rosters/the_fever_wood.json
- selftests 329/333: failures are HugeThings/TitanicCreatures (another helper in flight) + stale bridge DLL; none touch these files
