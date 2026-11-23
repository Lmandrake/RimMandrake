# Polish: the disk sense (a record; nobody takes lines from it)

- `seat_dirt.classify` runs one `git cat-file` per dirty safe-class path (`replaces_nothing_newer`, `on_origin`,
  `closed_copy`). One `git cat-file --batch-check` per clone would cut the forks. Not a fix: at 4 dirty paths the
  seat clone's reading took 1.7 s at load 45 on 2026-11-22.
