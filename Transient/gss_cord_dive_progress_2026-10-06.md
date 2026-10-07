# GSS cord dive-through — progress 2026-10-06

- started: relaunch after OOM death; no clone, work in bench clone
- planner: AStarDive + dive-aware Plan (DiveSpan); builder: LayDiving, strand DiveA/DiveB, plates on wall/rock faces, BuildOptions.DiveThrough
- selftest 793/793 (738 old + 55 new dive rows)
- census 200 seeds: vanilla bases 221 unroutable (b 11, c-wall 89, c-wall-conduit-elsewhere 121) -> 0 with dive on, 208 dives laid; fuzz 2850 worlds 0
- DLL built clean
