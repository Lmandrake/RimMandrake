/tmp is an 18G tmpfs: mutation-test and blind-read tree copies (/tmp/mut, mut1, sa_mut, bc_copy, ~17G) filled it to 0 free on 2026-11-03; a test that copies a tree to /tmp must delete it on exit and never leave multi-GB copies. Drain: rm -rf idle copies after checking no file touched in 45 min.
home: design/RimMandrake/standing_rulings.md
