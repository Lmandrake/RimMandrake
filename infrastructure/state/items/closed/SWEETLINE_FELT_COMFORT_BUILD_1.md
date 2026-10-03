
## spec
`design/Jawa/worldbuilding/biomes/sweetline_guardian_spec.md` §5 (ruling R12, engine E8), piece 6 of §11.
Split off `SWEETLINE_SCRATCHING_TREE_BUILD_1` (built the rubbing and the felt store).

## criteria
- `StatPart_RM_StuffComfort` appended to `StatDef Comfort` (PatchOperationAdd): +0.10 when the thing's Stuff carries `RM_StuffComfortExtension` (on `RM_SweetlineWool`).
- `ThoughtDef` + `ThoughtWorker` modelled on `ThoughtWorker_HumanLeatherApparel`: +2 while wearing any sweetline-felt apparel, not stacked.
- Each behind a LeaningScrub Mod Setting; a validation bar in `src/RimMandrake/LeaningScrub/validation.py`.
