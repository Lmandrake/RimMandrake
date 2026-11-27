# WB-cause-RIMMANDRAKE-LOAD-EDITED-CANONICAL-SAVE-ONCE-618-LINES-CUT-UNLOADED-20261126-221836

Home: cause:RIMMANDRAKE_LOAD_EDITED_CANONICAL_SAVE_ONCE_618_LINES_CUT_UNLOADED. One member:
`RIMMANDRAKE_STRIP_CORPSE_TWINS_OF_PRUNED_RACES_CHECK_SAID_NONE` (REAL).

- Red: `save_ghost_defs.py check` on R3 read FOUND 282. The 13:03 load log also had 42 `Meat_<race>` lines of the pruned
  races and 37 lines of older deletions. Total after the load line: 361.
- Tool, test first: `Meat_` is an implied prefix (4f93708d0c). A ghost map `<thing>` is removed whole, and an `<li>` thing
  needs `<def>` as its first child (fde50259f7, 9dc802677f). Before, strip climbed to the whole map `<li>`.
- R3, offline, twice: 324 implied-twin filter rows (fcc062121b), then 37 older-ghost lines (ef4d81a726). R3 is now sha256
  `0a4f2eee6338ad34`, the same in Saves. Backups: `…R3.rws.bak-pre-strip-implied-twins-2026-11-26` beside it, and
  `D:\ClaudeWork\backups\saves_pre_strip_implied_twins_2026-11-26\` on Archmagi. Both plans were rebuilt on the same
  dump capture, and only the pin moved.
- Live: one load of R3 on its 325-mod list on ArchBig at 16:51 PST. Playing at tick 10, 1 map, 12 colonists. Reference
  lines after the load line: 361 before, 0 after. No new kind of error line. The first exception is unchanged and
  pre-existing (`Can't load abstract class RimWorld.Planet.WorldComponent`). Log:
  `D:\ClaudeWork\rimmandrake\scratch\Player.R3_load2_ArchBig_2026-11-26.log` (Archmagi).
- Found and fixed without a ticket: `game_instance.py stop` returned before the game exited, so a `launch` right after
  said "already running" and started nothing. The CLI now waits (9870bee3ca), and its exit stays 0 so that callers keep
  their own escalation to `--force` (df7b3f3cc0, after the fresh reader's finding). The file is FLAGGED.
- Games left: ArchBig and ArchSmall both stopped. ArchBig's ModsConfig is back to the 315-mod list that was found.

Next: nothing. The bundle is done.
