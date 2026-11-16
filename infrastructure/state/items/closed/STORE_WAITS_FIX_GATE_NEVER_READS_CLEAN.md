## spec
`relentless_block.py diff` counts a store row `blocked` with a `wait` and no ledger block as a disagreement. Reading of 2026-11-06: 19 of 216 disagree and all 19 are `blocked+wait` (the kept candidates of `relentless_attrib`, released by evidence, never by the ledger). While any such wait stands `ready` cannot say READY, so step 2 of RIMFLOW_FIX_BLOCKS_LIFT_ON_CLOSE (deleting the store's status field) never opens, however long the nightly `rm-store-ledger-diff.timer` runs.

Decide and build one: export each store wait to the ledger as a block (redesign_2026-11-06 §3.4 item 1, "blocked is always read from the ledger"), so the disagreement really ends. Do not just subtract waits from the count: that would turn the gate green while the store still holds a second status.

Done when: a store wait shows as a ledger block in `rimflow show`, and a selftest proves `diff` reads 0 on a world holding one.
