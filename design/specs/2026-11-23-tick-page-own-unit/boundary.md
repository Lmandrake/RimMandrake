# BOUNDARY: the tick builds no page; the page has its own unit, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/maturation_dispatch.py` (`tick`, `_tick`, `main`'s `tick` verb) and the units
`src/RimMandrake/Utils/systemd/rm-maturation-page.service` and `.timer`. Item
`RIMMANDRAKE_SLIM_TICK_MEMORY_PAGE_BUILD_HITS_ONE_GIG_TICK_TOOK_FIVE_MIN`. Each promise has a test of its name in
`src/RimMandrake/rimflow/selftest_tick_page_own_unit.py`.

Measured 2026-11-23 in a helper clone, each in its own cgroup: a dry tick peaks at 344 MB in 100 s; the page build
(`maturation_now.py`, phone images included) peaks at 326 MB in 46 s. Until this change an applying tick ran the page
as its child, so both sat in the tick's cgroup together; the live unit read peaks of 642 MB to 1G at its 1G
MemoryMax, swap, and a 5 min 8 s tick (journal 02:15 to 02:31 PST).

## ACCEPTS (the only inputs this is built for)

- **the-shipped-units.** The page unit is installed by copying the two shipped files into `~/.config/systemd/user/`,
  as the dispatch unit is.

## DOES NOT SURVIVE (not handled)

- **a-page-older-than-its-timer.** The page now lags a launch by up to one page run plus 60 s (about 2 min), where it
  was built at the end of the tick that launched. A reader that needs the state at a launch reads the tick's
  `reading.json`.

## PROMISES (each one is owed a test of the same name)

- **applying-tick-starts-no-page-builder.** An applying tick, called as the timed unit calls it (no `--page`), starts
  no `maturation_now.py` process and calls no page builder.
- **hand-tick-page-still-builds.** `tick(..., page=True)` with apply (the hand `tick --apply --page`) still builds the
  page once.
- **page-has-its-own-unit.** The shipped `rm-maturation-page.service` runs `Utils/maturation_now.py` from the dispatch
  clone, its timer fires after each build ends, each limit in it (MemoryMax, TimeoutStartSec) has a comment naming its
  danger beside it, and the shipped dispatch unit's ExecStart passes no `--page`.

## REAL-SIZE CHECK

- **real-size-applying-tick-under-ceiling.** With `--real`: an applying tick whose facts are this repository's real
  gather (its ledger, run records and mods, held in memory as the tick holds them) runs in a cgroup capped at 600 MB
  with no swap, well under the unit's 1G, and ends with exit 0 inside a 20 min hang guard. Only side effects to temp
  folders: its state dir, holds, and the page output.
