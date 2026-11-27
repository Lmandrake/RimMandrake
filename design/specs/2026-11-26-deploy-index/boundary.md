# Deploy index: boundary page

Code: `src/RimMandrake/Utils/deploy_index.py`, used by `deploy_custom_mods.py` (compare) and `deploy_def_guard.py`
(`parse_defs`). Tests: `src/RimMandrake/Utils/selftest_deploy_index.py` (offline). Item:
`RIMMANDRAKE_TIME_SLOW_ACTIONS_DEPLOY_CHECK_TOOK_TWO_MINUTES`.

Why: a plan of one mod (`--mod GimmeSomeSlack --instance ArchSmall`) took 147 s on 2026-11-26, load average 21.
`cProfile` of that run: the def guard 133 s (open and parse of 4,645 XML files of the 103 other mods on the Windows
drive: open 34 s, parse 6.5 s, close 8 s; plus the walk of 105 mod trees: scandir 37 s, stat 27 s). The byte compare
of the target mod: 8.6 s. Evidence: `design/specs/2026-11-26-slow-actions/evidence.md`.

The index is DERIVED state. It lives on the Linux drive (`~/.local/state/rimmandrake/deploy_index/index.sqlite`, one
table, key = absolute path of the deployed file). Never in the repo. Delete it at any time: the next check reads
every file and writes it again.

## ACCEPTS

- **a-missing-index.** No file, an empty file or an unreadable file: the check reads every file, as before this page,
  and writes the index. Exit code and plan text do not change.
- **a-full-read-flag.** `--full-read` ignores every index entry for this run, reads every file, and rewrites the
  index from the bytes read. It is the act for a person who doubts the index.
- **a-corrupt-index.** A file that is not a valid database is replaced by a new one (derived state).
- **a-test-index-path.** `RM_DEPLOY_INDEX` names another file (tests).

## DOES NOT SURVIVE (not handled)

- **a-same-size-same-time-edit.** A deployed file whose bytes change while its size and its modified time (in
  nanoseconds) stay the same. Only `--full-read` finds it. A normal write moves the time; `touch -r`, `cp -p` and a
  tool that restores a time do not.
- **a-bit-rot.** A byte that changes on disk with no write. Only `--full-read` finds it.
- **a-source-side.** The index never covers the repo side: the repo file is always read (Linux drive, fast).
- **a-listing-that-hits-ENOMEM.** A folder whose listing fails (ENOMEM under load) is skipped by `xml_files` and
  `inventory`, as before this page: its files are then unseen. Not changed here (row on the slow-actions page).
- **a-listing.** The index does not replace the folder listing: a new or deleted file is found by the listing, as
  before, and costs the listing time (scandir and stat on the Windows drive).

## PROMISES (each one is owed a test of the same name)

- **a-new-size-is-a-difference.** A deployed file that changes size is reported changed (`~`).
- **a-new-time-is-a-difference.** A deployed file that keeps its size and gets a new modified time, and new bytes, is
  reported changed. The check reads that file again.
- **a-deleted-file-is-a-difference.** A deployed file that is deleted is reported new (`+`) when the repo has it; a
  file deleted from the repo is reported gone (`-`).
- **an-unchanged-file-is-not-read.** With a current index, a file whose size and time equal the index is not opened
  on the game side.
- **the-index-holds-only-bytes-that-were-read.** An entry is written only from bytes that were read from the game file
  in that run, with the size and time of the open file. A deploy drops the entry of each file it writes or deletes;
  the verify step reads the file again and records it.
- **a-same-size-different-bytes-is-changed.** An unindexed file of equal size and different bytes is reported changed.
- **the-parse-is-kept-with-its-stat.** The def guard's parse of a game XML file is reused only when size and time
  equal the entry; a changed XML is parsed again and its new defs are the ones that the guard uses.
- **a-folder-that-holds-no-defs-is-not-walked-for-another-mod.** The def guard does not enter Textures, Sounds,
  Assemblies or Languages in the game copy of a mod that is not a target (these and Patches hold 4,019 of 5,330 folders under ArchSmall's
  Mods). Def files under a load root (`Defs/`, `1.6/Defs/`, a LoadFolders entry) are still listed.
- **a-bad-index-never-fails-the-plan.** An index that cannot be opened, read or written never makes the plan fail or
  change its verdict.
