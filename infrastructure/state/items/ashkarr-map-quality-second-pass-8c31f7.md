## spec
⛔ 2026-08-19 — SAVEGAME WRITING IS OUT. Every "run X" in this item names a
script that has been DELETED; the map reaches the game over the live bridge
(design/Jawa/worldbuilding/ASHKARR_WORLD_DEFINITION.md §12). The DIAGNOSES and
the owner's ORDER below are still the work; the tooling named is not. The
current painter is `src/RimMandrake/Utils/ashkarr_paint.py` -> a CSV.

Ash'karr is BUILT and committed (`world/WORLDMAP_gen.rws`, seed `pumpkin`,
21,872 tiles, 12 factions all ours). This item is the owner's review list
from 2026-08-17, in HIS order. Everything below is diagnosed, not guessed.

🔑 THE TOOL THAT MAKES ALL OF IT POSSIBLE: `src/RimMandrake/Utils/world_graph.py`
builds the tile adjacency graph (cached `world/world_graph.npz`, verified by
the 12-pentagon test). Before it existed the painter could only make per-tile
decisions, which is why the map looked like confetti. `world_shape.py` has
despeckle / components / coastal / grow / roughen on top of it.

THE PIPELINE (⛔ DELETED 2026-08-19 - savegame writing is out; the map reaches
the game over the live bridge, ASHKARR_WORLD_DEFINITION.md §12. All five scripts
are gone and `worldmap.py`'s write() now raises. Kept only so the old stage names
in the notes below can be read):
  source -> paint_ashkarr -> populate_ashkarr -> name_ashkarr_regions
         -> name_ashkarr_factions -> clean_ashkarr_hydrology
         -> redo the world-object water mask -> load and read jawa/world_stats
⚠️ HOLE: no replacement exists yet for the populate / name-regions / name-factions
/ hydrology-prune stages. They must be re-specified as bridge importer work.

REMAINING WORK, owner's order:
1. ORDERING. Seas FIRST, then rivers, then the terrain that depends on rivers.
   Today rivers are inherited from worldgen and merely pruned. Author them:
   walk downhill neighbour-to-neighbour from mountain clusters to a sea, write
   the river arrays (they ARE arrays - see savegame-editing.md).
2. LUSH TERRAIN ONLY ON RIVERS. Jungle/dense vegetation placed after rivers
   exist, on river tiles only. AB_TarPits adjacent to those. AB_FeraliskInfested
   Jungle only there.
3. MUTATORS. 5,233 `Coast` of which 4,831 are on non-water tiles and 2,116 deep
   inland; 4 `VEE_CoralReef` incl. one at arc 177 on the nightside. They were
   placed for the ORIGINAL sea layout and the repaint moved the water. Editable:
   tileMutatorTilesDeflate (4B tile) + tileMutatorDefsDeflate (2B shortHash),
   38,877 entries, hashes resolve against DefDump/defs/TileMutatorDef.json.
   Recompute Coast from real adjacency; strip marine mutators inland. The
   ice-and-fire desert inside the extreme desert is almost certainly this too.
4. ROADS. Fragmented in the OLD save because clean_ashkarr_hydrology (⛔ deleted
   2026-08-19) removed segments in water and nothing reconnected them - that was
   an ERROR, not decay. Lay roads
   LAST, as shortest paths over the graph between actual settlements. Plus a
   specific one: the Fuel Works -> the propane lakes, along the cold swirl where
   it reaches nearest the twilight.
5. SHAPES. The Scald Spine is a perfect circle - use world_shape.roughen(). Only
   the crater itself may be round. No geometric shapes anywhere else.
6. PLACEMENT. Ascendant Helix sited by DENSITY OF BIOLOGICAL HORROR around it
   (ocular forest, horror wastes) - that is what they came to study. At least
   TWO Deepwater Compact settlements on The Scald despite the Empire.
7. HORROR WASTES lore is ruled (build_concepts, 2026-08-17): scattered small
   holdings in the rotting Twilight, RETREATING not spreading.
8. SANITY PASS. The owner's words: evaluate "how sane is this planet?", not
   "did the script run". Check: stranded coasts, biomes without their climate,
   rivers that reach no sea, single-tile islands, settlements unreachable by road,
   lush terrain off-river.

