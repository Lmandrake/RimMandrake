# Polish: the disk sense (a record; nobody takes lines from it)

- `scratch_clone.pool_reading` walks every pool clone with `find` on each pass (3.8 s for 15 clones, 105 GB, at
  4:20 PM PST 2026-11-22; 7.3 s on a cold cache). A per-clone size cache keyed on the clone's `.git/index` mtime would
  cut it. Not a fix yet: with the tidy out, the family read in about 4 s, and no overrun of the reads alone is on record.
