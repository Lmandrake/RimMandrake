# History: the rounds, the measurements, and the lines that were wrong

`SKILL.md` holds the lessons. This file holds dates, incidents and corrected lines (corrected 2026-11-23).

## The three mods

- The three mods were chosen on 2026-09-06 for this work. Decorative Cliffs was already active then.
- On 2026-11-23 the mod XML was read in the Steam workshop folders: `3526906079` (SimpleStairs), `3459462328` (Simple
  Visual Stairs) and `2453099145` (Decorative Cliffs, its `1.6` folder). None holds a DLL, and no About.xml names a
  dependency.
- The author quotes about SimpleStairs and Simple Visual Stairs are kept from the first version of the skill. The
  installed About.xml of `Kutte.Stairs` says "Plain stairs on top of floors, no costs." The two quoted sentences are not
  in the installed files. Their source is probably the Workshop pages. Nobody checked.
- Path costs and cover, from the XML: `Gomi_SimpleStair` none; `Gomi_Handrail`, `Gomi_HighWall` 200; `Gomi_FloorFence` 100;
  all three linked pieces PassThroughOnly with `fillPercent` 0.25. `REIK_Stairs_*` 20. Cliff pieces 90, PassThroughOnly,
  `fillPercent` 0.57. The About.xml of Decorative Cliffs says "Cliffs slow down movement and provide cover."

## The live test of the cliff run (2026-09-06)

A VERTICAL column (fixed x, varying z) of `Dirt_Hill_Right` rendered as a broken zigzag. The same pieces in a horizontal
row (same z, varying x) linked into one continuous mound. An isolated `build_batch` test showed both. That is the
§1 finding on horizontal runs.

## Round 1 and round 2 (2026-09-06)

Round 2 was a fresh critical-reviewer pass (§5). The scores run from 1 to 5. No later round is on record. Git: `4f7f44a61f` and `f17b09f836`.

| template | round 1 fix | round 2 finding | still open at the end of round 2 |
|---|---|---|---|
| Waste Camp | the floor sunk into a jagged pit; each prop clustered inside it | 2/5 on every metric; the reviewer took ambient map scatter for the camp's tent frame. The pit and the props were correctly in one place | the jagged edge needs to read more strongly at normal play zoom; a new review with a tight frame that cannot be confused with the map's own furniture (§5) |
| Boneyard | the gap from skull to ribcage closed to zero (the skull sat 5 cells from the ribcage, §3; it must be 0) | a fresh reviewer, with no link to the round 1 fix, read a bone-fragment prop at the far end of the tail as a second head. A direct query of the game data showed one skull object | swap or remove that prop (which of the two defs it is was not pinned down); the tree `TreeDead`, the stand-in for the silverbole, does not spawn through the live bridge path |
| Long Crossing | a dune lip as a VERTICAL column gave the zigzag; turned to a horizontal row, confirmed live | a horizontal run ONE CELL THICK reads as a wooden fence rail, not an earthen dune | widen the dune to 2-3 rows; taper the sand drift in z, or mask it to the z-span of the hull |

- The missing tree is a silent failure. The old text called it the same class as the mined-rock CLEAR gap of
  `waste_camp`. The cause was not found. The leading theory was that the terrain refused the plant for its fertility, not confirmed.
  `jawa/set_plants` reports why it refuses a cell, so that tool can settle the cause.
- `rimplace` now writes a note on the plan when CLEAR mode `all` cannot replace mined rock on the live path. So that gap is
  not silent now (`src/RimMandrake/Utils/rimplace/plan.py`). The present `waste_camp.lua` has no CLEAR.
- No mod loads the three templates. The closed item `INHABITED_AUGMENTATION_BUILD_1` names them as unwired. No open ticket
  holds the open parts (read 2026-11-23). So the open parts stay here, and nothing ships with them.

## Corrected lines

- **`grep <packageId> ModsConfig.xml`.** The game writes the packageIds in lower case, so a search for `Kutte.Stairs` or
  `Mlie.DecorativeCliffs` finds nothing. Root `CLAUDE.md` says to parse the file.
- **"Already active" (Decorative Cliffs), and "a visual lie with zero mechanical backing".** Which mods are active
  depends on the list. The stair of SimpleStairs has no pathing change. The linked pieces of SimpleStairs, the stairs of
  Simple Visual Stairs and the cliffs have a path cost. No piece has elevation.
- **"Same defName" and "blends SAME-row neighbors, not same-column ones".** `Graphic_Linked.LinkedDrawMatFrom` reads all
  four neighbours. `ShouldLinkWith` compares link flags, not defNames, and every cliff piece carries `Custom2` (and `MapEdge`). The texture
  sheets (`Cliff_Right_Atlas.png`, `CliffTop_Right_Atlas.png`) draw a full face for an east-west run. They draw a thin side
  edge for a north-south run, and the south end cell draws a small front. The `CornerFiller` fills corners only, where a diagonal and both its neighbours link.
- **The top piece as "the plateau surface behind/above" the face.** The top sheet draws a thin back edge and thin side
  edges. Inside the edge it is transparent, so the ground there is the terrain of the cell.
- **Long Crossing.** The template put the top row one z lower than the face, which is south, and its comment said north.
  In the render the top row was below the face. With that order the sheets draw the face with small posts and the top as a thin rail with
  posts. So the wrong order probably made the fence rail of round 2, beside the thin run. The template is corrected on
  2026-11-23. No live look of the corrected order exists.
- **"`rimbridge` §4a" and "`rimworld-debug-testing` §9".** `rimbridge` has no §4a. The screenshot rules are in
  `rimworld-debug-testing` §4a, and the threshold text moved to the `live-debugging-proof-harness` skill.
- **"Add it here with its evidence".** Root `CLAUDE.md` allows a skill edit only in a curation session. A lesson goes
  through `lessons.py add`.
- **"An external, cited source".** The web research was done on 2026-09-06. The first version of the skill (git
  `d8e152500d`) names no source. The sources are unknown now.
