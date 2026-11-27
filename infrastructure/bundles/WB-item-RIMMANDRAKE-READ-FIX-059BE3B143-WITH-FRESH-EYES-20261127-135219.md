# WB-item-RIMMANDRAKE-READ-FIX-059BE3B143-WITH-FRESH-EYES-20261127-135219

- RIMMANDRAKE_READ_FIX_059BE3B143_WITH_FRESH_EYES: REAL, done. Fresh read of 059be3b143 against
  design/specs/2026-11-27-canary-plant-only-cell/boundary.md.
  - selftest_canary.py: Problem (promise-untested, plant-only-cell-when-no-bare-cell): the fake destroy_batch kept
    plants whatever categories the canary sent. Fixed at 3dacd31cba; red on planted categories="Item,Plant" and on
    dropped categories, green on the real code. FLAGGED (no third read).
  - boundary_check.py, selftest_reuse.py: nothing significant; read-clean at 3dacd31cba.
  - Review record landed at a91334e3e7. Outcome check `fresh_reader.py holds ...` exits 0.
