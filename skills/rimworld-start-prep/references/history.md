# History: the measurements, and the lines that were wrong

`SKILL.md` holds the lessons. This file holds dates, measurements and corrected claims (corrected 2026-11-23).

## The load cost and the number of seats

The first version put a cold load at **~23–30 minutes**, and said that five seats shared one working tree, one game
and one install. Since then there are four games and one clone for each writer. `skills/rimworld-load-round/SKILL.md`
§0 holds the load times.

## RimSort's sort: `loadBottom` and `loadAfter`

Three claims in turn were wrong:

1. An early version of this skill: "loadBottom is a *stronger* constraint that defeats loadAfter". An early
   `rimworld-modding`: "loadBottom is only a hint and creates no edge". Both were corrected on 2026-08-19 from RimSort's
   sort code.
2. The text of 2026-08-19 to 2026-11-23: the tier split silently DELETES every `loadAfter` edge that crosses a tier
   boundary, and "the genuinely broken pairing is `loadBottom` + `loadBefore` a non-bottom mod (and its mirror,
   `loadTop` + `loadAfter`): tier order wins, the rule vanishes, nothing is logged". That text read the intersection
   `full_graph.get(mod_id, set()) & tier_mods` and missed the spread before it. `_collect_tier_three_mods` adds the
   reverse dependencies of each bottom mod, and `_collect_tier_mods` adds the dependencies of each top mod
   (`app/controllers/sort_controller.py`).
3. The same text: the tie-break "falls out of graph traversal order and incidental input ordering". `do_topo_sort`
   (`app/sort/topo_sort.py`) sorts each topological level by the lower-case name of the mod.

Measured 2026-11-23: the tier code of RimSort v1.13.1 ran on 20,000 random lists of 8 mods with random edges, bottom
mods and top mods. 0 lists had a violated edge. The same run with the spread removed (the planted fault) had 13,743.
The installed version is v1.13.1 (`RimSort.log`, 2026-10-01). The four sort files on RimSort's main branch were
byte-identical on 2026-11-23. The current release then was v1.17.4. The code of 2026-08-19 was not run.

On 2026-08-13, six of our thirteen User Rules carried both `loadBottom` and `loadAfter`. On 2026-11-23, one of the 14
User Rules sets `loadBottom` to true: `mandrake.rm.rimdefdump`.

Also read in v1.13.1 on 2026-11-23: the Save path is `_do_save`; the Troubleshooting import and clear-mods actions
(`controllers/troubleshooting_controller.py`) and the missing-file case (`controllers/metadata_controller.py`) also
write; `_delete_game_configs` in the first of those files deletes the config files; `closeEvent` asks nothing; the Run
button asks "Save and Run" or "Run Anyway"; the watchdog schedules the mod folders and the `.acf` files. A save to a
rules database with no path logs a warning and returns (`_do_update_rules_database`).

Settings on 2026-11-23: `watchdog_toggle` true, `sorting_algorithm` Topological,
`use_moddependencies_as_loadTheseBefore` false, Community Rules from a configured git repository, databases updated at
startup. Both folder paths were correct.

## RimWorld and `ModsConfig.xml`

This project documented the rewrite on exit as settled for a long time, and it was backwards. **Measured 2026-08-13:**
at game exit the last write of `Player.log` was **10:04:55**, and the mtime of `ModsConfig.xml` was **10:01**, *older
than the exit*. The same file then changed at **16:41:39 with no game running at all**. A second reading of that day
is in `design/Jawa/mods/forbidden_mods.md`.

The text until 2026-11-23 named the mod menu as "the only trigger", and named a seat and the owner as "the only
writers". The game source (read with RimSage on 2026-11-23) has more cases. `SKILL.md` §3 lists them.
`ModLister.RebuildModList` collects each "Deactivating" line and logs it only with `Prefs.LogVerbose`. So the old
sentence "RimWorld complains at launch" was wrong.

## Counts of the list

- The fix of the `packageId` regex alone took one census from dozens of "missing" mods down to one.
- **Measured 2026-08-15:** the file had **12 lines** and 580 `<li>` elements for 575 active mods. `grep -c` returned
  **6**. `grep -o '<li>' | wc -l` returned **580**, an overcount of exactly the **5 `knownExpansions`**.
- Until 2026-08-21, step 7 of §5 said that `grep -c` over-counted by 5 (`grep -o … | wc -l` does that). That
  contradicted trap 3 in the same file. The literals that once sat in step 7 went 12 mods stale.
- **Measured 2026-11-23:** the file had 327 lines and 315 active mods. Both greps returned 320, so `grep -c` was not
  6. The layout depends on the program that wrote the file.

## A packageId rename (2026-08-31)

Measured 2026-08-31, FOUNDRY, `RENAME_VERIFY_WINDOW_1`. The item holds the counts of dead ids in each saved list.

## A list-merge dedupe (2026-09-08)

`MOD_CONSOLIDATION_SPRINT_1`: a first-occurrence dedupe dropped the load-last patch catch-alls to mid-order (582 → 188
in position) and aborted the whole 590-mod load.

## The build stamp (2026-08-15)

Measured 2026-08-15: `Version.txt` read `1.6.4871 rev590`. The DefDump manifest and all six saves, each written by the
engine, read `rev591`. On 2026-11-23 `Version.txt` still read `rev590`, and the three newest manifests read `rev591`.
