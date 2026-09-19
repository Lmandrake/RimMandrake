# KCSG pawn symbols silently fall back to vanilla Colonist

## what was measured
FOUNDRY bridge wave 2, 2026-09-19, live 622-mod session, throwaway 250x250
`RUT_Desert` map. `jawa/kcsg_place structure RUT_Ashfall_Spire` placed three
times. The shipped layout carries exactly **five** pawn symbols
(`RUT_Symbol_HelixGrunt` x2, `..._HelixHeavy`, `..._HelixSpecialist`,
`..._HelixLeader`). Every placement filled all five cells with a spawned
Human — but the pawn's `kindDef` was the symbol's `pawnKindDef` only
**4 / 3 / 5** times:

| placement | kinds actually present |
|---|---|
| rect 170,170 | Grunt x2, Leader, Specialist, **+1 `Colonist`** |
| rect 20,20    | Heavy, Leader, Grunt, **+2 `Colonist`** |
| rect 20,110   | Grunt x2, Heavy, Specialist, Leader — all 5 correct |

## what it is NOT
- Not a layout bug: the symbol grid, the cell coordinates and the thing
  census (4 specimen cells, 1 console, 1 codes, 3 Tesla, 2 Railgun) are
  byte-identical across all three placements.
- Not a missing def: `PawnKindDef/RUT_Jawa_Helix_Heavy` resolves live, and
  `KCSG.SymbolDef/RUT_Symbol_HelixHeavy` reads back correct through
  `jawa/get_defs` (`pawnKindDef RUT_Jawa_Helix_Heavy`, `faction
  RUT_Jawa_AscendantHelix`, `numberToSpawn 1`).
- Not specific to one kind: the Heavy, the Specialist and a Grunt were each
  substituted in different placements.
- Not logged: `jawa/drain_log errorsOnly` shows zero lines naming Ashfall,
  Spire, KCSG, Helix or any of these defNames.

## the signature
The substituted pawn sits on the symbol's exact cell, carries the **right
faction** (Ascendant Helix) and **xenotype `Baseliner`** where the correct
pawns carry a faction xenotype (`RSW_RimMandrakeArkanian`,
`RSW_RimMandrakeKaminoan`). That is the shape of a `PawnGenerator` fallback
to `PawnKindDefOf.Colonist`, not of KCSG failing to read the symbol.

## why it matters beyond one dungeon
Every KCSG layout we ship stocks its guardians this way. A layout authored to
place a named boss can silently place a baseliner colonist instead, with the
right faction and no error — so **a per-defName pawn census of a KCSG layout
is not a deterministic check**, and any item that closes on "N pawns of kind
X appeared" has been reading a die roll.

## what to do
1. Read the generation path with RimSage (Desktop only): `SymbolResolver`
   for pawn symbols → whatever calls `PawnGenerator.GeneratePawn`, and find
   which `PawnGenerationRequest` failure re-requests `PawnKindDefOf.Colonist`.
   The faction-xenotype difference is the clue: `useFactionXenotypes` is
   true on all four Helix kinds, so a xenotype-resolution failure is the
   first suspect.
2. Then decide whether it is ours to fix (the kinds' own fields) or KCSG's.
   ⛔ Do not "fix" a layout on this finding — the layout is correct.

## criteria
- [ ] The substitution's cause named from the engine source, not inferred.
- [ ] A repeat test that says whether it is our PawnKindDefs or KCSG.
- [ ] If ours: fixed, and 5 placements in a row give the intended 5 kinds.
