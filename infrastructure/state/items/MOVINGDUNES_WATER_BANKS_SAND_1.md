# MOVINGDUNES_WATER_BANKS_SAND_1 — sand that hops onto water banks on the shore instead of vanishing

Found by the MovingDunes fuzz oracle (Transient/validation_movingdunes_20261007.md, 2026-10-07): a slab whose hop landed on a cell that cannot hold sand (water, space: the terrain's `holdSnowOrSand`) was refused by the landing and deleted, so a dune field beside a lake slowly lost mass to it and influx never replaced it.

## owner ruling (card, 2026-10-07)

Decision taken by question card: water banks the sand (a non-holding cell banks like a wall: the slab lands on the last cell before it).

## spec

1. `RM_DuneKernel.RunTransport`: a hop that meets a cell that cannot hold sand lands on the previous cell, exactly like a wall's lee (`IDuneField.CanHoldSand`; `MapDuneField` reads the terrain's `holdSnowOrSand`, the edifice half stays `BlocksSand`).
2. The batch ledger counts these (`Batch.WaterBanked`) and splits depth-cap overflow out of `DepositError` (`Batch.CapOverflow`), so `DepositError` is only the boundary nudge.
3. The fuzz mass invariant becomes: total change == -Lost - CapOverflow + DepositError - ErodeError + InPlaceDelta, with DepositError exactly 0 with the nudge off; no slab ever lands on water; a lake-shore unit conserves mass exactly and grows the shore.

## criteria

- A1 (L0): `selftest_movingdunes_fuzz.py` passes, reaches water banks, and fails when the shore line is deleted from the kernel (checked: 5/5 seeds red).
- A2 (L2): on a dune map with a lake downwind, sand piles on the shore and the lake cells stay at depth 0 over a storm (`MovingDunesProof` or a sand-grid read).

## NEXT

Live: load a dune-field map with water leeward and read the shore cells' depth before and after a forced storm.
