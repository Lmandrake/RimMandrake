
## spec
`design/Jawa/worldbuilding/biomes/sweetline_guardian_spec.md` §8 (ruling R13, engine E10), piece 7 of §11.
Split off `SWEETLINE_SCRATCHING_TREE_BUILD_1`.

## criteria
- `GenStepDef RM_SweetlineTrees` (order 910) in `RM_LeaningScrub`'s `extraGenSteps`; the frozen `RUT_` twin untouched.
- Chance `sweetlineTreeMapChance` (default 25%, labelled "affects newly generated maps; not worldgen"); 1 tree, 2 at 30%; cell rules per §8 (40 cells apart, 15 from the edge); give up silently after 200 tries.
- Off when "Named sweetline trees" is off or the chance is 0; a validation bar.
