## spec
Step 6 of `design/RimStarWars/cold_storage_line_2026-10-26.md` (§4.2). The ledger title's phrase "Full stasis at
every working grade" is WRONG and superseded by the owner's card ruling of 2026-10-26
(`OWNER.jsonl:1793027548999599115`, "Stasis grade → Strength follows grade"): **stasis strength follows the quality
grade** — Wrecked none, Kludged 0.2, Refurbished 0.75, Original full (rot factor on held items = 1 − strength). The
grade also sets capacity, power and flicker (doc §4.2 table).
- Layer 1 (coldstorage): `RM_AncientStasisLocker`, grade-aware when Wrecked Machines is present, plain loot otherwise.
  Sets `CompStorageClimate.StasisStrength` per instance from the grade (hook built by
  `COLDSTORAGE_STASIS_WIRE_GRADE_FACTOR`).
- Layer 2 (RSW skin): `RSW_RakatanStasisCasket` 1x2, `RSW_RakatanStasisVault` 3x3.
- Layer 3 (RUT): vault loot (`RUT_VaultType3_FrozenRakata`) at Wrecked/Kludged + `RUT_StasisHeldProvisions`; ship
  subsystem grant of `RSW_RakatanStasis` research.
Waits: step 1 (done). Owner Q2 is ruled (above); nothing else waits on him.

## verify
- L1: selftest: a Kludged / Refurbished / Original locker gives held items a rot factor of 0.8 / 0.25 / 0.
- L2: live, same food on each grade for one day: rot progress ratios match the table.