✅ THE HOLE IS SMALLER THAN IT LOOKS (CHECK, 2026-08-19). Deleting the nine
savegame writers did NOT take this item's tooling with it. Everything above is
an OFFLINE authoring judgement and the offline painter is intact:
`ashkarr_paint.py`, `ashkarr_settle.py` and `world_relief/hydro/biomes/settle.py`
still emit the whole bundle (`world/ASHKARR_WORLDMAP_*`), and `worldview.py`
still renders it. What died was only the tail - splicing that bundle into a
`.rws`. That tail is now `worldpaint-live-bridge-route-9d41c7`: the same arrays,
pushed into the live WorldGrid over the bridge. Settlement conversion and
faction/region naming, which `populate_ashkarr.py` and the two `name_*` scripts
used to do IN the save, are bundle fields today and become importer work.
⚠️ One thing genuinely cannot be re-measured by anything in the repo: the
Blackstar Company faction swap (was `swap_faction_def.py`) and the final
21,872-tile world-stats histogram. Treat both as historical, not as checks.

## verify
EMPTY

## criteria
the owner looks at the planet and does not immediately name a defect.

## notes
**Imported from `queue/CHECK.md`. Its `state:` read, verbatim:**

ready

owner ruling 2026-08-17, evening, after looking at 8 screenshots of the built world:

🔴 THE DIAGNOSIS, mine, accepted: the painter builds independent per-tile fields in
   PARALLEL and smooths the result. A planet is a CAUSAL CHAIN - elevation -> sea level
   -> drainage -> moisture -> vegetation -> settlement -> roads - and each stage must
   READ the one before it. Consequences visible on screen:
   * `RELIEF` is a per-region constant + jitter, so two neighbours differ by coin flip.
     There is no slope, so "downhill" is UNDEFINED and rivers are underivable.
   * The painter writes NO river. Every river on the OLD planet was a fossil of VANILLA's
     elevation field, truncated by clean_ashkarr_hydrology (⛔ deleted 2026-08-19) where it
     met the new water. That is why they started in flat sand and ended in open desert.
     🔑 The fix is unchanged and is now the bridge importer's job: author rivers ourselves.
   * Lush terrain is off-water because biome = region_of(arc, bearing, elev). Water is
     not an input to that function.
   * Anything defined by a RADIUS renders as a CIRCLE - the Scald disc, the Spine
     annulus, the Rust Cathedral bullseye. roughen() papers over it; the real fix is
     that a range must be a CONTOUR of a field, not the definition of a region.
   * "specks 2326 -> 237" was the wrong metric. It measures texture, not sense.

ORDER, ruled: 1 elevation field over the graph (plates + distance-to-boundary uplift +
   multi-octave noise) · 2 sea level = threshold on it · 3 rivers = priority-flood fill
   + steepest-descent routing + flow accumulation, graded into Creek/River/HugeRiver,
   arrays written by us · 4 rainfall field advected from seas + terminator ice, with
   orographic shadow · 5 biome = Whittaker f(temp, rainfall, elev), NOT a region
   predicate · 6 riparian pass, dilate rivers 1-2 and upgrade vegetation · 7 anisotropic
   blob growth along isotherms · 8 roads LAST, cost-weighted over the graph between real
   settlements · 9 offline sanity linter that must PASS before the owner ever looks.

Three owner answers, 2026-08-17:
   RIVER MOUTHS: BOTH. High-accumulation trunks MUST reach a sea; low-accumulation
     rivers MAY die in playas / salt pans. So "reaches no sea" is a defect only above
     the trunk threshold - the linter must know which.
   GREEN RIBBON: NILE-STYLE. A 1-2 tile lush band follows EVERY river wherever it goes,
     including through ExtremeDesert at the substellar point.
   REPAINT SCOPE: FULL REPAINT. ⛔ "from the pristine source ... passes re-run after"
     is DELETED 2026-08-19 - savegame writing is out and no source .rws is read or
     written. The RULING stands: nothing from the old world is preserved; the planet is
     derived end to end and delivered over the live bridge.

🔴 MAGENTA: FLAT_ONLY in paint_ashkarr.py (⛔ deleted 2026-08-19; the successor is
   `ashkarr_paint.py`) lists 3 biomes and the screenshots show many
   more (Nightspill, Gray Marches, South Marches, one on the nightside ice). Audit every
   biome x hilliness against the BiomesKit texture folders OFFLINE. This was catchable
   without a load and was not caught.

