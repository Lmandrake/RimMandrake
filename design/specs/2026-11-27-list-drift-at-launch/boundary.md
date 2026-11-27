# BOUNDARY: the list a launch loads, against modset_builder's last write, Design Version 0.1.0

Code: `src/RimMandrake/Utils/list_journal.py` (all of it); `src/RimMandrake/Utils/modset_builder.py` (`journal` and its
five calls: `repair_game_reset`, `restore_own`, `restore_before`, `--restore-full` and `--apply` in `main`);
`src/RimMandrake/Utils/game_instance.py` (`launch`, `mods_config`, `list_line`).
Item: `RIMMANDRAKE_TRACE_ARCHSMALL_TIER_SWAP_UNDONE_BEFORE_LAUNCH`, written 2026-11-27. On 2026-11-26 a tier write to
ArchSmall's list at 03:47 PST was gone by the 04:08 launch: an older list was back, with an old mtime (a copy that kept
its source's mtime). The writer is unknown. A run recorded a tier that the game did not load.
Each promise has a test of its name in `src/RimMandrake/Utils/selftest_list_drift_at_launch.py`, which also runs each
test on a planted fault and fails unless that fault turns it red. This page covers only these parts of the files named.

## ACCEPTS (the only inputs this is built for)

- **a-modsconfig-file.** The game's own `ModsConfig.xml`: ArchBig's LocalLow Config, or `<root>/<letter>/Config` for a
  named game. Any content: a list that is missing or does not parse is a third answer, not a list.
- **the-journal.** `<agent storage>/modset_swaps/list_writes.<letter>.jsonl` (or `RM_LIST_JOURNAL_DIR`), one JSON row per
  line, appended by `list_journal.record` and `launch_line`. A torn or foreign line is skipped.

## DOES NOT SURVIVE (not promised)

- **a-writer-that-is-not-modset-builder.** modlist_swap, modcheck's compose, RimWorld itself and a hand copy are not
  journaled. After one of them, the launch line says LIST CHANGED. That is true: the list is not modset_builder's last
  write. It is not a fault of that writer.
- **naming-the-unknown-writer.** The line names the time window and the copy with the same bytes and mtime, when one is
  under the journal folder. It does not name the process that wrote the list.
- **a-launch-that-is-refused.** Nothing here refuses a launch or writes a list. A run that ignores the line still loads
  the changed list.
- **a-selftest-list-outside-the-temp-folder.** A list under the system temp folder is never journaled unless
  `RM_LIST_JOURNAL_DIR` names a folder, so a selftest does not write the real journal. A test that puts its list
  elsewhere and names no folder writes rows (with its own list path, which no real list matches).

## PROMISES (each one is owed a test of the same name)

- **a-launch-on-modset-builders-last-write-names-its-tier-and-owner.** When the list is byte for byte the last journaled
  write of that file, the line reads `= tier <tier>, written by <owner> at <time>` (or `= the <act> of modset_builder`
  for a restore).
- **a-launch-after-another-writer-says-list-changed-with-md5-mtime-and-the-copy.** When the list differs from the last
  journaled write, the line starts `LIST CHANGED`, names that write (tier, md5, owner, time) and the list it loads (md5,
  mod count, mtime), and names each `ModsConfig*.xml` under the journal folder with the same bytes and the same mtime.
- **no-write-on-record-is-its-own-answer.** A game whose journal holds no write of that file reads `no modset_builder
  write of it on record`, never a match or a change.
- **a-list-or-journal-that-cannot-be-read-says-could-not-look.** A missing or unparsable list, or a journal that cannot
  be read, reads `COULD NOT LOOK` with the cause, never a match, a change or "no write on record".
- **every-verified-live-write-of-modset-builder-is-journaled-and-a-temp-list-is-not.** apply, restore, restore-own,
  repair-reset and restore-full of the live list each add one row with the act, tier, owner and md5 of what was
  written; the same functions on any other path add none.
- **game-instance-launch-carries-the-line-on-both-games.** `game_instance.launch` returns its own text followed by the
  list line, for ArchBig and for a named game, and the line is computed before the game is started.
- **the-line-never-fails-a-launch.** When the line cannot be made (a broken journal folder, a raising reader), the
  launch still starts the game and its text reads `COULD NOT LOOK`.

Later lists beside this page: `polish.md` (none yet).
