## verify
- Written by the Producer, Producer weekly re-plan 2026-10-29 (run folder D:\ClaudeWork\rimmandrake\producer\2026-10-29T0507Z_weekly), goal 1 (Producer proved, reliably: its plan order must reach `next`).
- A selftest raises three items in the order C, A, B (filed A, B, C) and `rimflow next --seat` offers C, then A, then B, for both ready items (`priority.rank`) and proposed ones (`cli._claimable`).
- An unraised item still never beats a raised one; the existing raise selftests stay green.
- Stopping point: finish.
