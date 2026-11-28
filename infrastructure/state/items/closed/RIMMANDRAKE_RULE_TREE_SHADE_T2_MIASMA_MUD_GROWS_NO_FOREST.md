# RIMMANDRAKE_RULE_TREE_SHADE_T2_MIASMA_MUD_GROWS_NO_FOREST: the T2 clauses that the live census contradicts

For the Conductor. Design: `design/RimMandrake/tree_shade_model_2026-10-19.md` §6 T2: *"the shaded share of open ground
... is at least 60% in the Greentide and the Miasma. The live census (§2.1) must land within ±10 points of the §2.2
estimate."* §6 also says: if T1–T4 fails after one fix round, fall back to (d), keyed on the map's measured canopy
fraction. The owner, 2026-10-19: *"If we have an excellent tree shade model working, then YES direct sun works the same
everywhere on the day side. If we do not go that route, we may choose to turn it off on tree-heavy maps (this would be an
inferior option)."*

## The evidence

`design/specs/2026-11-26-tree-crowns/canopy_census_2026-11-26.md` (ArchSmall, flat tile 30979, two runs, same numbers):

| Biome | crown-covered | estimate | 0.60 clause | ±10 clause |
|---|---|---|---|---|
| `RM_Greentide` | 0.974 | 0.99 | holds | holds |
| `RM_Miasma` | 0.274 | 0.97 | fails | fails |
| `RM_Webwork` | 0.694 | 0.97 | none | fails |

The Miasma's open ground is mostly `Mud` and `RM_MiasmaSaltCrust`, where its trees do not grow. The estimate placed
plants on every cell with no fertility (its docstring). The crown model shades the ground under its trees: the live
scene `src/RimMandrake/CreatureBehaviors/live_tree_crowns.py` shaded 69 of 69 cells under a veluthar and cleared them
after felling. So the misses are in the estimate, not in the model.

## spec

1. Rule one of: (a) drop the Miasma 0.60 clause and the ±10 clause (they rest on the estimate), so T2 reads "a dense
   forest map is mostly shade" (the Greentide holds it); (b) take fallback (d) as §6 says. Under (d), keyed on canopy
   fraction, the Miasma (0.27) is not a tree-heavy map either, so Direct Sun behaves the same there under both.
2. Log the call with `--per-ruling RIMMANDRAKE_ENACT_CONDUCTOR_MAY_DO_ALL_BUT_FIVE_ACTS --why "<call>; lost: ...; undo: ..."`
   (a looser bar).

## criteria

- The Conductor's ruling is on the ledger, and the design's §6 reading is fixed to match it.

## verify

Acceptance test: none, a ruling (the Conductor's act).
