# BOUNDARY: a visit's wait for an Arch game names SteveDesktop's two games, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/maturation_dispatch.py` (`steve_takes`, `steve_feed_off`, and the `driver_busy` and `bridge_held` lines of
`decide_ingame`), and `src/RimMandrake/rimflow/maturation.py` (`steve_mod_off`, and the "Where it runs" paragraph of
`ingame_brief_text`).
Item: `RIMMANDRAKE_SEND_MOD_VISITS_TO_STEVEDESKTOP_TICK_SEES_TWO_OF_FOUR_GAMES`, written Mon 2026-11-23. Each promise
has a test of its name in `src/RimMandrake/rimflow/selftest_tick_names_steve_games.py`, which also runs on four planted
faults (`--mutants`) and fails unless each goes red. This page covers only these parts of the file; the rest has its own
pages.

## The failure this guards

- **Measured 2026-11-23, 6:29 AM PST.** `./pipe why ExplosiveKnockback` read "no game is free: ArchBig: ...; ArchSmall:
  ..." for in-game visit 4. It named two of the four games. The Conductor read it as "the tick does not see Steve1 and
  Steve2" and filed the item. The truth: SteveDesktop could take none of the 56 checks, because none carries a testq
  block (`testq_blocks.py derive ExplosiveKnockback`: 54 need the proof build or a modcheck chain, 2 need the full
  list). The line must say that, so a reader does not hunt a routing defect that is not there, and sees the one that is.

## ACCEPTS (the only inputs this is built for)

- **the-visit-facts.** The in-game facts `maturation.add_ingame` builds: `to_run` (the owed checks), `checks`, and
  `testq` (the checks with a testq block).

## DOES NOT SURVIVE (not promised)

- **the-lane-state.** The clause says what the visit feed would send, not whether Steve1 or Steve2 is busy now or the
  lane is paused. Two standing stops are read (next section): the host work switch and testq's fill.stop. The lane's state is `steve_games.json` and the `steve.idle_with_takeable_min` reading.
- **routing.** This clause sends nothing. `testq/visit_feed.py` sends a check with a testq block
  (`design/specs/2026-11-22-steve-idle-takeable/boundary.md`).

## PROMISES (each one is owed a test of the same name)

- **the-wait-names-steve-and-why-it-takes-none.** When a visit waits because no Arch game is free (`bridge_held`) or
  every Arch game is driven (`driver_busy`), and none of its owed checks carries a testq block, the line names
  SteveDesktop (Steve1, Steve2), says it takes none of the checks, and names the command that says why per check.
- **the-wait-names-what-the-feed-sends.** When some owed checks carry a testq block, the line says how many of the owed
  checks the visit feed sends to the lane and how many need a Claude driver on ArchBig or ArchSmall.
- **the-wait-says-why-the-feed-sends-nothing.** When some owed checks carry a testq block, but the host work switch
  puts SteveDesktop on pipeline work only (`host_work_switch.py`) or testq's `fill.stop` stops the visit feed
  (`maturation.steve_mod_off`, the one reading), the line says SteveDesktop takes none of the checks now, names the
  switch or the stop, and says that all of them need a Claude driver on ArchBig or ArchSmall. It never says that the
  feed sends them. Measured 2026-11-25 10:58 PM PST: the line said "the visit feed sends the lane 53 of 65 checks" of
  Explosive Knockback visit 2, while both stops stood; all 53 ran on ArchBig.
- **the-brief-says-why-the-feed-sends-nothing.** The Stage 6 driver's brief (`maturation.ingame_brief_text`) tells it
  to queue the testq checks with `testq.py submit` only when neither stop stands; under either one it names the cause
  and runs every check on Archmagi.
- **could-not-read-the-checks-is-unmeasured.** When the owed checks or their testq blocks could not be read, the clause
  reads UNMEASURED, never "takes none".

Later lists beside this page: `polish.md` (none yet).
