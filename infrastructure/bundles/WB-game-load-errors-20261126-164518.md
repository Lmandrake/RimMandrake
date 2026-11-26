# WB-game-load-errors-20261126-164518: onboarding run of game:load-errors

State: step A done (2026-11-26 PST). Every member sorted; no member kept, so steps B and C have no work.

## Step A, the reality sort (measured 2026-11-26)

| member | class | evidence |
|---|---|---|
| CONFIGERRORS_FIX_FIVE_MORE_ON_LATEST_LOAD | done already by b4d133211d | `selftest_config_errors_five.py` PASS (424 HediffDefs); `selftest_researchretag.py` all pass; ArchBig Mods copies of RM_Dehydration.xml, RSW_BeskarNeverReforged.xml, RUT_ResearchTabAssign.xml byte-identical to src; deployed RimMandrakeColdStorage.dll equals src (RSW_BrinedCoodlerRoe loads); no file under the deployed StructureInjectionsSW names ZBiome_Grasslands. A1 "the game folder holds these trees" holds. |
| CONFIGERRORS_FIX_THREE_LEFTOVER_CLASSES | done already by bcd343e3df | `selftest_config_errors_leftover.py`: 3525 ThingDefs, 0 findings; ArchBig copies of RM_ThreeHeightFlora.xml and the KotOR Bowcaster weapon file byte-identical to src. A1 holds. |
| LOVIN_LOGSPAM_DIAGNOSE_IN_PLAY_EVICTIONS | done already by 2dd007742f (+ proof fix 19194036d9) | `selftest_mandrakepatches.py` all pass; `selftest_log_rise_census.py` ALL PASS; deployed RimMandrakePatches.dll equals src (LogSpamOff ships). Live A2 needs Intimacy and Mood Chain Reaction loaded, a full-list configuration; full-list testing is retired until integration. |
| PLANT_PRINT_FIX_NRE_ON_SAVE_LOAD | not worth the touch | One sighting (2026-11-03, one save load, cause unknown); effect is a one-way plant pop-in until the section re-meshes. `grep -c "off the main thread"` finds 11 in the original log and 0 in all 146 Player logs under D:\ClaudeWork\rimmandrake modified since 2026-11-04. Not serious and not seen again, so no hunt opens. |
| TICKER_NEVER_FIRES_FIX_1 | done already by 29c4ac1a8e (the ledger named 40553e46e9, which is not on origin/main) | `lint_ticker_compat.py` 0 ERROR today (was 5); A1, A2, A3, A5 passed live 2026-10-09/10; A4's target type RM_MapComponent_DryRooms was deleted (WETBULB_FOLD_INTO_HEAT_1), so A4 cannot be run as written; RM_CompDryFieldEmitter still runs from CompTick on the rare cadence. |

Counts: done already 4, not worth the touch 1, kept 0.

## Next
Nothing. The run ends after the closes and the drop.

## Pipeline fixes made in this run
- f96e4e6094: `rimflow close --evidence` on a built item whose criteria are all L0 refused as a second done and wrote
  nothing (seen on TICKER_NEVER_FIRES_FIX_1 and LOVIN_LOGSPAM_DIAGNOSE_IN_PLAY_EVICTIONS). Now the pass is written alone.
  Test: `selftest_close_gate.py` case EVIDENCE_FINISHES, red on the parent, green on the fix. Owed: one fresh reader of
  that cli.py hunk (this run may start no helper).
- c601231448: `selftest_cli.py` 59/62 on origin/main (claim preflight E12 refused three probe fixtures with no refs
  line); fixtures now carry `none: a probe fixture`; 62/62.

State: finished. Nothing is next for this bundle.
