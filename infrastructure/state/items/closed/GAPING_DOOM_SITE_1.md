# The Gaping Doom — dead sarlacc toxic-waste pit (owner, 2026-09-08 worldmap sitting)

Owner, verbatim: *"'The Gaping Doom' at 32.12N 94.76E in the Junker territory. This is
the dead sarlacc that they've been dumping severe toxic waste into (and selling that
right to anyone who has garbage to haul), causing a world-threatening buildup of
dangerous chemical, nuclear, and exotic energies."*

## spec
- **Location**: 32.12N 94.76E → **tile 2403** (MEASURED off the canon CSV: lat 32.1169,
  lon 94.7559, biome `ZBiome_Badlands` / the Cracked Lands, arc 94.0, elev 26 m).
  ⚠️ The CSV's bookkeeping `region` column says "Grey Sea" for this tile — read the live
  feature before trusting either; owner calls it **Junker territory** (the Junkers'
  stations are canon in `the_sump.md`; their waste-hauling trade is THIS site's economy).
- **What it is**: a dead sarlacc used as a waste pit. The Junkers sell dumping rights to
  anyone with garbage to haul. The buildup — chemical, nuclear, and exotic energies — is
  **world-threatening**: a plot element, not set dressing.
- **World presence**: landmark/world object on tile 2403. Base art exists:
  `AshkarrLandmarkArt/Textures/World/Landmarks/Ashkarr/sw_DeadSarlacc.png`.
  Note `sw_Sarlacc` has no mutator (skills/rimworld-world-editing §"landmark and mutator
  often have different defNames") — check what the dead variant needs.
- **Special art (owner's spec, verbatim intent)**: *"the sarlacc image, but with a bright
  green throat dull at the edges and growing brighter near the center (irregularly, not
  perfectly circular)"*. Derive from sw_DeadSarlacc.png (editing-images /
  generating-rimworld-sprites skills; silhouette must stay inside the original footprint).
- **Plot wiring**: separate follow-up once the site exists — quest/threat mechanism for
  the buildup (candidates: dumping-rights trade events, contamination clock, the
  "world-threatening" escalation). This item is the SITE + ART only; file the plot
  mechanism as its own item when the owner sits on it.

## verify
- Landmark def loaded (get_defs), placed on tile 2403, visible after world_commit,
  read back by def name; new art passes the offline sprite validator before any load.
- Owner LOOKS at the throat art (full native path handed to him) before it deploys.

## criteria
- The Gaping Doom appears on the world map at tile 2403 with the green-throat art and
  a name/description carrying the waste-pit lore; saved into the worldmap lineage.

## PROGRESS (BENCH, overnight 2026-09-09)
- ✅ Art done offline: `src/RimUtinni/AshkarrLandmarkArt/Textures/World/Landmarks/Ashkarr/RUT_GapingDoom.png`
  (1024², alpha byte-identical to sw_DeadSarlacc; green throat per owner's spec).
  Comparison: `D:\Luke\dev\Rimworld\Transient\final_review\gaping_doom_compare.png`.
- ✅ LandmarkDef authored + deployed: `RUT_GapingDoom` (UtinniPatches/Defs/LandmarkDefs).
- ⏳ OWED (one bridge call on the CANONICAL world, next clean session): place
  `RUT_GapingDoom` on tile 2403, set its name "The Gaping Doom" via the new
  `jawa/world_landmark_rename` tool (deploys next game restart), world_commit, save.
- ⏳ Plot mechanism (buildup clock / dumping-rights events) stays a separate item.
