# PROPERTY_CLAIM_ERASE_API_1 — RimProperty: a call that wipes other parties' claims

Caused by `SUMP_BEDAZZLE_SITTING_1` (turn 2). Consumer: `SUMP_SINKING_RITE_BUILD_1`. Free tier,
`mandrake.rm.property` (`src/RimMandrake/RimProperty/`). Design:
`design/Jawa/worldbuilding/biomes/sump_bedazzle_review_2026-10-01.md` §6 (Rite A, effect 3) and §9.

Owner, typed, turn 2: *"erases ownership as part of RimProperty (perhaps of something you still
keep...)"*; widened at the offerings card: *"I like Vault forgets, but it should be true about almost
anything you own"*.

## spec

`GameComponent_PropertyLedger` exposes `TryGetRecords` and `RecordClaim` only; there is no remove or
clear call (MEASURED, `GameComponent_PropertyLedger.cs`). Add the smallest API the rite needs, in this
mod, with no rite knowledge in it:

1. `int ClearForeignClaims(Thing thing, ClaimantRef keep)`: removes every stored `ClaimRecord` on
   `thing` whose claimant is not `keep` (the colony); returns the count removed. Covers every stored
   basis (`Stolen`, `Purchased`, `ClaimFeePaid`, `Gifted`, `Inherited`, `Looted`,
   `BattleLootOrigin`). `Territorial` and `Situational` are computed live and are untouched by design.
2. `List<(Thing, ClaimantRef, ClaimBasis)> ClearForeignClaimsWhere(Func<Thing,bool> filter, ClaimantRef keep)`:
   the same over every Thing the ledger holds records for, returning what was wiped (so a caller can
   write the letter that names each item and whose claim went).
3. `FactionRecord` (suspicion against pawns) is NOT touched. The owner has not ruled that the faction
   forgets the thief; that stays a separate decision.
4. Save-safe: records removed are gone from `ExposeData`'s next write; a Thing whose list empties drops
   its entry.
5. No Mod Settings change of its own (this is an API; the rite's settings decide when it is called).

## criteria

- Deterministic state check (functional script, `src/RimMandrake/RimProperty/validation.py`): on a
  quicktest map, record a `Stolen` claim by faction X and a `BattleLootOrigin` claim by faction Y on one
  item, plus a colony `Purchased` claim; call `ClearForeignClaims(item, colony)` through a debug
  `[Tool]`; `TryGetRecords` then returns exactly one record, the colony's, and the call returned 2.
- The bulk call over three items with mixed claimants returns the wiped list with the right count and
  leaves every colony record in place; a `FactionRecord` suspicion entry set before the call reads
  unchanged after it.
- Save, reload: the wiped records stay wiped.
