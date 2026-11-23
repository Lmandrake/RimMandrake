# GimmeSomeSlack 0.1.1 in-game visit 2 — polish list (a record; nobody takes lines from it)

- sc_walk: the test table's `observes` text names a 20 ms per-rewire frame time, a master off/on step and heap and texture MB
  at the end; gss_playtest_runner.py's journal records none of them by name (the run's verdict is cords, soak, ui and
  save_reload_b). Heap was read by hand for the record (process working set); texture MB has no tool. The criterion text
  claims more than the runner reads.
