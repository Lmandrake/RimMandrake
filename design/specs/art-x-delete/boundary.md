# BOUNDARY: art deletion on an owner ✕

Code: `src/RimMandrake/Utils/art/artledger.py` (`x_delete`) and `src/RimMandrake/Utils/art/enact.py` (its retry).
The tests are in `src/RimMandrake/Utils/art/selftest_art_x_ban_hardening.py`.

## ACCEPTS

- A picture's SHA named by a stamped owner ✕ in a decisions row. A newer owner keep or a lifted ban from this mark
  refuses the deletion. `enact` checks that removing live files leaves the game with art for each def.

## DOES NOT SURVIVE

- A torn ledger line needs ledger repair before retry. Flush ordering covers process interruption and append failure.
  Power loss and independent writes to the same texture path during the deletion are outside this guarantee.

## PROMISES

- **x-delete-flushes-receipts-before-unlink.** Flush the ban first, then the slot removals, keep releases and purge
  before unlinking any copy. A failed receipt flush leaves the game files and store bytes available for retry.
- **enact-retries-a-recorded-x-delete.** A retry finishes recorded removals that still hold the deleted SHA, even
  with no copy in the store, and reports the affected mod. It preserves replacement bytes and reuses the receipts.
