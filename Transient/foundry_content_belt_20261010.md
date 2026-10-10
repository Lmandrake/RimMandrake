# FOUNDRY content belt 2026-10-10

Ran 06:40 to about 07:45 PDT. Offline only; another window held the bridge. Milestones are listed in the order they happened.

## Milestones
- ART_TEXTURE_GAPS_FOLLOWUP_1: reconciled as partial. Installed our own KOTOR small crystal render at `small_dyeable` and deployed it (8cb6848dd). What remains needs the owner: the RM_Braskeen REDO pick and RM_Ismerrow (install A?). The item is now marked `needs owner`.
- SELFTEST_RED_EIGHT_1: all 8 named selftests now pass. Reconciled as complete and recorded as implemented, so the item is done (7d7ef3bef).
- STATUE_ART_EXPANSION_1: the commits were spec work only, so it is reconciled as partial. What remains lives in the child item.
- FLAME_STATUES_MOD_BUILD_1:
  - Step 7, the Helixien link (46b8039f5). ResourceOn was measured with ilspycmd on VEF PipeSystem.dll. A piped statue gives back the fuel it burned. VE's CanBeOn needs fuel in the tank, so a statue needs one first fill.
  - RM_FlameStatuary is retired to a load-only def, because 2 saves hold placed ones. The sun-rite moved to RUT_StatueGrand_Shkaar (106911edd).
  - Off-overlay fix (0f02036f3).
  - The v2 art jobs had failed with bad_job_file. Requeued them as v3 and installed the results with per-def texPaths and flame points measured from the art (ac860da1b).
  - Recorded as implemented with 3 live criteria still owed.
- LONGSHADE_SHADE_EXTRAS_1: closed. Its criteria are met: all 7 child items are filed.
- SCRAPNEST_BIRD_BASE_THEFT_1: set to `needs owner`. It is a decision card.
- TECHPRINT_FACTION_GATING_1:
  - Unblocked, because the owner had already ruled.
  - Each campaign faction now has its own categoryTag. Also added FactionCategoryTags_Compat.xml and the Hutt fence on every held print (ca7015ad9).
  - Blackstar is left open: tagging vanilla Pirate would tag PirateBandBase too.
  - Row assignment is next.
- DIRTY_CODE_REVIEW_STANDING_LOOP_1: marked 3 FlameStatues sources CLEAN.
- SUMP_GASLIGHT_1: noted that a failed surgery roll explains both live scrub results. Live recheck is next.
- STONEBACK_BOKKA_ART_STANDARD_1: the regen finished on 09-26. Old vs new is at `Transient/bokka_old_vs_new_20261010.png`. Set to `needs owner` (30e0590d4).
- CRYPTOFORGE_HARVEST_RETIRE_1: removed the VQE block again, and gen_armoury_patch.py now skips retired donors (8522dda17). Trap: running the generator against today's dump deletes about 790 lines.
- CRACKEDLANDS_FULL_RENAME_1: unblocked. The save gate comes first; noted on the item.
