# Dirty clone triage 2026-10-11

Method: compared every modified/untracked file and every unlanded commit against RimMandrake origin/main `ffb721531` (read from /home/mandrake/rm/bench). REDUNDANT = byte-identical at origin, generated (fixtures.json test counter, committed DLL/.srchash rebuilt from identical or superseded .cs, tool-written ModsConfig.before-tier-* backup), jsonl lines all present at origin, or commit patch-equivalent (git cherry) / HEAD an ancestor of origin/main. No process cwd in any clone; newest file mtime > 1600 min everywhere.

| clone | size MB | verdict | reason |
|---|---|---|---|
| .seat-tmp/clone3 | 13406 | DELETED | 6 .cs null-guard edits already at origin (JacketDisturbanceRadius dup, EnsureGrid, fluid==null, records!=null, waterBands!=null) or superseded (LuminousPigment FinishProject code no longer exists); DLLs regenerable; code_review jsonl lines at origin |
| .seat-tmp/clone4 | 13406 | DELETED | jsonl lines at origin; untracked md identical at origin |
| .seat-tmp/jawatow_clone | 13635 | DELETED | fixtures.json counter; 1 commit patch-equivalent |
| .seat-tmp/remark_clone | 12227 | DELETED | fixtures.json; 2 commits patch-equivalent |
| .seat-tmp/selftest_clone | 13631 | DELETED | fixtures.json; 1 commit patch-equivalent |
| .seat-tmp/sitting3_clone | 13484 | DELETED | 26 untracked Transient files identical at origin; FOUNDRY.jsonl lines at origin; 2 commits patch-equivalent; only ModsConfig.before-tier-acc_20261009c.xml absent at origin (modset_builder backup; 21 siblings tracked) - copy saved in rescued/sitting3_clone/ |
| .seat-tmp/validators_clone | 13634 | DELETED | fixtures.json; 1 commit patch-equivalent |
| .seat-tmp/harmony_tail_clone | 13406 | DELETED | clean; main tip efe67213 is identical to clone2 main (kept, bundled); work = 1 patch-equivalent commit |
| .seat-tmp/graffiti_rebuild | 13447 | DELETED | clean, no unlanded commits |
| .seat-tmp/ledger_clone | 13457 | DELETED | clean; 2 commits patch-equivalent |
| .seat-tmp/stillsand_clone | 7089 | DELETED | clean; its one unlanded commit: md identical at origin, item file moved to items/closed, ledger line present at origin. (Its object db had missing objects for 4 stale remote refs; fetch could not work.) |
| .seat-tmp/clone_di | 7054 | DELETED | HEAD (work) is ancestor of origin/main; DivingInteraction .cs identical, DLL regenerable; main = efe67213, same as clone2 main |
| rm/stv | 16843 | DELETED | fixtures.json; lint_stillsand_defs.py identical at origin; main already at origin |
| .seat-tmp/clone2 | 13581 | KEPT | branch `main` (tip efe67213ab, 2026-10-08 FOUNDRY crash history) holds 66 commits since merge-base e0c6f6dd4 that are NOT patch-equivalent to origin; 12 text files (8 item .md, 4 GimmeSomeSlack northstar_matrix .py: det_export, fakegame, oracle, placer) differ from an unchanged origin and ~80 more diverge. Most likely superseded by the 2026-10-10 realign, but unproven. Dirty files in the work tree are all redundant. |

Rescued (/home/mandrake/rm/bench/Transient/weekly_cleaning_2026-10-11/rescued/):
- clone2/clone2_main_unlanded_66_commits.bundle (3.5 MB, `git bundle` of e0c6f6dd4..main; restore with `git fetch <bundle> main:refs/heads/rescued`) - FOUNDRY's pre-realign crash-backup commit history (LongShade, LuminousPigment, GimmeSomeSlack northstar_matrix, EH, MovingDunes, ...) with DLL builds.
- sitting3_clone/ModsConfig.before-tier-acc_20261009c.xml (2 KB) - snapshot of the live mod list taken by modset_builder before an "acc" tier swap on 2026-10-09.

Non-git dirs under /home/mandrake/rm (sizes only, untouched): _foundry_dirty_backup_20261010 23 MB, _foundry_dirty_backup_20261010b 31 MB, aside_20261007 8 MB, scratch 7259 MB, ul_wip_backup 1 MB.

Disk (df -h /): before 509G used / 448G free; after 362G used / 594G free (freed ~147 GB of ext4 contents; the WSL VHD file only shrinks after compaction).
Never touched: rm/bench, rm/foundry, rm/foundry_old_20261011.
Owner decision left: delete clone2 after confirming the 66-commit crash history is superseded (bundle is the safety copy).