🔴 MAGENTA — SETTLED 2026-08-17, and my first two diagnoses were both wrong.
   CAUSE: `ZBiome_DesertOasis`, used in `dew_belt` (52 < arc < 92 around bearing 178 -
   exactly the twilight band where every magenta patch sits). It has a Forest/ texture
   set and NO Hills/ folder, and it was simply absent from `FLAT_ONLY`. The clamp at
   paint_ashkarr.py:334 was working the whole time (⛔ that file is deleted, so the line
   reference is unresolvable; the clamp logic moved to `ashkarr_paint.py`);
   `hh + (1 if random() < 0.18)`
   promotes ~18% of its tiles off flat, and those are the patches. FIXED.
   ⛔ REFUTED, do not re-raise: "missing _Snowy variants cause it". The snow suffix
   fires ONLY from per-biome `*SnowyBelow` temperature fields on
   ReGrowthCore.BiomesKitControl, and Alpha Biomes / More Vanilla Biomes / Advanced
   Biomes declare NONE - so their _SemiSnowy/_Snowy/_VerySnowy art is dead weight and
   can never be requested. Proof by correlation: RG_BoilingForest sets zero snow
   fields, ships zero snow art, and has never gone magenta.
   🔑 There is no Mountains/ folder anywhere - Mountains and Impassable live INSIDE
   Hills/. The Hills-vs-Mountains split I worried about does not exist.
   LATENT, not live: ExtremeDesert declares mountainsSnowyBelow -5 and ships only
   _SemiSnowy; Scarlands declares mountainsFullySnowyBelow -21 and ships no
   _FullySnowy. Both are dayside-hot on Ash'karr today. Recorded as COLD_FLAT.
   MOD SETTING: ReGrowth 2 -> General -> "Enable world map beautification"
   (`RG_WorldMapBeautificationProject`, default True, never toggled here - its store
   `Config/ModSettingsFrameworkMod_Settings.xml` does not exist). Turning it OFF does
   fix magenta, by removing the BiomesKitControl extensions entirely - i.e. it deletes
   every hill/forest/mountain sprite from the world map. It is a sledgehammer; the
   one-line FLAT_ONLY fix is the right tool.

🔑 RIVER/ROAD ADJACENCY - HOW FAR IT IS SOLVED, 2026-08-18. Read this before trying again.
   FORMAT: three parallel arrays; each entry is (origin tile uint32, adjacency byte,
   def shortHash uint16). Origins are SORTED ASCENDING and REPEAT - a tile carries one
   entry per link, so a through-tile appears twice.
   ✅ PROVED: the adjacency byte indexes an ANGULAR neighbour ordering. Evidence, and
   it is decisive: over the 67 river tiles and 163 road tiles that carry exactly two
   links, the slot DIFFERENCE is only ever 2 or 3 - never 0, 1, 4 or 5. A river passing
   through a tile bends 120 or 180 degrees and never doubles back at 60. Only an
   angular ordering makes a slot difference encode a turn angle. River 58.2% straight,
   road 67.5%, against 33.3% for a uniform distribution.
   ✅ PROVED: the rotation offset is PER-TILE, not global. Rivers and roads score their
   best on DIFFERENT (winding, rotation) pairs, and no pair beats ~0.27 reciprocity.
   ⛔ REFUTED, do not repeat: scoring candidate orderings by "is the implied target
   also a river tile". 27% of river origins have NO river neighbour, so the test tops
   out near chance whatever the mapping. It cost two rounds.
   ⛔ Distance-order and ID-order were both tried. Neither is it.
   ⇒ WHAT IS STILL NEEDED: one number per tile - which neighbour is slot 0, plus the
   winding. 21,872 of them. Only the engine has it. The route is a companion [Tool]
   that dumps Find.WorldGrid.GetTileNeighbors order per tile, which needs the game DOWN
   to deploy because the OS locks the assembly. `Outputs\Adjacent Distance Between
   Layer Tiles` exists as a debug action and RAN, but its output went to a window, not
   to Player.log or jawa/drain_log - if it prints per-tile distances IN neighbour order
   those distances are a fingerprint that recovers the permutation without any new code.
   Try reading it via rimworld/get_ui_state before building the DLL.
