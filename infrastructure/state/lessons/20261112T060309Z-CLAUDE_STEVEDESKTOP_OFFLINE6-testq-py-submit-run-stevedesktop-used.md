testq.py submit run on SteveDesktop used to write a local queue no dispatcher reads and print pending; since 780f797c48 it forwards to Archmagi's ~/rm/dispatch. A test that disables that forward submits a REAL local job: cancel it (TESTQ_QUEUE=... testq.py cancel).
item: HARNESS_REPAIR_CAUSE_8135787B
