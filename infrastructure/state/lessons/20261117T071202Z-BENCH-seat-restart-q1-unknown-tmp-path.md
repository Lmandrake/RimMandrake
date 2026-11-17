selftest_seat_restart Q1 (assistant_end quiet) was red on any clone whose seat is unresolved: its TMP dir is .seat-tmp/unknown/..., the UNMEASURED hold texts quote that path, and the test's 'unknown in hold' test matched the path word. It blocked ./publish from a scratch clone under ~/rm/scratch/unknown/. Fixed in the test (strip TMP before matching), published 445c1012a5. Instrument words can collide with path words: match on the hold's own fields, not on free text.
item: RIMMANDRAKE_UPGRADE_DESIGNER_CLEANSE_SIXTY_FOUR_BARS_LOCKED
home: src/RimMandrake/rimflow/selftest_seat_restart.py
