# RIMMANDRAKE_TRACE_ARCHSMALL_TIER_SWAP_UNDONE_BEFORE_LAUNCH

## spec

On 2026-11-26, `modset_builder.py --tier flowworks_list --apply --by BENCH` wrote the 21-mod list (md5 06c06b14) to
`D:\ClaudeWork\rimmandrake\instances\b\Config\ModsConfig.xml` at 03:47 PST, with ArchSmall stopped. ArchSmall launched
at 03:49 and was stopped at 04:06. The 04:08 launch ran 26 mods (`jawa/running_mods`). At 04:22 the live list was the
older list again: md5 a1069dfb, mtime 00:30:14. A run that swaps a tier and then tests can record a tier that the game
did not load (the jetty run's row, corrected at fd65b5d3b6). A repeat swap at 04:28 held over a stop and a relaunch.

What the trace ruled out (run of 2026-11-27, notes on this item):
- a modset_builder restore or repair of BENCH.b: the 03:47 marker still stood at 04:22, and its before-copy had mtime
  02:24, not 00:30:14;
- `wrapup.py restore_at_release`: its only restore ran at 03:31 PST, before the swap;
- an agent command: in every session transcript, only the jetty run touched ArchSmall's list from 03:47 to 04:22, and
  none of its commands writes ModsConfig;
- `game_instance.py prepare` and `launch`: they write the list only when it is missing, with a fresh mtime;
- a RimWorld crash reset: it writes Core and the DLC only, with a fresh mtime.
- Telemetry holds no modset_builder `modlist` event near 00:30.

The writer is still unknown. Its sign is a copy that keeps the source's mtime (`shutil.copy2`, or a Windows copy).

The work:
1. Make the next occurrence visible at the moment it matters: `game_instance.py launch` names the list that the load
   reads and says whether it is the list that modset_builder wrote last for that game. When it is not, the launch line
   says so, with the md5, the mtime and any known copy that holds the same bytes. modset_builder journals each write
   per game, so the window between the write and the launch is on record.
2. When ArchSmall is free, run the live acceptance test below.

## verify

Offline: `python3 src/RimMandrake/Utils/selftest_list_drift_at_launch.py` (the promises of
`design/specs/2026-11-27-list-drift-at-launch/boundary.md`).

Live (needs a free ArchSmall): on a stopped ArchSmall, `modset_builder.py --tier flowworks_list --apply --by <unique
owner>`, launch, stop, relaunch. After each launch, `jawa/running_mods` equals the tier's 21 packageIds, and the launch
line reads `= tier flowworks_list`.

## criteria

- A launch after a list change that modset_builder did not make prints the change in its result line, with md5, mtime
  and the copy that holds the same bytes when one is known.
- A launch on the list that modset_builder wrote last says so, with the tier and the owner.
- No launch is refused for this: the line informs, the load goes on.
- The live repro on ArchSmall reads the tier's 21 mods after each of two launches, or catches the drift by name.

## refs

file: src/RimMandrake/Utils/game_instance.py
file: src/RimMandrake/Utils/modset_builder.py
