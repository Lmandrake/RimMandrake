An auto-filer that writes to a fixed item id must check that the id is not dropped or superseded before it writes: when a sort retires the id, the ledger refuses the write, the timer exits 1, and TIMER_FAILED rings for a sweep that worked (deadman arms LIVE_RESTORE_UNITS and LIVE_RESTORE_OPS_WATCH, 2026-11-25 and 2026-11-26; fixed by arm_id at 92a02c2a75).
item: OPS_TIMER_REPAIR_PRXC_XKGA
home: design/specs/2026-11-19-one-fault-one-ticket/boundary.md
