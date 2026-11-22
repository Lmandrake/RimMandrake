# RIMMANDRAKE_OPT_DRAWN_GIANTS_INTO_HUGETHINGS_SWEETLINE_FIRST

Filed 2026-11-22 by the HugeThings ticket sweep (`RIMMANDRAKE_SWEEP_HUGETHINGS_TICKETS_MERGE_TO_MODERN_BUILD_THE_VALUABLE`).
Sweep record: `D:\ClaudeWork\rimmandrake\conductor\ticket_sweep_20261122\HugeThings.md`.

**Version: next, for HugeThings.** The first version's plant bars are about the giants that opt in (TheRot's
`RM_Nogtyl`). Opting more plants in is an extension, and the work is in the mods that own those plants. For the owning
mod it is a Problem: he met it live. `RM_SweetlineTree` belongs to LeaningScrub, which he holds
(`src/RimMandrake/rimflow/mod_owner_hold.json`), so its def edit waits for that hold to lift.

## spec

HugeThings gives a plant a click-anywhere picture and a solid trunk only when the plant opts in with
`RM_HugePlantExtension`. TheRot's eight giants opt in (`src/RimMandrake/TheRot/Patches/RotGiants_HugeFootprint.xml`).
`RM_SweetlineTree` (`src/RimMandrake/LeaningScrub/Defs/ThingDefs_Plants/RM_SweetlineTree.xml`, drawn 12.3 to 16 cells)
does not, so it holds one cell: on 2026-11-03 three bridge clicks on its own cell (125,125) selected a Tellurox shell and
a Vokkun pillar, never the tree.

1. Census every plant that we draw huge (draw size well over one cell), with `measure`, not a scan.
2. Measure each one's ground-contact footprint (`src/RimMandrake/HugeThings/measure_huge_plant_masks.py`).
3. Opt each one in, in its own mod, including trunks under `RM_Canopy`. `RM_SweetlineTree` first, when LeaningScrub's hold
   lifts.

## Acceptance test

Offline (watched RED on 2026-11-22, exit 1):
`grep -q "HugePlantExtension" src/RimMandrake/LeaningScrub/Defs/ThingDefs_Plants/RM_SweetlineTree.xml`, or the same
grep over the patch that opts it in. Sanity probe, the same grep on
`src/RimMandrake/TheRot/Patches/RotGiants_HugeFootprint.xml`, exits 0 today, so the grep can see an opt-in. Live: a click
on the tree's drawn crown selects the tree. Expected pass count: 1 offline command per opted-in plant.

## Merged into this ticket (2026-11-22)

| item | class | one line |
|---|---|---|
| `HUGE_TREES_WIRE_INTO_THE_FOOTPRINT_MOD` | KEEP, next | the same work, renamed to the current grammar |

## His words on the merged items (word for word)

- 2026-11-03 (`HUGE_TREES_WIRE_INTO_THE_FOOTPRINT_MOD`): "Oh wow... that is well below, and there is some kind of
  tellurox shell plate on the same square. Yes, I did eventually get there by clicking where the tellurox shell is,
  cycling through."
