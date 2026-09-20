# DESERT_ROUND2_IMPORTS_UNLANDED_1 — wire the landed round-2 imports, port the rest

## what is wrong

Of the owner's round-2 imports at 0.5 weight in the design rosters, **7 of 8
rows in `desert.json` and 3 of 3 rows in `dune_sea_deep_desert.json` were
never wired** into the deployed biome tables.

- `RSW_Stoneback` and `RSW_TruffleMole` already exist as defs (BiomesTeamPort)
  — wiring them is a one-line change each.
- `AA_SandLion`, `AA_GreatDevourer`, `AA_Groundrunner`, `AA_MatureFleshbeast`
  need porting under the 2026-09-20 "port all of them" ruling — no def exists
  for any of the four yet.
- `JOE_Cephalope` was ruled "absorb & retire mod" — no def exists anywhere in
  `src/`.

## why it matters

Half the owner's already-approved round-2 roster is simply missing from the
biomes it was ruled for.

## the work

1. Wire `RSW_Stoneback` 0.5 + `RSW_TruffleMole` 0.5 into RUT_Desert, and
   `RSW_TruffleMole` 0.5 into RUT_ExtremeDesert, now — guard both with
   `MayRequire="mandrake.rsw.swbestiary"`.
2. File the 4 `AA_` ports (`AA_SandLion`, `AA_GreatDevourer`,
   `AA_Groundrunner`, `AA_MatureFleshbeast`) plus the `JOE_Cephalope` absorb as
   **one port batch**, with reference closure, following the pattern in
   `BMT_FAUNA_ABSORPTION_1` (`infrastructure/state/items/BMT_FAUNA_ABSORPTION_1.md`).
3. `AA_GreatDevourer` and `AA_MatureFleshbeast` are **PORT BOTH** — see
   ruling below. Not superseded by `SARLACC_HABITAT_BUILD_1`.

## ruling (owner, 2026-09-20)

Owner chose: **PORT BOTH** `AA_GreatDevourer` and `AA_MatureFleshbeast`.
They are NOT superseded by `SARLACC_HABITAT_BUILD_1` — that item does not
replace them. Answered; no card to the owner is needed on this question.
The port itself (all 4 `AA_` creatures + the `JOE_Cephalope` absorb, as one
batch per point 2 above) is still this item's own owed work.

## Watch out

The `AA_` port batch (point 2) is still owed — this ruling only settles
whether `AA_GreatDevourer`/`AA_MatureFleshbeast` are in scope (they are);
it does not do the porting.

## verify

RUT_Desert and RUT_ExtremeDesert's `wildAnimals` lists carry
`RSW_Stoneback`/`RSW_TruffleMole` at the stated weights and guard; a
port-batch item (or an owner card) exists for the remaining 4 `AA_` creatures
+ `JOE_Cephalope`.

## criteria

Every round-2 import the owner already approved is either live in the biome
tables or has a named, filed successor.
