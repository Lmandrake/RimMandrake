# RHOSSAK_MIGRATE_ROOTS_TAKE_HOLD — rhossak and galled rhossak as our own animals that bind

Owner, by question card 2026-10-19 (asked how the Cauldron's two tree-spirit animals should come over from
the retiring Alpha Memes): *"You realize I made that mechanic right? I don't know why you're saying they
come from another mod. Make them animals and make them bind."*

## What the spec is

No separate spec exists. The binding mechanic is the text he approved for the two creatures on the Cauldron
sheet (rulings 2026-10-09: "Recreate name and description from art, but art is good." / "Regenerate name and
description but art is good, a tumorous version of the above creature."), shipped first as label patches in
`src/RimUtinni/UtinniPatches/Patches/Cauldron_Rename.xml`:
- rhossak: "Where a rhossak lies down to rest, the ground around it sprouts; three of them standing together
  long enough can root a whole new grove. Herds keep well clear of one."
- galled rhossak: "slower and gentler than its seed-bearing kin and carries no seed at all. The galls are edible."

Before this item NONE of it was code: the donor dryads ran the dryad think tree, which walks a tree-less dryad
off the map, and Alpha Memes' own merge-into-pod job only runs for player-owned dryads with a Gauranlen tree.

## What was built

- `RM_Rhossak` / `RM_GalledRhossak` (`src/RimMandrake/Cauldron/Defs/ThingDefs_Races/RM_Rhossak.xml`): plain
  animals (AnimalThingBase, vanilla Animal think tree), in `RM_Cauldron`'s roster (and the frozen
  `RUT_Cauldron` twin) in place of the AM_ rows. Art: his pick B copied in by
  `src/RimMandrake/Utils/art/rhossak_art.py` through the art ledger.
- `RM_CompRhossakGrove` (`src/RimMandrake/Cauldron/Source/RM_CompRhossakGrove.cs`, kernel
  `Kernel/RM_RhossakKernel.cs`): BIND to the nearest twisting thornwood, held there by our existing
  `RM_CompHomeTether` (CreatureBehaviors, now a Cauldron dependency); SPROUT while asleep; ROOT a young
  thornwood when three stand together. Three Mod Settings toggles ("Rhossak groves").

## Defaults taken where the text is silent

- grove tree = `RM_TwistingThornwood` only (the Cauldron's one TreeBase tree); tether radius 10 cells.
- no thornwood on the map -> unbound, a plain wild animal (never leaves the map); tree lost -> rebinds to the next.
- sprout = one seedling (growth 0.05) of the biome's own non-tree wild plants within 2 cells, mean every 3 h asleep.
- root = 3 rhossak (galled excluded), awake, within 4 cells, at least 6 cells from any thornwood (inside the 10-cell tether, so bound kin can reach it), 24 unbroken
  in-game hours -> one thornwood at growth 0.15; all three bind to it; 10-day cooldown; a message on a home map.
- galls = the donor's spawner kept: 40 rhossak meat every 2 days (also when wild).
- food VegetarianRoughAnimal; Wildness 0.75 / 0.5; manhunter-on-damage 1.0 / 0.1; no genders, no breeding
  (single adult life stage, as the donor); trainability None; sounds and dessicated art are vanilla Ideology dryad.

## criteria
- O1 L0: Cauldron DLL builds; cauldron fuzz `rhossak` family green (bind pick vs brute force, rooting count vs an oracle, gates) and proven able to fail; selftest_cauldron 88/88 healthy with the three new rows' breaks red; settings-screen selftest green
- A1 L2: `rhossak` chain, `rhossak_binds_to_thornwood`: a rhossak and a galled rhossak spawned 7 cells from a thornwood read "Bound to twisting thornwood" 600 ticks later
- A2 L2: `rhossak` chain, `rhossak_stays_by_its_tree`: both are within 14 cells of the tree 5000 ticks later
- A3 L2: `rhossak` chain, `rhossak_bind_off_unbinds`: with rhossakBindEnabled off the bind line is gone
- A4 L2: on a generated Cauldron map (TEST profile, no Alpha Memes) rhossak and galled rhossak spawn wild, and none has left the map after one in-game day
- A5 L2: a sleeping rhossak sets seedlings beside it over a few in-game hours (not yet scripted)
- A6 L2: three rhossak held together away from thornwood root a young thornwood after 24 h (not yet scripted)
- A7 L2: a galled rhossak drops rhossak meat every 2 days

## Watch out

- `RM_CompHomeTether` only tethers WILD pawns that are idle-wandering; a tamed rhossak stays bound (inspect line)
  but is not pulled home.
- The Cauldron's thornwood is common, so groves mostly root in the 6-10 cell ring of a bound tree or where thornwood is sparse.
- `Cauldron_Rename.xml` and the two UtinniPatches art folds still target the AM_ defs; they match nothing
  without Alpha Memes and can be deleted with the donor.
