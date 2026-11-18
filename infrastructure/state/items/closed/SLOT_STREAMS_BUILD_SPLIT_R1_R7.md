# SLOT_STREAMS_BUILD_SPLIT_R1_R7

## spec
Split each seat's allocator N (src/RimMandrake/Utils/slot_allocator.py, rules in slot_rules.json) across the
work streams R1-R7 of design/RimMandrake/work_allocation_framework_2026-10-26.md, as data in slot_rules.json,
and write the split into streams/allocation.json so the RimPulse "Builder slots" tile stops showing hollow.
Predecessor SLOT_ALLOCATOR_BUILD_RULES_FILE (a8725799ee) built the total (R8 fit) and the per-seat N only.

## verify
A selftest in selftest_slot_allocator.py: the stream counts sum to the seat's N for every mode, red before, green after.
