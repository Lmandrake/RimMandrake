# Art ledger vs committed tree — `art.py doctor`, FOUNDRY clone, HEAD, 2026-10-15

Read-only report. Nothing below was reinstalled, deleted or relabelled. Regenerate with
`python3 src/RimMandrake/Utils/art/art.py doctor`.

**12 slots disagree.**

- **9 BENCH ghosts** (FlowWorks doors/excavation, WreckedMachines distillation): the shared ledger says live from the BENCH 10-14 20:40 re-observation; the PNGs exist only uncommitted in `/home/mandrake/rm/bench`. BENCH's to commit or retire — not touched here.
- **1 FOUNDRY install with no file**: `RSW_Aiwha.png`, `install` 2026-10-15 07:28 under an owner ruling; neither tree nor worktree holds it. Needs a look (re-run of the install from the store), not done here.
- **2 TREE_RETIRED** (Etchcap, RM_Wickwood): retired 10-05 into their Graphic_Random folders but still committed (`c7c7b6a59`: no legal move-retire).
- The **18 FlowWorks installs of 10-07** no longer show: the 10-14 re-scan relabelled their slots back to the committed picture, so fold and tree now agree. Their newer renders are in the store; none was owner-kept.

| kind | path | ledger | tree | worktree | last event |
|---|---|---|---|---|---|
| TREE_RETIRED | `src/RimMandrake/Abyss/Textures/RM_Abyss/Things/Plant/Etchcap.png` | None | ef342d8975d2 | ef342d8975d2 | BENCH 2026-10-05T20:38:19-0700 script:src/RimMandrake/Utils/art/artledger.py retire (picture moved into its Graphic_Random folder, Abyss sheet sitting 2) |
| TREE_RETIRED | `src/RimMandrake/Abyss/Textures/RM_Abyss/Things/Plant/RM_Wickwood.png` | None | 79956fefc23e | 79956fefc23e | BENCH 2026-10-05T20:38:19-0700 script:src/RimMandrake/Utils/art/artledger.py retire (picture moved into its Graphic_Random folder, Abyss sheet sitting 2) |
| LIVE_NOT_IN_TREE | `src/RimMandrake/FlowWorks/Textures/Things/Building/FlowWorks/Doors/RM_SecurityGrateDoor_MenuIcon.png` | 40821d7ee76b | None | None | BENCH 2026-10-14T20:40:50-0700 backfill-observed |
| LIVE_NOT_IN_TREE | `src/RimMandrake/FlowWorks/Textures/Things/Building/FlowWorks/Doors/RM_SecurityGrateDoor_Mover.png` | 5d09ebe12153 | None | None | BENCH 2026-10-14T20:40:50-0700 backfill-observed |
| LIVE_NOT_IN_TREE | `src/RimMandrake/FlowWorks/Textures/Things/Building/FlowWorks/Doors/RM_Sluice_MenuIcon.png` | a754705c8785 | None | None | BENCH 2026-10-14T20:40:50-0700 backfill-observed |
| LIVE_NOT_IN_TREE | `src/RimMandrake/FlowWorks/Textures/Things/Building/FlowWorks/Doors/RM_Sluice_Mover.png` | 91cd6cc2e0d6 | None | None | BENCH 2026-10-14T20:40:50-0700 backfill-observed |
| LIVE_NOT_IN_TREE | `src/RimMandrake/FlowWorks/Textures/Things/Building/FlowWorks/Excavation/RM_WallFace_North.png` | 18e48c54fc0b | None | None | BENCH 2026-10-14T20:40:50-0700 backfill-observed |
| LIVE_NOT_IN_TREE | `src/RimMandrake/FlowWorks/Textures/Things/Building/FlowWorks/Excavation/RM_WallFace_Side.png` | 139b1ad78318 | None | None | BENCH 2026-10-14T20:40:50-0700 backfill-observed |
| LIVE_NOT_IN_TREE | `src/RimMandrake/WreckedMachines/Textures/WreckedMachines/Modules/Distillation/Kludged/RM_WM_Distillation.png` | f44fc18ab161 | None | None | BENCH 2026-10-14T20:40:50-0700 backfill-observed |
| LIVE_NOT_IN_TREE | `src/RimMandrake/WreckedMachines/Textures/WreckedMachines/Modules/Distillation/Repaired/RM_WM_Distillation.png` | a75e76a9401b | None | None | BENCH 2026-10-14T20:40:50-0700 backfill-observed |
| LIVE_NOT_IN_TREE | `src/RimMandrake/WreckedMachines/Textures/WreckedMachines/Modules/Distillation/Wrecked/RM_WM_Distillation.png` | 1d458d324de4 | None | None | BENCH 2026-10-14T20:40:50-0700 backfill-observed |
| LIVE_NOT_IN_TREE | `src/RimStarWars/SWBestiary/Textures/swanimals/RSW_Aiwha/RSW_Aiwha.png` | 03b57b24c572 | None | None | FOUNDRY 2026-10-15T07:28:19-0700 install |
