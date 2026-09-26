# DIVING_STALE_DEPLOYED_FILES_1 — the retired pawn-dive is still live in the game folder

Three files were deleted from `src/RimMandrake/DivingInteraction/` when the shore pawn-dive
mechanism was retired under the owner's SHIP-ONLY ruling. **They were never pruned from the
deployed mod, and the deployed mod is what RimWorld loads.**

```
C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\DivingInteraction\Patches\RM_ScaldDiveEligibleTerrain.xml     2026-09-24
C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\DivingInteraction\Defs\JobDefs\RM_DivingJobDefs.xml           2026-09-11
C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\DivingInteraction\Defs\ThoughtDefs\RM_DivingThoughtDefs.xml   2026-09-11
```

Found 2026-09-26 by the `deploy_custom_mods.py` **plan** for `DivingInteraction`, which lists
them as `-  (in game, not in repo; kept — use --prune to delete, or --pull to rescue)`.

🔑 **Deleting a file from `src/` does not remove it from the game folder.** Plain `--apply`
only writes and overwrites; removal needs `--prune`. Nothing in the retirement pass said so,
so "the mechanism is deleted" was true of the repo and false of the running game for two days.

## spec

- The patch is still tagging `RUT_ScaldWaterShallow`, `RUT_ScaldWaterMovingShallow` and
  `RUT_ScaldWaterMovingChestDeep` with the retired `RM_DiveEligible` tag.
- `RM_DivingJobDefs.xml` declares JobDefs whose `driverClass` types were deleted from
  `RimMandrake.DivingInteraction.dll`. ⚠️ **UNMEASURED:** whether that produces a def-load
  error on the next cold load or merely dead defs. Check `Player.log` on the next load
  rather than reasoning about it.
- Decide per file: prune, or rescue with `--pull` if any of it should come back.

## Watch out

- ⛔ `--prune` deletes from a live install. Do not run it blind — read the plan first and name
  what goes.
- The same drift may exist in other mods that have had content deleted. A `--mod`-less plan
  run would show it; do that before assuming this is the only one.

## verify

- `python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod DivingInteraction` shows no `-`
  lines.
- Next cold load's `Player.log` carries no error naming `RM_DiveEligible`, the diving JobDefs
  or the diving ThoughtDefs.

## caused by

`SEA_FLOOR_AND_CATCH_PASS_1` — whose correction note said the patch file "does not exist and
never did". It did, and it still does where it counts. Re-corrected there 2026-09-26.
